import requests
import time
import json

# API Base URL
BASE_URL = "http://35.200.185.69:8000"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# API Versions to test
VERSIONS = ["v1", "v2", "v3"]

# Common endpoints to test
ENDPOINTS = [
    "autocomplete",
    "autocomplete/all",
    "autocomplete/full",
    "autocomplete/names",
    "autocomplete/suggestions",
    "autocomplete/popular",
    "autocomplete/top",
    "search",
    "search/names",
    "search/suggestions",
    "search/popular",
    "suggestions",
    "names",
    "status",
    "version",
    "info",
    "meta",
    "config",
    "stats",
    "health",
    "rate_limit",
    "throttling",
    "limits",
    "data",
    "list",
    "all",
    "export",
    "download",
    "logs",
    "validate",
    "graphql",
    "api/graphql"
]

# Query parameters to test
QUERY_PARAMS = [
    "?query=a",
    "?query=",
    "?query=*&limit=100",
    "?query=a&page=2",
    "?query=a&sort=asc",
    "?query=a&type=name",
    "?query=a&lang=en"
]

# Storage for results
valid_endpoints = {}

def test_endpoint(version, endpoint, query=""):
    """Test an API endpoint and log results based on status codes."""
    url = f"{BASE_URL}/{version}/{endpoint}{query}"
    print(f" Testing: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        status = response.status_code

        if status == 200:
            print(f" FOUND: {url}")
            valid_endpoints[url] = response.json()

        elif status in [301, 302]:
            print(f" Redirect found: {url} (Check where it leads)")

        elif status == 400:
            print(f" Bad Request: {url}")

        elif status in [401, 403]:
            print(f" Access Denied: {url} (Requires authentication)")

        elif status == 404:
            print(f" Not Found: {url}")

        elif status == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f" Rate limit hit! Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            return test_endpoint(version, endpoint, query)

        elif 500 <= status < 600:
            print(f" Server Error {status}: {url} (Retrying after 10s)")
            time.sleep(10)
            return test_endpoint(version, endpoint, query)

        else:
            print(f"⚠️ Unexpected Status {status}: {url}")

    except requests.exceptions.RequestException as e:
        print(f" Request Failed: {url} | Error: {e}")

# Iterate through API versions, endpoints, and query params
for version in VERSIONS:
    for endpoint in ENDPOINTS:
        for query in QUERY_PARAMS:
            test_endpoint(version, endpoint, query)

# Save discovered endpoints to a file
with open("discovered_endpoints.json", "w") as f:
    json.dump(valid_endpoints, f, indent=4)

print("\n Scan Complete! Check discovered_endpoints.json for results.")
