-- Raw landing for the order items stream (item 4).
-- Run as FTC_DATA, the role that owns ECOM_DW.RAW. Safe to re-run.
-- Loaded by: uv run python -m amazon_elt.load_order_items

USE ROLE FTC_DATA;
USE WAREHOUSE PILOT_WH;
USE SCHEMA ECOM_DW.RAW;

-- How COPY INTO reads the files the extractor writes
CREATE FILE FORMAT IF NOT EXISTS PARQUET_FF
    TYPE = PARQUET;

-- Internal stage: PUT uploads the files here, encrypted at rest by Snowflake
CREATE STAGE IF NOT EXISTS RAW_STAGE
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- Append-only raw table: one row per order line, the whole source row in payload
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    payload          VARIANT,
    _source_file     VARCHAR,
    _file_row_number NUMBER,
    _dt              DATE,
    _loaded_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
