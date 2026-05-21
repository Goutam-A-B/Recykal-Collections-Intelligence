"""Load CSV data with normalized column names."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .settings import load_config, normalize_header


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_header(c) for c in df.columns]
    return df


def _resolve_csv_path(data_dir: Path, name: str) -> Path:
    exact = data_dir / f"{name}.csv"
    if exact.exists():
        return exact
    # Google Sheets download: "Recykal_Intern_Data.xlsx - customers.csv"
    matches = sorted(data_dir.glob(f"*{name}*.csv"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        for m in matches:
            if m.name.endswith(f" - {name}.csv") or m.name.endswith(f"- {name}.csv"):
                return m
        return matches[0]
    raise FileNotFoundError(
        f"Missing {name}.csv in {data_dir}. Export the '{name}' tab from Google Sheets."
    )


def load_table(name: str) -> pd.DataFrame:
    cfg = load_config()
    path = _resolve_csv_path(cfg["_data_dir"], name)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    # coerce numeric/date columns after normalize
    df = _normalize_columns(df)
    return df


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "customers": load_table("customers"),
        "shipments": load_table("shipments"),
        "payments": load_table("payments"),
    }


def fetch_csv_from_google(sheet_key: str, gid: str, dest: Path) -> bool:
    """Try public CSV export via GID or gviz endpoint. Returns True if saved."""
    import requests

    cfg = load_config()
    sid = cfg["spreadsheet"]["id"]

    # Try GID-based export first (faster, exact).
    if gid:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and "html" not in r.headers.get("Content-Type", "").lower():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.content)
            return True

    # Fallback: gviz endpoint using sheet name (works without GID).
    gviz_url = (
        f"https://docs.google.com/spreadsheets/d/{sid}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_key}"
    )
    r = requests.get(gviz_url, timeout=30)
    if r.status_code == 200 and "html" not in r.headers.get("Content-Type", "").lower():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return True

    return False
