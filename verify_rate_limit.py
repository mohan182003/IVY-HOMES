import requests
import time

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete?query=a"  # Test query
HEADERS = {"User-Agent": "Mozilla/5.0"}

time.sleep(60)

def find_rate_limit():
    request_count = 0
    start_time = time.time()
    
    while True:
        try:
            response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
            request_count += 1
            
            if response.status_code == 429:
                print(f" Rate limit reached after {request_count} requests.")
                break
            elif response.status_code != 200:
                print(f" Unexpected response {response.status_code}, stopping.")
                break
            
            print(f" Request {request_count} successful.")
            
        except requests.exceptions.RequestException as e:
            print(f" Request failed: {e}")
    wait_time=60-(time.time()-start_time)
    time.sleep(wait_time)
    try:
            response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
            request_count += 1
            
            if response.status_code == 429:
                print(f" Rate limit reached after {request_count} requests.")
                
            elif response.status_code != 200:
                print(f" Unexpected response {response.status_code}, stopping.")
                
            
            print(f" Request {request_count} successful.")
        
    except requests.exceptions.RequestException as e:
            print(f" Request failed: {e}")

    
    elapsed_time = time.time() - start_time
    print(f" Time taken: {elapsed_time:.2f} seconds")
    print(f" Estimated requests per minute: {request_count / (elapsed_time / 60):.2f}")

if __name__ == "__main__":
    find_rate_limit()
