"""Build an auditable AI-assisted issue queue and schema-mapping baseline."""

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"

CATEGORY_RULES = {
    "missing_record": ("Completeness", "Reload missing source record", 0.98),
    "duplicate_record": ("Uniqueness", "Merge or remove duplicate", 0.97),
    "invalid_email": ("Validity", "Correct or quarantine email", 0.94),
    "missing_phone": ("Completeness", "Request or recover phone", 0.91),
    "orphan_record": ("Referential integrity", "Repair customer foreign key", 0.99),
    "amount_mismatch": ("Accuracy", "Recalculate normalized amount", 0.96),
    "unmapped_customer": ("Referential integrity", "Migrate customer before order", 0.99),
}

LEGACY_FIELDS = {
    "client_id": "unique identifier for a legacy customer",
    "client_name": "customer full name",
    "email": "customer email address",
    "phone": "customer phone number",
    "country": "customer country name",
    "signup_date": "date when customer registered",
    "segment_code": "customer commercial segment",
    "order_id": "unique identifier for an order",
    "order_date": "date when order was placed",
    "amount": "monetary order amount in source currency",
    "currency": "currency of monetary amount",
    "status": "order lifecycle status",
    "channel": "sales channel where order was placed",
}

TARGET_FIELDS = {
    "customer_id": "unique identifier for a target customer",
    "legacy_client_id": "traceability identifier for a legacy customer",
    "customer_full_name": "customer full name",
    "email_address": "customer email address",
    "phone_e164": "standardized customer phone number",
    "country_code": "standardized customer country code",
    "created_at": "timestamp when customer registered",
    "customer_tier": "customer commercial tier",
    "order_key": "unique identifier for a target order",
    "legacy_order_id": "traceability identifier for a legacy order",
    "ordered_at": "timestamp when order was placed",
    "amount_clp": "order amount normalized to Chilean pesos",
    "order_status": "order lifecycle status",
    "sales_channel": "sales channel where order was placed",
}


def build_issue_queue(issues: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in issues.itertuples(index=False):
        category, action, confidence = CATEGORY_RULES.get(
            row.issue_type, ("Other", "Inspect issue manually", 0.55)
        )
        records.append(
            {
                "issue_id": row.issue_id,
                "suggested_category": category,
                "suggested_action": action,
                "confidence_score": confidence,
                "review_status": "Auto Accepted" if confidence >= 0.95 else "Human Review",
                "model_method": "transparent_rule_baseline_v1",
            }
        )
    return pd.DataFrame(records)


def build_schema_mapping() -> pd.DataFrame:
    legacy_items = list(LEGACY_FIELDS.items())
    target_items = list(TARGET_FIELDS.items())
    corpus = [f"{name} {description}" for name, description in legacy_items + target_items]
    vectors = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(corpus)
    legacy_vectors = vectors[: len(legacy_items)]
    target_vectors = vectors[len(legacy_items) :]
    scores = cosine_similarity(legacy_vectors, target_vectors)

    rows = []
    for i, (legacy_name, _) in enumerate(legacy_items):
        best_indices = scores[i].argsort()[::-1][:2]
        for rank, target_index in enumerate(best_indices, start=1):
            score = round(float(scores[i, target_index]), 4)
            rows.append(
                {
                    "legacy_field": legacy_name,
                    "suggested_target_field": target_items[target_index][0],
                    "candidate_rank": rank,
                    "similarity_score": score,
                    "review_status": "Suggested" if score >= 0.35 else "Human Review",
                    "model_method": "tfidf_semantic_baseline_v1",
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    issues_path = PROCESSED_DIR / "migration_issues.csv"
    if not issues_path.exists():
        raise FileNotFoundError("Run src/generate_data.py before building the AI review queue.")

    issues = pd.read_csv(issues_path)
    queue = build_issue_queue(issues)
    mapping = build_schema_mapping()
    queue.to_csv(PROCESSED_DIR / "ai_review_queue.csv", index=False)
    mapping.to_csv(PROCESSED_DIR / "schema_mapping_review.csv", index=False)
    print(f"Created {len(queue):,} issue-review rows and {len(mapping):,} mapping candidates.")


if __name__ == "__main__":
    main()

