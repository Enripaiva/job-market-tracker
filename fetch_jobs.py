# fetch_jobs.py
import requests
import json
import time
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, DEFAULT_NUM_PAGES, DEFAULT_DATE_POSTED, DEFAULT_COUNTRY, DEFAULT_REMOTE_ONLY

def fetch_jobs(
    query: str,
    num_pages: int = DEFAULT_NUM_PAGES,
    date_posted: str = DEFAULT_DATE_POSTED,
    country: str = DEFAULT_COUNTRY,
    remote_only: bool = DEFAULT_REMOTE_ONLY
) -> list[dict]:
    """
    Chiama JSearch API e ritorna una lista di offerte di lavoro (JSON grezzo).
    
    Args:
        query:       stringa di ricerca es. "data engineer" o "AI machine learning"
        num_pages:   quante pagine di risultati (10 offerte per pagina)
        date_posted: filtro data — "all", "today", "3days", "week", "month"
        country:     codice paese ISO 2 es. "it", "us", "gb"
        remote_only: se True filtra solo offerte remote
    
    Returns:
        Lista di dict (offerte grezze da JSearch)
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    all_jobs = []

    for page in range(1, num_pages + 1):
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": date_posted,
            "country": country,
            "remote_jobs_only": str(remote_only).lower()
        }

        print(f"  Fetching page {page}/{num_pages}...")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = data.get("data", [])
            if not jobs:
                print(f"  Nessun risultato a pagina {page}, stop.")
                break

            all_jobs.extend(jobs)
            print(f"  Trovate {len(jobs)} offerte (totale: {len(all_jobs)})")

            # Pausa educata tra le chiamate per non bucare il rate limit
            if page < num_pages:
                time.sleep(1)

        except requests.exceptions.HTTPError as e:
            print(f"  Errore HTTP pagina {page}: {e}")
            break
        except requests.exceptions.ConnectionError:
            print("  Errore di connessione. Controlla la rete.")
            break
        except requests.exceptions.Timeout:
            print("  Timeout. Riprova più tardi.")
            break

    print(f"\nFetch completato: {len(all_jobs)} offerte totali.")
    return all_jobs


def save_raw_json(jobs: list[dict], filepath: str) -> None:
    """Salva il JSON grezzo per debug / archivio."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"JSON grezzo salvato in: {filepath}")
