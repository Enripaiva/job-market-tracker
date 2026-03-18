# main.py
"""
Job Market Tracker — entry point
Uso:
    python main.py "data engineer italy"
    python main.py "AI machine learning" --pages 5 --date today --country us
    python main.py "economist" --remote-only --no-csv
"""
import argparse
import os
from datetime import datetime

from fetch_jobs import fetch_jobs, save_raw_json
from transform import extract, transform
from export import export_dta, export_csv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scarica offerte di lavoro da JSearch (Indeed/LinkedIn) e salva in .dta per Stata."
    )
    parser.add_argument(
        "query",
        type=str,
        help='Stringa di ricerca es. "data engineer" oppure "AI economist italy"'
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Numero di pagine da scaricare (10 offerte/pagina, default: 3)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="month",
        choices=["all", "today", "3days", "week", "month"],
        help="Filtro data pubblicazione (default: month)"
    )
    parser.add_argument(
        "--country",
        type=str,
        default="it",
        help="Codice paese ISO 2 lettere (default: it)"
    )
    parser.add_argument(
        "--remote-only",
        action="store_true",
        help="Mostra solo offerte remote"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Non salvare il CSV (solo .dta)"
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Salva anche il JSON grezzo per debug"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Timestamp per i nomi file
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = args.query.replace(" ", "_").replace("/", "-")[:40]
    base_name = f"{slug}_{ts}"

    os.makedirs("output", exist_ok=True)

    print(f"\n{'='*55}")
    print(f"  Job Market Tracker")
    print(f"  Query:   {args.query}")
    print(f"  Paese:   {args.country.upper()} | Data: {args.date} | Pagine: {args.pages}")
    print(f"{'='*55}\n")

    # --- STEP 1: FETCH ---
    print("[ 1/3 ] Fetch offerte...")
    jobs_raw = fetch_jobs(
        query=args.query,
        num_pages=args.pages,
        date_posted=args.date,
        country=args.country,
        remote_only=args.remote_only
    )

    if not jobs_raw:
        print("\nNessuna offerta trovata. Prova con una query diversa.")
        return

    if args.save_raw:
        save_raw_json(jobs_raw, f"output/{base_name}_raw.json")

    # --- STEP 2: TRANSFORM ---
    print("\n[ 2/3 ] Trasformazione con Pandas...")
    df_raw = extract(jobs_raw)
    df_clean = transform(df_raw)

    # Preview rapida
    print(f"\nAnteprima colonne: {list(df_clean.columns)}")

    # --- STEP 3: EXPORT ---
    print("\n[ 3/3 ] Export...")
    dta_path = f"output/{base_name}.dta"
    export_dta(df_clean, dta_path)

    if not args.no_csv:
        csv_path = f"output/{base_name}.csv"
        export_csv(df_clean, csv_path)

    print(f"\n{'='*55}")
    print(f"  Fatto! File salvati in /output/")
    print(f"  .dta  → {dta_path}")
    if not args.no_csv:
        print(f"  .csv  → {csv_path}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
