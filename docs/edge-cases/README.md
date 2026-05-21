# Recykal Collections System — Phase Edge Cases

Edge-case catalogs for each implementation phase defined in [recykal-phase-wise-architecture.md](../recykal-phase-wise-architecture.md).

| Phase | Document | Focus |
|-------|----------|--------|
| 0 | [phase-0-edge-cases.md](./phase-0-edge-cases.md) | Data contract, validation — [workbook](https://docs.google.com/spreadsheets/d/1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to/edit?gid=1296664018#gid=1296664018) |
| 1 | [phase-1-edge-cases.md](./phase-1-edge-cases.md) | Receivables engine, outstanding logic |
| 2 | [phase-2-edge-cases.md](./phase-2-edge-cases.md) | Automated payment reminders (A-1) |
| 3 | [phase-3-edge-cases.md](./phase-3-edge-cases.md) | Monthly balance confirmation (A-2) |
| 4 | [phase-4-edge-cases.md](./phase-4-edge-cases.md) | Real-time collections dashboard (B) |
| 5 | [phase-5-edge-cases.md](./phase-5-edge-cases.md) | Integration, triggers, observability |

## How to use

1. Implement the phase per architecture.
2. Walk the edge-case tables; mark **Pass / Fail / N/A** in your test log.
3. Add fixture rows in a `test_fixtures` sheet (or copy of workbook) matching **Test setup** columns.
4. Cross-phase cases (e.g. partial payment affecting reminders and dashboard) should pass in **both** phase files after Phase 1 is complete.

## Severity legend

| Level | Meaning |
|-------|---------|
| **P0** | Wrong money, wrong email, or silent data corruption — must fix before submit |
| **P1** | Business rule violation or misleading dashboard — fix before production |
| **P2** | Operational annoyance or rare failure — document workaround |
