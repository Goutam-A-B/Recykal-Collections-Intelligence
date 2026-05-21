"""Phase 3 — Monthly balance confirmation (dry-run)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .settings import load_config


def _load_existing_log(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(
            columns=["sent_at", "customer_id", "period", "email", "total_outstanding", "file", "dry_run"]
        )
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(
            columns=["sent_at", "customer_id", "period", "email", "total_outstanding", "file", "dry_run"]
        )


def run_monthly(receivables: pd.DataFrame) -> pd.DataFrame:
    cfg = load_config()
    cc = cfg["business"]["submission_cc"]
    eps = float(cfg["business"]["epsilon"])
    out_dir = cfg["_output_dir"] / "emails" / "monthly"
    out_dir.mkdir(parents=True, exist_ok=True)

    open_df = receivables[~receivables["is_settled"] & (receivables["outstanding"] > eps)]
    if open_df.empty:
        return _load_existing_log(cfg["_output_dir"] / "monthly_log.csv")

    period = datetime.now().strftime("%Y-%m")

    log_path = cfg["_output_dir"] / "monthly_log.csv"
    existing = _load_existing_log(log_path)
    sent_keys = set(
        zip(
            existing.get("customer_id", pd.Series(dtype=str)).astype(str),
            existing.get("period", pd.Series(dtype=str)).astype(str),
        )
    )

    new_rows: list[dict] = []
    for customer_id, grp in open_df.groupby("customer_id"):
        key = (str(customer_id).strip(), str(period).strip())
        if key in sent_keys:
            continue

        total = grp["outstanding"].sum()
        lines = []
        for _, r in grp.iterrows():
            due = r.get("due_date", "")
            dtd = r.get("days_to_due", "")
            lines.append(
                f"  {r['shipment_id']}: "
                f"invoice {r['invoice_amount']:,.2f}, "
                f"paid {r['amount_paid_total']:,.2f}, "
                f"outstanding {r['outstanding']:,.2f}, "
                f"due {due} (days_to_due={dtd})"
            )
        body = (
            f"Monthly Balance Confirmation — {period}\n\n"
            f"Customer: {grp.iloc[0]['customer_name']} ({customer_id})\n\n"
            + "\n".join(lines)
            + f"\n\nTotal outstanding: {total:,.2f}\n\n"
            f"Please confirm or dispute by reply.\nCC: {cc}\n"
        )
        email = grp.iloc[0].get("email", "unknown")
        fname = f"{customer_id}_{period}.txt"
        (out_dir / fname).write_text(body, encoding="utf-8")
        new_rows.append(
            {
                "sent_at": datetime.now().isoformat(timespec="seconds"),
                "customer_id": customer_id,
                "period": period,
                "email": email,
                "total_outstanding": total,
                "file": str(out_dir / fname),
                "dry_run": not cfg.get("email", {}).get("enabled", False),
            }
        )
        sent_keys.add(key)

    combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    return combined
