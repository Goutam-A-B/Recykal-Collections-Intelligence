# Phase 3 — Monthly Balance Confirmation (A-2): Edge Cases

**Architecture reference:** Phase 3 in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Goal under test:** One consolidated email per customer on the 1st; all open/partial lines; correct total; CC; no duplicate monthly sends.

---

## 1. Scheduling & calendar

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E01 | Run on 1st of month 09:00 config TZ | Job executes once in window | Set clock / mock date Apr 1 | P0 |
| P3-E02 | Trigger fires twice on same 1st | Second run skipped via `monthly_log(customer_id, yyyy-MM)` | Double installable trigger | P0 |
| P3-E03 | Manual run on Apr 1 after auto run | No duplicate for same period | Menu twice | P0 |
| P3-E04 | Manual run on Apr 15 | Policy: allow mid-month manual **or** block — document; default block duplicate period | Mid-month | P1 |
| P3-E05 | February 1 / month with 28–31 days | Cron still fires 1st | Feb 1 | P2 |
| P3-E06 | Daylight saving shift | 09:00 local still correct | DST boundary | P2 |
| P3-E07 | Job fails on 1st; retry on 2nd | Either no send (miss) or send with log — document; prefer allow send if no log for period | Failed 1st | P1 |

---

## 2. Customer eligibility & totals

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E08 | Customer with zero total outstanding | **No** email | All shipments settled | P0 |
| P3-E09 | Customer with one unpaid shipment | One email, one line, total = invoice | Single open | P0 |
| P3-E10 | Mix unpaid + partial | All lines listed; total = sum of line outstanding | 2 shipments | P0 |
| P3-E11 | Many shipments (20+) | Email readable (table); no truncation without notice | Large open portfolio | P1 |
| P3-E12 | Total in footer matches sum of rows | Arithmetic exact | Multi-line | P0 |
| P3-E13 | Large segment customer with exposure | Still receives monthly confirmation (no exclusion in problem statement) | Large, open | P0 |
| P3-E14 | Customer exists but no shipments ever | No email | Empty history | P2 |

---

## 3. Line-item content

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E15 | Each row shows shipment_id, invoice, paid, outstanding | Matches receivables engine | Partial row | P0 |
| P3-E16 | Settled shipment mid-month before Apr 1 | Excluded from Apr 1 email | Paid Mar 28 | P0 |
| P3-E17 | Payment posted Mar 31 23:59 vs Apr 1 00:01 | Outstanding as of run time — document snapshot rule | Boundary payment | P1 |
| P3-E18 | Shipment due in future vs overdue in same email | Both included if outstanding > 0 | Not due + overdue | P1 |
| P3-E19 | Zero outstanding shipment with open status bug | Must not appear | Engine error injection | P0 |

---

## 4. Email delivery & CC

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E20 | CC submission address on monthly | Same as reminders | Header check | P0 |
| P3-E21 | Reply invites confirm/dispute | Instructional copy present | Read template | P2 |
| P3-E22 | Invalid email — one customer | Skip; log; others send | Bad customer 3 of 10 | P1 |
| P3-E23 | `DRY_RUN` monthly | Log body + recipient, no send | Config flag | P1 |
| P3-E24 | HTML table renders in Gmail mobile | Readable | Mobile preview | P2 |

---

## 5. Interaction with daily reminders (Phase 2)

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E25 | Apr 1 also hits 7D window for shipment | Customer may get **monthly + 7D** same day — acceptable; document | Align dates | P1 |
| P3-E26 | Monthly shows same numbers as yesterday's reminder | Consistent outstanding | Compare fields | P0 |
| P3-E27 | Overdue notice suppressed (Large) but monthly lists overdue amount | Monthly still shows balance; no contradiction in amounts | Large overdue | P0 |

---

## 6. Deduplication & logging

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E28 | `monthly_log` key `customer_id + yyyy-MM` | Unique per month | DB inspect | P0 |
| P3-E29 | January send does not block February | New period | Run Feb 1 | P0 |
| P3-E30 | Log deleted → risk duplicate | Document ops hazard | Clear log | P2 |

---

## 7. Data churn on the 1st

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P3-E31 | New payments sheet rows during job | Snapshot at start or end — document; prefer snapshot at start + consistent recompute | Live ETL | P1 |
| P3-E32 | New customer added Apr 1 before job | Included if outstanding > 0 | Morning append | P2 |
| P3-E33 | Customer_id renamed mid-run | Unlikely; use stable IDs | — | P2 |

---

## 8. Phase 3 exit checklist

- [ ] P3-E08–E10, E12, E13, E20, P3-E02 pass
- [ ] Footer total = line sum (P3-E12)
- [ ] Large customer receives monthly with overdue lines (P3-E13, P3-E27)
- [ ] No email when fully settled (P3-E08)

---

## 9. Sample customer scenarios

| Customer | Shipments | Expected Apr 1 |
|----------|-----------|----------------|
| C1 | 1 open 50k | Email, total 50k |
| C2 | 2 partial 30k + 20k | Email, total 50k |
| C3 | All paid | No email |
| C4 (Large) | 1 overdue 100k | Email with 100k; no auto overdue that day from Phase 2 |
