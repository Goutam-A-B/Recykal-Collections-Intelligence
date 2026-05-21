# Data folder

Place three CSV exports here.

**Exact names (best):** `customers.csv`, `shipments.csv`, `payments.csv`

**Also works:** Google’s download names like `Recykal_Intern_Data.xlsx - customers.csv` (auto-detected).

| File | Sheet tab |
|------|-----------|
| `customers.csv` | customers |
| `shipments.csv` | shipments |
| `payments.csv` | payments |

**Note:** Recykal payments use `customer_id` (not `shipment_id`). The pipeline allocates payments to invoices **FIFO by due date** per customer.

## How to export from Google Sheets

1. Open your [workbook](https://docs.google.com/spreadsheets/d/1FRzRXR5Wp8RObFKaykUKHrWSsbI9dDr_w1hnBsvm8to/edit).
2. Select the **customers** tab → **File → Download → Comma Separated Values (.csv)**.
3. Save as `customers.csv` in this folder.
4. Repeat for **shipments** and **payments**.

Or run from `python/` folder:

```bash
python run.py fetch-data
```

(Requires view access on the sheet; set `gids` in `config.yaml` if needed.)
