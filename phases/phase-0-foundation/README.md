# Phase 0 — Foundation & Data Contract

**Status:** Implemented  
**Architecture:** [docs/architecture-python.md](../../docs/architecture-python.md)  
**Edge cases:** [docs/edge-cases/phase-0-edge-cases.md](../../docs/edge-cases/phase-0-edge-cases.md)

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Schema contract | [SCHEMA.md](./SCHEMA.md) |
| Data validation | `python/src/validate.py` → `python/output/data_issues.csv` |

## Workbook

**CSV source workbook:** [Open spreadsheet](https://docs.google.com/spreadsheets/d/1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to/edit?gid=1296664018#gid=1296664018) · ID `1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to`

**Reference data:** [Recykal_Intern_Data](https://docs.google.com/spreadsheets/d/177AdQbbkhVgAuoDARJOhtsB4lngpHK8fgHu_4NkQxJ4/edit?gid=2064198405#gid=2064198405)

## Setup steps

Export `customers`, `shipments`, `payments` as CSV into `python/data/` (or configure `python/config.yaml` gids and use `python run.py fetch-data`), then:

1. `cd python`
2. `pip install -r requirements.txt`
3. `python run.py validate`
4. Fix any **P0** rows in `python/output/data_issues.csv`

## Notes

- This repo intentionally does **not** create “solution tabs” inside Google Sheets.
- All validation + logs are generated in `python/output/` and published to `deploy/` by Phase 5.

## Exit criteria checklist

- [ ] `customers`, `shipments`, `payments` present with required headers
- [ ] `config` contains `SUBMISSION_CC` = `ai-strategy-interns-case-submissionsleads@recykal.com`
- [ ] Validation runs with 0 P0 errors on clean data
- [ ] New shipment/payment rows appear after exporting fresh CSVs (or via scheduled fetch)
- [ ] `python/output/data_issues.csv` is empty (header-only) when data is valid

## Next phase

Phase 1 computes `python/output/receivables_computed.csv` via `python/src/receivables.py`.
