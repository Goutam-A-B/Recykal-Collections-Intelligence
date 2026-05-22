# Phase 5 Operator Summary

Generated: 2026-05-22T20:49:00

## Status

- Validation P0 errors: 0
- Validation warnings/info rows: 0
- Receivables processed: 595
- Open shipments: 190
- Reminder previews prepared: 8
- Monthly confirmation previews prepared: 15
- Total outstanding: 622,147,416.02
- Dashboard reconciliation: PASS
- Email mode: dry-run previews only

## Outputs

- Data issues: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\data_issues.csv`
- Receivables: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\receivables_computed.csv`
- Reminder log: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\reminder_log.csv`
- Monthly log: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\monthly_log.csv`
- Dashboard HTML: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\dashboard.html`
- Dashboard Excel for Google Sheets upload: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\collections_dashboard.xlsx`
- Run log: `C:\Users\goutam\.trae\work\6a106d6d92064cbb96837b22\push_repo\python\output\run_log.csv`

## Automation / “No Delay” Refresh

The intended deployment is a scheduled run (cron). In this repo:
- local run: `python run.py phase5`
- CI option: GitHub Actions workflow `.github/workflows/refresh.yml`

```powershell
cd python
python run.py phase5
```

For submission, upload `collections_dashboard.xlsx` to Google Drive and open it with Google Sheets.
