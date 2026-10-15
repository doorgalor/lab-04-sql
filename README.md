# Lab 04: Working with SQL

The goal of this activity is to get you comfortable with SQL (Structured Query Language) for data engineering workflows. You will practice writing SQL scripts, connecting Python applications to databases, and integrating SQL into ETL pipelines. Follow the steps below to build database-driven applications that demonstrate how SQL powers real-world data systems.

## Best practices

Before you start, review the general [best practices for readable and maintainable code](https://github.com/ksiller/DS2022/blob/main/best-practices.md), then take note of these rules for SQL strings in Python:

- **Never use Python string formatting** (`f"..."`, `.format()`, or `%` operators) to insert variables directly into the SQL string. Doing so creates a SQL injection vulnerability.
- **Do not put quotes around `%s`** even if the column expects a string value (e.g., use `WHERE email = %s`, not `WHERE email = '%s'`). The library handles the correct quoting and escaping automatically.
- **Always pass a tuple or list as the second argument** to `cursor.execute()`, even if you are only passing a single parameter (e.g., `(value,)` instead of just `(value)`, which evaluates as an ordinary parenthesized expression rather than a tuple).

**UNSAFE** (string formatting into SQL):

```python
query = "SELECT id, name FROM users WHERE email = %s" % email_str
cursor.execute(query)
```

**WRONG** (trailing comma makes `query` a tuple, not a string):

```python
query = "SELECT id, name FROM users WHERE email = %s", email_str
cursor.execute(query)
```

**SAFE** (parameterized query):

```python
query = "SELECT id, name FROM users WHERE email = %s"  # %s is a placeholder
cursor.execute(query, (email_str,))  # pass values as a tuple/list, not by formatting the string
```

For a full `INSERT` example using the same pattern, see [Insert (Parameterized)](https://github.com/ksiller/DS2022/blob/main/class/04-sql/README.md#insert-parameterized) in the class materials (and [`insert_data.py`](https://github.com/ksiller/DS2022/blob/main/class/04-sql/insert_data.py)).

## Setup

Install the `mycli` command line tool. Follow the [mycli install instructions](https://github.com/ksiller/DS2022/blob/main/class/04-sql/README.md#setup).

Fork this repository on GitHub (keep the default name), then clone your fork. Recommended location: `~/ds2022-fall-2026/lab-04-sql`.

Change into the `lab-04-sql` directory and set up the Python project. Run `uv init` to create the project layout (including `src/sql_lab/`), then `uv add` to install packages. You need `mysql-connector-python` and `pandas`. `sqlalchemy` is optional (needed only for bulk upload approach B in Case Study 2).

```bash
cd ~/ds2022-fall-2026/lab-04-sql
uv init --name "sql_lab" --description "sql work for DS2022"
uv add mysql-connector-python pandas
```

MySQL database access:

- **DB host:** `ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com`
- **DB port:** `3306`
- **DB username:** your UVA computing ID
- **DB password:** your UVA computing ID — for `mycli`, set with `export MYSQL_PWD='COMPUTING_ID'` (do not use `-p` when redirecting SQL into stdin)

>**Note:** The AWS RDS instance is shared, but access is per student. You have a MySQL user named after your UVA computing ID (password = your computing ID) with read-write privileges **only** on your two databases: `COMPUTING_ID_media` and `COMPUTING_ID_mock` (e.g., `mst3k_media` and `mst3k_mock`). You cannot read or write other students' databases. Use `COMPUTING_ID_media` for Case Study 1 and `COMPUTING_ID_mock` for Case Study 2. Replace `COMPUTING_ID` with your UVA computing ID wherever you see it in this lab. **Do not use the shared `ds2022` account for this lab.**

## Case Study 1: SQL CLI & Scripts

A colleague approaches you, frustrated and in despair. They've been tediously populating a database with new tables, running one command at a time. The database crashed halfway through, and they have to start over from scratch. You offer to show them the power of SQL scripts: writing out all SQL statements in a file and executing them in bulk. If the database crashes again, they can simply rerun the script and be back up and running in minutes.

You're walking your colleague through the following steps:

### Step 1: Create Your Database Schema

In the top-level directory of your cloned repo (e.g., `~/ds2022-fall-2026/lab-04-sql`), create a new file `initialize.sql`.

Write SQL statements in `initialize.sql` that:

- Create two related tables, `users` and `posts`, with a **primary key** / **foreign key** relationship. Example: `users` with primary key `user_id`; `posts` with primary key `post_id` and foreign key `user_id` referencing `users`. You may alter field/key names as long as the relationship is clear.
- Give each table at least 3-4 columns with appropriate data types (`INT`, `VARCHAR`, `TEXT`, `DATETIME`, etc.). You can reuse column names from the in-class activity or invent your own.
- Add at least **10 INSERT statements** for each table. Primary key values must be unique, and foreign key values in `posts` must reference valid primary keys in `users`.

**Hints:** Review the examples in [Working with SQL](https://github.com/ksiller/DS2022/blob/main/class/04-sql/README.md) for table creation syntax and insert statement examples.

### Step 2: Execute Your SQL Script

Execute your `initialize.sql` script against the MySQL database. First export your password (same as your computing ID), then run `mycli` without `-p`. Redirected stdin cannot supply a password prompt:

```bash
export MYSQL_PWD='COMPUTING_ID'
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u COMPUTING_ID -D COMPUTING_ID_media < initialize.sql
```

Replace `COMPUTING_ID` with your UVA computing ID. The `-D` flag selects your database, so your SQL script does not need its own `USE` statement. For example, if your computing ID is `mst3k`:

```bash
export MYSQL_PWD='mst3k'
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u mst3k -D mst3k_media < initialize.sql
```

**Password:** Set `MYSQL_PWD` to your computing ID before any `mycli` command that redirects a SQL file into stdin (see Setup).

**Hint:** See [Working with SQL](https://github.com/ksiller/DS2022/blob/main/class/04-sql/README.md) for more details on executing SQL scripts.

### Step 3: Create a Query Script

Create a new file `media_query.sql` that contains a SQL SELECT query. Your query should:

- Select a subset of records from your tables.
- Use at least one JOIN to combine data from both tables.
- Include a WHERE clause to filter the results.

Execute the query and save the output to a file:

```bash
export MYSQL_PWD='COMPUTING_ID'
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u COMPUTING_ID -D COMPUTING_ID_media < media_query.sql > media_results.txt
```

Command line options:

- **-h:** host of the database instance
- **-u:** username
- **-P:** port (3306 is the MySQL default)
- **-D:** database to use
- **MYSQL_PWD:** password via environment variable (required when redirecting SQL into `mycli`; do not use `-p` with stdin redirect)

Include `initialize.sql`, `media_query.sql`, and `media_results.txt` in your `lab-04-sql` directory.

**Success!** You've created and executed SQL scripts. This demonstrates how database schemas are typically initialized and how queries can be automated.

## Case Study 2: Performing bulk data upload in Python

**The Case:** Case Study 1 showed you how to create tables and insert rows by hand in SQL. That works for a handful of records, but not for hundreds. Here you will upload spreadsheet-format data into a MySQL table without typing an `INSERT` for every row.

**Your Task:** Generate mock CSV data, map its column types to SQL types, then write a Python script that reads, cleans, and loads the file into your `COMPUTING_ID_mock` database.

### Setup

Python packages (`mysql-connector-python`, `pandas`) were installed in the lab [Setup](#setup). If `import mysql.connector` or `import pandas` fails, re-run `uv add mysql-connector-python pandas` from the repo root.

**Environment variables:** Set your database connection variables in the terminal (same credentials as Case Study 1):

```bash
export DBHOST='ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com'
export DBUSER='COMPUTING_ID'
export DBPASS='COMPUTING_ID'
export DBNAME='COMPUTING_ID_mock'
```

Replace `COMPUTING_ID` with your UVA computing ID. 

### Step 1: Create mock data

Go to [Mockaroo](https://www.mockaroo.com) and create a new dataset with:

- First field: `Field Name` = `id`, `Type` = `Row Number`, `Options blank` = `0%`
- Second field: `Field Name` = `group`, `Type` = `Custom List`, provide a list of 3-5 items, `random`, `Options blank` = `5%`
- Four additional fields of your choosing; two of those four should have `Options blank` = `5%`
- `# Rows` = `200`
- `Format` = `CSV`
- `Line ending` = `Unix (LF)`
- `Include header` = checked

Click `Preview` to check the output, then click `Generate Data` and download the file. Keep the default name `MOCK_DATA.csv` (do not rename it). Move `MOCK_DATA.csv` into the top level of your `lab-04-sql` directory (same folder as `README.md`).

### Step 2: Inspect the data

Inspect the CSV file on your computer:

```bash
cd ~/ds2022-fall-2026/lab-04-sql
uv run --with jupyter jupyter lab
```

Create a new notebook and read the CSV file with [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html):

```python
import pandas as pd
df = pd.read_csv("MOCK_DATA.csv")
```

```python
df.head()
```

```python
df.dtypes
```

The `read_csv` function makes a best attempt to map each column to a particular data type (e.g. `int64`, `float64`, `bool`, `datetime64[ns]`, `object` for text, etc.). **Take note of these dtypes and use that info to map them in Step 3 to SQL data types, like `INT`, `VARCHAR`, `DATETIME`.**

### Step 3: Define your SQL table schema

Use the dtypes you noted in Step 2 to choose a [SQL data type](https://www.w3schools.com/sql/sql_datatypes.asp) for each column. In Python you can create a dictionary to help with the mapping:

```python
type_mapping = {
    "int64": "BIGINT",
    "int32": "INT",
    "float64": "DOUBLE",
    "bool": "TINYINT(1)",
    "datetime64[ns]": "DATETIME",
    "object": "VARCHAR(255)",  # safe default varchar length
    "string": "VARCHAR(255)",
}
```

### Step 4: Develop Python script for data preprocessing & upload

Create a script `process.py` under `src/sql_lab/` (the package directory created by `uv init --name "sql_lab"`) that does the following:

- Read DB host, DB name, DB user, DB password from environment variables.
- Create a function `read_data` that loads the CSV into a pandas DataFrame. It should accept one argument `filename` and return a DataFrame.
- Create a function `clean_data` that prepares the DataFrame for upload (e.g., handle missing values, rename columns, cast types). It should accept one argument `data`, remove rows with missing values, and return the cleaned DataFrame.
- Create a function `load_data` that writes the DataFrame to MySQL. It should accept two arguments: `data` (your DataFrame) and `table` (the destination table name). **Always pass `"mock"` as the table name** so it is consistent across all databases. The function should create the `mock` table (if it doesn't exist) and upload the DataFrame into it. Implement the upload using either **approach A** (row-by-row `INSERT`s with `mysql-connector-python`) or **approach B** (bulk upload with pandas + SQLAlchemy), described below.
- Create a function `main` that calls `read_data`, `clean_data`, and `load_data` in sequence. Invoke `main` inside an `if __name__ == "__main__":` block.
- Use logging to report status in each function.
- Use a docstring at the beginning of each function.
- Use comments in your code.

**Load approach A: row-by-row inserts with `mysql-connector-python`:** loop over the DataFrame rows and `cursor.execute()` an `INSERT` for each row. Use parameterized queries (`%s` placeholders + a tuple of values). Building SQL with f-strings or string concatenation creates a [SQL injection](https://bobby-tables.com/python) vulnerability and must be avoided. Wrap the code that opens, uses, and closes the database connection in a `try`/`except` block. Include logging statements for success and errors. See [class/04-sql/](https://github.com/ksiller/DS2022/tree/main/class/04-sql/) for an example.

**Load approach B: bulk upload with pandas + SQLAlchemy:** create a SQLAlchemy engine and call [DataFrame.to_sql()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html) to write the whole DataFrame in one step. Add SQLAlchemy if needed (`uv add sqlalchemy`) and use a connection URL of the form `mysql+mysqlconnector://USER:PASS@HOST:PORT/DBNAME`. Wrap the code that opens, uses, and closes the database connection in a `try`/`except` block. Include logging statements for success and errors. See [class/04-sql/](https://github.com/ksiller/DS2022/tree/main/class/04-sql/) for an example.

### Step 5: Run your script to upload to database

Run your script and watch the log output for errors:

```bash
uv run python src/sql_lab/process.py
```

### Step 6: Confirm table in database

Connect to your database and verify that the `mock` table exists and holds the uploaded rows:

```bash
export MYSQL_PWD='COMPUTING_ID'
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u COMPUTING_ID -D COMPUTING_ID_mock
```

For example, if your computing ID is `mst3k`:

```bash
export MYSQL_PWD='mst3k'
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u mst3k -D mst3k_mock
```

```sql
SHOW TABLES;
DESCRIBE mock;
SELECT COUNT(*) FROM mock;
SELECT * FROM mock LIMIT 5;
```

`SELECT COUNT(*) FROM mock` returns a single number: how many rows are in the table. After a successful upload (and after `clean_data` drops rows with missing values), this count should match the number of rows remaining in your cleaned DataFrame, not necessarily the original 200 from Mockaroo.

### Step 7: Develop a Python script to query the database

In `src/sql_lab/`, create a new script `query.py` that retrieves data from the `mock` table in **your** `COMPUTING_ID_mock` database (the one you uploaded in Steps 4-6). Use [basic-sql.py](https://github.com/ksiller/DS2022/blob/main/class/04-sql/basic-sql.py) in the course repo as inspiration (especially `get_people_by_lastname` and `plot_continent_counts`), but adapt it to **your** columns in `mock`. Do not connect to the shared class `media` database or assume the `media.MOCK_DATA` schema from the example.

The script should follow the same best practices as `process.py` (parameterized queries, env vars for credentials, logging, docstrings, comments).

Required components:

- Read DB host, DB name, DB user, and DB password from environment variables (same pattern as `process.py`).
- Create a function `get_data_by_group` that takes one argument `value`. It should run a parameterized `SELECT` that returns all rows where the `group` column equals `value` (same idea as `get_people_by_lastname(lname)` in the example). Because `GROUP` is a reserved word in MySQL, quote the column name with backticks in your SQL (e.g., `` WHERE `group` = %s ``). Document the filter column in the function docstring.
- Create a function `plot_counts` that takes one argument `groupby` (a column name). It should run a `SELECT ... GROUP BY` query that counts rows per distinct value of that column (same idea as `plot_continent_counts` in the example, but without hardcoding the column). You may show a bar chart with matplotlib, or simply return/print the counts; either is fine.
- Create a function `main` that calls your query functions (as in `basic-sql.py`) so you can demonstrate them. Invoke `main` inside an `if __name__ == "__main__":` block.
- `print` statements are fine inside `main` (as in `basic-sql.py`). Use `logging` to report status in all other functions (as in `process.py`).
- Give every function a docstring. Comment your code.

Run it with:

```bash
uv run python src/sql_lab/query.py
```

### [Optional] Step 8: DuckDB

For an additional challenge, create `src/sql_lab/process_duckdb.py` and use [DuckDB](https://duckdb.org/) to create a local database and upload the `mock` table to it. See an example in [class/04-sql/](https://github.com/ksiller/DS2022/tree/main/class/04-sql/).

### [Optional] Step 9: Accept Excel spreadsheets

Update the `read_data` function to check the extension of the filename passed. Expand its functionality so it can process both `.csv` and Microsoft Excel `.xlsx` files.

## Learning Outcomes

With your SQL integration complete, you've successfully demonstrated how databases power data engineering workflows. You've learned how to:

- Write SQL scripts to create database schemas with primary and foreign keys
- Execute SQL scripts from the command line and save their output to a file
- Use JOIN operations to combine related tables and WHERE clauses to filter results
- Connect Python applications to MySQL databases
- Map pandas dtypes to appropriate SQL data types
- Bulk load CSV data into a database table from Python
- Query MySQL from Python with parameterized filters and aggregations
- Use parameterized queries to prevent SQL injection
- Integrate SQL databases into ETL pipelines

These skills are essential for data engineering. SQL databases provide the persistence, relationships, and querying power that make large-scale data systems possible. The patterns you've practiced here (connecting applications to databases, writing parameterized queries, and using JOINs) are used in every production data system.

## Submit your work

Your repository should look roughly like this (other `uv init` files are fine too):

```text
lab-04-sql/
├── .gitignore
├── README.md
├── MOCK_DATA.csv
├── initialize.sql
├── media_query.sql
├── media_results.txt
├── pyproject.toml
├── uv.lock
└── src/
    └── sql_lab/
        ├── __init__.py
        ├── process.py
        └── query.py
```

**Submission steps**

Confirm that `.venv` and `.vscode` are listed in `.gitignore`, then run `git status` and verify that `.venv/` and `.vscode/` are **not** staged for commit.

Add all project files (gitignored paths stay out automatically):

```bash
git add .
```

Commit your work:

```bash
git commit -m "Complete Lab 04: Working with SQL"
```

Push to your repository:

```bash
git push origin main
```

Submit the URL of your forked repository in the Canvas assignment. The URL should look like: `https://github.com/YOUR_USERNAME/lab-04-sql`
