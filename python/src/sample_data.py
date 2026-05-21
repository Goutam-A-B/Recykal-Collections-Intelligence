"""Generate minimal valid sample CSVs for pipeline testing."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .settings import load_config


def write_sample_data() -> Path:
    cfg = load_config()
    data_dir = cfg["_data_dir"]
    data_dir.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame(
        [
            {"customer_id": "C001", "customer_name": "Bhavya Metals Pvt Ltd", "segment": "Mid", "email": "customer.1@recykal.com"},
            {"customer_id": "C002", "customer_name": "Greentech Recyclers Pvt Ltd", "segment": "Large", "email": "customer.2@recykal.com"},
            {"customer_id": "C003", "customer_name": "Apex Metal Industries", "segment": "Mid", "email": "customer.3@recykal.com"},
        ]
    )

    shipments = pd.DataFrame(
        [
            {"shipment_id": "S001", "customer_id": "C001", "invoice_amount": 100000, "invoice_date": "2025-04-01", "due_date": "2025-05-01"},
            {"shipment_id": "S002", "customer_id": "C002", "invoice_amount": 250000, "invoice_date": "2025-03-15", "due_date": "2025-04-29"},
            {"shipment_id": "S003", "customer_id": "C003", "invoice_amount": 80000, "invoice_date": "2025-04-10", "due_date": "2025-05-25"},
        ]
    )

    payments = pd.DataFrame(
        [
            {"payment_id": "P001", "shipment_id": "S001", "amount_paid": 40000, "payment_date": "2025-04-20"},
            {"payment_id": "P002", "shipment_id": "S003", "amount_paid": 80000, "payment_date": "2025-05-01"},
        ]
    )

    for name, df in [("customers", customers), ("shipments", shipments), ("payments", payments)]:
        path = data_dir / f"{name}.csv"
        df.to_csv(path, index=False)

    return data_dir
