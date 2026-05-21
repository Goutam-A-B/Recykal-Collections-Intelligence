"""Allocate customer-level payments to shipments (FIFO by due date)."""
from __future__ import annotations

import pandas as pd

from .validate import _parse_date, _parse_number


def allocate_payments_to_shipments(
    shipments: pd.DataFrame, payments: pd.DataFrame, epsilon: float = 0.01
) -> pd.DataFrame:
    """
    Returns DataFrame: shipment_id, amount_paid_total
    Uses shipment_id on payments when present; else FIFO by due_date per customer.
    """
    if "shipment_id" in payments.columns and payments["shipment_id"].astype(str).str.strip().ne("").any():
        pays = payments.copy()
        pays["amount_paid"] = pays["amount_paid"].map(_parse_number).fillna(0)
        return (
            pays.groupby("shipment_id", as_index=False)["amount_paid"]
            .sum()
            .rename(columns={"amount_paid": "amount_paid_total"})
        )

    ships = shipments[["shipment_id", "customer_id", "invoice_amount", "due_date"]].copy()
    ships["invoice_amount"] = ships["invoice_amount"].map(_parse_number).fillna(0)
    ships["due_parsed"] = ships["due_date"].map(_parse_date)
    ships = ships.sort_values(["customer_id", "due_parsed", "shipment_id"])

    pays = payments.copy()
    pays["amount_paid"] = pays["amount_paid"].map(_parse_number).fillna(0)
    if "payment_date" in pays.columns:
        pays["pay_parsed"] = pays["payment_date"].map(_parse_date)
        pays = pays.sort_values(["customer_id", "pay_parsed", "payment_id"])
    else:
        pays = pays.sort_values(["customer_id", "payment_id"])

    allocated: dict[str, float] = {str(s): 0.0 for s in ships["shipment_id"]}

    for cid in pays["customer_id"].astype(str).unique():
        if not cid or cid == "nan":
            continue
        cust_ships = ships[ships["customer_id"].astype(str) == cid]
        if cust_ships.empty:
            continue
        ship_list = cust_ships["shipment_id"].astype(str).tolist()
        inv_map = dict(zip(ship_list, cust_ships["invoice_amount"].tolist()))
        idx = 0
        pool = 0.0

        for _, prow in pays[pays["customer_id"].astype(str) == cid].iterrows():
            pool += float(prow["amount_paid"])
            while pool > epsilon and idx < len(ship_list):
                sid = ship_list[idx]
                outstanding = inv_map[sid] - allocated[sid]
                if outstanding <= epsilon:
                    idx += 1
                    continue
                apply_amt = min(outstanding, pool)
                allocated[sid] += apply_amt
                pool -= apply_amt
                if inv_map[sid] - allocated[sid] <= epsilon:
                    idx += 1

    rows = [{"shipment_id": k, "amount_paid_total": v} for k, v in allocated.items()]
    return pd.DataFrame(rows)
