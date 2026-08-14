"""
validate.py
Post-load validation for the orders ETL pipeline.
Run this after transform.py to confirm the output is trustworthy
before handing it off or loading it into a downstream system.
"""
import pandas as pd
import sys

RAW_PATH = 'output/raw_orders.csv'
CLEAN_PATH = 'output/clean_orders.csv'
REVIEW_PATH = 'output/needs_review.csv'

failures = []


def check(label: str, condition: bool, detail: str = '') -> None:
    status = 'PASS' if condition else 'FAIL'
    print(f"[{status}] {label}" + (f" - {detail}" if detail else ''))
    if not condition:
        failures.append(label)


def main() -> int:
    raw = pd.read_csv(RAW_PATH)
    clean = pd.read_csv(CLEAN_PATH)
    review = pd.read_csv(REVIEW_PATH)

    raw_dedup_count = len(raw.drop_duplicates())

    check(
        "Row count reconciles (clean + review == deduped raw)",
        len(clean) + len(review) == raw_dedup_count,
        f"clean={len(clean)}, review={len(review)}, raw_dedup={raw_dedup_count}"
    )
    check(
        "No duplicate order_ids in clean output",
        clean['order_id'].duplicated().sum() == 0
    )
    check(
        "No nulls in 'amount' in clean output",
        clean['amount'].isna().sum() == 0
    )
    check(
        "Status values are standardized",
        set(clean['status'].unique()) <= {'Completed', 'Pending', 'Cancelled', 'Unknown'},
        f"found: {sorted(clean['status'].unique())}"
    )
    check(
        "Region values are standardized",
        set(clean['region'].unique()) <= {'US', 'EU', 'APAC'},
        f"found: {sorted(clean['region'].unique())}"
    )
    check(
        "All emails contain '@'",
        clean['email'].str.contains('@', na=False).all()
    )

    print()
    if failures:
        print(f"VALIDATION FAILED: {len(failures)} check(s) did not pass.")
        return 1
    else:
        print("VALIDATION PASSED: all checks succeeded.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
