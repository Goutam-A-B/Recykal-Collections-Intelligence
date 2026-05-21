# Phase 4 — Real-Time Collections Dashboard (B): Edge Cases

**Architecture reference:** Phase 4 in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Goal under test:** KPIs, customer outstanding table, aging buckets, 30-day trend — dynamic ranges, reconciled totals.

---

## 1. Summary KPIs

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E01 | Total Invoice Value | `SUM(all shipments.invoice_amount)` regardless of payment status | 3 invoices | P0 |
| P4-E02 | Total Collected | `SUM(all payments.amount_paid)` | Multiple payments | P0 |
| P4-E03 | Total Outstanding | Sum per-shipment `(invoice - paid)`; only positive exposure or net — **document**: typically sum of positive outstanding per shipment | Mixed | P0 |
| P4-E04 | KPI reconciliation | `Total Outstanding` ≈ sum of aging buckets (if buckets use same rules) | Cross-check | P0 |
| P4-E05 | # Overdue Shipments | Count open shipments where `today > due_date` and outstanding > 0 | 2 overdue, 1 paid overdue | P0 |
| P4-E06 | Settled but historically overdue | Not counted in overdue **count** if outstanding = 0 | Paid yesterday, was 60d late | P0 |
| P4-E07 | New shipment row appended | KPIs update without range edit | +1 row bottom | P0 |
| P4-E08 | New payment row appended | Collected + Outstanding update | +payment | P0 |
| P4-E09 | Deleted shipment row | KPIs decrease; no #REF! | Remove row | P1 |
| P4-E10 | Invoice amount edited | Invoice Value + Outstanding change | Amend invoice | P1 |

---

## 2. Outstanding by customer

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E11 | Sort descending by outstanding | Highest exposure first | C1: 10k, C2: 50k, C3: 30k | P0 |
| P4-E12 | Tie on outstanding | Stable secondary sort (name or id) | Two at 25k | P2 |
| P4-E13 | Customer with 0 outstanding | Omitted or shown as 0 — document; typically omit from priority list | All paid | P1 |
| P4-E14 | # open shipments column | Count only unsettled shipments | 3 open, 2 paid | P1 |
| P4-E15 | Segment column visible | Helps Large manual follow-up | Mixed segments | P2 |
| P4-E16 | Customer with shipments but missing master | Flag or exclude with `data_issues` link | Orphan | P0 |
| P4-E17 | Same customer name, different IDs | Two rows — no erroneous merge | Duplicate names | P1 |

---

## 3. Invoice aging buckets

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E18 | Not Yet Due | Outstanding > 0 and `today <= due_date` | Due next week | P0 |
| P4-E19 | 1–30 days overdue | `1 <= today - due <= 30` | 15 days late | P0 |
| P4-E20 | 31–60 days overdue | 31–60 inclusive | 45 days late | P0 |
| P4-E21 | 61+ days overdue | `today - due >= 61` | 90 days late | P0 |
| P4-E22 | Due today, outstanding > 0 | Bucket = Not Yet Due (`today <= due_date`) | Due today | P0 |
| P4-E23 | Exactly 30 days overdue | In 1–30 bucket (inclusive upper bound) | due = today - 30 | P0 |
| P4-E24 | Exactly 31 days overdue | In 31–60 bucket | due = today - 31 | P0 |
| P4-E25 | Settled shipment | Excluded from all buckets (outstanding not > 0) | Paid in full | P0 |
| P4-E26 | Partial payment in overdue bucket | Bucket amount = **remaining** outstanding, not full invoice | 50% paid, 60d late | P0 |
| P4-E27 | Bucket sum vs total outstanding | Equal within rounding | All open shipments | P0 |
| P4-E28 | Shipment with outstanding 0 in 61+ due date past | Not in 61+ (settled) | Edge settle | P0 |

---

## 4. Daily collections trend (30 days)

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E29 | Payment today | Appears in today's bar/point | Pay today | P0 |
| P4-E30 | Payment 31 days ago | Outside 30-day window | Old payment | P1 |
| P4-E31 | Multiple payments same day | Sum aggregated for that date | 3 rows same date | P0 |
| P4-E32 | Day with zero collections | Show 0, not gap break | No payments 5 days | P2 |
| P4-E33 | Future-dated payment | Policy: exclude or include — document; recommend exclude | payment_date tomorrow | P1 |
| P4-E34 | Payment with invalid date | Excluded + flagged | Bad date | P1 |
| P4-E35 | Chart range dynamic | Adding row extends chart source | +10 payments | P0 |
| P4-E36 | Timezone date boundary on payment_date | Bucketed by spreadsheet TZ | UTC vs IST | P1 |

---

## 5. Real-time & formula mechanics

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E37 | Hardcoded `A2:A500` in dashboard | Fail review — use Table/QUERY | Inspect | P1 |
| P4-E38 | QUERY #REF! when sheet renamed | Error visible; fix mapping | Rename `shipments` | P1 |
| P4-E39 | Circular dependency | Sheet warns; no silent wrong KPI | Bad formula link | P0 |
| P4-E40 | IMPORTRANGE stale | Dashboard shows old until refresh | External source delay | P2 |
| P4-E41 | onEdit trigger refresh | Optional; chart updates after edit | Toggle feature | P2 |
| P4-E42 | 10k rows performance | Acceptable load time < 30s or document limit | Stress | P2 |

---

## 6. Consistency with Phase 1–3

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E43 | Dashboard outstanding = email outstanding for same shipment | Identical numbers | Compare one ID | P0 |
| P4-E44 | Overdue count aligns with overdue notices eligible set | Non-Large overdue open ⊆ overdue count; Large overdue still in count if outstanding > 0 | Large overdue | P1 |
| P4-E45 | Monthly total per customer = dashboard customer row | Same engine | Apr 1 snapshot | P0 |

---

## 7. Display & UX edge cases

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P4-E46 | Very large numbers (crores) | Formatted readable; no scientific notation | 1e7 amounts | P1 |
| P4-E47 | Empty dashboard (no data) | Zeros or "No data"; no errors | Empty workbook | P2 |
| P4-E48 | Protected dashboard sheet | KPIs still update from backend sheets | Protect dashboard tab | P2 |
| P4-E49 | User sorts customer table manually | Sort resets on recalc or use QUERY order — document | Click sort | P2 |

---

## 8. Phase 4 exit checklist

- [ ] P4-E07, E08 (dynamic append)
- [ ] P4-E11, E18–E21, E27 (aging)
- [ ] P4-E29, E31, E35 (trend)
- [ ] P4-E04, E43, E45 (reconciliation with engine)

---

## 9. Aging placement reference

| Days relative to due (outstanding > 0) | Bucket |
|--------------------------------------|--------|
| due ≥ today | Not Yet Due |
| 1–30 overdue | 1–30 |
| 31–60 overdue | 31–60 |
| 61+ overdue | 61+ |
