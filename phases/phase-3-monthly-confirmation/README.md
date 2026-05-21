# Phase 3 — Monthly Balance Confirmation (Task A-2)

**Status:** Implemented (Python, dry-run previews)  
**Depends on:** Phase 1

## Implementation (Python)

- Code: `python/src/monthly.py`
- Schedule intent: 1st of month (handled by cron / GitHub Actions)
- Dedup: `python/output/monthly_log.csv` key `(customer_id, period)`
- Outputs: `python/output/emails/monthly/*.txt`

## Edge cases

[phase-3-edge-cases.md](../../docs/edge-cases/phase-3-edge-cases.md)
