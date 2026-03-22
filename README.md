# Job Market Tracker

Python pipeline that downloads job postings from JSearch (Indeed, LinkedIn, Glassdoor via RapidAPI), cleans them with Pandas, and exports both the full dataset and a query-level summary.

## Structure

```text
job-market-tracker/
├── .env               # Local credentials (gitignored)
├── export.py          # CSV, Parquet, and Stata export helpers
├── fetch_jobs.py      # API call -> raw JSON -> DataFrame
├── main.py            # CLI entry point and run orchestration
├── pipeline.py        # Extract, transform, export steps
├── queries.py         # Default query list
├── transform.py       # Cleaning and normalization
├── requirements.txt
└── output/            # Generated files (gitignored)
```

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/TUO_USERNAME/job-market-tracker.git
cd job-market-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create local credentials file (.env)
cat > .env << 'EOF'
RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY
RAPIDAPI_HOST=jsearch.p.rapidapi.com
EOF
```

Get your API key from:
https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

## Usage

```bash
# Run all queries from queries.py
python main.py

# Single query override
python main.py --query "data engineer"

# Advanced search
python main.py --query "AI economist" --pages 5 --date week --country us
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--query` | all items in `queries.py` | Search string override |
| `--pages` | 5 | Pages to fetch (10 jobs per page) |
| `--date` | all | `all`, `today`, `3days`, `week`, `month` |
| `--country` | it | ISO country code such as `it`, `us`, `gb` |

## Output

Each run writes four files into `output/`, all sharing the same timestamped base name:

```text
output/
├── multi_query_20260321_101530.csv
├── multi_query_20260321_101530.parquet
├── multi_query_20260321_101530_summary.csv
└── multi_query_20260321_101530_summary.parquet
```

### Main Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| `job_id` | string | Unique job identifier (from API) |
| `job_title` | string | Job title |
| `employer_name` | string | Company name |
| `city` | string | Job city |
| `country` | string | Job country |
| `description` | string | Normalized job description |
| `fetched_at` | string | UTC timestamp of the fetch |
| `search_query` | string | Query that produced the record |

### Summary Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| `search_query` | string | Query label |
| `job_count` | integer | Number of rows exported for that query |

## Runtime Flow

1. `run_extract(...)` downloads jobs for each query.
2. `run_transform(...)` normalizes the raw API payload.
3. `run_export(...)` writes the main dataset and the summary dataset in CSV and Parquet format.
4. `log_run_end(...)` prints the paths of all generated files.

## Dependencies

- `requests` for HTTP API calls
- `pandas` for data transformation
- `pyarrow` as the Parquet engine used by `DataFrame.to_parquet(...)`
- `pyreadstat` for optional Stata `.dta` exports via `export.py`
- `python-dotenv` for loading `.env`


## Upload su S3

Per caricare i file generati su un bucket S3, usa lo script `upload_to_s3.py` (richiede `boto3` e credenziali AWS configurate):

```python
from pathlib import Path
import boto3

BUCKET_NAME = "job-market-tracker-enrico"
REGION = "eu-west-1"
files_to_upload = [
	"output/multi_query_20260321_225229.parquet",
	"output/multi_query_20260321_225229.csv",
]
s3 = boto3.client("s3", region_name=REGION)
for local_path in files_to_upload:
	s3_key = f"jobs/{Path(local_path).name}"
	if Path(local_path).exists():
		s3.upload_file(local_path, BUCKET_NAME, s3_key)
		print(f"✅ Uploaded: {local_path} → s3://{BUCKET_NAME}/{s3_key}")
	else:
		print(f"❌ File not found: {local_path}")
```

La chiave S3 viene generata automaticamente dal nome file locale, con prefisso `jobs/`.

## Notes

- The free JSearch plan on RapidAPI allows 200 calls per month.
- Each requested page costs one API call, so `--pages 3` uses 3 calls per query.
- Files in `output/` and `.env` should stay uncommitted.
