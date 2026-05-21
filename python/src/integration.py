"""Phase 5 - local integration and observability for the Python track."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from time import perf_counter
from typing import Any, Callable

import pandas as pd

from .dashboard import build_dashboard, write_excel, write_html
from .io_loaders import load_all
from .monthly import run_monthly
from .receivables import compute_receivables
from .reminders import run_reminders
from .settings import load_config
from .validate import validate_all


def _run_step(
    rows: list[dict[str, Any]],
    job_name: str,
    fn: Callable[[], Any],
    count_fn: Callable[[Any], int] | None = None,
) -> Any:
    started = perf_counter()
    run_at = datetime.now().isoformat(timespec="seconds")
    try:
      result = fn()
      count = count_fn(result) if count_fn else 0
      rows.append(
          {
              "run_at": run_at,
              "job_name": job_name,
              "status": "Success",
              "records": count,
              "errors": 0,
              "duration_seconds": round(perf_counter() - started, 2),
              "notes": "",
          }
      )
      return result
    except Exception as exc:
      rows.append(
          {
              "run_at": run_at,
              "job_name": job_name,
              "status": "Failed",
              "records": 0,
              "errors": 1,
              "duration_seconds": round(perf_counter() - started, 2),
              "notes": str(exc),
          }
      )
      raise


def _count_rows(value: Any) -> int:
    if isinstance(value, pd.DataFrame):
        return len(value)
    return 0


def run_phase5_pipeline() -> dict[str, Any]:
    cfg = load_config()
    out_dir: Path = cfg["_output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    project_root = cfg["_root"].parent
    deploy_dir = project_root / "deploy"
    deploy_dir.mkdir(parents=True, exist_ok=True)

    run_rows: list[dict[str, Any]] = []
    data = _run_step(run_rows, "load_data", load_all)

    issues = _run_step(run_rows, "validate", lambda: validate_all(data), _count_rows)
    issues_path = out_dir / "data_issues.csv"
    issues.to_csv(issues_path, index=False)
    p0_errors = len(issues[issues["severity"] == "P0"]) if len(issues) else 0
    if p0_errors:
        raise RuntimeError(f"Validation failed with {p0_errors} P0 errors. See {issues_path}.")

    receivables = _run_step(
        run_rows,
        "compute_receivables",
        lambda: compute_receivables(data),
        _count_rows,
    )
    receivables_path = out_dir / "receivables_computed.csv"
    receivables.to_csv(receivables_path, index=False)

    reminders = _run_step(
        run_rows,
        "prepare_reminders",
        lambda: run_reminders(receivables),
        _count_rows,
    )
    reminder_log_path = out_dir / "reminder_log.csv"
    reminders.to_csv(reminder_log_path, index=False)

    monthly = _run_step(
        run_rows,
        "prepare_monthly_confirmations",
        lambda: run_monthly(receivables),
        _count_rows,
    )
    monthly_log_path = out_dir / "monthly_log.csv"
    monthly.to_csv(monthly_log_path, index=False)

    dashboard = _run_step(
        run_rows,
        "build_dashboard",
        lambda: build_dashboard(data, receivables),
        lambda result: len(result["open_receivables"]),
    )
    html_path = out_dir / "dashboard.html"
    xlsx_path = out_dir / "collections_dashboard.xlsx"
    write_html(dashboard, html_path)
    write_excel(dashboard, xlsx_path)

    run_log = pd.DataFrame(run_rows)
    run_log_path = out_dir / "run_log.csv"
    run_log.to_csv(run_log_path, index=False)

    summary_path = out_dir / "phase5_operator_summary.md"
    _write_summary(
        summary_path=summary_path,
        cfg=cfg,
        p0_errors=p0_errors,
        issues=issues,
        receivables=receivables,
        reminders=reminders,
        monthly=monthly,
        dashboard=dashboard,
        paths={
            "issues": issues_path,
            "receivables": receivables_path,
            "reminders": reminder_log_path,
            "monthly": monthly_log_path,
            "dashboard_html": html_path,
            "dashboard_xlsx": xlsx_path,
            "run_log": run_log_path,
        },
    )

    # Publish recruiter-facing artifacts into /deploy (keeps a stable, easy-to-find path).
    shutil.copyfile(html_path, deploy_dir / "index.html")
    shutil.copyfile(xlsx_path, deploy_dir / "collections_dashboard.xlsx")
    shutil.copyfile(run_log_path, deploy_dir / "run_log.csv")
    shutil.copyfile(summary_path, deploy_dir / "phase5_operator_summary.md")

    return {
        "run_log": run_log,
        "summary_path": summary_path,
        "dashboard_xlsx": xlsx_path,
        "dashboard_html": html_path,
        "p0_errors": p0_errors,
        "receivables_rows": len(receivables),
        "open_shipments": int((~receivables["is_settled"]).sum()),
        "reminders": len(reminders),
        "monthly": len(monthly),
    }


def _write_summary(
    *,
    summary_path: Path,
    cfg: dict[str, Any],
    p0_errors: int,
    issues: pd.DataFrame,
    receivables: pd.DataFrame,
    reminders: pd.DataFrame,
    monthly: pd.DataFrame,
    dashboard: dict[str, pd.DataFrame],
    paths: dict[str, Path],
) -> None:
    open_shipments = int((~receivables["is_settled"]).sum())
    total_outstanding = float(dashboard["kpis"].loc[
        dashboard["kpis"]["metric"] == "Total Outstanding", "value"
    ].iloc[0])

    text = f"""# Phase 5 Operator Summary

Generated: {datetime.now().isoformat(timespec="seconds")}

## Status

- Validation P0 errors: {p0_errors}
- Validation warnings/info rows: {len(issues) - p0_errors}
- Receivables processed: {len(receivables)}
- Open shipments: {open_shipments}
- Reminder previews prepared: {len(reminders)}
- Monthly confirmation previews prepared: {len(monthly)}
- Total outstanding: {total_outstanding:,.2f}
- Email mode: {'enabled' if cfg.get('email', {}).get('enabled') else 'dry-run previews only'}

## Outputs

- Data issues: `{paths['issues']}`
- Receivables: `{paths['receivables']}`
- Reminder log: `{paths['reminders']}`
- Monthly log: `{paths['monthly']}`
- Dashboard HTML: `{paths['dashboard_html']}`
- Dashboard Excel for Google Sheets upload: `{paths['dashboard_xlsx']}`
- Run log: `{paths['run_log']}`

## Automation / “No Delay” Refresh

The intended deployment is a scheduled run (cron). In this repo:
- local run: `python run.py phase5`
- CI option: GitHub Actions workflow `.github/workflows/refresh.yml`

```powershell
cd python
python run.py phase5
```

For submission, upload `collections_dashboard.xlsx` to Google Drive and open it with Google Sheets.
"""
    summary_path.write_text(text, encoding="utf-8")
