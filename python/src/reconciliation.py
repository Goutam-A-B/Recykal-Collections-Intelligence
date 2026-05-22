"""Deterministic dashboard reconciliation computed from raw source CSV exports.

Purpose:
- Prove dashboard KPIs reconcile to raw CSV exports.
- Detect negative / inconsistent balances.
- Provide a single PASS/FAIL status that can gate deployment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from .payment_allocation import allocate_payments_to_shipments
from .settings import load_config
from .validate import _parse_number


def compute_reconciliation(
    data: dict[str, pd.DataFrame],
    receivables: pd.DataFrame,
) -> pd.DataFrame:
    """Return a single-row DataFrame with reconciliation summary."""

    cfg = load_config()
    eps = float(cfg["business"]["epsilon"])

    shipments = data["shipments"].copy()
    payments = data["payments"].copy()

    if "invoice_amount" not in shipments.columns:
        raise KeyError("Missing required column: shipments.invoice_amount")
    if "amount_paid" not in payments.columns:
        raise KeyError("Missing required column: payments.amount_paid")

    shipments["invoice_amount_num"] = shipments["invoice_amount"].map(_parse_number).fillna(0.0)
    payments["amount_paid_num"] = payments["amount_paid"].map(_parse_number).fillna(0.0)

    raw_invoiced_total = float(shipments["invoice_amount_num"].sum())
    raw_paid_total = float(payments["amount_paid_num"].sum())

    # Deterministically recompute outstanding directly from raw CSV inputs (independent of dashboard UI).
    ships_alloc = shipments[["shipment_id", "customer_id", "due_date"]].copy()
    ships_alloc["invoice_amount"] = shipments["invoice_amount_num"]
    pays_alloc = payments.copy()
    pays_alloc["amount_paid"] = payments["amount_paid_num"]

    paid_by_shipment = allocate_payments_to_shipments(ships_alloc, pays_alloc, eps)
    tmp = shipments[["shipment_id", "invoice_amount_num"]].merge(
        paid_by_shipment, on="shipment_id", how="left"
    )
    tmp["amount_paid_total"] = tmp["amount_paid_total"].fillna(0.0)
    tmp["outstanding"] = tmp["invoice_amount_num"] - tmp["amount_paid_total"]
    tmp["is_settled"] = tmp["outstanding"] <= eps
    raw_outstanding_total = float(tmp[(~tmp["is_settled"]) & (tmp["outstanding"] > eps)]["outstanding"].sum())

    # Match the dashboard's "Total Outstanding" KPI definition (open receivables only).
    dashboard_open = receivables[
        (~receivables["is_settled"]) & (receivables["outstanding"] > eps)
    ].copy()
    dashboard_outstanding_total = float(dashboard_open["outstanding"].sum())

    difference_amount = raw_outstanding_total - dashboard_outstanding_total

    # Detect negative / inconsistent balances on recomputed raw outstanding.
    negative_outstanding_count = int((tmp["outstanding"] < -eps).sum())
    overpaid_count = int((tmp["amount_paid_total"] - tmp["invoice_amount_num"] > eps).sum())

    pass_diff = abs(difference_amount) <= eps
    pass_consistency = (negative_outstanding_count == 0) and (overpaid_count == 0)
    status = "PASS" if (pass_diff and pass_consistency) else "FAIL"

    note_parts: list[str] = []
    if not pass_diff:
        note_parts.append(f"Difference exceeds epsilon ({eps:g}).")
    if negative_outstanding_count:
        note_parts.append(f"{negative_outstanding_count} shipments have negative outstanding.")
    if overpaid_count:
        note_parts.append(f"{overpaid_count} shipments have paid > invoice.")

    return pd.DataFrame(
        [
            {
                "raw_csv_outstanding_total": raw_outstanding_total,
                "dashboard_outstanding_total": dashboard_outstanding_total,
                "difference_amount": difference_amount,
                "validation_status": status,
                "last_validation_timestamp": datetime.now().isoformat(timespec="seconds"),
                # supporting fields (useful for audit/debug; can remain hidden in UI)
                "raw_invoiced_total": raw_invoiced_total,
                "raw_paid_total": raw_paid_total,
                "allocated_paid_total": float(tmp["amount_paid_total"].sum()),
                "negative_outstanding_count": negative_outstanding_count,
                "overpaid_count": overpaid_count,
                "note": " ".join(note_parts),
            }
        ]
    )
