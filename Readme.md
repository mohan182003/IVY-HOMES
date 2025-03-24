# API & Autocomplete Name Extraction

## Problem Statement

We were given access to an autocomplete API at `http://35.200.185.69:8000` with the objective of extracting all possible names available through the autocomplete system. The API had no official documentation, requiring us to explore and understand its behavior through testing.

## Approach

To systematically extract all possible names, we used a combination of brute-force techniques, directory enumeration, and API fuzzing. The key steps taken were:

### 1. Initial Exploration

- Discovered the known endpoint: `/v1/autocomplete?query=<string>`
- Identified multiple API versions: `/v1/`, `/v2/`, `/v3/`
- Observed different name limits per version:
  - **v1** → 10 names per request
  - **v2** → 12 names per request
  - **v3** → 15 names per request

### 2. Enumeration Techniques Used

#### **ffuf (Fuzz Faster U Fool)**
- Used to brute-force possible hidden API endpoints and parameters.

#### **gau (Get All URLs)**
- Collected publicly available API endpoints related to the target.

#### **dirsearch**
- Used for discovering directories and additional API functionalities.

#### **SQL Injection & Other Attacks**
- Attempted SQL-based enumeration but found no SQL injection vulnerabilities.

#### **Brute-Force Using BFS Strategy**
- Implemented a breadth-first search (BFS) algorithm with character-based expansion to systematically extract names.

### 3. Handling API Rate Limits & IP Bans

- The API imposed request rate limits.
- Encountered **HTTP 429 (Too Many Requests)** responses.
- Implemented **request throttling** and **exponential backoff** to avoid bans.
- Used **proxies and IP rotation** to bypass rate limits when necessary.
- Introduced **parallel processing** using **ThreadPoolExecutor** to speed up enumeration while maintaining rate limits.
- **Optimized** request scheduling to distribute queries across multiple threads, reducing overall execution time.
- Implemented **BFS-based prefix search** to ensure efficient and systematic enumeration.



## API Behavior Observations

During testing, we found some surprising behaviors:

- The API returned default responses for certain queries:
  - **"a", "#", "+", "&"** in v1 always returned the same set of names.
  - **"0", "#", "+", "&"** in v2 and v3 returned identical responses.
- Querying **non-alphanumeric characters** sometimes produced results unrelated to expected patterns.

## Results

| Metric | Value |
|--------|-------|
| Total API Requests Made | around 22,873 |
| Total Unique Names Extracted | 29943 |
| Unique Names in v1 | 12004 |
| Unique Names in v2 | 8777 |
| Unique Names in v3 | 9162 |
| Number of Hidden Endpoints Found | None except for the 3 already mentioned |
| Rate-Limited Requests Encountered | 100 per minute |

## Improvements & Future Work

- **Optimize API Calls**: Implement adaptive rate control based on observed API behavior.
- **Automated Proxy Rotation**: To prevent IP bans more effectively.
- **Explore Other HTTP Methods**: Check for additional functionality beyond GET requests.
- **Investigate Non-Alphanumeric Queries Further**: To determine if more unique responses exist.

## How to Run the Script

### Install dependencies:
```sh
pip install requests
```

### Run the script:
```sh
python final_find_names.py
```

Extracted names will be saved in `final_versions_with_names.json`.

## Submission Contents

- **Working Code** (`final_find_names.py`)
- **README** (This file)
- **Enumeration Logs & Findings**
- **Total Requests & Extracted Data Report**

---

This project demonstrated the importance of API security and systematic exploration when documentation is unavailable. The methodology used here can be extended to other API enumeration challenges.
