"""
generate_data.py
Generates a synthetic 'raw_orders.csv' that mimics a messy real-world
client export: missing values, inconsistent casing, duplicate rows.
Used only to create sample input for this demo pipeline.
"""
import pandas as pd
import numpy as np

np.random.seed(42)
n = 200

data = {
    'order_id': list(range(1001, 1001 + n)),
    'customer_name': [f'Customer {i}' if i % 17 != 0 else None for i in range(n)],
    'email': [f'cust{i}@example.com' if i % 13 != 0 else f'CUST{i}@EXAMPLE.COM ' for i in range(n)],
    'order_date': pd.date_range('2024-01-01', periods=n, freq='D').astype(str).tolist(),
    'amount': [round(np.random.uniform(10, 500), 2) if i % 11 != 0 else None for i in range(n)],
    'status': np.random.choice(['completed', 'Completed', 'PENDING', 'pending', 'cancelled', None], n).tolist(),
    'region': np.random.choice(['US', 'us', 'EU', 'eu ', 'APAC'], n).tolist(),
}
df = pd.DataFrame(data)

# introduce duplicate rows (common real-world issue)
dupes = df.sample(5, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

df.to_csv('output/raw_orders.csv', index=False)
print(f"Generated output/raw_orders.csv with {len(df)} rows")
