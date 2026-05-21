# Phase 2 — Automated Payment Reminder System (A-1): Edge Cases

**Architecture reference:** Phase 2 in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Problem statement:** 7d / 3d / 1d / overdue triggers; mandatory email fields; Large overdue exclusion; CC on all sends.

---

## 1. Reminder window timing

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E01 | Exactly 7 days before due | One `7D` reminder sent | `due_date = today + 7` | P0 |
| P2-E02 | Exactly 3 days before due | One `3D` reminder sent | `due_date = today + 3` | P0 |
| P2-E03 | Exactly 1 day before due | One `1D` (Final) reminder sent | `due_date = today + 1` | P0 |
| P2-E04 | Due date is today (day 0) | No 1-day-before email; overdue only if outstanding and past due per rule | Due today, unpaid | P0 |
| P2-E05 | 6 days before due | No 7D email (off-by-one guard) | today + 6 | P0 |
| P2-E06 | 8 days before due | No 7D email yet | today + 8 | P1 |
| P2-E07 | 1 day overdue | Overdue notice (non-Large) | due = yesterday | P0 |
| P2-E08 | 30+ days overdue | Overdue notice policy: daily vs once — **document**: architecture implies daily job; dedup log prevents repeat same type same cycle | Long overdue | P1 |
| P2-E09 | Job did not run on exact window day | Missed reminder unless compensating run — log gap | Skip Sunday run, due window Monday | P1 |
| P2-E10 | Two windows same day (data error: due in 7 and also 3 impossible) | At most one type per evaluation priority — document precedence | Bad data | P2 |

---

## 2. Outstanding & settlement gates

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E11 | Fully paid before 7D window | No reminder of any type | Pay in full 8 days before due | P0 |
| P2-E12 | Partial payment before 3D window | Email shows paid + **remaining** outstanding | Pay 50% at T-5 | P0 |
| P2-E13 | Payment arrives morning of 1D window | If job runs after payment and settled, no 1D email | Pay full on due-1 | P0 |
| P2-E14 | Payment after overdue started | Outstanding updated; ongoing overdue emails only if still open | Partial pay when 5 days overdue | P0 |
| P2-E15 | Outstanding = 0.01 | Still eligible (not settled) | Tiny balance | P1 |
| P2-E16 | Overpayment settled | No overdue | Overpay | P0 |

---

## 3. Large segment & overdue exclusion

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E17 | Large customer, 7/3/1 day windows | Pre-due reminders **sent** (exclusion is overdue only) | Large, due in 7 days | P0 |
| P2-E18 | Large customer, overdue with balance | **No** automated overdue notice | Large, due yesterday, open | P0 |
| P2-E19 | Large customer, same day as non-Large overdue test | Confirm only segment differs | Side-by-side customers | P0 |
| P2-E20 | `large` vs `Large` case sensitivity | Match config enum after trim | Wrong case segment | P1 |

---

## 4. Email content & delivery

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E21 | All mandatory fields present | Name, Shipment ID, Invoice, Paid, Outstanding, Due, Days to/since due | Inspect HTML/text | P0 |
| P2-E22 | Days until due on 7D email | Positive integer (7) | 7D template | P0 |
| P2-E23 | Days since due on overdue | Positive days overdue | 5 days late | P0 |
| P2-E24 | CC always included | `ai-strategy-interns-case-submissionsleads@recykal.com` on every send | Sent mail headers | P0 |
| P2-E25 | Invalid customer email | Skip send; log error; continue batch | bad@ | P1 |
| P2-E26 | Multiple contact emails per customer | Document: first email vs all — must be consistent | Two emails in cell | P2 |
| P2-E27 | Gmail daily quota exceeded | Partial batch + `run_log` error | Stress send | P2 |
| P2-E28 | `DRY_RUN=true` | Log would-send without Gmail call | Menu dry run | P1 |

---

## 5. Deduplication & idempotency

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E29 | Job runs twice same day (7D window) | Second run: no duplicate 7D | Double trigger | P0 |
| P2-E30 | Manual "Run Reminders Now" after scheduled run | No duplicate if log key exists | Double manual | P0 |
| P2-E31 | `due_date` changed after 7D sent | New due date → new dedup cycle allowed | Extend due +14 days | P1 |
| P2-E32 | Reminder log cleared accidentally | Risk duplicate — ops warning in docs | Delete log rows | P2 |
| P2-E33 | Unique key: `shipment_id + type + due_date` | Collision test: same shipment new invoice cycle (new shipment id) | New `shipment_id` | P1 |

---

## 6. Multi-shipment & batch behavior

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P2-E34 | Customer with 3 open shipments on different windows | Up to 3 emails same day (one per shipment) | 3 due dates | P1 |
| P2-E35 | Same customer, two shipments same window | Two separate emails (per shipment) | 2× 7D same day | P1 |
| P2-E36 | One shipment fails send | Others still send; failure in log | Invalid email on 1 of 3 | P1 |

---

## 7. Lifecycle sequences (integration scenarios)

| ID | Sequence | Expected |
|----|----------|----------|
| P2-E37 | T-7 → T-3 → T-1 → due → overdue | Four distinct emails if still unpaid (non-Large overdue) |
| P2-E38 | T-7 → pay full at T-5 | No T-3, T-1, overdue |
| P2-E39 | T-7 → partial → T-3 | T-3 shows reduced outstanding |
| P2-E40 | Large: T-1 sent, then overdue | T-1 yes; overdue no |

---

## 8. Phase 2 test matrix (quick reference)

| Case | Segment | Outstanding | Days to due | Expect email |
|------|---------|-------------|-------------|--------------|
| A | SMB | >0 | 7 | 7D |
| B | SMB | 0 | 7 | None |
| C | SMB | >0 | -3 | Overdue |
| D | Large | >0 | -3 | None (overdue) |
| E | Large | >0 | 3 | 3D |
| F | SMB | >0 | 5 | None |

---

## 9. Phase 2 exit checklist

- [ ] P2-E01–E04, E11–E13, E17–E18, E21, E24, E29 pass
- [ ] Partial payment email shows remaining balance (P2-E12)
- [ ] Dedup on double run (P2-E29)
