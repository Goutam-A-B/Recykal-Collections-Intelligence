# Phase 2 — Automated Payment Reminders (Task A-1)

**Status:** Implemented (Python, dry-run previews)  
**Depends on:** Phase 1

## Implementation (Python)

- Code: `python/src/reminders.py`
- Rule windows: 7D / 3D / 1D / OVERDUE (Large excluded for overdue)
- Dedup: `python/output/reminder_log.csv` key `(shipment_id, reminder_type, due_date)`
- Outputs: `python/output/emails/reminders/*.txt`

## Edge cases

[phase-2-edge-cases.md](../../docs/edge-cases/phase-2-edge-cases.md)
