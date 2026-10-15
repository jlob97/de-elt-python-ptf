import logging
from pathlib import Path

from amazon_elt.config import SnowflakeConfig
from amazon_elt.snowflake_conn import connect

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/order_items")
STAGE_PATH = "@RAW_STAGE/order_items"

# $1 is the whole Parquet row. METADATA$ columns tell us which file and row it came from
COPY_SQL = f"""
COPY INTO ORDER_ITEMS (payload, _source_file, _file_row_number, _dt)
FROM (
    SELECT
        $1,
        METADATA$FILENAME,
        METADATA$FILE_ROW_NUMBER,
        TO_DATE(REGEXP_SUBSTR(METADATA$FILENAME, 'dt=([0-9-]+)', 1, 1, 'e'))
    FROM {STAGE_PATH}/
)
FILE_FORMAT = (FORMAT_NAME = 'PARQUET_FF')
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    conn = connect(SnowflakeConfig.from_env())
    cursor = conn.cursor()

    for path in sorted(RAW_DIR.glob("dt=*/order_items.parquet")):
        local_file = path.resolve().as_posix()
        target = f"{STAGE_PATH}/{path.parent.name}/"
        cursor.execute(f"PUT 'file://{local_file}' {target} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        logger.info("Uploaded %s to %s", path, target)

    cursor.execute(COPY_SQL)
    for row in cursor.fetchall():
        logger.info("COPY result: %s", row)

    conn.close()


if __name__ == "__main__":
    main()