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
- Snowflake (PUT + COPY INTO, append-only raw layer)
- dbt
- Airflow
- ruff, mypy, pytest, GitHub Actions (checks, tests and CI/CD)

## Setup

```bash
uv sync
cp .env.example .env   # then fill in your own credentials
```

## Progress

- [x] Project scaffold + tooling
- [x] SP-API client
- [ ] Order items extractor
- [ ] Load to Snowflake RAW
- [ ] dbt models
- [ ] CI
- [ ] Airflow DAG

## Data & credentials

All credentials live in `.env`. No customer data is committed to this repo.

### Data handling note

This is a learning project. Report files are saved to `data/raw/` as plain text, which
goes against Amazon's rule for the Reports API: *"Unencrypted report content must never be
stored on disk, even temporarily"* ([Reports API use case guide](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-use-case-guide)).
A production version would encrypt these files at rest or stream the data straight into
Snowflake. `data/` is in `.gitignore`, so no report data reaches GitHub.

Slight chance that I dockerize this at the end, for CI/CD with Jenkins or similar.
