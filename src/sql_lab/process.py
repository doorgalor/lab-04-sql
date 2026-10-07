#!/usr/bin/env python3
"""Read mock CSV data, drop incomplete rows, and load the rest into MySQL."""

import logging
import os
from pathlib import Path

import mysql.connector
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# pandas dtype -> MySQL type. object/string stay short text.
TYPE_MAPPING = {
    "int64": "BIGINT",
    "int32": "INT",
    "float64": "DOUBLE",
    "bool": "TINYINT(1)",
    "datetime64[ns]": "DATETIME",
    "object": "VARCHAR(255)",
    "string": "VARCHAR(255)",
    "str": "VARCHAR(255)",
}

# process.py lives in src/sql_lab/, so the repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "MOCK_DATA.csv"


def read_data(filename):
    """Load a CSV file into a pandas DataFrame.

    Args:
        filename: Path to the CSV file.

    Returns:
        DataFrame with one row per record in the file.
    """
    logger.info("Reading %s", filename)
    frame = pd.read_csv(filename)
    logger.info("Loaded %s rows and %s columns", len(frame), len(frame.columns))
    return frame


def clean_data(data):
    """Remove rows with missing values and cast the registration timestamp.

    Args:
        data: Raw DataFrame returned by read_data.

    Returns:
        DataFrame containing only complete rows.
    """
    logger.info("Cleaning %s rows", len(data))
    # Blank CSV cells become NaN; those rows cannot be inserted as-is.
    cleaned = data.dropna().copy()
    if "registered_at" in cleaned.columns:
        cleaned["registered_at"] = pd.to_datetime(cleaned["registered_at"])
    removed = len(data) - len(cleaned)
    logger.info("Dropped %s incomplete rows; %s remain", removed, len(cleaned))
    return cleaned


def _sql_type(dtype):
    """Return the MySQL type that matches a pandas dtype."""
    dtype_name = str(dtype)
    if dtype_name.startswith("datetime64"):
        return "DATETIME"
    if dtype_name not in TYPE_MAPPING:
        logger.warning("No SQL mapping for %s; using VARCHAR(255)", dtype_name)
        return "VARCHAR(255)"
    return TYPE_MAPPING[dtype_name]


def _quote_ident(name):
    """Backtick a simple SQL identifier. `group` is a reserved word."""
    if not name.replace("_", "").isalnum():
        raise ValueError(f"Refusing unsafe identifier: {name}")
    return f"`{name}`"


def _connection():
    """Open MySQL using DBHOST, DBUSER, DBPASS, and DBNAME."""
    missing = [
        name
        for name in ("DBHOST", "DBUSER", "DBPASS", "DBNAME")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    return mysql.connector.connect(
        host=os.environ["DBHOST"],
        user=os.environ["DBUSER"],
        password=os.environ["DBPASS"],
        database=os.environ["DBNAME"],
    )


def _bind_value(value):
    """Turn a pandas cell into a value the connector can bind to %s."""
    if hasattr(value, "to_pydatetime"):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        return value.item()
    return value


def load_data(data, table):
    """Create `table` if needed and insert each DataFrame row.

    Args:
        data: Cleaned DataFrame to upload.
        table: Destination table name. Pass "mock".
    """
    logger.info("Preparing to load %s rows into %s", len(data), table)
    columns = list(data.columns)
    column_defs = []
    for column in columns:
        definition = f"{_quote_ident(column)} {_sql_type(data[column].dtype)}"
        if column == "id":
            definition += " PRIMARY KEY"
        column_defs.append(definition)

    # Values stay in the parameter tuple. Only checked identifiers are quoted.
    placeholders = ", ".join(["%s"] * len(columns))
    quoted_columns = ", ".join(_quote_ident(column) for column in columns)
    quoted_table = _quote_ident(table)
    insert_sql = (
        f"INSERT INTO {quoted_table} ({quoted_columns}) VALUES ({placeholders})"
    )

    connection = None
    cursor = None
    try:
        connection = _connection()
        cursor = connection.cursor()
        # Replace any previous upload so the row count matches this file.
        cursor.execute(f"DROP TABLE IF EXISTS {quoted_table}")
        cursor.execute(
            f"CREATE TABLE {quoted_table} ({', '.join(column_defs)})"
        )
        for _, row in data.iterrows():
            values = tuple(_bind_value(row[column]) for column in columns)
            cursor.execute(insert_sql, values)
        connection.commit()
        logger.info("Uploaded %s rows into %s", len(data), table)
    except mysql.connector.Error as error:
        logger.error("Upload failed: %s", error)
        if connection is not None and connection.is_connected():
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            logger.info("Closed database connection")


def main():
    """Read MOCK_DATA.csv, clean it, and load it into the mock table."""
    filename = os.environ.get("CSV_FILE", str(DEFAULT_CSV))
    frame = read_data(filename)
    cleaned = clean_data(frame)
    load_data(cleaned, "mock")


if __name__ == "__main__":
    main()
