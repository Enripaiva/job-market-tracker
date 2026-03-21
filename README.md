# Job Market Tracker 📊

Python pipeline that downloads job postings from **JSearch** (Indeed, LinkedIn, Glassdoor via RapidAPI), cleans them with **Pandas**, and exports them as native Stata **.dta** files.

---

## Structure

```
job-market-tracker/
├── .env               # Local credentials (gitignored)
├── fetch_jobs.py      # API call -> raw JSON
├── transform.py       # Pandas: cleaning and normalization
├── export.py          # Export -> .dta (Stata) + .csv
├── main.py            # Entry point with argparse
├── queries.py         # Default query list
├── requirements.txt
└── output/            # Generated files (gitignored)
```

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/TUO_USERNAME/job-market-tracker.git
cd job-market-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create local credentials file (.env)
cat > .env << 'EOF'
RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY
RAPIDAPI_HOST=jsearch.p.rapidapi.com
EOF

# 4. Get your key at:
#    https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
```

---

## Usage

```bash
# Run all queries from queries.py
python main.py

# Single query override
python main.py --query "data engineer"

# Advanced search
python main.py --query "AI economist" --pages 5 --date week --country us
```

### Available Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--query` | all items in `queries.py` | Search string override |
| `--pages` | 3 | Pages to fetch (10 jobs/page) |
| `--date` | month | `all`, `today`, `3days`, `week`, `month` |
| `--country` | it | ISO country code (`it`, `us`, `gb`, ...) |

---

## Output

Files are saved in the `output/` folder with automatic naming:

```
output/
├── data_engineer_20240315_143022.dta    <- import directly in Stata
└── data_engineer_20240315_143022.csv    <- quick preview
```

### Variables in .dta

| Variable | Type | Description |
|-----------|------|-------------|
| `job_id` | string | Unique job ID |
| `job_title` | string | Job title |
| `employer_name` | string | Company |
| `employment_type` | string | FULLTIME / PARTTIME / CONTRACTOR |
| `is_remote` | int (0/1) | Remote position |
| `city`, `state`, `country` | string | Location |
| `posted_at` | datetime | Posted date (UTC) |
| `salary_min`, `salary_max` | float | Min/max salary |
| `salary_currency` | string | Currency (EUR, USD, ...) |
| `salary_period` | string | YEAR / MONTH / HOUR |
| `description` | string | Job description text |
| `highlight_qualifications` | string | Qualifications (pipe-separated) |
| `highlight_responsibilities` | string | Responsibilities |
| `highlight_benefits` | string | Benefits |
| `apply_link` | string | Application link |
| `search_query` | string | Query that generated the job record |
| `fetched_at` | string | Fetch timestamp |

---

## Import in Stata

```stata
* Direct import
use "output/data_engineer_20240315_143022.dta", clear

* Or from CSV
import delimited "output/data_engineer_20240315_143022.csv", clear stringcols(_all)

* Basic analysis
describe
tab employment_type
tab is_remote
summarize salary_min salary_max
```

---

## Dependencies

- `requests` - HTTP API calls
- `pandas` - data transformation
- `pyreadstat` - native .dta writing for Stata 14/15
- `python-dotenv` - load local environment variables in `main.py`

---

## Note

- The **free** JSearch plan on RapidAPI allows **200 calls/month** (about 2,000 jobs)
- Each page = 1 API call, so `--pages 3` uses 3 calls
- Files in `output/` and `.env` are gitignored; do not commit personal data or API keys
