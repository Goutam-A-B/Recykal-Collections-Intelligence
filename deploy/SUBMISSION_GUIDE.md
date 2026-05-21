# Recykal Assignment Submission Guide

## Recommended Evaluator Links

1. **Interactive dashboard:** deploy `deploy/index.html` as a static site.
2. **Google Sheets dashboard:** upload `deploy/collections_dashboard.xlsx` to Google Drive and open it with Google Sheets.
3. **Observability proof:** include `deploy/phase5_operator_summary.md` and `deploy/run_log.csv`.

## Easiest Static Deployment

Use Netlify Drop:

1. Open `https://app.netlify.com/drop`
2. Drag the whole `deploy/` folder onto the page
3. Copy the generated site URL

The interactive dashboard is self-contained in `index.html`, so it does not need a backend.

## What The Dashboard Demonstrates

- Summary KPIs: total invoice value, total collected, total outstanding, overdue shipments
- Outstanding by customer sorted by exposure
- Invoice aging buckets
- Daily collections trend for the previous 30 days
- Search, segment, aging, and top-N filters
- Open invoice detail with invoice amount, paid amount, outstanding amount, due date, and days-to-due

## Automation / Phase 5 Replacement

Apps Script was unreliable for this workbook, so the final automation is implemented as a reproducible Python command:

```powershell
cd python
python run.py phase5
```

This regenerates validation output, receivables, reminder previews, monthly confirmation previews, dashboard files, `run_log.csv`, and `phase5_operator_summary.md`.

### Scheduled refresh (“no delay” sync)

To keep artifacts continuously updated, enable the GitHub Actions workflow:
- `.github/workflows/refresh.yml` (runs every 15 minutes)

It best-effort fetches latest CSV exports (if the sheet is accessible) and regenerates `deploy/` + `python/output/`, committing refreshed artifacts.

## Submission Note

Suggested wording:

> Apps Script binding was unstable in the provided workbook, so I implemented the same business rules through a Python automation pipeline. It dynamically reads customers, shipments, and payments; calculates outstanding balances with partial payments; prepares reminder and monthly email previews; generates a Google-Sheets-compatible dashboard workbook; and provides an interactive HTML dashboard plus run logs for observability.
