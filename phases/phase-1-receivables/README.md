# Phase 1 — Receivables Engine

**Status:** Implemented (Python)  
**Depends on:** Phase 0 validation

## Implementation (Python)

- Code: `python/src/receivables.py` (single calculation layer)
- Payment mapping: `python/src/payment_allocation.py` (FIFO allocation when payments lack `shipment_id`)
- Output: `python/output/receivables_computed.csv`

## Exit criteria

See [docs/architecture-python.md](../../docs/architecture-python.md) and [edge cases](../../docs/edge-cases/phase-1-edge-cases.md).
