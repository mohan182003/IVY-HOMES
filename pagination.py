import requests
import time

# API Base URL
BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def check_pagination(query="a", max_pages=10):
    """Fetch multiple pages and compare results to check if pagination works."""
    seen_results = set()  # Track names seen before

    for page in range(10, max_pages + 1):
        url = f"{BASE_URL}?query={query}&page={page}"
        print(f"🔍 Fetching Page {page}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                names = data.get("results", [])

                if not names:
                    print(f" Page {page} returned no names. Stopping.")
                    break  # Stop if an empty page is reached

                # Print first few names to detect duplicates
                print(f"Page {page}: {names[:5]}... ({len(names)} total)")

                # Check if results are unique
                if set(names).issubset(seen_results):
                    print(f" Page {page} is returning duplicate names. Pagination may not be working!")
                    break  # Stop if we detect repeated pages
                
                seen_results.update(names)  # Store results to check for repeats

            elif response.status_code == 429:
                print(" Rate limit hit. Waiting before retrying...")
                time.sleep(5)
                continue

            else:
                print(f" Unexpected Status {response.status_code}. Stopping.")
                break

        except requests.exceptions.RequestException as e:
            print(f" Request failed: {e}")
            break

# Run the pagination check
check_pagination()