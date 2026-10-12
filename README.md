# de-python-test

ELT pipeline that extracts real e-commerce data from the Amazon Selling Partner API (US + MX),
loads it into Snowflake, and models it with dbt. Orchestrated with Airflow.

#### WIP ####

## Architecture

Amazon SP-API → Python extractors → Snowflake `RAW` → dbt (staging → marts) → Airflow

## Stack

- Python 3.12, managed with [uv]
- httpx + tenacity + pydantic (SP-API client)
- Snowflake (PUT + COPY INTO, append-only raw layer)
- dbt
- Airflow
- ruff, mypy, pytest, GitHub Actions #For checks, tests, and CI/CD

## Setup

```bash
uv sync
cp .env.example .env   # then fill in your own credentials

Progress

- [ ] Project scaffold + tooling
- [ ] SP-API client
- [ ] Order items extractor
- [ ] Load to Snowflake RAW
- [ ] dbt models
- [ ] CI
- [ ] Airflow DAG

Data & credentials

All credentials live in .env (git-ignored). No customer data is committed to this repo.

Slight chance that I dockerize this at the end, for CI/CD with Jenkins or similar.