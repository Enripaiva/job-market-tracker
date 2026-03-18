import argparse
import os
from datetime import datetime

from fetch_jobs import fetch_jobs, save_raw_json
from transform import extract, transform
from export import export_dta, export_csv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download job postings from JSearch (Indeed/LinkedIn) and save them as .dta for Stata."
    )
    parser.add_argument(
        "query",
        type=str,
        help='Search string, e.g. "data engineer" or "AI economist italy"'
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Number of pages to fetch (10 jobs/page, default: 3)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="month",
        choices=["all", "today", "3days", "week", "month"],
        help="Posted date filter (default: month)"
    )
    parser.add_argument(
        "--country",
        type=str,
        default="it",
        help="2-letter ISO country code (default: it)"
    )
    parser.add_argument(
        "--remote-only",
        action="store_true",
        help="Include remote jobs only"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Do not save CSV (only .dta)"
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Also save raw JSON for debugging"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Timestamp for output file names
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = args.query.replace(" ", "_").replace("/", "-")[:40]
    base_name = f"{slug}_{ts}"

    os.makedirs("output", exist_ok=True)

    print(f"\n{'='*55}")
    print(f"  Job Market Tracker")
    print(f"  Query:   {args.query}")
    print(f"  Country: {args.country.upper()} | Date: {args.date} | Pages: {args.pages}")
    print(f"{'='*55}\n")

    # --- STEP 1: FETCH ---
    print("[ 1/3 ] Fetch jobs...")
    jobs_raw = fetch_jobs(
        query=args.query,
        num_pages=args.pages,
        date_posted=args.date,
        country=args.country,
        remote_only=args.remote_only
    )

    if not jobs_raw:
        print("\nNo jobs found. Try a different query.")
        return

    if args.save_raw:
        save_raw_json(jobs_raw, f"output/{base_name}_raw.json")

    # --- STEP 2: TRANSFORM ---
    print("\n[ 2/3 ] Transform with Pandas...")
    df_raw = extract(jobs_raw)
    df_clean = transform(df_raw)

    # Quick preview
    print(f"\nPreview columns: {list(df_clean.columns)}")

    # --- STEP 3: EXPORT ---
    print("\n[ 3/3 ] Export...")
    dta_path = f"output/{base_name}.dta"
    export_dta(df_clean, dta_path)

    if not args.no_csv:
        csv_path = f"output/{base_name}.csv"
        export_csv(df_clean, csv_path)

    print(f"\n{'='*55}")
    print(f"  Done! Files saved in /output/")
    print(f"  .dta  → {dta_path}")
    if not args.no_csv:
        print(f"  .csv  → {csv_path}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
