import argparse
import os
from datetime import datetime

from fetch_jobs import fetch_jobs, save_raw_json
from transform import transform
from export import export_csv

# ── Defaults ────────────────────────────────────────────
DEFAULT_PAGES   = 100
DEFAULT_DATE    = "all"   # all | today | 3days | week | month
DEFAULT_COUNTRY = "it"
# ────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download job postings from JSearch (Indeed/LinkedIn) and save them as CSV."
    )
    parser.add_argument(
        "query",
        type=str,
        help='Search string, e.g. "data engineer" or "AI economist italy"'
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_PAGES,
        help=f"Number of pages to fetch (10 jobs/page, default: {DEFAULT_PAGES})"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=DEFAULT_DATE,
        choices=["all", "today", "3days", "week", "month"],
        help=f"Posted date filter (default: {DEFAULT_DATE})"
    )
    parser.add_argument(
        "--country",
        type=str,
        default=DEFAULT_COUNTRY,
        help=f"2-letter ISO country code (default: {DEFAULT_COUNTRY})"
    )
    parser.add_argument(
        "--remote-only",
        action="store_true",
        help="Include remote jobs only"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Do not save CSV file"
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
    print("[ 1/2 ] Fetch jobs...")
    df = fetch_jobs(
        query=args.query,
        num_pages=args.pages,
        date_posted=args.date,
        country=args.country,
        remote_only=args.remote_only
    )

    if df.empty:
        print("\nNo jobs found. Try a different query.")
        return

    if args.save_raw:
        save_raw_json(df.to_dict('records'), f"output/{base_name}_raw.json")

    # --- STEP 2: TRANSFORM ---
    print("\n[ 2/2 ] Transform with Pandas...")
    df_clean = transform(df)

    # Quick preview
    print(f"\nPreview columns: {list(df_clean.columns)}")

    # --- STEP 3: EXPORT ---
    print("\n[ 2/2 ] Export...")

    if not args.no_csv:
        csv_path = f"output/{base_name}.csv"
        export_csv(df_clean, csv_path)

    print(f"\n{'='*55}")
    print(f"  Done! Files saved in /output/")
    if not args.no_csv:
        print(f"  .csv  → {csv_path}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
