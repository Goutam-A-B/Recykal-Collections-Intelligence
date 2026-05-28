# Phase 5 Operator Summary

Generated: 2026-05-28T18:09:17

## Status

- Validation P0 errors: 0
- Validation warnings/info rows: 0
- Receivables processed: 595
- Open shipments: 190
- Reminder previews prepared: 9
- Monthly confirmation previews prepared: 15
- Total outstanding: 622,147,416.02
- Dashboard reconciliation: PASS
- Email mode: dry-run previews only

## Outputs

- Data issues: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/data_issues.csv`
- Receivables: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/receivables_computed.csv`
- Reminder log: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/reminder_log.csv`
- Monthly log: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/monthly_log.csv`
- Dashboard HTML: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/dashboard.html`
- Dashboard Excel for Google Sheets upload: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/collections_dashboard.xlsx`
- Run log: `/home/runner/work/Recykal-Collections-Intelligence/Recykal-Collections-Intelligence/python/output/run_log.csv`

## Automation / “No Delay” Refresh

The intended deployment is a scheduled run (cron). In this repo:
- local run: `python run.py phase5`
- CI option: GitHub Actions workflow `.github/workflows/refresh.yml`

```powershell
cd python
python run.py phase5
```

For submission, upload `collections_dashboard.xlsx` to Google Drive and open it with Google Sheets.
