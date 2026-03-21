import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

from pipeline import ExportPaths, run_export, run_extract, run_transform
from queries import DEFAULT_QUERIES

# ── Defaults ────────────────────────────────────────────
DEFAULT_PAGES = 3
DEFAULT_DATE = "all"  # all | today | 3days | week | month
DEFAULT_COUNTRY = "it"
DEFAULT_RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
DEFAULT_JSEARCH_SEARCH_URL = "https://jsearch.p.rapidapi.com/search"
EXPORT_LABELS = {
    "csv": "main csv",
    "parquet": "main parquet",
    "summary_csv": "summary csv",
    "summary_parquet": "summary parquet",
}
# ────────────────────────────────────────────────────────


def get_default_query() -> str:
    if not DEFAULT_QUERIES:
        raise RuntimeError(
            "DEFAULT_QUERIES is empty. Add at least one query in queries.py or pass a query from CLI."
        )

    return DEFAULT_QUERIES[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download job postings from JSearch (Indeed/LinkedIn) and save them as CSV."
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help='Search string, e.g. "data engineer" or "AI economist italy". If omitted, all queries from queries.py are used.',
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_PAGES,
        help=f"Number of pages to fetch (10 jobs/page, default: {DEFAULT_PAGES})",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=DEFAULT_DATE,
        choices=["all", "today", "3days", "week", "month"],
        help=f"Posted date filter (default: {DEFAULT_DATE})",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=DEFAULT_COUNTRY,
        help=f"2-letter ISO country code (default: {DEFAULT_COUNTRY})",
    )
    return parser.parse_args()


def resolve_queries(query: str | None) -> list[str]:
    if query:
        return [query]
    return DEFAULT_QUERIES


def build_base_name(query: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = query.replace(" ", "_").replace("/", "-")[:40]
    return f"{slug}_{ts}"


def log_run_start(queries: list[str], args: argparse.Namespace) -> None:
    query_label = queries[0] if len(queries) == 1 else f"{len(queries)} queries"
    print(f"\n{'='*55}")
    print("  Job Market Tracker")
    print(f"  Query:   {query_label}")
    print(
        f"  Country: {args.country.upper()} | Date: {args.date} | Pages: {args.pages}"
    )
    print(f"{'='*55}\n")


def load_api_settings() -> tuple[str, str]:
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    api_key = (os.getenv("RAPIDAPI_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("Missing RAPIDAPI_KEY in .env")

    api_host = (os.getenv("RAPIDAPI_HOST") or "").strip() or DEFAULT_RAPIDAPI_HOST
    return api_key, api_host


def log_run_end(export_paths: ExportPaths) -> None:
    print(f"\n{'='*55}")
    print("  Done! Files saved in /output/")
    for key, label in EXPORT_LABELS.items():
        path = export_paths.get(key)
        if path:
            print(f"  {label:<15} → {path}")
    print(f"{'='*55}\n")


def main() -> None:
    args = parse_args()
    queries = resolve_queries(args.query)
    run_label = queries[0] if len(queries) == 1 else "multi_query"
    base_name = build_base_name(run_label)
    api_key, api_host = load_api_settings()

    os.makedirs("output", exist_ok=True)
    log_run_start(queries, args)

    frames: list[pd.DataFrame] = []
    for query in queries:
        df = run_extract(
            query=query,
            num_pages=args.pages,
            date_posted=args.date,
            country=args.country,
            api_key=api_key,
            api_host=api_host,
            api_url=DEFAULT_JSEARCH_SEARCH_URL,
        )
        if df.empty:
            continue

        df_clean = run_transform(df)
        df_clean["search_query"] = query
        frames.append(df_clean)

    if not frames:
        print("\nNo jobs found for any query.")
        raise SystemExit(0)

    df_clean = pd.concat(frames, ignore_index=True)

    summary_df = (
        df_clean.groupby("search_query")
        .size()
        .reset_index(name="job_count")
    )

    export_paths = run_export(df_clean, summary_df, base_name)

    log_run_end(export_paths)


if __name__ == "__main__":
    main()
