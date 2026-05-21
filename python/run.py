#!/usr/bin/env python3
"""Recykal Collections — Python track CLI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# allow running from python/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.dashboard import build_dashboard, write_excel, write_html
from src.io_loaders import fetch_csv_from_google, load_all
from src.integration import run_phase5_pipeline
from src.monthly import run_monthly
from src.receivables import compute_receivables
from src.reminders import run_reminders
from src.sample_data import write_sample_data
from src.settings import load_config
from src.validate import validate_all


def cmd_sample_data() -> int:
    d = write_sample_data()
    print(f"Wrote sample CSVs to {d} (replace with your real exports for submission)")
    return 0


def cmd_fetch_data() -> int:
    cfg = load_config()
    gids = cfg["spreadsheet"].get("gids", {})
    data_dir = cfg["_data_dir"]
    ok = 0
    for name in ("customers", "shipments", "payments"):
        gid = gids.get(name) or ""
        dest = data_dir / f"{name}.csv"
        if fetch_csv_from_google(name, gid, dest):
            print(f"OK  {dest}")
            ok += 1
        else:
            print(f"SKIP {name} - set gids.{name} in config.yaml or download CSV manually")
    if ok == 0:
        print("\nManual export: see data/README.md")
        return 1
    return 0


def cmd_validate() -> int:
    data = load_all()
    issues = validate_all(data)
    out = load_config()["_output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "data_issues.csv"
    issues.to_csv(path, index=False)
    p0 = len(issues[issues["severity"] == "P0"]) if len(issues) else 0
    p1 = len(issues[issues["severity"] == "P1"]) if len(issues) else 0
    print(f"Wrote {path}")
    print(f"P0 errors: {p0}, P1 warnings: {p1}")
    if p0 > 0:
        print(issues[issues["severity"] == "P0"].head(10).to_string())
        return 1
    print("Validation passed (no P0).")
    return 0


def cmd_receivables() -> int:
    data = load_all()
    rec = compute_receivables(data)
    out = load_config()["_output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "receivables_computed.csv"
    rec.to_csv(path, index=False)
    print(f"Wrote {path} ({len(rec)} shipments)")
    open_count = (~rec["is_settled"]).sum()
    print(f"Open shipments: {open_count}")
    return 0


def cmd_reminders() -> int:
    data = load_all()
    rec = compute_receivables(data)
    log = run_reminders(rec)
    out = load_config()["_output_dir"] / "reminder_log.csv"
    log.to_csv(out, index=False)
    print(f"Reminders prepared: {len(log)} - see output/emails/reminders/")
    return 0


def cmd_monthly() -> int:
    data = load_all()
    rec = compute_receivables(data)
    log = run_monthly(rec)
    out = load_config()["_output_dir"] / "monthly_log.csv"
    log.to_csv(out, index=False)
    print(f"Monthly emails prepared: {len(log)} - see output/emails/monthly/")
    return 0


def cmd_dashboard() -> int:
    data = load_all()
    rec = compute_receivables(data)
    dash = build_dashboard(data, rec)
    out = load_config()["_output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    write_html(dash, out / "dashboard.html")
    write_excel(dash, out / "collections_dashboard.xlsx")
    print(f"Wrote {out / 'dashboard.html'}")
    print(f"Wrote {out / 'collections_dashboard.xlsx'}  (upload to Google Sheets for Task B)")
    return 0


def cmd_all() -> int:
    steps = [cmd_validate, cmd_receivables, cmd_reminders, cmd_monthly, cmd_dashboard]
    for fn in steps:
        print(f"\n--- {fn.__name__} ---")
        if fn() != 0 and fn == cmd_validate:
            return 1
    return 0


def cmd_phase5() -> int:
    result = run_phase5_pipeline()
    print("Phase 5 local integration complete.")
    print(f"Receivables rows: {result['receivables_rows']}")
    print(f"Open shipments: {result['open_shipments']}")
    print(f"Reminder previews: {result['reminders']}")
    print(f"Monthly previews: {result['monthly']}")
    print(f"Dashboard HTML: {result['dashboard_html']}")
    print(f"Dashboard Excel: {result['dashboard_xlsx']}")
    print(f"Operator summary: {result['summary_path']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Recykal Collections (Python track)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch-data", help="Try CSV export from Google Sheet")
    sub.add_parser("sample-data", help="Write test CSVs to data/ (for pipeline demo)")
    sub.add_parser("validate", help="Phase 0 data validation")
    sub.add_parser("receivables", help="Phase 1 compute outstanding")
    sub.add_parser("reminders", help="Phase 2 reminder previews (dry-run)")
    sub.add_parser("monthly", help="Phase 3 monthly previews (dry-run)")
    sub.add_parser("dashboard", help="Phase 4 HTML + Excel dashboard")
    sub.add_parser("phase5", help="Run local Phase 5 integration with run_log and operator summary")
    sub.add_parser("all", help="Run validate → receivables → reminders → monthly → dashboard")

    args = parser.parse_args()
    handlers = {
        "fetch-data": cmd_fetch_data,
        "sample-data": cmd_sample_data,
        "validate": cmd_validate,
        "receivables": cmd_receivables,
        "reminders": cmd_reminders,
        "monthly": cmd_monthly,
        "dashboard": cmd_dashboard,
        "phase5": cmd_phase5,
        "all": cmd_all,
    }
    return handlers[args.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
