-- Performance breakdown for segmentation, channel-mix and territory analysis.
-- Drives the segment / channel / region charts in the dashboard and the
-- cross-sell / re-engagement recommendations.

-- a) By customer segment (who to prioritise for cross-sell / up-sell)
SELECT
  segment,
  COUNT(*)                                AS recipients,
  SAFE_DIVIDE(SUM(converted), COUNT(*))   AS conversion_rate,
  SAFE_DIVIDE(SUM(revenue),  COUNT(*))     AS revenue_per_recipient,
  SUM(revenue)                            AS total_revenue
FROM `campaign.marketing_campaign`
GROUP BY segment
ORDER BY conversion_rate DESC;

-- b) By channel (where to shift budget)
SELECT
  channel,
  COUNT(*)                                AS recipients,
  SAFE_DIVIDE(SUM(opened),   COUNT(*))     AS open_rate,
  SAFE_DIVIDE(SUM(converted), COUNT(*))   AS conversion_rate,
  SAFE_DIVIDE(SUM(revenue),  COUNT(*))     AS revenue_per_recipient
FROM `campaign.marketing_campaign`
GROUP BY channel
ORDER BY conversion_rate DESC;

-- c) By region x group (territory view of the A/B lift)
SELECT
  region,
  campaign_group,
  COUNT(*)                                AS recipients,
  SAFE_DIVIDE(SUM(converted), COUNT(*))   AS conversion_rate
FROM `campaign.marketing_campaign`
GROUP BY region, campaign_group
ORDER BY region, campaign_group;
