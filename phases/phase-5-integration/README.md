# Phase 5 — Integration & Observability

**Status:** Implemented (Python)  
**Depends on:** Phases 2–4

## Implementation (Python)

- Code: `python/src/integration.py`
- Entry point: `python run.py phase5`
- Writes:
  - `python/output/run_log.csv`
  - `python/output/phase5_operator_summary.md`
  - and publishes the latest artifacts into `deploy/`
- Scheduling (“no delay”): `.github/workflows/refresh.yml` runs the same pipeline on a cron.

## Edge cases

[phase-5-edge-cases.md](../../docs/edge-cases/phase-5-edge-cases.md)
