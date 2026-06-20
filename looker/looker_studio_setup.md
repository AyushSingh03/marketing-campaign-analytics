# Looker Studio dashboard — setup

The dashboard turns the SQL outputs into a one-page campaign scorecard. Two ways to build it.

## Option A — straight from the CSV (5 minutes, free)
1. Go to [Looker Studio](https://lookerstudio.google.com) → **Create → Data source → File Upload**.
2. Upload `data/marketing_campaign.csv`.
3. **Create → Report** and add these components:

| Component | Type | Setup |
|---|---|---|
| A/B conversion | Bar chart | Dimension `campaign_group`, Metric `AVG(converted)` (format %) |
| Funnel | Bar/column | Metrics `SUM(opened)`, `SUM(clicked)`, `SUM(converted)` |
| Segment performance | Table | Dimension `segment`, Metrics conversion rate + `AVG(revenue)` |
| Channel mix | Bar chart | Dimension `channel`, Metric conversion rate |
| Region map/table | Table | Dimension `region`, Metric conversion rate |
| Filters | Controls | Drop-downs on `campaign_group`, `region`, `segment`, `channel` |

Add a calculated field for conversion rate:
```
Conversion Rate = SUM(converted) / COUNT(customer_id)
```

## Option B — on BigQuery (shows the GCP + SQL stack)
1. Create dataset `campaign` and run `sql/01_schema_and_load.sql`, then load the CSV
   (`bq load --autodetect --source_format=CSV campaign.marketing_campaign data/marketing_campaign.csv`).
2. In Looker Studio choose **BigQuery** as the connector and either point at the table
   or paste a **Custom Query** from the `sql/` folder (e.g. `02_ab_test_lift.sql`).
3. Build the same components as Option A.

The PNGs in `outputs/figures/` mirror this dashboard for anyone viewing the repo without Looker access.
