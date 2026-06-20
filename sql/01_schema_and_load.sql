-- BigQuery: create the table, then load marketing_campaign.csv via the console
-- (Create table > Upload) or the bq CLI:
--   bq load --autodetect --source_format=CSV \
--     campaign.marketing_campaign data/marketing_campaign.csv

CREATE TABLE IF NOT EXISTS `campaign.marketing_campaign` (
  customer_id     INT64,
  age             INT64,
  age_group       STRING,
  region          STRING,
  segment         STRING,
  channel         STRING,
  campaign_group  STRING,   -- 'A' = control, 'B' = personalised offer
  offer_type      STRING,
  prior_purchases INT64,
  contacted       INT64,
  opened          INT64,
  clicked         INT64,
  converted       INT64,
  revenue         FLOAT64
);
