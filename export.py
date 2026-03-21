import pandas as pd
import pyreadstat
from pathlib import Path


def _prepare_for_stata(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # 1. Column names: max 32 chars, no spaces, no special characters
    df.columns = [
        col[:32].replace(" ", "_").replace("-", "_").replace(".", "_")
        for col in df.columns
    ]

    # 2. Bool -> int8
    bool_cols = df.select_dtypes(include=["bool"]).columns
    for col in bool_cols:
        df[col] = df[col].astype("int8")

    # 3. Timezone-aware datetime -> naive UTC (Stata has no tz support)
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)

    # 4. Truncate very long strings (Stata 14 max 2045 chars)
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str).str[:2045]

    # 5. Convert date-like object columns to strings
    date_cols = [c for c in df.columns if "date" in c and df[c].dtype == "object"]
    for col in date_cols:
        df[col] = df[col].astype(str)

    return df


def export_dta(df: pd.DataFrame, filepath: str, stata_version: int = 15) -> None:

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    df_stata = _prepare_for_stata(df)

    try:
        pyreadstat.write_dta(
            df_stata,
            filepath,
            version=stata_version,
            variable_value_labels={}
        )
    except Exception as exc:
        # Some pyreadstat builds do not accept the version parameter.
        if "Version not supported" not in str(exc):
            raise
        pyreadstat.write_dta(
            df_stata,
            filepath,
            variable_value_labels={}
        )
        stata_version = -1

    print(f".dta saved to: {filepath}")
    print(f"  Observations: {len(df_stata)}")
    print(f"  Variables:    {len(df_stata.columns)}")
    if stata_version == -1:
        print("  .dta written with pyreadstat default format version")
    else:
        print(f"  Compatible with Stata (version={stata_version})")


def export_csv(df: pd.DataFrame, filepath: str) -> None:
    """Save CSV as backup / quick preview."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"CSV saved to: {filepath}")


def export_parquet(df: pd.DataFrame, filepath: str) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(filepath, index=False)
    print(f"Parquet saved to: {filepath}")
