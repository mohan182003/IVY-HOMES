import requests
import time
import json
import string
from collections import deque
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Base URL
BASE_URL = "http://35.200.185.69:8000"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# API Versions and their name limits
VERSION_LIMITS = {"v1": 10, "v2": 12, "v3": 15}

# API Rate Limit Control
REQUEST_LIMIT = 100  # Max requests per minute
COOLDOWN_TIME = 60  # Time to wait after hitting the rate limit
THREADS = 5  # Number of parallel threads
MAX_RETRIES = 5  # Maximum retries per request
IP_BAN_COOLDOWN = 1800  # 30 minutes cooldown if IP is temporarily banned

# Characters to query (only lowercase a-z and numbers 0-9)
CHARACTERS = list(string.ascii_lowercase) + [str(i) for i in range(10)]

# Tracking request count and unique names count
total_requests = 0
total_unique_names = 0

def log_skipped_query(query, reason):
    """Log skipped queries for later review."""
    with open("skipped_queries.log", "a") as f:
        f.write(f"{query} - {reason}\n")
    print(f" Skipped query logged: {query} ({reason})")

# Load existing names from `final_versions_with_names.json`
if os.path.exists("final_versions_with_names.json"):
    with open("final_versions_with_names.json", "r") as f:
        final_versions_with_names = json.load(f)
    final_versions_with_names = {version: set(names) for version, names in final_versions_with_names.items()}
    print(f" Loaded {sum(len(names) for names in final_versions_with_names.values())} existing names.")
else:
    final_versions_with_names = {version: set() for version in VERSION_LIMITS.keys()}

# Load BFS checkpoint (last searched prefix)
if os.path.exists("final_bfs_checkpoint.json"):
    with open("final_bfs_checkpoint.json", "r") as f:
        final_bfs_checkpoint = json.load(f)
    print(f" Resuming BFS from checkpoint: {final_bfs_checkpoint}")
else:
    final_bfs_checkpoint = {version: None for version in VERSION_LIMITS.keys()}  # Start fresh if no checkpoint exists

request_count = 0
request_lock = time.time()  # Track request timing to respect rate limits

def save_progress():
    """Save progress to final_versions_with_names.json and final_bfs_checkpoint.json."""
    with open("final_versions_with_names.json", "w") as f:
        json.dump({v: list(final_versions_with_names[v]) for v in VERSION_LIMITS.keys()}, f, indent=4)
    with open("final_bfs_checkpoint.json", "w") as f:
        json.dump(final_bfs_checkpoint, f, indent=4)
    with open("final_requests.json", "w") as f:
        json.dump(total_requests, f, indent=4)  
    
    print(" Progress saved to final_versions_with_names.json and final_bfs_checkpoint.json.")

def fetch_names(version, query):
    """Fetch names for a given prefix with retry limits and proper error handling."""
    global request_count, request_lock, total_requests, total_unique_names
    url = f"{BASE_URL}/{version}/autocomplete?query={query}"

    for attempt in range(1, MAX_RETRIES + 1):
        print(f" Attempt {attempt}: Fetching {url}")

        # Handle rate limits
        if request_count >= REQUEST_LIMIT:
            elapsed = time.time() - request_lock
            if elapsed < 60:
                wait_time = 60 - elapsed
                print(f" Rate limit approaching! Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            request_count = 0  # Reset counter
            request_lock = time.time()

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            request_count += 1
            total_requests += 1

            if response.status_code == 200:
                data = response.json()
                names = set(data.get("results", []))

                new_names = names - final_versions_with_names[version]
                if new_names:
                    final_versions_with_names[version].update(new_names)
                    total_unique_names += len(new_names)
                    print(f" Added {len(new_names)} new names to {version}")
                    save_progress()

                return query if len(names) == VERSION_LIMITS[version] else None

            elif response.status_code == 429:
                print(f"⏳ Rate limit hit on {version}. Retrying in {COOLDOWN_TIME} seconds...")
                time.sleep(COOLDOWN_TIME)
            else:
                print(f" Unexpected Status {response.status_code} for {version}. Retrying...")

        except requests.exceptions.RequestException as e:
            print(f" Request failed: {e}")
            if "Max retries exceeded" in str(e):
                print(f" Possible temporary IP ban detected. Waiting {IP_BAN_COOLDOWN} seconds before resuming...")
                save_progress()
                time.sleep(IP_BAN_COOLDOWN)
                return None
            if attempt < MAX_RETRIES:
                wait_time = min(5 * (2 ** (attempt - 1)), 300)  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retrying... (Attempt {attempt})")
                time.sleep(wait_time)
            else:
                print(" Max retries reached. Skipping query.")
                log_skipped_query(query, str(e))
                return None

def ordered_prefix_search(version):
    """Perform BFS search with proper checkpointing and rate limit handling."""
    queue = deque(CHARACTERS)
    last_prefix = final_bfs_checkpoint.get(version)
    if last_prefix:
        queue = deque([p for p in CHARACTERS if p >= last_prefix])
        print(f" Resuming {version} from prefix: {last_prefix}")
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        while queue:
            prefix = queue.popleft()
            final_bfs_checkpoint[version] = prefix
            new_prefix = fetch_names(version, prefix)
            if new_prefix:
                for char in CHARACTERS:
                    queue.append(new_prefix + char)

try:
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(ordered_prefix_search, version): version for version in VERSION_LIMITS.keys()}
        for future in as_completed(futures):
            print(f" Completed extraction for {futures[future]}")
except Exception as e:
    print(f" Error in ThreadPoolExecutor: {e}")

finally:
    save_progress()

print(f"\n Extraction Complete! Total unique names: {total_unique_names}")
print(f" Total API requests made: {total_requests}")
for version in VERSION_LIMITS.keys():
    print(f" {version}: {len(final_versions_with_names[version])} names extracted")
