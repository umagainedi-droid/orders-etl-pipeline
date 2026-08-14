# Orders ETL Pipeline

A small end-to-end ETL pipeline that extracts a messy customer orders
export, cleans and standardizes it, and validates the output before
it's considered safe to load downstream.

Built to demonstrate a realistic data cleaning workflow: **nothing is
silently dropped** — records with data quality issues are flagged into
a separate file for human review rather than discarded.

## Problem

Client data exports are rarely clean. This pipeline handles a typical
CSV export from an orders system with:

- Missing customer names and order amounts
- Inconsistent email casing and stray whitespace
- Inconsistent status values (`completed` / `Completed` / `PENDING`)
- Inconsistent region codes (`US` / `us` / `eu `)
- Duplicate rows

## Pipeline

```
generate_data.py   -> creates a synthetic messy dataset (demo only)
transform.py        -> extract, clean, standardize, split into clean vs. review
validate.py          -> post-load checks confirming the output is trustworthy
```

### Design decisions

- **Missing `amount`**: rows are not dropped. They're flagged into
  `needs_review.csv` with a reason, so a human can follow up rather
  than losing data silently.
- **Missing `customer_name`**: same approach — flagged, not dropped.
- **Status field**: standardized to Title Case (`Completed`, `Pending`,
  `Cancelled`), with missing values mapped to `Unknown` rather than left blank.
- **Idempotency**: exact duplicate rows are removed before any other
  processing, so re-running the pipeline on the same file is safe.
- **Reconciliation**: the pipeline asserts that `clean` + `review` row
  counts always equal the deduplicated input — if they don't, it fails
  loudly instead of producing a silently wrong result.

## How to run

```bash
python3 generate_data.py   # creates output/raw_orders.csv (sample data)
python3 transform.py        # produces clean_orders.csv and needs_review.csv
python3 validate.py          # runs data quality checks, exits non-zero on failure
```

## Output

| File | Description |
|---|---|
| `output/raw_orders.csv` | Raw input (sample/demo data) |
| `output/clean_orders.csv` | Cleaned, standardized, ready to load |
| `output/needs_review.csv` | Flagged rows with a `review_reasons` column explaining why |

## Validation checks

`validate.py` confirms, and prints a pass/fail report for:

- Row counts reconcile (no rows lost or duplicated between clean/review)
- No duplicate `order_id`s in the clean output
- No null `amount` values in the clean output
- `status` and `region` values are fully standardized
- All emails are well-formed

## Part 2: Loading into a database (SQL)

`load_to_db.py` loads `clean_orders.csv` into a SQLite database using
an **UPSERT** pattern (`INSERT ... ON CONFLICT DO UPDATE`) rather than
a naive full reload. This is what a real incremental pipeline needs:

- Running the load repeatedly on unchanged data does **not** create duplicates
- If a source row changes (e.g. an order's amount is corrected), re-running
  the load updates that row in place instead of duplicating it

This was verified directly: loading twice with unchanged data kept the
row count identical, and changing one row's value and reloading updated
it in place with the total row count unaffected.

`queries.sql` contains example analytical queries against the loaded
table (revenue by region, order counts by status, monthly volume, a
running-total window function example) — the kind of reporting a
client typically asks for once data is loaded.

### How to run Part 2

```bash
python3 load_to_db.py   # loads clean_orders.csv into orders.db (SQLite)
# then run queries.sql against orders.db using any SQLite client,
# or Python's built-in sqlite3 module
```

## Tech

Python, pandas, SQLite (upsert/MERGE-style loading). The SQL used here
(`ON CONFLICT ... DO UPDATE`) is close to standard ANSI SQL and maps
directly to Postgres; SQL Server and MySQL use equivalent `MERGE` /
`ON DUPLICATE KEY UPDATE` syntax for the same pattern.
