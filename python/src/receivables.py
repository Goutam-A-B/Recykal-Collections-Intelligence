"""Phase 1 — Receivables engine."""
from __future__ import annotations

from datetime import date

import pandas as pd

from .payment_allocation import allocate_payments_to_shipments
from .settings import load_config
from .validate import _parse_date, _parse_number


def compute_receivables(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cfg = load_config()
    eps = float(cfg["business"]["epsilon"])
    large_seg = cfg["business"]["large_segment"]
    today = pd.Timestamp(date.today()).normalize()

    customers = data["customers"].copy()
    shipments = data["shipments"].copy()
    payments = data["payments"].copy()

    for col in ["invoice_amount"]:
        if col in shipments.columns:
            shipments[col] = shipments[col].map(_parse_number)

    paid_by_shipment = allocate_payments_to_shipments(shipments, payments, eps)

    df = shipments.merge(paid_by_shipment, on="shipment_id", how="left")
    df["amount_paid_total"] = df["amount_paid_total"].fillna(0)
    df["outstanding"] = df["invoice_amount"] - df["amount_paid_total"]
    df["is_settled"] = df["outstanding"] <= eps

    df["due_date_parsed"] = df["due_date"].map(_parse_date)
    df["days_to_due"] = (df["due_date_parsed"] - today).dt.days
    df["days_overdue"] = df["days_to_due"].apply(lambda d: max(0, -d) if pd.notna(d) else 0)

    df = df.merge(
        customers[["customer_id", "customer_name", "segment", "email"]],
        on="customer_id",
        how="left",
    )

    df["eligible_for_reminder"] = ~df["is_settled"]
    df["eligible_for_overdue"] = (
        df["eligible_for_reminder"]
        & (df["days_to_due"] < 0)
        & (df["segment"].astype(str).str.strip() != large_seg)
    )
    df["in_7d_window"] = df["days_to_due"] == 7
    df["in_3d_window"] = df["days_to_due"] == 3
    df["in_1d_window"] = df["days_to_due"] == 1

    return df
