# Data dictionary

## Raw source tables

### `legacy_customers.csv`

| Column | Type | Description |
|---|---|---|
| `client_id` | integer | Legacy customer key |
| `client_name` | text | Full customer name |
| `email` | text | Customer email |
| `phone` | text | Chilean phone in legacy display format |
| `country` | text | Country name |
| `signup_date` | date | Customer registration date |
| `segment_code` | text | Legacy segment: A, B, or C |

### `legacy_orders.csv`

| Column | Type | Description |
|---|---|---|
| `order_id` | integer | Legacy order key |
| `client_id` | integer | Legacy customer key |
| `order_date` | date | Order date |
| `amount` | decimal | Amount in the stated currency |
| `currency` | text | CLP or USD |
| `status` | text | completed, cancelled, or refunded |
| `channel` | text | web, mobile, or sales |

## Migrated target tables

### `target_customers.csv`

| Column | Type | Description |
|---|---|---|
| `customer_id` | integer | Target customer key |
| `legacy_client_id` | integer | Traceability key to source |
| `customer_full_name` | text | Standardized customer name |
| `email_address` | text | Normalized email |
| `phone_e164` | text | Phone in E.164-style format |
| `country_code` | text | ISO-like country code |
| `created_at` | datetime | Registration timestamp |
| `customer_tier` | text | Gold, Silver, or Bronze |

### `target_orders.csv`

| Column | Type | Description |
|---|---|---|
| `order_key` | integer | Target order key |
| `legacy_order_id` | integer | Traceability key to source |
| `customer_id` | integer | Target customer key |
| `ordered_at` | datetime | Order timestamp |
| `amount_clp` | decimal | Normalized amount in CLP |
| `order_status` | text | Standardized order status |
| `sales_channel` | text | Standardized sales channel |

## Analytical tables

### `migration_issues.csv`

Deterministically detected or intentionally injected migration defects.

| Column | Description |
|---|---|
| `issue_id` | Unique issue identifier |
| `entity_type` | customer or order |
| `legacy_id` | Source identifier where available |
| `issue_type` | Machine-readable error category |
| `severity` | Critical, High, Medium, or Low |
| `description` | Human-readable explanation |
| `detected_by` | rule or controlled_injection |

### `ai_review_queue.csv`

Issue classification and triage output.

| Column | Description |
|---|---|
| `issue_id` | Link to migration issue |
| `suggested_category` | AI-assisted issue grouping |
| `suggested_action` | Proposed remediation |
| `confidence_score` | Value from 0 to 1 |
| `review_status` | Auto Accepted or Human Review |
| `model_method` | Transparent method identifier |

### `schema_mapping_review.csv`

Candidate mappings between legacy and target fields, including similarity score and human-review status.

### `dim_date.csv`

Calendar dimension used by the Power BI model.

## Recommended Power BI relationships

```text
dim_date[date]             1 -> * target_orders[order_date]
target_customers[customer_id] 1 -> * target_orders[customer_id]
migration_issues[issue_id] 1 -> 1 ai_review_queue[issue_id]
```

Use single-direction filtering. Keep source reconciliation tables separate from the primary reporting star where possible.

