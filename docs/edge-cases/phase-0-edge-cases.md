# Phase 0 — Foundation & Data Contract: Edge Cases

**Architecture reference:** Phase 0 in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Goal under test:** Stable schema, dynamic tables, validation, and config before receivables or automation.

---

## Workbooks (Recykal)

| Role | Property | Value |
|------|----------|--------|
| **Solution (editable)** | URL | [Spreadsheet](https://docs.google.com/spreadsheets/d/1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to/edit?gid=1296664018#gid=1296664018) |
| | Spreadsheet ID | `1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to` |
| **Reference** | Original data | [Recykal_Intern_Data](https://docs.google.com/spreadsheets/d/177AdQbbkhVgAuoDARJOhtsB4lngpHK8fgHu_4NkQxJ4/edit?gid=2064198405#gid=2064198405) |
| **Source tabs** | | `customers` · `shipments` · `payments` |

**Apps Script binding:** Script bound to this workbook. `SpreadsheetApp.getActiveSpreadsheet()` is used when bound; fallback ID `1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to`. Do not hardcode row ranges.

### Observed `customers` schema (live source)

| Column | Notes |
|--------|--------|
| `customer_id` | PK, e.g. `C001` |
| `customer_name` | Legal / display name |
| `contact_person` | Optional ops field |
| `city`, `state` | Location |
| `gstin`, `pan` | Tax identifiers |
| `credit_terms_days` | e.g. 30, 45 — terms may inform due dates on shipments |
| `segment` | Values include **`Large`**, **`Mid`**, **`SME`** (overdue auto-exclusion applies to `Large` only) |
| `email` | Reminder / monthly recipient |
| `phone` | Not required for automation |

Confirm `shipments` and `payments` column headers against the same workbook before Phase 1 (expected: `shipment_id`, `customer_id`, `invoice_amount`, `invoice_date`, `due_date`; `payment_id`, `shipment_id`, `amount_paid`, `payment_date` per problem statement).

**Access note:** Request edit access or **File → Make a copy** into your Drive for Apps Script triggers and dashboard sheets. View-only access is insufficient for automation deployment.

---

## 1. Schema & primary keys

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P0-E01 | Duplicate `customer_id` in `customers` | Flag in `data_issues`; do not silently overwrite | Two rows with same `customer_id` | P0 |
| P0-E02 | Duplicate `shipment_id` in `shipments` | Flag; downstream joins must not double-count invoice | Two rows same `shipment_id`, different amounts | P0 |
| P0-E03 | Duplicate `payment_id` in `payments` | Flag; risk of double-counting paid amount | Two rows same `payment_id` | P0 |
| P0-E04 | Empty `customer_id` on shipment row | Flag; exclude from automation until fixed | Blank `customer_id` | P0 |
| P0-E05 | Empty `shipment_id` on payment row | Flag; payment cannot attach to invoice | Blank `shipment_id` | P0 |
| P0-E06 | `shipment_id` exists only in payments, not shipments | Orphan payment flagged | Payment for `SHP-999` with no shipment | P0 |
| P0-E07 | `customer_id` on shipment not in `customers` | Orphan shipment flagged | `customer_id = C-UNKNOWN` | P0 |
| P0-E08 | Extra/unexpected columns added by user | Script reads by header name, not column index; or validation warns | Insert column between PK and amount | P1 |
| P0-E09 | Header row renamed (e.g. `Customer ID` vs `customer_id`) | Config mapping or fail loud; no silent empty reads | Rename header | P1 |
| P0-E10 | Completely empty sheet (headers only) | Validation passes with 0 rows; no script errors | Delete all data rows | P2 |

---

## 2. Data types & formats

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P0-E11 | `invoice_amount` stored as text (`"1,00,000"`) | Parse or flag; never treat as 0 | Locale-formatted string | P0 |
| P0-E12 | Negative `invoice_amount` | Flag or reject | `-5000` | P1 |
| P0-E13 | Zero `invoice_amount` | Allowed if business permits; flag for review | `0` | P2 |
| P0-E14 | `due_date` before `invoice_date` | Flag logical inconsistency | due < invoice | P1 |
| P0-E15 | Invalid date string in `due_date` | Flag; skip in automation | `31/02/2025` or `TBD` | P0 |
| P0-E16 | Date entered as serial number vs display string | Normalized to Date in script timezone | Mixed cell formats | P1 |
| P0-E17 | `amount_paid` negative (refund/adjustment) | Document rule: flag, or net into paid sum with business sign-off | `-1000` payment row | P1 |
| P0-E18 | Blank `email` for customer | Flag before Phase 2; reminders must not send to empty | Missing email | P1 |

---

## 3. Dynamic ranges & tables

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P0-E19 | New row appended below table | Auto-included in `getDataRange()` / Table expand | Paste 100 rows at bottom | P0 |
| P0-E20 | Row inserted in middle of table | Still read correctly | Insert row between existing | P1 |
| P0-E21 | Row deleted from middle | IDs no longer referenced; orphan payments if shipment deleted | Delete shipment, keep payments | P0 |
| P0-E22 | Filtered view hides rows | Script reads full data range, not filtered visible rows only | Apply filter on sheet | P1 |
| P0-E23 | Frozen rows / hidden columns | Headers still discoverable | Hide column A | P2 |
| P0-E24 | Second header row accidentally added | Validation detects duplicate headers or wrong row count | Duplicate row 1 | P1 |
| P0-E25 | Hardcoded range `A2:A100` in legacy formula | Document as anti-pattern; Phase 0 exit criteria fails if present | Inspect formulas | P1 |

---

## 4. Config sheet

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P0-E26 | CC email missing in `config` | Reminder job aborts with clear `run_log` error | Clear CC cell | P0 |
| P0-E27 | Invalid CC email format | Fail validation on deploy / menu setup | `not-an-email` | P1 |
| P0-E28 | Timezone blank | Default to spreadsheet timezone with logged warning | Empty timezone | P1 |
| P0-E29 | Segment enum typo (`Large ` with trailing space) | Trim on read; overdue exclusion must match intended segment | `Large ` vs `Large` | P0 |
| P0-E30 | Multiple CC addresses required | Support comma-separated CC or secondary config row | Add second evaluator email | P2 |

---

## 5. Access, binding & operations

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P0-E31 | Apps Script not bound to spreadsheet | Document binding step; triggers fail clearly | Standalone script project | P1 |
| P0-E32 | User lacks edit permission | Menu shows read-only message | Viewer role account | P2 |
| P0-E33 | Concurrent edit while validation runs | Last write wins; next validation picks up changes | Two users append payments | P2 |
| P0-E34 | `IMPORTRANGE` delay / #REF! on source | `data_issues` shows import failure | Break source link | P1 |
| P0-E35 | Very large sheet (10k+ rows) | Validation completes within execution time limit; consider batching | Stress dataset | P2 |

---

## 6. Phase 0 exit checklist (edge-case gate)

Before starting Phase 1, confirm:

- [ ] P0-E06, P0-E07, P0-E01–E03 all **flag**, not crash
- [ ] P0-E19 passes without editing formula ranges
- [ ] P0-E26 blocks misconfigured email automation
- [ ] Orphan payment after shipment delete (P0-E21) is visible to ops

---

## 7. Suggested test fixtures (minimal)

| Fixture name | Purpose |
|--------------|---------|
| `VALID_BASE` | 3 customers, 5 shipments, 4 payments, all FKs valid |
| `ORPHAN_PAYMENT` | `VALID_BASE` + payment for unknown `shipment_id` |
| `DUPLICATE_PK` | Duplicate `shipment_id` pair |
| `BAD_DATES` | One shipment with non-date `due_date` |
