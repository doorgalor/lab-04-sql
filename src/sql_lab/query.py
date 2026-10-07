#!/usr/bin/env python3
"""Query the mock table by group and count rows for a chosen column."""

import logging
import os
import re

import mysql.connector
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Column names are identifiers, so they cannot be passed as %s values.
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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


def get_data_by_group(value):
    """Return every mock row whose `group` column equals `value`.

    The filter column is `group`. The comparison value is bound with a
    placeholder so it is never formatted into the SQL text.
    """
    query = "SELECT * FROM mock WHERE `group` = %s"
    logger.info("Selecting rows where group = %s", value)
    connection = None
    cursor = None
    try:
        connection = _connection()
        cursor = connection.cursor()
        cursor.execute(query, (value,))
        rows = cursor.fetchall()
        logger.info("Found %s rows for group %s", len(rows), value)
        return rows
    except mysql.connector.Error as error:
        logger.error("Group query failed: %s", error)
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def plot_counts(groupby):
    """Count mock rows for each distinct value of `groupby`.

    Args:
        groupby: Column to aggregate. Must be a plain identifier such as
            "group" or "city".

    Returns:
        DataFrame with the grouping column and a row_count column.
    """
    if not IDENTIFIER.match(groupby):
        raise ValueError(f"Refusing unsafe column name: {groupby}")

    # Backticks are required because GROUP is reserved. The name was checked above.
    query = (
        f"SELECT `{groupby}` AS group_value, COUNT(*) AS row_count "
        f"FROM mock GROUP BY `{groupby}` ORDER BY row_count DESC"
    )
    logger.info("Counting rows grouped by %s", groupby)
    connection = None
    cursor = None
    try:
        connection = _connection()
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        frame = pd.DataFrame(rows, columns=["group_value", "row_count"])
        logger.info("Grouped %s into %s buckets", groupby, len(frame))
        return frame
    except mysql.connector.Error as error:
        logger.error("Count query failed: %s", error)
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def main():
    """Show one filtered group and the counts for the group column."""
    print("=== by group ===")
    print(get_data_by_group("Alpha"))

    print("=== counts ===")
    print(plot_counts("group"))


if __name__ == "__main__":
    main()
