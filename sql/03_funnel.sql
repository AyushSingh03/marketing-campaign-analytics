-- Campaign funnel: contacted -> opened -> clicked -> converted,
-- with stage conversion and overall drop-off. Split by campaign_group so you can
-- see where the personalised offer (B) widens the funnel.

SELECT
  campaign_group,
  SUM(contacted)                                       AS contacted,
  SUM(opened)                                          AS opened,
  SUM(clicked)                                         AS clicked,
  SUM(converted)                                       AS converted,
  SAFE_DIVIDE(SUM(opened),    SUM(contacted))          AS open_rate,
  SAFE_DIVIDE(SUM(clicked),   SUM(opened))             AS click_through_rate,
  SAFE_DIVIDE(SUM(converted), SUM(clicked))            AS click_to_convert_rate,
  SAFE_DIVIDE(SUM(converted), SUM(contacted))          AS overall_conversion_rate
FROM `campaign.marketing_campaign`
GROUP BY campaign_group
ORDER BY campaign_group;
