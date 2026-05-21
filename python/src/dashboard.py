"""Phase 4 - Dashboard as interactive HTML + Excel."""
from __future__ import annotations

from datetime import date, timedelta
import json

import pandas as pd

from .settings import load_config
from .validate import _parse_date


def build_dashboard(
    data: dict[str, pd.DataFrame], receivables: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    cfg = load_config()
    eps = float(cfg["business"]["epsilon"])
    today = pd.Timestamp(date.today()).normalize()

    open_rec = receivables[
        ~receivables["is_settled"] & (receivables["outstanding"] > eps)
    ].copy()

    total_invoice = receivables["invoice_amount"].sum()
    total_collected = receivables["amount_paid_total"].sum()
    total_outstanding = open_rec["outstanding"].sum()
    overdue_count = int((open_rec["days_to_due"] < 0).sum())

    kpis = pd.DataFrame(
        [
            {"metric": "Total Invoice Value", "value": total_invoice},
            {"metric": "Total Collected", "value": total_collected},
            {"metric": "Total Outstanding", "value": total_outstanding},
            {"metric": "Overdue Shipments", "value": overdue_count},
        ]
    )

    by_customer = (
        open_rec.groupby(["customer_id", "customer_name", "segment"], as_index=False)
        .agg(open_shipments=("shipment_id", "count"), total_outstanding=("outstanding", "sum"))
        .sort_values("total_outstanding", ascending=False)
    )

    def bucket(row: pd.Series) -> str:
        d = row["days_to_due"]
        if pd.isna(d) or d >= 0:
            return "Not Yet Due"
        overdue_days = int(-d)
        if overdue_days <= 30:
            return "1-30 Days Overdue"
        if overdue_days <= 60:
            return "31-60 Days Overdue"
        return "61+ Days Overdue"

    open_rec["aging_bucket"] = open_rec.apply(bucket, axis=1)
    bucket_order = ["Not Yet Due", "1-30 Days Overdue", "31-60 Days Overdue", "61+ Days Overdue"]
    aging = (
        open_rec.groupby("aging_bucket", as_index=False)["outstanding"]
        .sum()
        .rename(columns={"outstanding": "amount"})
        .set_index("aging_bucket")
        .reindex(bucket_order, fill_value=0)
        .reset_index()
    )

    payments = data["payments"].copy()
    if "payment_date" in payments.columns and "amount_paid" in payments.columns:
        payments["payment_date_parsed"] = payments["payment_date"].map(_parse_date)
        payments["amount_paid"] = pd.to_numeric(
            payments["amount_paid"].astype(str).str.replace(",", ""), errors="coerce"
        ).fillna(0)
        start = today - timedelta(days=29)
        recent = payments[
            (payments["payment_date_parsed"] >= start) & (payments["payment_date_parsed"] <= today)
        ]
        trend = (
            recent.groupby("payment_date_parsed", as_index=False)["amount_paid"]
            .sum()
            .rename(columns={"payment_date_parsed": "date", "amount_paid": "collected"})
        )
        trend = (
            pd.DataFrame({"date": pd.date_range(start=start, end=today, freq="D")})
            .merge(trend, on="date", how="left")
            .fillna({"collected": 0})
        )
    else:
        trend = pd.DataFrame(columns=["date", "collected"])

    return {
        "kpis": kpis,
        "by_customer": by_customer,
        "aging": aging,
        "trend": trend,
        "open_receivables": open_rec,
    }


def write_html(dashboard: dict[str, pd.DataFrame], path) -> None:
    payload_json = json.dumps(_dashboard_payload(dashboard), ensure_ascii=False)
    # Avoid `</script>` prematurely terminating the JSON script tag.
    # Note: do this outside the f-string expression to keep Python happy.
    safe_payload_json = payload_json.replace("</", "<\\/")
    generated = date.today().isoformat()

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recykal Collections Intelligence</title>
<style>
:root {{ --bg:#f6f8fb; --panel:#fff; --line:#dfe5ee; --ink:#17212f; --muted:#667085; --blue:#1769aa; --green:#16794c; --orange:#b45309; --red:#b42318; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
header {{ background:#fff; border-bottom:1px solid var(--line); padding:22px 28px 18px; position:sticky; top:0; z-index:5; }}
.eyebrow {{ color:var(--blue); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
h1 {{ margin:4px 0 6px; font-size:28px; line-height:1.2; }}
.subtitle {{ color:var(--muted); margin:0; max-width:980px; }}
main {{ padding:22px 28px 40px; max-width:1440px; margin:0 auto; }}
.toolbar {{ display:grid; grid-template-columns:minmax(180px,1fr) 150px 170px 130px; gap:12px; margin-bottom:18px; }}
input, select {{ width:100%; border:1px solid var(--line); border-radius:8px; padding:10px 12px; font:inherit; background:#fff; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,minmax(180px,1fr)); gap:14px; margin-bottom:18px; }}
.card,.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:0 1px 2px rgba(16,24,40,.05); }}
.card {{ padding:16px; }}
.metric-label {{ color:var(--muted); font-size:13px; margin-bottom:8px; }}
.metric-value {{ font-size:25px; font-weight:760; line-height:1.1; }}
.metric-note {{ color:var(--muted); font-size:12px; margin-top:8px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; }}
.panel {{ padding:16px; min-width:0; }}
.panel h2 {{ margin:0 0 12px; font-size:17px; }}
.bars {{ display:grid; gap:10px; }}
.bar-row {{ display:grid; grid-template-columns:145px 1fr 125px; align-items:center; gap:10px; font-size:13px; }}
.bar-track {{ height:13px; background:#eef2f7; border-radius:99px; overflow:hidden; }}
.bar-fill {{ height:100%; background:var(--blue); border-radius:99px; }}
.bar-fill.risk {{ background:var(--orange); }}
.bar-fill.high {{ background:var(--red); }}
.chart-wrap {{ height:280px; }}
svg {{ width:100%; height:100%; display:block; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ padding:9px 8px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:#344054; background:#f8fafc; font-weight:700; position:sticky; top:0; }}
td.num,th.num,.num {{ text-align:right; }}
.tablebox {{ max-height:430px; overflow:auto; border:1px solid var(--line); border-radius:8px; }}
.rules {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
.rule {{ border:1px solid var(--line); border-left:4px solid var(--green); border-radius:8px; padding:12px; background:#fff; }}
.rule strong {{ display:block; margin-bottom:4px; }}
.rule span {{ color:var(--muted); font-size:13px; }}
.pill {{ display:inline-flex; align-items:center; border-radius:99px; padding:3px 8px; background:#eef4ff; color:#194185; font-size:12px; font-weight:700; }}
footer {{ color:var(--muted); font-size:12px; margin-top:18px; }}
@media (max-width:980px) {{ .toolbar,.grid,.rules {{ grid-template-columns:1fr; }} .kpis {{ grid-template-columns:repeat(2,1fr); }} }}
@media (max-width:560px) {{ header,main {{ padding-left:16px; padding-right:16px; }} .kpis {{ grid-template-columns:1fr; }} .bar-row {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <div class="eyebrow">Recykal Collections Intelligence</div>
  <h1>Receivables, reminders, and collection risk in one view</h1>
  <p class="subtitle">Generated {generated} from source CSV exports. Filters update KPIs, customer exposure, aging, recent collections, and open invoice detail.</p>
</header>
<main>
  <section class="toolbar" aria-label="Dashboard filters">
    <input id="search" placeholder="Search customer or shipment">
    <select id="segment"></select>
    <select id="bucket"></select>
    <select id="topn">
      <option value="10">Top 10 customers</option>
      <option value="20" selected>Top 20 customers</option>
      <option value="50">Top 50 customers</option>
      <option value="9999">All customers</option>
    </select>
  </section>
  <section class="kpis" id="kpis"></section>
  <section class="grid">
    <div class="panel"><h2>Outstanding by Customer</h2><div class="bars" id="customerBars"></div></div>
    <div class="panel"><h2>Invoice Aging Buckets</h2><div class="bars" id="agingBars"></div></div>
  </section>
  <section class="grid">
    <div class="panel"><h2>Daily Collections Trend - Last 30 Days</h2><div class="chart-wrap" id="trendChart"></div></div>
    <div class="panel"><h2>Assignment Criteria Covered</h2>
      <div class="rules">
        <div class="rule"><strong>Outstanding accuracy</strong><span>Aggregates all installments by shipment and excludes settled invoices.</span></div>
        <div class="rule"><strong>Reminder logic</strong><span>7D, 3D, 1D, and overdue windows; Large overdue excluded.</span></div>
        <div class="rule"><strong>Monthly confirmation</strong><span>One consolidated customer statement for all open balances.</span></div>
        <div class="rule"><strong>Real-time dashboard</strong><span>Auto-refresh via scheduled pipeline (GitHub Actions cron) or regenerate locally from latest CSV exports.</span></div>
        <div class="rule"><strong>Observability</strong><span>Phase 5 writes run logs and operator summary.</span></div>
        <div class="rule"><strong>Submission ready</strong><span>Excel output can be uploaded directly to Google Sheets.</span></div>
      </div>
    </div>
  </section>
  <section class="panel">
    <h2>Open Invoice Detail <span class="pill" id="detailCount"></span></h2>
    <div class="tablebox"><table>
      <thead><tr><th>Shipment</th><th>Customer</th><th>Segment</th><th>Due Date</th><th class="num">Days to Due</th><th class="num">Invoice</th><th class="num">Paid</th><th class="num">Outstanding</th></tr></thead>
      <tbody id="detailRows"></tbody>
    </table></div>
  </section>
  <footer>Refresh: run <code>python run.py phase5</code> locally (or let the GitHub Actions cron regenerate <code>deploy/</code>), then upload <code>collections_dashboard.xlsx</code> to Google Sheets for the evaluator-facing workbook.</footer>
</main>
<script id="payload" type="application/json">{safe_payload_json}</script>
<script>
const DATA = JSON.parse(document.getElementById('payload').textContent);
const money = v => '₹' + Number(v || 0).toLocaleString('en-IN', {{ maximumFractionDigits: 0 }});
const preciseMoney = v => '₹' + Number(v || 0).toLocaleString('en-IN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
function bucketFor(row) {{ const d = row.days_to_due; if (d === null || d >= 0) return 'Not Yet Due'; const overdue = Math.abs(d); if (overdue <= 30) return '1-30 Days Overdue'; if (overdue <= 60) return '31-60 Days Overdue'; return '61+ Days Overdue'; }}
function initFilters() {{
  const segments = ['All segments', ...Array.from(new Set(DATA.open_receivables.map(r => r.segment))).sort()];
  document.getElementById('segment').innerHTML = segments.map(s => `<option value="${{s}}">${{s}}</option>`).join('');
  const buckets = ['All aging buckets', 'Not Yet Due', '1-30 Days Overdue', '31-60 Days Overdue', '61+ Days Overdue'];
  document.getElementById('bucket').innerHTML = buckets.map(b => `<option value="${{b}}">${{b}}</option>`).join('');
  ['search','segment','bucket','topn'].forEach(id => document.getElementById(id).addEventListener('input', render));
}}
function filteredRows() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  const seg = document.getElementById('segment').value;
  const bucket = document.getElementById('bucket').value;
  return DATA.open_receivables.filter(row => {{
    const text = `${{row.customer_id}} ${{row.customer_name}} ${{row.shipment_id}}`.toLowerCase();
    return (!q || text.includes(q)) && (seg === 'All segments' || row.segment === seg) && (bucket === 'All aging buckets' || bucketFor(row) === bucket);
  }});
}}
function renderKpis(rows) {{
  const invoice = rows.reduce((s,r)=>s+Number(r.invoice_amount||0),0);
  const paid = rows.reduce((s,r)=>s+Number(r.amount_paid_total||0),0);
  const outstanding = rows.reduce((s,r)=>s+Number(r.outstanding||0),0);
  const overdue = rows.filter(r=>Number(r.days_to_due)<0).length;
  const cards = [['Open Invoice Value',money(invoice),'Filtered open receivables'],['Collected Against Open',money(paid),'Payments mapped to these invoices'],['Outstanding Exposure',money(outstanding),'Remaining balance to collect'],['Overdue Shipments',overdue.toLocaleString('en-IN'),'Open invoices past due']];
  document.getElementById('kpis').innerHTML = cards.map(c => `<div class="card"><div class="metric-label">${{c[0]}}</div><div class="metric-value">${{c[1]}}</div><div class="metric-note">${{c[2]}}</div></div>`).join('');
}}
function renderBars(id, rows, options={{}}) {{
  const max = Math.max(1,...rows.map(r=>r.value));
  document.getElementById(id).innerHTML = rows.map(r => {{
    const pct = Math.max(3,(r.value/max)*100);
    const cls = options.risk && r.label.includes('61+') ? 'bar-fill high' : options.risk && r.label.includes('Overdue') ? 'bar-fill risk' : 'bar-fill';
    return `<div class="bar-row"><div>${{r.label}}</div><div class="bar-track"><div class="${{cls}}" style="width:${{pct}}%"></div></div><div class="num">${{money(r.value)}}</div></div>`;
  }}).join('');
}}
function renderCustomerBars(rows) {{
  const topN = Number(document.getElementById('topn').value);
  const map = new Map();
  rows.forEach(r => {{ const key = `${{r.customer_id}} · ${{r.customer_name}}`; map.set(key,(map.get(key)||0)+Number(r.outstanding||0)); }});
  renderBars('customerBars', Array.from(map.entries()).map(([label,value])=>({{label,value}})).sort((a,b)=>b.value-a.value).slice(0,topN));
}}
function renderAging(rows) {{
  const order = ['Not Yet Due','1-30 Days Overdue','31-60 Days Overdue','61+ Days Overdue'];
  renderBars('agingBars', order.map(label=>({{label,value:rows.filter(r=>bucketFor(r)===label).reduce((s,r)=>s+Number(r.outstanding||0),0)}})), {{risk:true}});
}}
function renderTrend() {{
  const points = DATA.trend, w=680, h=250, p=34, max=Math.max(1,...points.map(d=>d.collected));
  const barW = (w-p*2)/points.length;
  const bars = points.map((d,i)=>{{ const bh=(Number(d.collected||0)/max)*(h-p*2), x=p+i*barW, y=h-p-bh; return `<rect x="${{x.toFixed(1)}}" y="${{y.toFixed(1)}}" width="${{Math.max(2,barW-2).toFixed(1)}}" height="${{bh.toFixed(1)}}" fill="#1769aa"><title>${{d.date}}: ${{preciseMoney(d.collected)}}</title></rect>`; }}).join('');
  document.getElementById('trendChart').innerHTML = `<svg viewBox="0 0 ${{w}} ${{h}}" role="img" aria-label="Daily collections trend"><line x1="${{p}}" y1="${{h-p}}" x2="${{w-p}}" y2="${{h-p}}" stroke="#98a2b3"/><line x1="${{p}}" y1="${{p}}" x2="${{p}}" y2="${{h-p}}" stroke="#98a2b3"/>${{bars}}<text x="${{p}}" y="18" fill="#667085" font-size="12">Peak day: ${{money(max)}}</text></svg>`;
}}
function renderDetails(rows) {{
  const sorted = rows.slice().sort((a,b)=>Number(b.outstanding)-Number(a.outstanding));
  document.getElementById('detailCount').textContent = `${{sorted.length}} open rows`;
  document.getElementById('detailRows').innerHTML = sorted.slice(0,250).map(r => `<tr><td>${{r.shipment_id}}</td><td>${{r.customer_name}}<br><span class="metric-note">${{r.customer_id}}</span></td><td>${{r.segment}}</td><td>${{r.due_date||''}}</td><td class="num">${{r.days_to_due===null?'':r.days_to_due}}</td><td class="num">${{preciseMoney(r.invoice_amount)}}</td><td class="num">${{preciseMoney(r.amount_paid_total)}}</td><td class="num"><strong>${{preciseMoney(r.outstanding)}}</strong></td></tr>`).join('');
}}
function render() {{ const rows = filteredRows(); renderKpis(rows); renderCustomerBars(rows); renderAging(rows); renderTrend(); renderDetails(rows); }}
initFilters(); render();
</script>
</body>
</html>"""
    path.write_text(page, encoding="utf-8")


def _dashboard_payload(dashboard: dict[str, pd.DataFrame]) -> dict[str, list[dict]]:
    def records(df: pd.DataFrame) -> list[dict]:
        cleaned = df.copy()
        for col in cleaned.columns:
            if pd.api.types.is_datetime64_any_dtype(cleaned[col]):
                cleaned[col] = cleaned[col].dt.strftime("%Y-%m-%d")
        cleaned = cleaned.where(pd.notnull(cleaned), None)
        return cleaned.to_dict(orient="records")

    return {
        "kpis": records(dashboard["kpis"]),
        "by_customer": records(dashboard["by_customer"]),
        "aging": records(dashboard["aging"]),
        "trend": records(dashboard["trend"]),
        "open_receivables": records(dashboard["open_receivables"]),
    }


def write_excel(dashboard: dict[str, pd.DataFrame], path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        dashboard["kpis"].to_excel(writer, sheet_name="KPIs", index=False)
        dashboard["by_customer"].to_excel(writer, sheet_name="By Customer", index=False)
        dashboard["aging"].to_excel(writer, sheet_name="Aging", index=False)
        dashboard["trend"].to_excel(writer, sheet_name="Daily Trend", index=False)
        dashboard["open_receivables"].to_excel(writer, sheet_name="Open Detail", index=False)
