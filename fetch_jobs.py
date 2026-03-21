# fetch_jobs.py
import json
import time

import pandas as pd
import requests


def fetch_jobs(
    api_key: str,
    api_host: str,
    api_url: str,
    query: str,
    num_pages: int,
    date_posted: str,
    country: str,
) -> pd.DataFrame:

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
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
        }

        print(f"  Fetching page {page}/{num_pages}...")
        page_done = False

        for attempt in range(1, 4):
            try:
                response = requests.get(
                    api_url,
                    headers=headers,
                    params=params,
                    timeout=30,
                )
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
