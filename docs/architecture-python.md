# Python Architecture (Recruiter-Friendly)

This repository implements the Recykal intern assignment **without Apps Script**. All business logic runs in a Python pipeline that consumes `customers.csv`, `shipments.csv`, and `payments.csv`, then generates:

- **Task A-1**: reminder **email previews** (dry-run) + `reminder_log.csv`
- **Task A-2**: monthly balance confirmation **email previews** (dry-run) + `monthly_log.csv`
- **Task B**: dashboard artifacts: `dashboard.html` + `collections_dashboard.xlsx` (upload to Google Sheets)

The pipeline is designed so a scheduler (GitHub Actions cron) can run it periodically to keep outputs fresh (“no delay” = bounded by the schedule interval).

---

## 1) Data model

Source tables (CSV exports):

- `customers`: `customer_id`, `customer_name`, `segment`, `email`, …
- `shipments`: `shipment_id`, `customer_id`, `invoice_amount`, `invoice_date`, `due_date`, …
- `payments`: `payment_id`, `payment_date`, `amount_paid`, …

### Important note about the provided dataset
The provided `payments.csv` is keyed by `customer_id` (not `shipment_id`). To still compute **per-shipment outstanding**, the pipeline performs a deterministic **FIFO allocation** of each customer’s payments to that customer’s shipments (oldest due first). This rule is documented and consistent across reminders/monthly/dashboard.

---

## 2) Single source of truth: receivables engine (Phase 1)

All tasks are driven by the computed view:

`python/output/receivables_computed.csv`

Computed fields (per shipment):
- `amount_paid_total`
- `outstanding`
- `is_settled`
- `days_to_due` (negative means overdue)
- `days_overdue`
- eligibility flags: `in_7d_window`, `in_3d_window`, `in_1d_window`, `eligible_for_overdue` (Large excluded)

Code:
- `python/src/receivables.py`
- `python/src/payment_allocation.py`

---

## 3) Task A-1 — automated reminders (Phase 2)

Rule windows:
- 7 days before due: `days_to_due == 7`
- 3 days before due: `days_to_due == 3`
- 1 day before due: `days_to_due == 1`
- overdue: `days_to_due < 0 AND segment != Large AND outstanding > 0`

Deduplication:
- Uses `python/output/reminder_log.csv`
- Unique key: `(shipment_id, reminder_type, due_date)`

Output:
- `python/output/emails/reminders/*.txt`

Code:
- `python/src/reminders.py`

---

## 4) Task A-2 — monthly balance confirmation (Phase 3)

One file per customer per month containing:
- all unpaid + partially paid shipments
- shipment-wise invoice/paid/outstanding (+ due date)
- total outstanding exposure

Deduplication:
- Uses `python/output/monthly_log.csv`
- Unique key: `(customer_id, period_yyyy_mm)`

Output:
- `python/output/emails/monthly/*.txt`

Code:
- `python/src/monthly.py`

---

## 5) Task B — dashboard (Phase 4)

Generated views:
- Summary KPIs
- Outstanding by customer (desc)
- Aging buckets (Not Yet Due, 1–30, 31–60, 61+)
- Daily collections trend (last 30 days)

Outputs:
- `python/output/dashboard.html` (interactive, opens locally)
- `python/output/collections_dashboard.xlsx` (upload to Google Sheets for submission)

Code:
- `python/src/dashboard.py`

---

## 6) Phase 5 — integration + “no delay” refresh

`python run.py phase5` runs:
1) load data
2) validate (writes `data_issues.csv`)
3) compute receivables
4) generate reminder previews + logs (deduped)
5) generate monthly previews + logs (deduped)
6) generate dashboard HTML + XLSX
7) write `run_log.csv` + `phase5_operator_summary.md`
8) publish latest artifacts into `deploy/` (recruiter-facing)

Code:
- `python/src/integration.py`

Scheduler (recommended):
- GitHub Actions cron workflow: `.github/workflows/refresh.yml`

---

## 7) How the recruiter can verify correctness quickly

1) Run validation:
   - `python run.py validate` → check `python/output/data_issues.csv`
2) Run full pipeline:
   - `python run.py phase5`
3) Open dashboard:
   - `deploy/index.html` (or `python/output/dashboard.html`)
4) Upload workbook:
   - `deploy/collections_dashboard.xlsx` → Google Drive → Open with Google Sheets
5) Inspect proof logs:
   - `deploy/run_log.csv`
   - `deploy/phase5_operator_summary.md`

