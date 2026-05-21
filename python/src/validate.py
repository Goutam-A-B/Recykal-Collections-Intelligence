"""Phase 0 validation — mirrors Apps Script ValidationService."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

from .settings import load_config

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _issue(
    severity: str,
    sheet: str,
    row: int,
    record_id: str,
    field: str,
    issue_type: str,
    message: str,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "sheet": sheet,
        "row_number": row,
        "record_id": record_id,
        "field": field,
        "issue_type": issue_type,
        "message": message,
        "detected_at": datetime.now().isoformat(timespec="seconds"),
    }


def _parse_number(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace(",", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(val: Any) -> pd.Timestamp | None:
    if val is None or str(val).strip() == "":
        return None
    ts = pd.to_datetime(val, errors="coerce", dayfirst=False)
    if pd.isna(ts):
        return None
    return ts.normalize()


def validate_all(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cfg = load_config()
    biz = cfg["business"]
    issues: list[dict[str, Any]] = []

    schemas = {
        "customers": {
            "pk": "customer_id",
            "required": ["customer_id", "customer_name", "segment", "email"],
            "numeric": [],
            "dates": [],
            "enum": {"segment": biz["valid_segments"]},
        },
        "shipments": {
            "pk": "shipment_id",
            "required": ["shipment_id", "customer_id", "invoice_amount", "due_date"],
            "numeric": ["invoice_amount"],
            "dates": ["invoice_date", "due_date"],
            "enum": {},
        },
        "payments": {
            "pk": "payment_id",
            "required": ["payment_id", "amount_paid"],
            "numeric": ["amount_paid"],
            "dates": ["payment_date"],
            "enum": {},
        },
    }

    # Recykal intern data: payments keyed by customer_id (allocated FIFO to shipments)
    pay_df = data.get("payments")
    if pay_df is not None and "shipment_id" not in pay_df.columns:
        if "customer_id" not in pay_df.columns:
            schemas["payments"]["required"].append("customer_id")
        else:
            schemas["payments"]["_link"] = "customer_id"
    elif pay_df is not None and "shipment_id" in pay_df.columns:
        schemas["payments"]["required"].append("shipment_id")

    for sheet_name, schema in schemas.items():
        if sheet_name not in data:
            issues.append(
                _issue("P0", sheet_name, 0, "", "", "MISSING_SHEET", f"No data for {sheet_name}")
            )
            continue

        df = data[sheet_name]
        missing_cols = [c for c in schema["required"] if c not in df.columns]
        for col in missing_cols:
            issues.append(
                _issue("P0", sheet_name, 1, "", col, "MISSING_COLUMN", f"Required column: {col}")
            )
        if missing_cols:
            continue

        seen_pk: set[str] = set()
        for idx, row in df.iterrows():
            row_num = int(idx) + 2
            pk = str(row.get(schema["pk"], "")).strip()
            record_id = pk

            for req in schema["required"]:
                v = row.get(req, "")
                if str(v).strip() == "":
                    issues.append(
                        _issue(
                            "P0",
                            sheet_name,
                            row_num,
                            record_id,
                            req,
                            "EMPTY_REQUIRED",
                            f"Empty {req}",
                        )
                    )

            if pk:
                if pk in seen_pk:
                    issues.append(
                        _issue(
                            "P0",
                            sheet_name,
                            row_num,
                            pk,
                            schema["pk"],
                            "DUPLICATE_PK",
                            f"Duplicate {schema['pk']}: {pk}",
                        )
                    )
                seen_pk.add(pk)

            for num_field in schema["numeric"]:
                if num_field not in row:
                    continue
                n = _parse_number(row[num_field])
                if str(row[num_field]).strip() and n is None:
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            num_field,
                            "INVALID_NUMBER",
                            str(row[num_field]),
                        )
                    )
                elif n is not None and n < 0:
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            num_field,
                            "NEGATIVE_AMOUNT",
                            str(n),
                        )
                    )

            for date_field in schema["dates"]:
                if date_field not in row or str(row[date_field]).strip() == "":
                    continue
                if _parse_date(row[date_field]) is None:
                    issues.append(
                        _issue(
                            "P0",
                            sheet_name,
                            row_num,
                            record_id,
                            date_field,
                            "INVALID_DATE",
                            str(row[date_field]),
                        )
                    )

            if sheet_name == "shipments":
                inv = _parse_date(row.get("invoice_date"))
                due = _parse_date(row.get("due_date"))
                if inv is not None and due is not None and due < inv:
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            "due_date",
                            "DUE_BEFORE_INVOICE",
                            "due_date before invoice_date",
                        )
                    )

            if sheet_name == "customers" and "segment" in schema["enum"]:
                seg = str(row.get("segment", "")).strip()
                if seg and seg not in schema["enum"]["segment"]:
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            "segment",
                            "INVALID_SEGMENT",
                            seg,
                        )
                    )
                email = str(row.get("email", "")).strip()
                if not email:
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            "email",
                            "BLANK_EMAIL",
                            "Required for reminders",
                        )
                    )
                elif not EMAIL_RE.match(email):
                    issues.append(
                        _issue(
                            "P1",
                            sheet_name,
                            row_num,
                            record_id,
                            "email",
                            "INVALID_EMAIL",
                            email,
                        )
                    )

    # FK checks
    if all(k in data for k in ("customers", "shipments", "payments")):
        cust_ids = set(data["customers"]["customer_id"].astype(str).str.strip())
        ship_ids = set(data["shipments"]["shipment_id"].astype(str).str.strip())

        for idx, row in data["shipments"].iterrows():
            cid = str(row.get("customer_id", "")).strip()
            if cid and cid not in cust_ids:
                issues.append(
                    _issue(
                        "P0",
                        "shipments",
                        int(idx) + 2,
                        str(row.get("shipment_id", "")),
                        "customer_id",
                        "ORPHAN_FK",
                        cid,
                    )
                )

        pay_link = schemas.get("payments", {}).get("_link", "shipment_id")
        if pay_link == "shipment_id":
            for idx, row in data["payments"].iterrows():
                sid = str(row.get("shipment_id", "")).strip()
                if sid and sid not in ship_ids:
                    issues.append(
                        _issue(
                            "P0",
                            "payments",
                            int(idx) + 2,
                            str(row.get("payment_id", "")),
                            "shipment_id",
                            "ORPHAN_PAYMENT",
                            sid,
                        )
                    )
        else:
            for idx, row in data["payments"].iterrows():
                cid = str(row.get("customer_id", "")).strip()
                if cid and cid not in cust_ids:
                    issues.append(
                        _issue(
                            "P0",
                            "payments",
                            int(idx) + 2,
                            str(row.get("payment_id", "")),
                            "customer_id",
                            "ORPHAN_PAYMENT",
                            cid,
                        )
                    )

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=[
            "severity",
            "sheet",
            "row_number",
            "record_id",
            "field",
            "issue_type",
            "message",
            "detected_at",
        ]
    )
