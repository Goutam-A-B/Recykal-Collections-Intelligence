# Phase 1 — Receivables Engine & Materialized View: Edge Cases

**Architecture reference:** Phase 1 + Section 4 (Core Receivables Logic) in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Goal under test:** Single source of truth for `amount_paid`, `outstanding`, `is_settled`, and open-shipment lists.

---

## 1. Payment aggregation

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E01 | No payments for shipment | `amount_paid = 0`, `outstanding = invoice_amount` | Unpaid invoice 100,000 | P0 |
| P1-E02 | Single full payment | `outstanding <= 0`, `is_settled = true` | Pay 100,000 on 100,000 invoice | P0 |
| P1-E03 | Two partial payments | `amount_paid = 50,000`, `outstanding = 50,000` | 30k + 20k on 100k invoice | P0 |
| P1-E04 | Many installments (5+ rows) | Sum all rows for `shipment_id` | Five payment rows | P0 |
| P1-E05 | Overpayment (sum paid > invoice) | `outstanding <= 0`, settled; no negative outstanding in emails | Pay 110,000 on 100,000 | P0 |
| P1-E06 | Exact penny settlement | Settled with epsilon tolerance if floats used | 99.99 + 0.01 on 100.00 | P1 |
| P1-E07 | Duplicate payment rows same amount (duplicate PK not caught) | If only amount duplicated without unique `payment_id`, risk double count — Phase 0 must catch | Same payment pasted twice | P0 |
| P1-E08 | Payment on wrong `shipment_id` | Does not reduce intended invoice; orphan flagged in Phase 0 | Mis-keyed ID | P0 |
| P1-E09 | Payment dated before invoice_date | Still reduces outstanding (cash application); optional warn | Early payment row | P2 |

---

## 2. Settlement & open lists

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E10 | Fully paid shipment in `getOpenShipmentsForCustomer()` | Excluded | Settled shipment | P0 |
| P1-E11 | Partially paid shipment | Included with correct outstanding | 40k paid / 100k invoice | P0 |
| P1-E12 | Customer with all shipments settled | Empty open list; total exposure 0 | All paid | P0 |
| P1-E13 | Customer with mix settled + open | Only open/partial in list | 2 shipments: 1 paid, 1 open | P0 |
| P1-E14 | Zero outstanding but floating-point noise | Treated as settled (`outstanding <= epsilon`) | 33.33 × 3 payments vs 100 | P1 |

---

## 3. Date & aging inputs (engine outputs)

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E15 | Due date = today | `days_to_due = 0` (not in 1-day window unless defined as 1) | Due today | P0 |
| P1-E16 | Due date tomorrow | `days_to_due = 1` → eligible for 1-day reminder in Phase 2 | Due T+1 | P0 |
| P1-E17 | Due date 7 days out | `days_to_due = 7` | Calendar match | P0 |
| P1-E18 | Due date yesterday, outstanding > 0 | `days_to_due` negative; overdue flag true | Open overdue | P0 |
| P1-E19 | Due on weekend; job runs Monday | Windows evaluated on calendar date, not business days only | Due Sunday, run Monday | P1 |
| P1-E20 | Timezone: script midnight vs IST | Same calendar day as spreadsheet timezone | Run trigger UTC vs Asia/Kolkata | P0 |
| P1-E21 | `due_date` edited after reminders sent | Receivables refresh; Phase 2 dedup key includes `due_date` | Extend due date | P1 |

---

## 4. Customer segment join

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E22 | Large segment customer, open overdue | `eligible_for_overdue = false`; still open in receivables | Large + overdue | P0 |
| P1-E23 | Non-Large segment, open overdue | `eligible_for_overdue = true` | SMB overdue | P0 |
| P1-E24 | Missing segment on customer | Default policy: treat as non-Large or block automation — document choice | Blank segment | P1 |
| P1-E25 | Segment changed mid-cycle | Use current segment at computation time | Large → SMB | P1 |

---

## 5. Materialized view & refresh

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E26 | New payment row added | `receivables_computed` / formulas update outstanding within seconds | Append payment | P0 |
| P1-E27 | Script refresh mid-formula edit | No partial corrupt state; idempotent full recompute | Run refresh during edit | P2 |
| P1-E28 | Shipment with no matching customer | Row skipped or flagged; no throw | Orphan per P0-E07 | P0 |
| P1-E29 | Empty payments sheet | All shipments show full outstanding | No payments | P1 |
| P1-E30 | Concurrent payments for same shipment | Final sum equals sum of all rows | Rapid double entry | P1 |

---

## 6. Formula vs script (hybrid)

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P1-E31 | ARRAYFORMULA spill blocked | Error visible; script path still works | Obstacle in spill range | P1 |
| P1-E32 | Script outstanding ≠ formula outstanding | Investigation required — single truth policy | Compare columns | P0 |
| P1-E33 | Filtered QUERY omits settled rows | Open shipments only where designed | QUERY on computed tab | P1 |

---

## 7. Cross-phase dependencies

| ID | Downstream impact if wrong | Phase |
|----|----------------------------|-------|
| P1-E03 | Reminder shows 100k due instead of 50k | 2, 3, 4 |
| P1-E10 | Reminder sent on paid invoice | 2 |
| P1-E22 | Overdue email to Large account | 2 |
| P1-E15–E18 | Wrong reminder type or missed window | 2 |
| P1-E11–E13 | Wrong monthly total | 3 |
| P1-E05 | KPI outstanding ≠ truth | 4 |

---

## 8. Phase 1 exit checklist

- [ ] P1-E03, P1-E05, P1-E10, P1-E22 verified
- [ ] Script and formula (if both used) agree on P1-E32
- [ ] `getOpenShipmentsForCustomer()` matches manual sum of open lines

---

## 9. Numeric test matrix

| Invoice | Payments | Expected outstanding | Settled? |
|---------|----------|------------------------|----------|
| 100,000 | — | 100,000 | No |
| 100,000 | 100,000 | 0 | Yes |
| 100,000 | 40,000 | 60,000 | No |
| 100,000 | 60,000; 40,000 | 0 | Yes |
| 100,000 | 110,000 | 0 (overpaid) | Yes |
| 50,000 | 25,000; 10,000 | 15,000 | No |
