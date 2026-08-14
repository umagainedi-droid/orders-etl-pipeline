"""
transform.py
ETL pipeline: extracts a raw orders export, cleans and standardizes it,
and separates records that need manual review instead of silently
dropping bad data.

Input:  output/raw_orders.csv
Output: output/clean_orders.csv   (records safe to load downstream)
        output/needs_review.csv   (records flagged with a reason, for human follow-up)
"""
import pandas as pd

RAW_PATH = 'output/raw_orders.csv'
CLEAN_PATH = 'output/clean_orders.csv'
REVIEW_PATH = 'output/needs_review.csv'


def extract(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[EXTRACT] Read {len(df)} rows from {path}")
    return df


def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    before = len(df)
    df = df.drop_duplicates().copy()
    print(f"[TRANSFORM] Removed {before - len(df)} exact duplicate rows")

    # Standardize text fields
    df['email'] = df['email'].str.strip().str.lower()
    df['region'] = df['region'].str.strip().str.upper()
    df['status'] = df['status'].str.strip().str.title().fillna('Unknown')
    df['order_date'] = pd.to_datetime(df['order_date'])

    # Identify every issue per row (a row can have more than one)
    df['review_reasons'] = ''
    missing_amount = df['amount'].isna()
    missing_name = df['customer_name'].isna()

    df.loc[missing_amount, 'review_reasons'] += 'missing_amount;'
    df.loc[missing_name, 'review_reasons'] += 'missing_customer_name;'

    needs_review = df[df['review_reasons'] != ''].copy()
    clean_df = df[df['review_reasons'] == ''].drop(columns=['review_reasons']).copy()

    print(f"[TRANSFORM] Clean rows: {len(clean_df)}")
    print(f"[TRANSFORM] Flagged for review: {len(needs_review)}")

    # Reconciliation check happens here, not just in a separate script -
    # a pipeline should fail loudly if the math doesn't add up
    assert len(clean_df) + len(needs_review) == len(df), "Row count mismatch after split!"

    return clean_df, needs_review


def load(clean_df: pd.DataFrame, needs_review: pd.DataFrame) -> None:
    clean_df.to_csv(CLEAN_PATH, index=False)
    needs_review.to_csv(REVIEW_PATH, index=False)
    print(f"[LOAD] Wrote {len(clean_df)} rows to {CLEAN_PATH}")
    print(f"[LOAD] Wrote {len(needs_review)} rows to {REVIEW_PATH}")


if __name__ == '__main__':
    raw = extract(RAW_PATH)
    clean, review = transform(raw)
    load(clean, review)
