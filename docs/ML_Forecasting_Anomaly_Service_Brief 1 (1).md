

## 1. Summary

NEPA is a wholesale distributor. Its platform (a Python/FastAPI backend, a React web app, Postgres) holds roughly three years of invoice history, current stock levels and a customer master. Today every "intelligent" feature is a **rule or a simple statistic**: fixed day-count thresholds, week-over-week percentage changes, z-scores and item-item collaborative filtering. No learned model is in production.

Your job is to build a **separate, standalone ML service** in your own repository that learns from that history and returns numbers the platform can use:

| # | Deliverable | Replaces / improves | Priority |
|---|---|---|---|
| A | KPI forecasting + anomaly scoring ("expected vs actual, how unusual") | Hand-set week-over-week thresholds | **1 — start here** |
| B | Product x warehouse demand forecasting | Fixed day-count stock rules (Appendix B) | 2 |
| C | Customer next-order / churn prediction | Rule-based dormancy buckets and spend-drop z-score | 3 |
| D | Learned recommendations | Item-item collaborative filtering | 4 (optional) |

The outputs of A feed an **LLM-written weekly executive brief** (built by the platform team, section 9). The LLM only writes prose; **every number comes from your service or from SQL**.

**Explicit non-goals:** training or hosting your own large language model; using a model to write SQL; anything that writes to the sales, stock or customer tables.

---

## 2. How your work fits in

- You build and deploy a **standalone HTTP service** (suggested: FastAPI). The platform's backend calls it; you never import platform code and it never imports yours.
- The **only coupling** is (1) read access to the database and (2) the HTTP contract in section 8.4. Keep the contract stable and versioned.
- Framework choice is yours (PyTorch or TensorFlow). The platform is Python 3.11; the service is CPU-friendly (the data is small, section 3.1).
- The platform's own backend is FastAPI + SQLAlchemy, with React on the front end. You do not need to touch either.

---

## 3. Access and credentials

You will be given:

1. **Database credentials** for the primary Postgres database.
2. **NEPAX credentials** (`NEPAX_BASE_URL`, `NEPAX_TENANT_ID`, `NEPAX_API_KEY`). NEPAX is the platform's internal AI gateway: one instance serves an LLM gateway under `/llm/v1/*` and an agent orchestrator at `/agents/execute`, scoped per tenant and API key. **You do not need NEPAX for deliverables A to C.** It is only relevant if you later prototype the narrative step of section 9, or if the platform team asks you to call it. Ask what the rate limits and allowed models are before building on it. (This brief only knows the endpoints above; ask the platform team for the exact request formats.)

Handling rules:

- **Treat the database as read-only, always.** Ideally the platform team gives you a dedicated **read-only role** (`SELECT` only). If you were given a general application credential instead, ask for a read-only one before you start; do not use a credential that can write.
- **Never run schema changes, inserts, updates or deletes** on the platform database. If you need somewhere to store your own tables (forecasts, snapshots, model metadata), use **your own database**, not theirs.
- The database contains real customer and financial data. Do not copy raw data to personal machines, third-party services or public repos. Do not commit credentials or data extracts; use environment variables and a `.gitignore`d `.env`. Keep any local extracts to the minimum you need.
- Connect from an approved network/IP only (ask if a firewall blocks you).
- Rotate or return credentials when the engagement ends.
- Heavy queries: the database serves the live application. Run large scans off-peak, use `LIMIT` while exploring, prefer date-bounded queries, and use one connection (not many parallel ones). Extract once to your own store, then train from that.

---

## 4. The data

All tables below are in the primary database. Data is mirrored from **Odoo**, the ERP, so table names follow Odoo conventions.

### 4.1 Volumes (dev DB, read 2026-09-19)

| Thing | Value |
|---|---|
| Invoice headers (`account_move_sales`) | 311,013 rows, `invoice_date` from 2023-11-12 (see 4.6 on future dates) |
| Invoice lines (`account_move_sales_line`) | about 16.4 million rows |
| Document types | 285,343 `out_invoice`, 25,670 `out_refund` |
| Distinct billed customers | 7,278 |
| Products (`product_product`) | about 35,400 |
| Stock rows (`stock_quant`) | about 171,000 |
| Warehouses (`stock_warehouse`) | 31 rows (4.4) |
| Typical monthly invoice volume | 11,000 to 13,500 headers per month in 2026 |

