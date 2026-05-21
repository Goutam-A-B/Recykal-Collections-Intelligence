# Phase 5 Operator Summary

Generated: 2026-05-21T14:44:42

## Status

- Validation P0 errors: 0
- Validation warnings/info rows: 0
- Receivables processed: 3
- Open shipments: 2
- Reminder previews prepared: 1
- Monthly confirmation previews prepared: 2
- Total outstanding: 310,000.00
- Email mode: dry-run previews only

## Outputs

- Data issues: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/data_issues.csv`
- Receivables: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/receivables_computed.csv`
- Reminder log: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/reminder_log.csv`
- Monthly log: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/monthly_log.csv`
- Dashboard HTML: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/dashboard.html`
- Dashboard Excel for Google Sheets upload: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/collections_dashboard.xlsx`
- Run log: `/home/ubuntu/repos/Recykal-Collections-Intelligence/python/output/run_log.csv`

## Automation / “No Delay” Refresh

The intended deployment is a scheduled run (cron). In this repo:
- local run: `python run.py phase5`
- CI option: GitHub Actions workflow `.github/workflows/refresh.yml`

```powershell
cd python
python run.py phase5
```

For submission, upload `collections_dashboard.xlsx` to Google Drive and open it with Google Sheets.
