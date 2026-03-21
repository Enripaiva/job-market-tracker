import pandas as pd

from export import export_csv
from fetch_jobs import fetch_jobs
from transform import transform


def run_extract(
    query: str,
    num_pages: int,
    date_posted: str,
    country: str,
    api_key: str,
    api_host: str,
    api_url: str,
) -> pd.DataFrame:
    """Fetch jobs for a single search query."""
    print(f"[ 1/3 ] Fetch jobs for: {query}")

    df = fetch_jobs(
        api_key=api_key,
        api_host=api_host,
        api_url=api_url,
        query=query,
        num_pages=num_pages,
        date_posted=date_posted,
        country=country,
    )

    if df.empty:
        print(f"\nNo jobs found for query: {query}")

    return df


def run_transform(df: pd.DataFrame) -> pd.DataFrame:
    """Run the transform step and show the resulting schema preview."""
    print("\n[ 2/3 ] Transform with Pandas...")
    df_clean = transform(df)
    print(f"\nPreview columns: {list(df_clean.columns)}")
    return df_clean


def run_export(df_clean: pd.DataFrame, base_name: str) -> str:
    """Run the export step using the configured output module."""
    print("\n[ 3/3 ] Export...")

    csv_path = f"output/{base_name}.csv"
    export_csv(df_clean, csv_path)
    return csv_path