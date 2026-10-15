import logging
from pathlib import Path

from amazon_elt.config import SnowflakeConfig
from amazon_elt.load.connection import connect

logger = logging.getLogger(__name__)

RAW_ROOT = Path("data/raw")

COPY_SQL = """
COPY INTO {table} (payload, _source_file, _file_row_number, _dt)
FROM (
    SELECT
        $1,
        METADATA$FILENAME,
        METADATA$FILE_ROW_NUMBER,
        TO_DATE(REGEXP_SUBSTR(METADATA$FILENAME, 'dt=([0-9-]+)', 1, 1, 'e'))
    FROM @RAW_STAGE/{stream}/
)
FILE_FORMAT = (FORMAT_NAME = 'PARQUET_FF')
"""


def run_load(stream: str, table: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("snowflake.connector").setLevel(logging.WARNING)

    conn = connect(SnowflakeConfig.from_env())
    cursor = conn.cursor()

    for path in sorted((RAW_ROOT / stream).glob(f"dt=*/{stream}.parquet")):
        local_file = path.resolve().as_posix()
        target = f"@RAW_STAGE/{stream}/{path.parent.name}/"
        cursor.execute(f"PUT 'file://{local_file}' {target} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        logger.info("Uploaded %s to %s", path, target)

    cursor.execute(COPY_SQL.format(table=table, stream=stream))
    for row in cursor.fetchall():
        logger.info("COPY result: %s", row)

    conn.close()