That is small enough to train on a laptop CPU. A GPU is not needed for any deliverable here.

### 4.2 Core tables and columns

**`account_move_sales`** (invoice header, 39 columns). Key columns: `id`, `invoice_date` (date), `state` (use `'posted'`), `move_type` (`out_invoice` / `out_refund`), `partner_id` (customer), `journal_id` and `company_id` (together they identify the warehouse, see 4.4), `amount_total_signed`, `amount_untaxed_signed`, `payment_state`, `net_commission`, `write_date`.

**`account_move_sales_line`** (invoice line, 28 columns). Key columns: `move_id` (join to header `id`), `product_id`, `quantity`, `price_unit`, `price_subtotal`, `nepa_cogs_price` (the **total** line cost, not a unit cost) and `standard_price`, `discount`, `account_id` (the revenue-account filter). **Do not use the line's own `partner_id`, `company_id`, `date` or `account_move_id`**: the first three are 84% NULL and `account_move_id` has been 100% NULL since May 2026; join lines to headers on `move_id` and take customer, company and date from the header.

**`product_product`**: `id`, `display_name`, `name`, `default_code`, `barcode`, `categ_id`, `lst_price`, `standard_price`, `qty_available`, `active`, `sale_ok`.

**`stock_quant`**: `product_id`, `location_id`, `location_name`, `location_usage`, `quantity`, `reserved_quantity`, `available_quantity`, `value`, `company_id`, `write_date`. This is a **current snapshot only** (4.6, item 5). Warehouse ownership of a location: see 4.5.

**`res_partner`** (customers): `partner_id` (**not** `id`), `display_name`, `nepa_customer_type`, `city`, `state_id`, `user_id` (assigned sales rep), `create_date`, `nepa_last_invoice_date`, `partner_latitude`, `partner_longitude`.

**`sale_order`**: `date_order`, `state`, `partner_id`, `warehouse_id`, `amount_total`, `user_id` (rep). Sale orders are **not** invoices. `invoice_status` is unreliable, `name` is often NULL (use `display_name`), and returns appear as negative amounts.

**`stock_warehouse`**: `id`, `name`, `code`, `company_id`, `active`, `lot_stock_id`.

**Pre-aggregated views** (faster, but check freshness first):

| View | Grain | Data through (read 2026-09-19) |
|---|---|---|
| `mv_sales_product_day` | product x day | 2026-09-03 |
| `mv_sales_lines_enriched` | invoice line | **2026-04-24, about five months stale. Do not train on it.** |
| `mv_partner_day` | partner x day | inspect its column names before use |

### 4.3 The canonical revenue definition (must match production exactly)

The platform's dashboards compute sales like this. Any target you build must agree, or your numbers will not match what the business sees.

```sql
FROM account_move_sales ams
JOIN account_move_sales_line amsl ON amsl.move_id = ams.id
WHERE ams.state = 'posted'
  AND ams.partner_id NOT IN (15436,1,55657,56001,65388,54176,76773,15310,
                             23364,15308,54095,15421,15,54568,62331)   -- sister companies
  AND amsl.account_id IN (24,636,684,822,1085,1158,1982,205)          -- revenue accounts
```

- **Revenue** = `SUM(amsl.price_subtotal)` over the rows above.
- **Returns:** rows whose header has `move_type = 'out_refund'` are returns and are multiplied by **-1** so net revenue is correct.
- **Order count** = distinct posted `out_invoice` headers passing the same filters.
- **Sister companies** (the excluded partner ids) are related NEPA entities. Forgetting the exclusion inflates every volume.
- These two id lists **change over time** (accounts 664 and 3310 were removed on 2026-05-22). Keep them in one config file in your code, with the date you last confirmed them, and ask the platform team to reconfirm before each release.
- **Margin** = `price_subtotal - nepa_cogs_price` with the same return sign flip (`nepa_cogs_price` is the total line cost; do **not** multiply it by quantity). For the reference week below it gives 7.0%, identical to the platform's `mv_partner_day`.
- **Reconciliation is mandatory in week 1.** Reference figures from the dev database for the Sunday-to-Saturday week 2026-08-09 to 2026-08-15 (posted, sister companies excluded, revenue accounts only): **all journals 5,778,426.72** net revenue (5,681,438.37 across warehouses plus 96,988.35 across vans) and cost 5,375,833, margin 7.0%. Per-warehouse figures are in `Sales_Customer_Data_Schema.md` section 7.4. Your reproduction must match to the cent; a difference is a question for the platform team, not something to work around.
- **Companion documents:** `Sales_Customer_Data_Schema.md` (every table you need, joins, tested queries) and `NEPAX_LLM_Gateway_Guide.md` (calling the LLM gateway).

