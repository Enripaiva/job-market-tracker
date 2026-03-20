import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from pipeline import run_export, run_extract, run_transform

# ── Defaults ────────────────────────────────────────────
DEFAULT_PAGES   = 5
DEFAULT_DATE    = "all"   # all | today | 3days | week | month
DEFAULT_COUNTRY = "it"
DEFAULT_RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
# ────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
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


def build_base_name(query: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = query.replace(" ", "_").replace("/", "-")[:40]
    return f"{slug}_{ts}"


def load_api_settings() -> tuple[str, str]:
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    api_key = (os.getenv("RAPIDAPI_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("Missing RAPIDAPI_KEY in .env")

    api_host = (os.getenv("RAPIDAPI_HOST") or "").strip() or DEFAULT_RAPIDAPI_HOST
    return api_key, api_host


def log_run_start(args: argparse.Namespace) -> None:
    print(f"\n{'='*55}")
    print("  Job Market Tracker")
    print(f"  Query:   {args.query}")
    print(f"  Country: {args.country.upper()} | Date: {args.date} | Pages: {args.pages}")
    print(f"{'='*55}\n")


def log_run_end(csv_path: Optional[str]) -> None:
    print(f"\n{'='*55}")
    print("  Done! Files saved in /output/")
    if csv_path:
        print(f"  .csv  → {csv_path}")
    print(f"{'='*55}\n")


def main() -> None:
    args = parse_args()
    base_name = build_base_name(args.query)
    api_key, api_host = load_api_settings()

    os.makedirs("output", exist_ok=True)
    log_run_start(args)

    df = run_extract(args, base_name, api_key, api_host)

    df_clean = run_transform(df)

    csv_path = run_export(df_clean, base_name, args.no_csv)
    
    log_run_end(csv_path)


if __name__ == "__main__":
    main()
