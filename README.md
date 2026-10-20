# AI-Assisted Data Migration Quality Dashboard

Portfolio project demonstrating how SQL, Python, Power BI, and AI-assisted review can be combined to monitor a CRM data migration.

## Business problem

A company is migrating customer and order data from a legacy CRM into a new analytics platform. The migration team needs to know:

- whether all expected records were transferred;
- whether customer and order values remained consistent;
- which data-quality problems are critical;
- which ambiguous cases should be sent to human review;
- whether the migrated data is ready for business reporting.

## Project status

- [x] Reproducible synthetic source and target datasets
- [x] Controlled migration defects
- [x] Data dictionary and target star-schema specification
- [x] SQL quality checks
- [x] AI-assisted review queue baseline
- [ ] Power Query transformations
- [ ] DAX measures
- [ ] Power BI report
- [ ] Dashboard screenshots and findings

## Dataset

The generator creates 1,000 legacy customers and 5,000 legacy orders. The target system contains intentionally injected defects: missing records, duplicate customers, invalid emails, missing phone numbers, orphan orders, transformed dates, and amount mismatches.

All generated people and transactions are synthetic.

## AI-assisted component

The AI layer is used only for ambiguous work. Deterministic reconciliation remains in SQL and Python.

The current baseline:

1. ranks probable target fields for each legacy field;
2. classifies migration issues;
3. assigns a confidence score;
4. routes low-confidence cases to human review.

The baseline is reproducible and does not require an API key. Its decisions are stored in CSV files so they can be audited in Power BI.

## Repository structure

```text
data/
  raw/                 Legacy source extracts
  processed/           Migrated tables and analytical outputs
docs/                   Project scope and data dictionary
powerbi/                Power BI model and report instructions
sql/                    PostgreSQL schema and quality checks
src/                    Python data and AI-review pipelines
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/generate_data.py
python src/build_ai_review_queue.py
```

Then import the files from `data/processed/` into Power BI Desktop.

## Main Power BI KPIs

- Migration Readiness Score
- Customer Migration Rate
- Order Migration Rate
- Duplicate Rate
- Referential Integrity Rate
- Amount Reconciliation Difference
- Critical Issues
- AI Suggestions Accepted
- Records Requiring Human Review

## Design principle

AI proposes; deterministic checks verify; people approve ambiguous cases.

