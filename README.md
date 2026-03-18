# Job Market Tracker 📊

Pipeline Python che scarica offerte di lavoro da **JSearch** (Indeed, LinkedIn, Glassdoor via RapidAPI), le pulisce con **Pandas** e le esporta in formato **.dta nativo Stata**.

---

## Struttura

```
job-market-tracker/
├── config.py          # API key e parametri default
├── fetch_jobs.py      # Chiamata API → JSON grezzo
├── transform.py       # Pandas: pulizia e normalizzazione
├── export.py          # Export → .dta (Stata) + .csv
├── main.py            # Entry point con argparse
├── requirements.txt
└── output/            # File generati (gitignored)
```

---

## Setup

```bash
# 1. Clona il repo
git clone https://github.com/TUO_USERNAME/job-market-tracker.git
cd job-market-tracker

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Inserisci la tua API key in config.py
#    Ottienila su: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
```

---

## Uso

```bash
# Ricerca base (default: Italia, ultimo mese, 3 pagine = ~30 offerte)
python main.py "data engineer"

# Ricerca avanzata
python main.py "AI economist" --pages 5 --date week --country us

# Solo remote, senza CSV
python main.py "machine learning" --remote-only --no-csv

# Salva anche il JSON grezzo (utile per debug)
python main.py "quantitative analyst" --save-raw
```

### Parametri disponibili

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `query` | — | Stringa di ricerca (obbligatorio) |
| `--pages` | 3 | Pagine da scaricare (10 offerte/pagina) |
| `--date` | month | `all`, `today`, `3days`, `week`, `month` |
| `--country` | it | Codice ISO paese (`it`, `us`, `gb`, ...) |
| `--remote-only` | False | Solo offerte remote |
| `--no-csv` | False | Non genera il CSV |
| `--save-raw` | False | Salva il JSON grezzo |

---

## Output

I file vengono salvati nella cartella `output/` con naming automatico:

```
output/
├── data_engineer_20240315_143022.dta    ← importa direttamente in Stata
└── data_engineer_20240315_143022.csv    ← preview rapida
```

### Variabili nel .dta

| Variabile | Tipo | Descrizione |
|-----------|------|-------------|
| `job_id` | string | ID univoco offerta |
| `job_title` | string | Titolo posizione |
| `employer_name` | string | Azienda |
| `employment_type` | string | FULLTIME / PARTTIME / CONTRACTOR |
| `is_remote` | int (0/1) | Posizione remota |
| `city`, `state`, `country` | string | Localizzazione |
| `posted_at` | datetime | Data pubblicazione (UTC) |
| `salary_min`, `salary_max` | float | Salario min/max |
| `salary_currency` | string | Valuta (EUR, USD, ...) |
| `salary_period` | string | YEAR / MONTH / HOUR |
| `description` | string | Descrizione offerta (testo) |
| `highlight_qualifications` | string | Requisiti (pipe-separated) |
| `highlight_responsibilities` | string | Responsabilità |
| `highlight_benefits` | string | Benefits |
| `apply_link` | string | Link candidatura |
| `fetched_at` | string | Timestamp del fetch |

---

## Import in Stata

```stata
* Import diretto
use "output/data_engineer_20240315_143022.dta", clear

* Oppure da CSV
import delimited "output/data_engineer_20240315_143022.csv", clear stringcols(_all)

* Analisi base
describe
tab employment_type
tab is_remote
summarize salary_min salary_max
```

---

## Dipendenze

- `requests` — chiamate HTTP all'API
- `pandas` — trasformazione dati
- `pyreadstat` — scrittura .dta nativo Stata 14/15

---

## Note

- Il piano **free** di JSearch su RapidAPI permette **200 chiamate/mese** (≈ 2.000 offerte)
- Ogni pagina = 1 chiamata API → con `--pages 3` usi 3 chiamate
- I file in `output/` sono gitignored — non committare dati personali o chiavi API
