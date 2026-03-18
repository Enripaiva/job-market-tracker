# fetch_jobs.py
import requests
import json
import time
import pandas as pd
from config import RAPIDAPI_KEY, RAPIDAPI_HOST

def fetch_jobs(
    query: str,
    num_pages: int,
    date_posted: str,
    country: str,
    remote_only: bool
) -> pd.DataFrame:

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    all_jobs = []
    fatal = False

    for page in range(1, num_pages + 1):
        if fatal:
            break

        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": date_posted,
            "country": country,
            "remote_jobs_only": str(remote_only).lower()
        }

        print(f"  Fetching page {page}/{num_pages}...")
        page_done = False

        for attempt in range(1, 4):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                print(f"  DEBUG raw response: {json.dumps(data, indent=2)[:500]}")

                jobs = data.get("data", [])
                if not jobs:
                    api_status = data.get("status", "unknown")
                    print(f"  No results on page {page} (API status: {api_status}), stopping.")
                    fatal = True
                    break

                all_jobs.extend(jobs)
                print(f"  Found {len(jobs)} jobs (total: {len(all_jobs)})")
                page_done = True
                break

            except requests.exceptions.HTTPError as e:
                print(f"  HTTP error on page {page}: {e}")
                fatal = True
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"  {type(e).__name__} on page {page}, attempt {attempt}/3.")
                if attempt < 3:
                    time.sleep(3 * attempt)
                else:
                    fatal = True

        if page_done and page < num_pages:
            time.sleep(1)

    print(f"\nFetch completed: {len(all_jobs)} total jobs.")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_jobs)
    return df


def save_raw_json(jobs: list[dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"Raw JSON saved to: {filepath}")
