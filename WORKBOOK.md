# Workbook links

## Active solution workbook (CSV export source)

**[Open spreadsheet](https://docs.google.com/spreadsheets/d/1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to/edit?gid=1296664018#gid=1296664018)**

| Property | Value |
|----------|--------|
| Spreadsheet ID | `1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to` |
| Status | Used as the source for CSV exports / auto-fetch |
| Source tabs | `customers`, `shipments`, `payments` |
| Notes | This repository no longer uses Apps Script; automation runs in Python. |

### Quick checks

1. Ensure the tabs `customers`, `shipments`, `payments` exist and are populated.
2. Export each tab as CSV into `python/data/` **or** configure `python/config.yaml` gids and run `python run.py fetch-data`.
3. Run `python run.py validate` and confirm `python/output/data_issues.csv` has no P0 errors.

## Original assignment data (reference)

[Recykal_Intern_Data](https://docs.google.com/spreadsheets/d/177AdQbbkhVgAuoDARJOhtsB4lngpHK8fgHu_4NkQxJ4/edit?gid=2064198405#gid=2064198405) · ID `177AdQbbkhVgAuoDARJOhtsB4lngpHK8fgHu_4NkQxJ4`

## Deployment note

Publishing the latest recruiter-facing artifacts is done by running:

```powershell
cd python
python run.py phase5
```

This refreshes `deploy/` (dashboard + workbook + logs).
