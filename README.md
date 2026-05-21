# Recykal Collections Intelligence System (Python-only)

Automated payment reminders (Task A-1), monthly balance confirmation (Task A-2), and a collections dashboard (Task B) implemented as a **Python pipeline**.

This repo intentionally **does not use Apps Script** (removed due to reliability/binding issues). Instead:
- data is pulled as CSV exports (manual or auto-fetch),
- business logic runs in Python (single receivables engine),
- outputs are generated as **email previews + logs + dashboard HTML + an Excel workbook that can be uploaded to Google Sheets**,
- “no-delay sync” is demonstrated via a **scheduled GitHub Actions refresh**.

## Documentation

| Resource | Path |
|----------|------|
| Problem statement | [docs/recykal problem statement.md](docs/recykal%20problem%20statement.md) |
| Architecture (Python) | [docs/architecture-python.md](docs/architecture-python.md) |
| Edge cases | [docs/edge-cases/](docs/edge-cases/) |
| Submission guide | [deploy/SUBMISSION_GUIDE.md](deploy/SUBMISSION_GUIDE.md) |

## Quick start (recruiter-friendly)

```powershell
cd python
pip install -r requirements.txt

# Option A: manual exports (most reliable)
# put customers.csv, shipments.csv, payments.csv into python/data/

python run.py phase5
```

### Outputs (generated under `python/output/` and also published to `deploy/`)
- `data_issues.csv` (data validation)
- `receivables_computed.csv` (single source of truth)
- `emails/reminders/*.txt` (Task A-1 dry-run previews)
- `emails/monthly/*.txt` (Task A-2 dry-run previews)
- `dashboard.html` (Task B dashboard view)
- `collections_dashboard.xlsx` (**upload to Google Drive → open with Google Sheets**)
- `run_log.csv` + `phase5_operator_summary.md` (proof for recruiter)

## Automation / “no delay” sync

This repo includes a GitHub Actions workflow that can run on a cron schedule (e.g., every 15 minutes):
1) fetch latest CSV exports from the Google Sheet (if accessible), and  
2) regenerate `deploy/` artifacts so the dashboard stays current.

See `.github/workflows/refresh.yml` and `python/config.yaml`.

## Project structure

```
python/         # Python pipeline (phases 0→5)
deploy/         # Recruiter-facing artifacts (latest run)
docs/           # Problem statement + architecture + edge cases
phases/         # Phase notes mapped to Python modules
```
