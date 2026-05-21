# Data schema contract — Phase 0

Solution workbook: ID `1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to`  
Reference data: Recykal_Intern_Data `177AdQbbkhVgAuoDARJOhtsB4lngpHK8fgHu_4NkQxJ4`

Scripts read columns **by header name** (case/space normalized to `snake_case`). Do not rely on column position.

---

## `customers` (master)

| Column | Required | Type | Notes |
|--------|----------|------|-------|
| `customer_id` | Yes | string | PK |
| `customer_name` | Yes | string | |
| `segment` | Yes | enum | `Large`, `Mid`, `SME` |
| `email` | Yes | string | Reminder recipient |
| `contact_person` | No | string | |
| `city` | No | string | |
| `state` | No | string | |
| `gstin` | No | string | |
| `pan` | No | string | |
| `credit_terms_days` | No | number | 30, 45, etc. |
| `phone` | No | string | |

**Business rule (Phase 2+):** `Large` → no automated **overdue** notices; pre-due reminders still allowed.

---

## `shipments` (invoices)

| Column | Required | Type | Notes |
|--------|----------|------|-------|
| `shipment_id` | Yes | string | PK |
| `customer_id` | Yes | string | FK → `customers` |
| `invoice_amount` | Yes | number | ≥ 0 |
| `due_date` | Yes | date | |
| `invoice_date` | No | date | If both set: `due_date` ≥ `invoice_date` |

---

## `payments` (installments)

| Column | Required | Type | Notes |
|--------|----------|------|-------|
| `payment_id` | Yes | string | PK |
| `shipment_id` | Yes | string | FK → `shipments` |
| `amount_paid` | Yes | number | ≥ 0; sum per shipment |
| `payment_date` | No | date | Used in Phase 4 trend |

---

## Solution sheets (created by Phase 0 setup)

### `config` (key | value | description)

| Key | Default |
|-----|---------|
| `SPREADSHEET_ID` | Official workbook ID |
| `SUBMISSION_CC` | `ai-strategy-interns-case-submissionsleads@recykal.com` |
| `TIMEZONE` | `Asia/Kolkata` |
| `LARGE_SEGMENT` | `Large` |
| `DRY_RUN` | `true` |

### `data_issues`

Validation output: severity, sheet, row, issue type, message.

### `reminder_log` / `monthly_log` / `run_log`

Reserved for Phases 2–5; headers created in Phase 0.

---

## Relationships

```
customers.customer_id ← shipments.customer_id
shipments.shipment_id ← payments.shipment_id
```

---

## Validation rules (implemented)

| Code | Severity | Rule |
|------|----------|------|
| `DUPLICATE_PK` | P0 | Duplicate `customer_id` / `shipment_id` / `payment_id` |
| `ORPHAN_FK` | P0 | Shipment `customer_id` not in customers |
| `ORPHAN_PAYMENT` | P0 | Payment `shipment_id` not in shipments |
| `EMPTY_REQUIRED` | P0 | Blank required field |
| `MISSING_COLUMN` | P0 | Required header absent |
| `INVALID_DATE` | P0 | Unparseable date |
| `INVALID_NUMBER` | P1 | Non-numeric amount |
| `NEGATIVE_AMOUNT` | P1 | Amount < 0 |
| `DUE_BEFORE_INVOICE` | P1 | due_date < invoice_date |
| `INVALID_SEGMENT` | P1 | Segment not in enum |
| `BLANK_EMAIL` / `INVALID_EMAIL` | P1 | Customer email |
