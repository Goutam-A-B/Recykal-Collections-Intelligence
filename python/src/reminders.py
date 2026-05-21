"""Phase 2 — Payment reminders (dry-run writes HTML; optional SMTP)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .settings import load_config


def _reminder_type(row: pd.Series) -> str | None:
    if not row.get("eligible_for_reminder"):
        return None
    if row.get("in_7d_window"):
        return "7D"
    if row.get("in_3d_window"):
        return "3D"
    if row.get("in_1d_window"):
        return "1D"
    if row.get("eligible_for_overdue"):
        return "OVERDUE"
    return None


def _build_body(row: pd.Series, rtype: str, cc: str) -> str:
    days = row["days_to_due"]
    if rtype == "OVERDUE":
        day_label = f"{int(row['days_overdue'])} day(s) overdue"
    else:
        day_label = f"{int(days)} day(s) until due"

    return f"""Payment Reminder ({rtype})

Customer: {row['customer_name']}
Shipment ID: {row['shipment_id']}
Segment: {row.get('segment', '')}
Invoice Amount: {row['invoice_amount']:,.2f}
Amount Paid: {row['amount_paid_total']:,.2f}
Outstanding Balance: {row['outstanding']:,.2f}
Due Date: {row.get('due_date', '')}
{day_label}

CC: {cc}
"""

def _load_existing_log(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "sent_at",
                "shipment_id",
                "reminder_type",
                "due_date",
                "customer_email",
                "outstanding",
                "file",
                "dry_run",
            ]
        )
    try:
        return pd.read_csv(path)
    except Exception:
        # If file is corrupted, start fresh but don't crash the pipeline.
        return pd.DataFrame(
            columns=[
                "sent_at",
                "shipment_id",
                "reminder_type",
                "due_date",
                "customer_email",
                "outstanding",
                "file",
                "dry_run",
            ]
        )


def run_reminders(receivables: pd.DataFrame) -> pd.DataFrame:
    cfg = load_config()
    cc = cfg["business"]["submission_cc"]
    out_dir = cfg["_output_dir"] / "emails" / "reminders"
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = cfg["_output_dir"] / "reminder_log.csv"
    existing = _load_existing_log(log_path)
    sent_keys = set(
        zip(
            existing.get("shipment_id", pd.Series(dtype=str)).astype(str),
            existing.get("reminder_type", pd.Series(dtype=str)).astype(str),
            existing.get("due_date", pd.Series(dtype=str)).astype(str),
        )
    )

    new_rows: list[dict] = []
    for _, row in receivables.iterrows():
        rtype = _reminder_type(row)
        if not rtype:
            continue

        due_key = str(row.get("due_date", "")).strip()
        key = (str(row["shipment_id"]).strip(), str(rtype).strip(), due_key)
        if key in sent_keys:
            continue

        body = _build_body(row, rtype, cc)
        fname = f"{row['shipment_id']}_{rtype}_{datetime.now().strftime('%Y%m%d')}.txt"
        (out_dir / fname).write_text(body, encoding="utf-8")

        new_rows.append(
            {
                "sent_at": datetime.now().isoformat(timespec="seconds"),
                "shipment_id": row["shipment_id"],
                "reminder_type": rtype,
                "due_date": due_key,
                "customer_email": row.get("email", ""),
                "outstanding": row["outstanding"],
                "file": str(out_dir / fname),
                "dry_run": not cfg.get("email", {}).get("enabled", False),
            }
        )

        sent_keys.add(key)

    combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    return combined
