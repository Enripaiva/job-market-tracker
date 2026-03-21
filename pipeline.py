import pandas as pd
from typing import TypeAlias

from export import export_csv, export_parquet
from fetch_jobs import fetch_jobs
from transform import transform


ExportPaths: TypeAlias = dict[str, str]


def build_export_paths(base_name: str) -> ExportPaths:
    """Build the output file paths for the main dataset and the summary."""
    return {
        "csv": f"output/{base_name}.csv",
        "parquet": f"output/{base_name}.parquet",
        "summary_csv": f"output/{base_name}_summary.csv",
        "summary_parquet": f"output/{base_name}_summary.parquet",
    }


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


def run_export(
    df_clean: pd.DataFrame, summary_df: pd.DataFrame, base_name: str
) -> ExportPaths:
    """Run the export step using the configured output module."""
    print("\n[ 3/3 ] Export...")

    export_paths = build_export_paths(base_name)

    export_csv(df_clean, export_paths["csv"])
    export_parquet(df_clean, export_paths["parquet"])
    export_csv(summary_df, export_paths["summary_csv"])
    export_parquet(summary_df, export_paths["summary_parquet"])

    return export_paths
