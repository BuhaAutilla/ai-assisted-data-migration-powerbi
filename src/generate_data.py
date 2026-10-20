"""Generate reproducible synthetic CRM migration data with controlled defects."""

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20261020
N_CUSTOMERS = 1_000
N_ORDERS = 5_000
USD_TO_CLP = 900.0

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

FIRST_NAMES = [
    "Sofia", "Mateo", "Isidora", "Benjamin", "Camila", "Tomas",
    "Valentina", "Vicente", "Antonia", "Martin", "Catalina", "Joaquin",
]
LAST_NAMES = [
    "Gonzalez", "Munoz", "Rojas", "Diaz", "Perez", "Soto",
    "Contreras", "Silva", "Martinez", "Sepulveda", "Morales", "Rodriguez",
]


def make_customers(rng: np.random.Generator) -> pd.DataFrame:
    ids = np.arange(1, N_CUSTOMERS + 1)
    first = rng.choice(FIRST_NAMES, N_CUSTOMERS)
    last = rng.choice(LAST_NAMES, N_CUSTOMERS)
    signup = pd.Timestamp("2023-01-01") + pd.to_timedelta(
        rng.integers(0, 1_095, N_CUSTOMERS), unit="D"
    )
    segment = rng.choice(["A", "B", "C"], N_CUSTOMERS, p=[0.18, 0.37, 0.45])
    return pd.DataFrame(
        {
            "client_id": ids,
            "client_name": first + " " + last,
            "email": [f"client{i:04d}@example.cl" for i in ids],
            "phone": [f"+56 9 {8_000_0000 + i:08d}" for i in ids],
            "country": "Chile",
            "signup_date": signup.date,
            "segment_code": segment,
        }
    )


def make_orders(rng: np.random.Generator) -> pd.DataFrame:
    ids = np.arange(1, N_ORDERS + 1)
    currencies = rng.choice(["CLP", "USD"], N_ORDERS, p=[0.9, 0.1])
    base_clp = np.round(rng.lognormal(mean=11.1, sigma=0.65, size=N_ORDERS), 0)
    amounts = np.where(currencies == "USD", np.round(base_clp / USD_TO_CLP, 2), base_clp)
    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 730, N_ORDERS), unit="D"
    )
    return pd.DataFrame(
        {
            "order_id": ids,
            "client_id": rng.integers(1, N_CUSTOMERS + 1, N_ORDERS),
            "order_date": dates.date,
            "amount": amounts,
            "currency": currencies,
            "status": rng.choice(
                ["completed", "cancelled", "refunded"],
                N_ORDERS,
                p=[0.86, 0.09, 0.05],
            ),
            "channel": rng.choice(["web", "mobile", "sales"], N_ORDERS, p=[0.48, 0.42, 0.1]),
        }
    )


def migrate_customers(
    legacy: pd.DataFrame, rng: np.random.Generator
) -> tuple[pd.DataFrame, list[dict]]:
    issues: list[dict] = []
    missing_ids = set(rng.choice(legacy.client_id, 50, replace=False).tolist())
    target = legacy.loc[~legacy.client_id.isin(missing_ids)].copy()
    target = target.rename(
        columns={
            "client_id": "legacy_client_id",
            "client_name": "customer_full_name",
            "email": "email_address",
            "signup_date": "created_at",
        }
    )
    target.insert(0, "customer_id", np.arange(100_001, 100_001 + len(target)))
    target["phone_e164"] = target["phone"].str.replace(" ", "", regex=False)
    target["country_code"] = "CL"
    target["created_at"] = pd.to_datetime(target["created_at"]).dt.strftime("%Y-%m-%d 09:00:00")
    target["customer_tier"] = target["segment_code"].map(
        {"A": "Gold", "B": "Silver", "C": "Bronze"}
    )
    target = target.drop(columns=["phone", "country", "segment_code"])

    for legacy_id in sorted(missing_ids):
        issues.append(issue("customer", legacy_id, "missing_record", "Critical", "Legacy customer is absent from target."))

    invalid_idx = rng.choice(target.index, 12, replace=False)
    for idx in invalid_idx:
        target.loc[idx, "email_address"] = target.loc[idx, "email_address"].replace("@", "")
        issues.append(issue("customer", int(target.loc[idx, "legacy_client_id"]), "invalid_email", "Medium", "Target email has an invalid format."))

    phone_idx = rng.choice(target.index.difference(invalid_idx), 25, replace=False)
    for idx in phone_idx:
        target.loc[idx, "phone_e164"] = pd.NA
        issues.append(issue("customer", int(target.loc[idx, "legacy_client_id"]), "missing_phone", "Low", "Target phone is missing."))

    duplicate_rows = target.sample(20, random_state=SEED).copy()
    duplicate_rows["customer_id"] = np.arange(200_001, 200_001 + len(duplicate_rows))
    for legacy_id in duplicate_rows.legacy_client_id:
        issues.append(issue("customer", int(legacy_id), "duplicate_record", "High", "Customer appears more than once in target."))
    target = pd.concat([target, duplicate_rows], ignore_index=True)
    return target, issues


