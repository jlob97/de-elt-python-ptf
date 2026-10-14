# de-python-test

ELT pipeline that extracts real e-commerce data from the Amazon Selling Partner API,
loads it into Snowflake, and models it with dbt. Orchestrated with Airflow.

Scope: the US marketplace (Amazon.com).

#### WIP ####

## Architecture

Amazon SP-API → Python extractors → Snowflake `RAW` → dbt (staging → marts) → Airflow

## Stack

- Python 3.12, managed with [uv]
- httpx + pydantic + python-dotenv (SP-API client)
- pandas + pyarrow (raw files as Parquet)
- Snowflake (PUT + COPY INTO, append-only raw layer)
- dbt
- Airflow
- ruff, mypy, pytest, GitHub Actions (checks, tests and CI/CD)

## Setup

```bash
uv sync
cp .env.example .env   # then fill in your own credentials
```

## Order items extract

```bash
uv run python -m amazon_elt.order_items                                       # last 3 days, ending yesterday
uv run python -m amazon_elt.order_items --start 2026-07-01 --end 2026-09-30   # backfill
```

- Source: `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` (SP-API Reports).
- One report per UTC day, written to `data/raw/order_items/dt=YYYY-MM-DD/order_items.parquet`.
  `dt` is the day the order lines were last updated, not the purchase day.
- **Idempotent:** a rerun overwrites the day's file, and the writer sorts columns and rows,
  so the same data gives a byte-identical file (verified with SHA256).
- **3-day lookback:** each daily run re-pulls the last 3 days to catch late Amazon updates.
- Raw keeps every column as text and every sales channel. The report ignores the marketplace
  filter in North America, so the US filter (`sales-channel = 'Amazon.com'`) and the dedupe
  (latest `last-updated-date` per order line) happen in dbt.

## Progress

- [x] Project scaffold + tooling
- [x] SP-API client
- [x] Order items extractor
- [ ] Load to Snowflake RAW
- [ ] dbt models
- [ ] CI
- [ ] Airflow DAG

## Data & credentials

All credentials live in `.env`. No customer data is committed to this repo.

### Data handling note

This is a learning project. Report data is saved to `data/raw/` as unencrypted Parquet files, which
goes against Amazon's rule for the Reports API: *"Unencrypted report content must never be
stored on disk, even temporarily"* ([Reports API use case guide](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-use-case-guide)).
A production version would encrypt these files at rest or stream the data straight into
Snowflake. `data/` is in `.gitignore`, so no report data reaches GitHub.

Slight chance that I dockerize this at the end, for CI/CD with Jenkins or similar.