### 4.4 Warehouses, journals and vans

The 31 `stock_warehouse` rows include real warehouses, sister-company entities and **vans** (delivery routes). Sales are assigned to a warehouse by **journal**, not by a warehouse column:

| Warehouse id | Meaning | Journal id |
|---|---|---|
| 3 | NEPA 1 | 29 |
| 14 | LEEPER | 149 |
| 26 | NEPA 1 Van (retired 2026-05-12, historical only) | 332 |
| 27 | NEPA 305 Van (company 1) | 351 |
| 28 | NEPA 954 Van (company 17) | 354 |
| 29 | NEPA 2 Van (DB name "VAN N2", company 4) | 375 |
| 30 | NEPA 407 Van (company 12) | 379 |
| 31 | NEPA Dallas Van (company 5) | 405 |

Rules:

- **Van journals** are exactly: 332, 351, 354, 375, 379, 405. Vans share a `company_id` with a physical warehouse, so **vans must be separated by `journal_id`, never by company**.
- **Every other warehouse** is resolved through its company **and** the journal must not be a van journal (that stops a physical warehouse absorbing its own vans' sales).
- The database already contains this mapping in the table **`warehouse_sales_scope(warehouse_id, scope_type, journal_id, company_id)`** (`scope_type` is `journal` or `company`). Use it. The companion document `Sales_Customer_Data_Schema.md` has its full contents and a query that joins it. **Do not use `journal_warehouse_map`**: it is a legacy table that maps van journals onto physical warehouses and contradicts these rules.
- **Company-wide totals exclude vans by default**; views that attribute sales to reps include them. This is a business choice, not a technical one. **Agree with the business owner which population each model uses and write it down** (open question 1).
- Selecting a warehouse and its van together must sum, not double-count; the rules above guarantee that.
- Journal 379 (NEPA 407 Van) has historically been the easiest to lose; check any van-inclusive total against a known figure.

### 4.5 Stock by warehouse

`stock_location.complete_name` is **not unique** (all vans are called `VAN/Stock`; ten NEPA-named companies are `NEPA /Stock`). Do **not** match locations by name. Ownership is resolved by ID. The platform maintains a database function for this, `fn_warehouse_location_ids(int[])` (returns `location_id, warehouse_id`); check whether it exists in your database (`\df fn_warehouse_location_ids`). If it does, use it. If it does not, ask the platform team, because a name-based join will double count and leak stock between warehouses (it overstated van stock by about 3.9x).

### 4.5a Existing baselines already in the database

The platform already produces simple forecasts and risk scores. They are the numbers your models must beat, and you can read them directly:

- `clearo_forecasts`: monthly demand forecast per product template x warehouse (Holt linear smoothing, with `lower_bound` / `upper_bound`; last fitted 2026-09-12). Baseline for Deliverable B.
- `radar_pair` (per customer x product: `median_gap`, `overdue_ratio`, `p_lapse`, `signal`), `radar_customer` (`status`, `trend_z`, `at_risk_value`) and `radar_opportunity` (`affinity`, `expected_value`). Baselines for Deliverables C and D.

### 4.6 Known data problems (each one has already caused wrong numbers)

0. **Join key trap.** `account_move_sales_line.account_move_id` has been NULL on every new line since May 2026 and several platform views join on it, so they return nothing recent. Always join lines to headers on `move_id`.
1. **Future-dated invoices.** `MAX(invoice_date)` is 2026-11-17 while today in the dev environment is 2026-09-19 (a handful of rows in October and November 2026). Clip or drop them. Never take "now" from `MAX(invoice_date)` without filtering.
2. **Anchor on the data frontier, not on today.** Some sources lag. Training and scoring windows must end at the last **complete** day of data, and your responses must state the "data through" date.
3. **December 2025 looks thin** (about 4,600 invoice headers versus about 13,000 in a normal month). It may be a real gap or an outage. Investigate before using it as a training month, and consider masking it.
4. **`mv_sales_lines_enriched` is about five months stale.** Use the raw tables, or `mv_sales_product_day` after checking its end date.
5. **No stock history.** Stock-movement sync (`stock_picking`, `stock_move_line`) has been dead since 2026-06-03, and `stock_quant` is only the current snapshot. Derive demand from **sales**, not from stock moves. Start a **daily snapshot of `stock_quant` into your own database on day one**; it is the only way to get stock history going forward. Also, purchase-line history stopped in April 2025 in one source table, so do not rely on it for inbound.
6. **Time zones.** Business days are **New York (Florida) time**. The production server runs in UTC, but `invoice_date` is already aligned to New York days. Business weeks are **Sunday to Saturday**, never Saturday to Friday.
7. **Returns** are separate documents. Forgetting the sign flip inflates revenue.
8. **`res_partner` key is `partner_id`**, not `id`.
9. **Product names are not clean.** Substring matches like `%raz%` hit other brands. Prefer ids and categories. The category tree stores `parent_name` empty on child rows; build the hierarchy from parent ids.
10. **Sale-order data traps** (if you use `sale_order`): `name` is NULL (use `display_name`), `invoice_status` lies, returns are negative.

---

## 5. Deliverable A — KPI forecasting and anomaly scoring (start here)

### 5.1 Goal

For each tracked KPI and slice, output **what we expected, what happened, and how unusual the gap is**. This is what lets the weekly brief say "revenue at NEPA DALLAS was 18% below expected and this is the largest miss this year" instead of a raw week-over-week percentage.

### 5.2 KPIs (initial scope)

| KPI | Definition | Slices |
|---|---|---|
| Net revenue | 4.3 formula, returns signed negative | company-wide, per warehouse |
| Order count | distinct posted `out_invoice` headers | company-wide, per warehouse |
| Returns value and rate | `out_refund` value, and refund value divided by invoice value | company-wide, per warehouse |
| Units sold | `SUM(quantity)` | company-wide, per top-N category |
| Active customers | distinct `partner_id` with a posted invoice | company-wide, per warehouse |

Later: gross margin, per-rep revenue, per-category revenue.

### 5.3 Granularity and horizon

Daily series with weekly roll-ups (Sunday to Saturday). Forecast the next 1 to 4 weeks, and always score the **most recent complete day and week** against what the model expected for it.

### 5.4 Modelling guidance

The history is about 34 months, so each series is short. Start simple and earn complexity:

1. **Baselines first** (they must exist before any neural model): last-year-same-week, trailing 4-week mean, and a day-of-week seasonal naive. Every later model is judged against them.
2. **Statistical / boosting:** ETS or STL, or gradient-boosted trees on calendar and lag features.
3. **Deep learning (PyTorch or TensorFlow):** a **global** model across slices (one network, slice embedding as input), for example a small LSTM/GRU, N-BEATS or a Temporal Fusion Transformer with **quantile outputs**. Global models usually beat per-series models when each series is short.
4. **Calendar features:** day of week, US holidays, month start/end, known promotions or closures (no single list of these exists today; ask the business).
5. **Anomaly score:** the standardized residual, or where the actual falls in the predicted quantile interval, expressed as a 0 to 1 "how unusual" value.

### 5.5 Evaluation protocol (non-negotiable)

- **Rolling-origin backtest:** train up to week T, forecast T+1 to T+4, move T forward, repeat over at least the last 26 weeks. No random train/test splits on time series.
- Metrics: WAPE and sMAPE for point accuracy; pinball (quantile) loss and interval coverage for probabilistic accuracy. Report per slice.
- **Ship gate:** beats the seasonal-naive baseline on WAPE for at least 80% of slices, and the 80% prediction interval covers between 70% and 90% of actuals.
- **Anomaly quality:** produce the top 20 flagged weeks and have a business owner label which were real events. Precision on that list matters more than any aggregate metric.

---

## 6. Deliverable B — Product x warehouse demand forecasting

### 6.1 Goal

Forecast weekly units per (product, warehouse) so reorder and overstock decisions use predicted demand rather than fixed day-count rules.

### 6.2 Baseline to beat (the current rules)

See Appendix B: low stock = under 5 days of average daily sales cover; overstock = over 120 days of supply; slow mover = 30 days of zero sales; an inventory lifecycle with 28 / 42 / 56 day gates.

### 6.3 Modelling guidance

- Demand is **sparse and intermittent** for most of the roughly 35,000 products. Use Croston/TSB as baselines, then a global model with a count-appropriate output (Tweedie or negative binomial).
- Share strength across product families using the category hierarchy (4.6 item 9).
- Include price, discount and stock-out signals. Beware **censored demand**: zero sales during a stock-out is not zero demand. Only the current stock snapshot exists (4.6 item 5), so start snapshotting now.
- Version 1: only the top products by revenue (for example the ones covering 80% of revenue), then expand.

### 6.4 Evaluation

Backtest as in 5.5. Also simulate the decision: given your forecast, would a reorder policy have produced fewer stock-outs or less overstock than the current rules over the same period? That comparison, not raw accuracy, is what the business cares about.

---

## 7. Deliverable C — Customer next-order and churn prediction

### 7.1 Goal

Per customer, predict when they will order next and the probability they lapse, so sales reps get a ranked "who is about to slip" list.

### 7.2 Baseline to beat

Today customers are put into tiers (warm prospect / alert / cooling / at-risk / churned) by comparing **days since last order** with **their own average gap between orders**, for example "at least the average gap plus 5 days" (Appendix B has the details as far as they are known). A separate spend-drop z-score flags falling spend. Dormancy buckets: **slow** = 3 to 12 months without an order, **dead** = 12+ months.

### 7.3 Modelling guidance

- Frame as **time-to-event** (a discrete-time hazard model, or a sequence model over order history), or as classification with a fixed horizon ("orders in the next 30 days?").
- Features: recency, frequency, monetary value, mean and variance of inter-order gaps, category mix, spend trend, returns rate, assigned rep, customer type, geography.
- **Leakage warning:** compute features only from data strictly before the prediction date. Build datasets with an explicit `as_of_date`.
- Churn and at-risk states are computed network-wide, while "membership" is warehouse-scoped. Ask before combining them.

### 7.4 Evaluation

Point-in-time backtest: choose several historical `as_of` dates, predict, and check against what actually happened in the following 30, 60 and 90 days. Report AUC, precision at top-K (K = a plausible rep call list, for example 50) and calibration. Compare with the rule-based labels on the same dates.

---

## 8. Service design

### 8.1 Your repository (suggested layout)

```
ml-service/
  pyproject.toml          # dependencies, pinned; CPU-only wheels are fine
  README.md
  .env.example            # variable names only, never values
  app/
    main.py               # FastAPI app
    api/                  # routers
    data/                 # SQL + dataset builders (ONE place holds the 4.3 definition)
    models/               # network definitions, training loops
    jobs/                 # scheduled training and scoring
    core/                 # settings, auth, logging
  artifacts/              # trained weights + metadata (or object storage)
  tests/
  docs/
```

### 8.2 Authentication

The platform's backend calls your service. Use a **static service key** (sent in a header such as `X-API-Key`) that you generate and share with the platform team over a secure channel. **Do not ask for, and do not use, the platform's JWT signing secret**; your service never needs to issue or verify user tokens. Add a rate limit and reject unknown keys with 401. The service must not be reachable from the public internet unless the platform team asks for that.

### 8.3 Storage

Use **your own database** (a small Postgres instance) for forecasts, model metadata and the daily stock snapshot. The platform database is read-only for you (section 3).

### 8.4 API contract (proposal, to finalize with the platform team)

All endpoints under `/api/v1/ml`. Dates are ISO `YYYY-MM-DD`; weeks start on Sunday; amounts are USD.

`GET /kpi/forecast?kpi=net_revenue&warehouse_id=5&horizon_weeks=4`

```json
{
  "kpi": "net_revenue",
  "slice": {"warehouse_id": 5},
  "model_version": "kpi-global-2026-09-20",
  "data_through": "2026-09-13",
  "points": [
    {"week_start": "2026-09-20", "p10": 41200.0, "p50": 48900.0, "p90": 57300.0}
  ]
}
```

`GET /kpi/anomalies?week_start=2026-09-13&min_score=0.9`

```json
{
  "week_start": "2026-09-13",
  "data_through": "2026-09-19",
  "items": [
    {
      "kpi": "net_revenue",
      "slice": {"warehouse_id": 5},
      "actual": 39100.0,
      "expected_p50": 48200.0,
      "gap_pct": -18.9,
      "unusualness": 0.97,
      "direction": "below"
    }
  ]
}
```

`GET /demand/forecast?product_id=123&warehouse_id=5&horizon_weeks=4` returns a weekly quantile forecast, same shape as the KPI forecast.

`GET /customers/risk?warehouse_id=5&top=50` returns ranked customers with `p_lapse_30d`, `p_lapse_90d`, `expected_days_to_next_order`, and the two or three features that drove the score.

`GET /health` and `GET /models` (model versions, training date, data-through date, backtest metrics).

### 8.5 Training and scoring

- Scheduled retraining (weekly for A and B) and daily scoring, with cron or APScheduler.
- Every model version records: training window, data-through date, code version, backtest metrics. Never silently overwrite an artifact; keep the previous version for rollback.
- Scoring anchors on the last complete day of data (4.6 item 2). If the source data is stale, report that in `/models` and in every response, rather than scoring stale input as if it were fresh.

### 8.6 Deployment

Package as a container with its own resource limits (training must never share resources with the live application). Where it runs, and who owns deployment credentials, is an open question (section 12).

---

## 9. How the LLM weekly brief uses your output

The platform team builds this part; you provide the numbers.

1. Your `/kpi/anomalies` and `/kpi/forecast` supply "expected versus actual" and the unusualness score.
2. The platform runs SQL drill-downs (by product, rep, customer) for each flagged item.
3. A language model receives **only finished numbers** and writes the narrative. It never writes SQL and never computes figures.
4. An evaluation set with fixed known numbers guards against a prompt change silently altering figures.

For you this means the response fields in 8.4 are a **contract**. Keep them stable, versioned and documented.

---

## 10. Milestones and acceptance criteria

| Milestone | Scope | Done when |
|---|---|---|
| M0, onboarding (week 1) | Read-only access confirmed, reproduce net revenue for one warehouse-week from raw tables, start the daily `stock_quant` snapshot | The reproduced number matches the business's dashboard figure; each item in 4.6 confirmed or corrected |
| M1, baselines | Dataset builder, naive/ETS baselines, rolling-backtest harness for the KPIs | Backtest report exists for all KPIs x slices |
| M2, KPI model | Global neural quantile model plus anomaly score | Meets the ship gate in 5.5; top-20 anomaly list reviewed by a business owner |
| M3, service | HTTP service with the 8.4 endpoints, service-key auth, scheduled retrain and score, container | The platform team can call it from the dev environment; `/models` shows metrics |
| M4, demand model | Section 6 for the top products | Decision simulation beats the current rules |
| M5, customer risk | Section 7 | Precision at 50 beats the rule-based list on point-in-time backtest |
| M6, optional | Recommendations | Beats item-item collaborative filtering on hit-rate at K |

Critical path: M0, M1, M2, M3. B and C can run in parallel after M3 if a second person is available.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Numbers differ from the business's dashboards | One shared dataset builder implementing 4.3; reconcile in M0 |
| Data gaps (Dec 2025, stale views, dead stock sync) | Explicit data-quality checks in the pipeline; mask or flag suspect periods; report data-through dates |
| Overfitting on about 34 months | Simple baselines first, global models, rolling-origin evaluation, strict ship gates |
| Leakage in customer models | Mandatory `as_of_date` in every feature query; review by a second person |
| Business rules drift (excluded partners, revenue accounts, van journals) | Single config file with dates; ask the platform team to reconfirm before each release; a fixed-sample test that fails if your revenue differs from the reference |
| Load on the live database | Read-only role, off-peak extracts, extract once and train from your own store |
| Users trusting a wrong model | Show uncertainty (quantiles) and the data-through date; keep the previous model for rollback |
| Credential leakage | Env vars only, no credentials or data in git, least-privilege role, rotate on exit |

---

## 12. Open questions (to settle with the platform and business owners)

1. Which population is "company-wide": with or without vans? Decide per model and document it.
2. Is there a record of promotions, price changes, holidays or closures usable as features?
3. Was December 2025 a real dip or a sync gap? Can it be backfilled?
4. What is the exact gross-margin definition?
5. Who consumes the outputs first (the weekly brief, sales reps, inventory planning), and how fast do they need them?
6. Where does the service run, and who owns its deployment credentials?
7. Does the platform team want the forecasts written back into their database (they would create the tables) or only served over HTTP?
8. NEPAX: which models and rate limits apply, and is it in scope for this project at all?
9. Confirm the reference figures for the M0 reconciliation (which warehouse and week, and the expected net revenue).

---

## 13. First-week checklist

- [ ] Confirm access: read-only DB role works; NEPAX reachable (if needed); keep credentials in environment variables only.
- [ ] Get the M0 reference figure from the platform team.
- [ ] Reproduce one week of net revenue for one warehouse from raw tables and match it.
- [ ] Profile the data problems in 4.6 yourself and confirm or correct each.
- [ ] Set up your own database and the daily `stock_quant` snapshot.
- [ ] Write the rolling-backtest harness with the naive baselines before any neural model.
- [ ] Stand up `/health` for your service in your own repo.

---

## Appendix A — Definitions you must reproduce

### A.1 Net revenue, orders, customers

See 4.3. Canonical filters: posted only; exclude sister-company partner ids; revenue accounts only; returns negative.

### A.2 Warehouse assignment of a sale (pseudocode)

```
def warehouse_of(header):                      # header = account_move_sales row
    if header.journal_id in VAN_JOURNAL_TO_WAREHOUSE:      # 332,351,354,375,379,405
        return VAN_JOURNAL_TO_WAREHOUSE[header.journal_id] # 26..31
    if header.journal_id == 149:  return 14                # LEEPER
    if header.journal_id == 29:   return 3                 # NEPA 1
    # everything else: by company
    return stock_warehouse where company_id == header.company_id   # non-van journals only
```

SQL for "sales of warehouse set W (non-van warehouses resolved by company)":

```sql
( ams.company_id IN (SELECT company_id FROM stock_warehouse WHERE id IN (:other_ids))
  AND ams.journal_id NOT IN (332,351,354,375,379,405) )
OR ams.journal_id IN (:journals_of_journal_mapped_or_van_warehouses_requested)
```

### A.3 Van and warehouse reference

Van warehouses: 27, 28, 29, 30, 31 are selectable; 26 is retired (historical rows only, kept out of NEPA 1's total). Display names: 26 NEPA 1 Van, 27 NEPA 305 Van, 28 NEPA 954 Van, 29 NEPA 2 Van, 30 NEPA 407 Van, 31 NEPA Dallas Van.

---

## Appendix B — Existing rule thresholds (your baselines)

| Rule | Value |
|---|---|
| Low stock | less than 5 days of average daily sales cover |
| Overstock | more than 120 days of supply |
| Slow mover | zero sales for 30 days |
| Trending up / down | week-over-week change above 50% |
| Sudden drop | week-over-week decline above 80% |
| Inventory lifecycle gates | 28, 42 and 56 days |
| Customer tiers | days since last order versus the customer's own average gap between orders (about "average gap + 5 days" for cooling); warm prospect = no order yet and created under 14 days ago |
| Dormancy | slow = 3 to 12 months; dead = 12+ months |

These numbers come from the current application and can change; they define what "the current system does", so your models are judged against them.

---

## Appendix C — Business time

- Business day boundaries and reporting use **New York (Florida) time**.
- Weeks run **Sunday to Saturday**. In SQL: `(date_trunc('week', d::timestamp + interval '1 day') - interval '1 day')::date`.
- The application server runs in UTC, but invoice dates are already New York days; do not shift them again.
- The working week for staff is Monday to Saturday; Sunday is off (matters only for HR-style features, not for sales).

---

## Glossary

- **Odoo:** the ERP the data is synced from.
- **Sister companies:** related NEPA entities excluded from sales analytics by partner id.
- **Vans:** delivery-route "warehouses" with their own journals.
- **Journal:** an accounting ledger; here it is what ties an invoice to a warehouse or van.
- **Data frontier / data-through date:** the last date for which data is complete; scoring anchors here, not on today.
- **NEPAX:** the platform's internal AI gateway (LLM gateway plus agent orchestrator).
- **WAPE / sMAPE:** weighted absolute percentage error / symmetric mean absolute percentage error.
- **Pinball loss:** the loss for training and scoring quantile forecasts.
