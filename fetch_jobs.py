# fetch_jobs.py
import requests
import json
import time
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, DEFAULT_NUM_PAGES, DEFAULT_DATE_POSTED, DEFAULT_COUNTRY, DEFAULT_REMOTE_ONLY

def fetch_jobs(
    query: str,
    num_pages: int = DEFAULT_NUM_PAGES,
    date_posted: str = DEFAULT_DATE_POSTED,
    country: str = DEFAULT_COUNTRY,
    remote_only: bool = DEFAULT_REMOTE_ONLY
) -> list[dict]:

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    all_jobs = []

    for page in range(1, num_pages + 1):
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": date_posted,
            "country": country,
            "remote_jobs_only": str(remote_only).lower()
        }

        print(f"  Fetching page {page}/{num_pages}...")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = data.get("data", [])
            if not jobs:
                print(f"  No results on page {page}, stopping.")
                break

            all_jobs.extend(jobs)
            print(f"  Found {len(jobs)} jobs (total: {len(all_jobs)})")

            # Small pause between calls to reduce the chance of hitting rate limits
            if page < num_pages:
                time.sleep(1)

        except requests.exceptions.HTTPError as e:
            print(f"  HTTP error on page {page}: {e}")
            break
        except requests.exceptions.ConnectionError:
            print("  Connection error. Check your network.")
            break
        except requests.exceptions.Timeout:
            print("  Timeout. Try again later.")
            break

    print(f"\nFetch completed: {len(all_jobs)} total jobs.")
    return all_jobs


def save_raw_json(jobs: list[dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"Raw JSON saved to: {filepath}")
