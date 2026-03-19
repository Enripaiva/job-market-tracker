import argparse
from typing import Optional

import pandas as pd

from export import export_csv
from fetch_jobs import fetch_jobs, save_raw_json
from transform import transform


def run_extract(args: argparse.Namespace, base_name: str) -> pd.DataFrame:
    """Run the extract step and optionally persist the fetched payload."""
    print("[ 1/3 ] Fetch jobs...")

    df = fetch_jobs(
        query=args.query,
        num_pages=args.pages,
        date_posted=args.date,
        country=args.country,
        remote_only=args.remote_only,
    )

    if df.empty:
        print("\nNo jobs found. Try a different query.")
        raise SystemExit(0)

    if args.save_raw:
        save_raw_json(df.to_dict("records"), f"output/{base_name}_raw.json")

    return df


def run_transform(df: pd.DataFrame) -> pd.DataFrame:
    """Run the transform step and show the resulting schema preview."""
    print("\n[ 2/3 ] Transform with Pandas...")
    df_clean = transform(df)
    print(f"\nPreview columns: {list(df_clean.columns)}")
    return df_clean


def run_export(df_clean: pd.DataFrame, base_name: str, no_csv: bool) -> Optional[str]:
    """Run the export step using the configured output module."""
    print("\n[ 3/3 ] Export...")

    if no_csv:
        return None

    csv_path = f"output/{base_name}.csv"
    export_csv(df_clean, csv_path)
    return csv_path