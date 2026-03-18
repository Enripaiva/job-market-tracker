# transform.py
import pandas as pd
from datetime import datetime


# Colonne che vogliamo estrarre dal JSON grezzo di JSearch
COLUMNS_MAP = {
    "job_id":                   "job_id",
    "job_title":                "job_title",
    "employer_name":            "employer_name",
    "employer_logo":            "employer_logo",
    "job_employment_type":      "employment_type",
    "job_is_remote":            "is_remote",
    "job_city":                 "city",
    "job_state":                "state",
    "job_country":              "country",
    "job_posted_at_datetime_utc": "posted_at",
    "job_apply_link":           "apply_link",
    "job_description":          "description",
    "job_min_salary":           "salary_min",
    "job_max_salary":           "salary_max",
    "job_salary_currency":      "salary_currency",
    "job_salary_period":        "salary_period",
    "job_required_experience":  "experience_raw",   # dict — viene appiattito sotto
    "job_highlights":           "highlights_raw",   # dict — viene appiattito sotto
}


def extract(jobs_raw: list[dict]) -> pd.DataFrame:
    """Converte la lista di dict grezzi in DataFrame."""
    df = pd.DataFrame(jobs_raw)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pulisce e normalizza il DataFrame.
    - Seleziona e rinomina le colonne rilevanti
    - Converte i tipi
    - Appiattisce i campi nested (experience, highlights)
    - Aggiunge colonna di timestamp del fetch
    """
    # --- Seleziona solo colonne esistenti ---
    available = {k: v for k, v in COLUMNS_MAP.items() if k in df.columns}
    df = df[list(available.keys())].rename(columns=available)

    # --- Tipo data ---
    if "posted_at" in df.columns:
        df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce", utc=True)
        # Versione solo-data per comodità in Stata
        df["posted_date"] = df["posted_at"].dt.date

    # --- Boolean remote ---
    if "is_remote" in df.columns:
        df["is_remote"] = df["is_remote"].fillna(False).astype(bool)

    # --- Salari numerici ---
    for col in ["salary_min", "salary_max"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Appiattisci experience_raw ---
    if "experience_raw" in df.columns:
        exp_df = df["experience_raw"].apply(
            lambda x: x if isinstance(x, dict) else {}
        ).apply(pd.Series).add_prefix("exp_")
        df = pd.concat([df.drop(columns=["experience_raw"]), exp_df], axis=1)

    # --- Appiattisci highlights_raw (Qualifications, Responsibilities, Benefits) ---
    if "highlights_raw" in df.columns:
        for section in ["Qualifications", "Responsibilities", "Benefits"]:
            col_name = f"highlight_{section.lower()}"
            df[col_name] = df["highlights_raw"].apply(
                lambda x: " | ".join(x.get(section, [])) if isinstance(x, dict) else None
            )
        df = df.drop(columns=["highlights_raw"])

    # --- Pulizia descrizione (rimuovi newline multipli) ---
    if "description" in df.columns:
        df["description"] = (
            df["description"]
            .fillna("")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # --- Timestamp fetch ---
    df["fetched_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # --- Rimuovi duplicati per job_id ---
    if "job_id" in df.columns:
        df = df.drop_duplicates(subset=["job_id"])

    # --- Reset index ---
    df = df.reset_index(drop=True)

    print(f"Transform completato: {len(df)} offerte, {len(df.columns)} colonne.")
    return df


def load(df: pd.DataFrame, filepath: str) -> None:
    """Salva il DataFrame come CSV (debug/preview)."""
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"CSV salvato in: {filepath}")