def migrate_orders(
    legacy_orders: pd.DataFrame,
    target_customers: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, list[dict]]:
    issues: list[dict] = []
    missing_order_ids = set(rng.choice(legacy_orders.order_id, 200, replace=False).tolist())
    target = legacy_orders.loc[~legacy_orders.order_id.isin(missing_order_ids)].copy()
    customer_map = (
        target_customers.drop_duplicates("legacy_client_id")
        .set_index("legacy_client_id")["customer_id"]
    )
    target["customer_id"] = target["client_id"].map(customer_map)
    target["amount_clp"] = np.where(
        target["currency"].eq("USD"), target["amount"] * USD_TO_CLP, target["amount"]
    ).round(0)
    target = target.rename(
        columns={
            "order_id": "legacy_order_id",
            "order_date": "ordered_at",
            "status": "order_status",
            "channel": "sales_channel",
        }
    )
    target.insert(0, "order_key", np.arange(500_001, 500_001 + len(target)))
    target["ordered_at"] = pd.to_datetime(target["ordered_at"]).dt.strftime("%Y-%m-%d 12:00:00")
    target = target.drop(columns=["client_id", "amount", "currency"])

    for legacy_id in sorted(missing_order_ids):
        issues.append(issue("order", legacy_id, "missing_record", "Critical", "Legacy order is absent from target."))

    orphan_idx = rng.choice(target.index[target.customer_id.notna()], 30, replace=False)
    for idx in orphan_idx:
        target.loc[idx, "customer_id"] = 999_999
        issues.append(issue("order", int(target.loc[idx, "legacy_order_id"]), "orphan_record", "Critical", "Order references a customer that does not exist."))

    amount_idx = rng.choice(target.index.difference(orphan_idx), 15, replace=False)
    for idx in amount_idx:
        target.loc[idx, "amount_clp"] *= 10
        issues.append(issue("order", int(target.loc[idx, "legacy_order_id"]), "amount_mismatch", "High", "Target amount differs materially from the normalized source amount."))

    # Missing customers can produce additional null foreign keys; record them explicitly.
    null_customer_rows = target[target.customer_id.isna()]
    for _, row in null_customer_rows.iterrows():
        issues.append(issue("order", int(row.legacy_order_id), "unmapped_customer", "Critical", "Order customer was not migrated, leaving no valid target key."))

    return target, issues


def issue(entity: str, legacy_id: int, issue_type: str, severity: str, description: str) -> dict:
    return {
        "entity_type": entity,
        "legacy_id": legacy_id,
        "issue_type": issue_type,
        "severity": severity,
        "description": description,
        "detected_by": "controlled_injection",
    }


def make_date_dimension() -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    iso = dates.isocalendar()
    return pd.DataFrame(
        {
            "date": dates.date,
            "year": dates.year,
            "quarter": "Q" + dates.quarter.astype(str),
            "month_number": dates.month,
            "month_name": dates.month_name(),
            "week_number": iso.week.astype(int).to_numpy(),
            "day_of_week": dates.day_name(),
        }
    )


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    customers = make_customers(rng)
    orders = make_orders(rng)
    target_customers, customer_issues = migrate_customers(customers, rng)
    target_orders, order_issues = migrate_orders(orders, target_customers, rng)

    issues = pd.DataFrame(customer_issues + order_issues)
    issues.insert(0, "issue_id", [f"ISS-{i:05d}" for i in range(1, len(issues) + 1)])

    customers.to_csv(RAW_DIR / "legacy_customers.csv", index=False)
    orders.to_csv(RAW_DIR / "legacy_orders.csv", index=False)
    target_customers.to_csv(PROCESSED_DIR / "target_customers.csv", index=False)
    target_orders.to_csv(PROCESSED_DIR / "target_orders.csv", index=False)
    issues.to_csv(PROCESSED_DIR / "migration_issues.csv", index=False)
    make_date_dimension().to_csv(PROCESSED_DIR / "dim_date.csv", index=False)

    print(f"Generated {len(customers):,} legacy customers and {len(orders):,} legacy orders.")
    print(f"Generated {len(target_customers):,} target customer rows and {len(target_orders):,} target orders.")
    print(f"Recorded {len(issues):,} migration issues.")


if __name__ == "__main__":
    main()

