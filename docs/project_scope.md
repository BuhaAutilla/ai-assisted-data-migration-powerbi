# Project scope

## Audience

- Migration manager
- Data analyst
- Data steward
- Business operations lead

## Decisions supported

1. Is the migrated dataset ready for reporting?
2. Which defects block migration sign-off?
3. Which entities and error categories require attention first?
4. Which AI suggestions can be accepted automatically and which require review?

## Controlled migration scenarios

| Scenario | Expected scale | Severity |
|---|---:|---|
| Missing target customers | 50 customers | Critical |
| Duplicate target customers | 20 rows | High |
| Invalid target emails | 12 customers | Medium |
| Missing target phones | 25 customers | Low |
| Missing target orders | 200 orders | Critical |
| Orphan target orders | 30 orders | Critical |
| Incorrect order amounts | 15 orders | High |
| Ambiguous schema mappings | Several fields | Review |

Exact counts are reproducible with the generator seed and are also recorded in `migration_issues.csv`.

## Definition of done

- Data generation runs from a clean checkout.
- SQL checks reproduce the principal defect counts.
- Power BI uses a documented star schema.
- Every headline KPI has a defined formula.
- AI recommendations expose method, confidence, and review status.
- README includes final dashboard screenshots and three business findings.

