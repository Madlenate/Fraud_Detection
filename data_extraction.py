import sqlite3
from pathlib import Path

import kagglehub
import pandas as pd

data = Path(kagglehub.competition_download("ieee-fraud-detection"))

db_path = Path(__file__).parent / "fraud.db"
conn = sqlite3.connect(db_path)

for csv_file in sorted(data.glob("*.csv")):
    table = csv_file.stem 
    print(f"Loading {csv_file.name} -> table:  {table} ")

    first = True
    for chunk in pd.read_csv(csv_file, chunksize=50000, low_memory=False):
        chunk.columns = chunk.columns.str.replace("-", "_")  # test_identity uses id-01, train uses id_01
        chunk.to_sql(
            table,
            conn,
            if_exists="replace" if first else "append",
            index = False
        )
        first = False

for table in ["train_transaction", "train_identity", 
              "test_transaction", "test_identity"]:
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table}_tid ON {table}(TransactionID)"
    )
conn.commit()

# 5. Sanity check: row counts
for (name,) in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
):
    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"{name}: {count:,} rows")

conn.close()
print("Done ->", db_path)