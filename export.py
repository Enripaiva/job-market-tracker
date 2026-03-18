# export.py
"""
Export del DataFrame in formato .dta nativo Stata.
Usiamo pyreadstat che genera Stata 14/15 .dta senza bisogno di Stata installato.

Nota: Stata ha alcune limitazioni sui tipi:
  - Nomi colonna max 32 caratteri
  - Stringhe: max 2045 char in Stata 14, 2M in Stata 15 (strL)
  - Bool → int (0/1)
  - datetime con timezone → converti in naive UTC prima
"""
import pandas as pd
import pyreadstat
from pathlib import Path


def _prepare_for_stata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adatta il DataFrame alle limitazioni di Stata prima dell'export.
    """
    df = df.copy()

    # 1. Nomi colonna: max 32 char, no spazi, no caratteri speciali
    df.columns = [
        col[:32].replace(" ", "_").replace("-", "_").replace(".", "_")
        for col in df.columns
    ]

    # 2. Bool → int8
    bool_cols = df.select_dtypes(include=["bool"]).columns
    for col in bool_cols:
        df[col] = df[col].astype("int8")

    # 3. datetime con timezone → naive UTC (Stata non gestisce tz)
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)

    # 4. Tronca stringhe troppo lunghe (Stata 14 max 2045 char)
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str).str[:2045]

    # 5. Converti date in stringa (Stata non ha tipo date nativo semplice)
    date_cols = [c for c in df.columns if "date" in c and df[c].dtype == "object"]
    for col in date_cols:
        df[col] = df[col].astype(str)

    return df


def export_dta(df: pd.DataFrame, filepath: str, stata_version: int = 118) -> None:
    """
    Salva il DataFrame in formato .dta per Stata.

    Args:
        df:             DataFrame pulito
        filepath:       percorso output es. "output/jobs.dta"
        stata_version:  118 = Stata 14/15 (default), 117 = Stata 13
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    df_stata = _prepare_for_stata(df)

    # Label per le variabili (usa i nomi originali come label)
    variable_labels = {col: col.replace("_", " ").title() for col in df_stata.columns}

    pyreadstat.write_dta(
        df_stata,
        filepath,
        version=stata_version,
        variable_value_labels={},
        variable_labels=variable_labels
    )

    print(f".dta salvato in: {filepath}")
    print(f"  Osservazioni: {len(df_stata)}")
    print(f"  Variabili:    {len(df_stata.columns)}")
    print(f"  Compatibile con Stata 14+ (version={stata_version})")


def export_csv(df: pd.DataFrame, filepath: str) -> None:
    """Salva anche un CSV come backup / preview rapida."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"CSV salvato in: {filepath}")
