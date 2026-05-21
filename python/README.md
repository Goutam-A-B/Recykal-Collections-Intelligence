# Python implementation (primary)

This repository is **Python-only** (Apps Script removed). Use this pipeline to generate all Task A + Task B deliverables.

**Full guide:** [docs/alternate-python-approach.md](../docs/alternate-python-approach.md)

## Quick start

```powershell
cd python
pip install -r requirements.txt
```

### 1. Get data (pick one)

**A — Manual (most reliable)**  
Export `customers`, `shipments`, `payments` as CSV into `python/data/` (see [data/README.md](data/README.md)).

**B — Auto-fetch**  
Set tab `gid` values in `config.yaml` (from sheet URL `#gid=...`), then:

```powershell
python run.py fetch-data
```

### 2. Run pipeline

```powershell
python run.py all
```

### 3. Outputs (`python/output/`)

| File | Purpose |
|------|---------|
| `data_issues.csv` | Phase 0 validation |
| `receivables_computed.csv` | Phase 1 balances |
| `emails/reminders/*.txt` | Phase 2 dry-run emails |
| `emails/monthly/*.txt` | Phase 3 dry-run |
| `dashboard.html` | Phase 4 view in browser |
| `collections_dashboard.xlsx` | **Upload to Google Sheets** for Task B |

## Commands

| Command | Phase |
|---------|-------|
| `python run.py validate` | 0 |
| `python run.py receivables` | 1 |
| `python run.py reminders` | 2 |
| `python run.py monthly` | 3 |
| `python run.py dashboard` | 4 |
| `python run.py phase5` | 0-5 integration + run log |
| `python run.py all` | 0→4 |

## Phase 5 (recommended entry point)

```powershell
python run.py phase5
```

This writes `output/run_log.csv`, `output/phase5_operator_summary.md`, and refreshed dashboard artifacts.

## Task B (Google Sheets)

You do not need live Apps Script for the dashboard:

1. Generate `output/collections_dashboard.xlsx`
2. Google Drive → **New → File upload**
3. Open with **Google Sheets**
4. Share link in submission

Business logic follows the problem statement (outstanding accuracy, reminder windows, Large overdue exclusion).
