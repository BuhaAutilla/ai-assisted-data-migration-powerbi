# Power BI build notes

## Import

Load these files from `data/processed/`:

- `target_customers.csv`
- `target_orders.csv`
- `migration_issues.csv`
- `ai_review_queue.csv`
- `schema_mapping_review.csv`
- `dim_date.csv`

Also load both files from `data/raw/` for source-to-target reconciliation.

## Power Query

1. Set explicit column types.
2. Add an `order_date` column from `target_orders[ordered_at]`.
3. Disable automatic date/time intelligence.
4. Keep issue and AI tables separate; relate them by `issue_id`.
5. Validate uniqueness before creating one-to-many relationships.

## Planned report pages

1. Executive Overview
2. Migration Reconciliation
3. Data Quality
4. AI Review Queue
5. Schema Mapping Review

The `.pbix` file and exported screenshots will be added after the analytical layer is validated.

