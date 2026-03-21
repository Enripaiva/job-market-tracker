# transform.py
import pandas as pd
from datetime import datetime, timezone


# Columns to extract from JSearch raw JSON
COLUMNS_MAP = {
    "job_title":                "job_title",
    "employer_name":            "employer_name",
    "job_employment_type":      "employment_type",
    "job_is_remote":            "is_remote",
    "job_city":                 "city",
    "job_state":                "state",
    "job_country":              "country",
    "job_description":          "description",
}

OUTPUT_COLUMNS = [
    "job_title",
    "employer_name",
    "city",
    "country",
    "description",
    "fetched_at",
]


def _select_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[list(COLUMNS_MAP.keys())].rename(columns=COLUMNS_MAP)

def _normalize_remote_flag(df: pd.DataFrame) -> pd.DataFrame:
    df["is_remote"] = df["is_remote"].fillna(False).astype(bool)
    return df

def _clean_description(df: pd.DataFrame) -> pd.DataFrame:
    df["description"] = (
        df["description"]
        .fillna("")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df

def _add_fetch_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return df

def _select_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.filter(items=OUTPUT_COLUMNS)

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the extracted jobs DataFrame."""
    # Work on a copy so callers keep their original DataFrame untouched.
    df = df.copy()

    df = _select_and_rename_columns(df)
    df = _normalize_remote_flag(df)
    df = _clean_description(df)
    df = _add_fetch_timestamp(df)
    df = _select_output_columns(df)
    df = df.reset_index(drop=True)

    print(f"Transform completed: {len(df)} jobs, {len(df.columns)} columns.")
    return df

