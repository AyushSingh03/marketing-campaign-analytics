-- A/B test headline: conversion rate, absolute & relative lift, revenue per recipient.
-- This is the query that backs the "A/B test" scorecard in the Looker Studio dashboard.

WITH grp AS (
  SELECT
    campaign_group,
    COUNT(*)                                  AS recipients,
    SUM(converted)                            AS conversions,
    SAFE_DIVIDE(SUM(converted), COUNT(*))     AS conversion_rate,
    SAFE_DIVIDE(SUM(revenue),  COUNT(*))      AS revenue_per_recipient
  FROM `campaign.marketing_campaign`
  GROUP BY campaign_group
),
pivoted AS (
  SELECT
    MAX(IF(campaign_group = 'A', conversion_rate, NULL))       AS cr_control,
    MAX(IF(campaign_group = 'B', conversion_rate, NULL))       AS cr_treatment,
    MAX(IF(campaign_group = 'A', revenue_per_recipient, NULL)) AS rev_control,
    MAX(IF(campaign_group = 'B', revenue_per_recipient, NULL)) AS rev_treatment
  FROM grp
)
SELECT
  cr_control,
  cr_treatment,
  cr_treatment - cr_control                                   AS absolute_lift_pp,
  SAFE_DIVIDE(cr_treatment - cr_control, cr_control)          AS relative_lift,
  rev_control,
  rev_treatment,
  SAFE_DIVIDE(rev_treatment - rev_control, rev_control)       AS revenue_lift
FROM pivoted;
