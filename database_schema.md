# fraud.db: Relational Map

SQLite database built by `data_extraction.py` from the Kaggle **IEEE-CIS Fraud Detection** competition data.

## Entity Relationship Diagram

```mermaid
erDiagram
    train_transaction ||--o| train_identity : "TransactionID"
    test_transaction  ||--o| test_identity  : "TransactionID"
    test_transaction  ||--|| sample_submission : "TransactionID"

    train_transaction {
        int    TransactionID PK
        int    isFraud "target: 0 or 1"
        int    TransactionDT "seconds from a reference time"
        float  TransactionAmt
        string ProductCD
        float  card1_to_card6 "card info"
        float  addr1_addr2 "billing region / country"
        float  dist1_dist2 "distances"
        string P_emaildomain "purchaser email"
        string R_emaildomain "recipient email"
        float  C1_to_C14 "counts"
        float  D1_to_D15 "time deltas"
        string M1_to_M9 "match flags T/F"
        float  V1_to_V339 "Vesta engineered features"
    }

    train_identity {
        int    TransactionID PK, FK
        float  id_01_to_id_38 "identity / network features"
        string DeviceType "desktop / mobile"
        string DeviceInfo
    }

    test_transaction {
        int    TransactionID PK
        int    TransactionDT
        float  TransactionAmt
        string ProductCD
        string other_columns "same as train, no isFraud"
    }

    test_identity {
        int    TransactionID PK, FK
        float  id_01_to_id_38 "renamed from id-01 ... id-38"
        string DeviceType
        string DeviceInfo
    }

    sample_submission {
        int    TransactionID PK, FK
        float  isFraud "placeholder 0.5; replace with predictions"
    }
```

## Relationships

| Parent | Child | Join key | Cardinality | Notes |
|---|---|---|---|---|
| `train_transaction` | `train_identity` | `TransactionID` | 1 to 0..1 | Only ~24% of transactions have identity data |
| `test_transaction` | `test_identity` | `TransactionID` | 1 to 0..1 | ~28% coverage |
| `test_transaction` | `sample_submission` | `TransactionID` | 1 to 1 | One prediction row per test transaction |

There is **no link between train and test tables**. They are separate splits by time, and test comes after train.

## Row Counts

| Table | Rows | Columns |
|---|---|---|
| `train_transaction` | 590,540 | 394 |
| `train_identity` | 144,233 | 41 |
| `test_transaction` | 506,691 | 393 |
| `test_identity` | 141,907 | 41 |
| `sample_submission` | 506,691 | 2 |

## Indexes

| Index | Table | Column |
|---|---|---|
| `idx_train_transaction_tid` | `train_transaction` | `TransactionID` |
| `idx_train_identity_tid` | `train_identity` | `TransactionID` |
| `idx_test_transaction_tid` | `test_transaction` | `TransactionID` |
| `idx_test_identity_tid` | `test_identity` | `TransactionID` |

## Important Notes

- **These relationships are not enforced.** The tables were created by `pandas.to_sql`, so there are no `PRIMARY KEY` or `FOREIGN KEY` constraints. The relationships above are how the data fits together, but SQLite won't stop bad data from being inserted.
- **Use `LEFT JOIN` for identity data.** An `INNER JOIN` would drop about 76% of transactions.

## Example Join

```sql
SELECT t.TransactionID,
       t.TransactionAmt,
       t.isFraud,
       i.DeviceType
FROM train_transaction AS t
LEFT JOIN train_identity AS i
       ON t.TransactionID = i.TransactionID;
```
