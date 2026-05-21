# Phase 5 — Integration, Observability & Documentation: Edge Cases

**Architecture reference:** Phase 5 in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md)  
**Goal under test:** End-to-end reliability, triggers, logging, operator tools, and cross-phase failure modes.

---

## 1. Trigger orchestration

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E01 | No installable triggers configured | Menu/setup warns; jobs do not silently no-op | Fresh deploy | P0 |
| P5-E02 | Duplicate daily reminder triggers | Dedup still prevents double email; document removing extras | Two `runDailyReminderJob` | P1 |
| P5-E03 | User copies spreadsheet | Triggers not copied — README notes re-auth | File → Make copy | P1 |
| P5-E04 | Authorization revoked | Next run logs OAuth error clearly | Revoke script access | P1 |
| P5-E05 | Execution time limit exceeded (6 min) | Batch with continuation token or shipment paging | 5k+ shipments | P1 |
| P5-E06 | Daily + monthly same morning | Both complete; order documented (e.g. receivables refresh first) | Apr 1 08:00 + 09:00 | P1 |
| P5-E07 | Clock skew / trigger delayed hours | Windows may miss — gap in `run_log` | Delayed run | P1 |

---

## 2. Logging & audit

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E08 | Every sent reminder in `reminder_log` | shipment_id, type, timestamp | After 7D send | P0 |
| P5-E09 | Every monthly in `monthly_log` | customer_id, period | After Apr 1 | P0 |
| P5-E10 | `run_log` on success | job name, count sent, duration | Daily job | P1 |
| P5-E11 | `run_log` on partial failure | N sent, M failed with reasons | 1 bad email | P0 |
| P5-E12 | Log sheet full (5M cell limit) | Archival strategy documented | Long-running prod | P2 |
| P5-E13 | PII in logs | Emails optional in log; shipment_id sufficient | Privacy review | P2 |

---

## 3. Error handling & recovery

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E14 | `GmailApp` throws on one send | Catch; continue; record failure | Invalid recipient | P0 |
| P5-E15 | Sheet read throws (timeout) | Abort job; `run_log` critical; no partial wrong emails | Simulate | P1 |
| P5-E16 | Mid-batch script kill | Rerun: dedup prevents duplicate for completed sends | Stop execution | P1 |
| P5-E17 | Config sheet missing | Fail fast with message | Delete config tab | P0 |
| P5-E18 | Admin notification on failure | Optional email to ops — document if enabled | Force error | P2 |

---

## 4. Operator menu & manual runs

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E19 | "Run Reminders Now" | Same logic as scheduled; respects DRY_RUN | Menu | P0 |
| P5-E20 | "Dry Run Monthly" | No Gmail; log preview | Menu | P1 |
| P5-E21 | "Refresh Dashboard" | Recompute script-backed ranges if any | Menu | P2 |
| P5-E22 | Non-editor runs menu | Permission error | Viewer | P2 |
| P5-E23 | Double-click menu rapidly | Idempotent / locked | Spam click | P2 |

---

## 5. End-to-end cross-phase scenarios

| ID | Scenario | Expected end state | Phases involved | Sev |
|----|----------|-------------------|-----------------|-----|
| P5-E24 | New day: ETL adds 50 shipments + 20 payments | Validation → receivables → dashboard updated; reminders next schedule | 0–4 | P0 |
| P5-E25 | Full lifecycle one SMB shipment | 7D→3D→1D→overdue emails; dashboard aging moves; monthly includes until paid | 1–4 | P0 |
| P5-E26 | Full lifecycle Large overdue | No overdue email; dashboard shows overdue; monthly includes | 2–4 | P0 |
| P5-E27 | Pay in full between 3D and 1D | No 1D, no overdue; dashboard 0; monthly excludes | 1–4 | P0 |
| P5-E28 | Partial pay reduces aging bucket amount | Bucket $ drops; reminder shows new outstanding | 1–4 | P0 |
| P5-E29 | Bad orphan payment added live | Flagged; KPIs not corrupted | 0, 1, 4 | P0 |
| P5-E30 | Evaluator changes due_date during test | Dedup + reminders follow new date; document in README | 2, 5 | P1 |

---

## 6. Security & configuration

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E31 | API keys in sheet cells | Anti-pattern; use Script Properties | Inspect cells | P1 |
| P5-E32 | Script Properties missing | Clear setup error | Empty properties | P1 |
| P5-E33 | Shared link "anyone with link" editor | Document risk of data tampering | Sharing settings | P2 |
| P5-E34 | Version mismatch (old script, new sheets) | Version note in README | Deploy head vs old | P1 |

---

## 7. Documentation & evaluation readiness

| ID | Scenario | Expected behavior | Test setup | Sev |
|----|----------|-------------------|------------|-----|
| P5-E35 | README lists all triggers with TZ | Reviewer can reproduce | Read docs | P1 |
| P5-E36 | Assumptions match architecture §10 | No contradiction | Cross-read | P1 |
| P5-E37 | Test playbook references edge-case IDs | Traceability | This folder | P2 |
| P5-E38 | Screenshots / Loom for trigger install | Optional but reduces eval friction | Submit pack | P2 |

---

## 8. Regression suite (minimal E2E)

Run in order on `test_fixtures` copy:

| Step | Action | Verify |
|------|--------|--------|
| 1 | Load VALID_BASE | Phase 0 validation green |
| 2 | Compute receivables | Phase 1 matrix |
| 3 | Mock today = due-7; dry-run reminders | One 7D log row |
| 4 | Mock today = Apr 1; dry-run monthly | C1 email, C3 none |
| 5 | Append payment settling largest open | Dashboard KPIs ↓ outstanding |
| 6 | Full send (non-dry) one shipment | CC present |

---

## 9. Phase 5 exit checklist

- [ ] P5-E01, E11, E14, E17, E24–E28 pass
- [ ] All triggers documented (P5-E35)
- [ ] `run_log` explains failures without silent drop (P5-E11)
- [ ] Evaluator can trace logic to [recykal problem statement.md](../recykal%20problem%20statement.md)

---

## 10. Known acceptable limitations (document, not fail)

| Item | Rationale |
|------|-----------|
| Missed reminder if job down on exact window day | Ops reruns manual with log dedup |
| Large overdue manual only | By business rule |
| Sub-minute dashboard lag | Meets "real-time" expectation |
| Dispute replies not auto-processed | Out of scope |
