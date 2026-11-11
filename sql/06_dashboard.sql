-- Frequency distributions preserve exact percentiles under interactive filters.
CREATE OR REPLACE VIEW permitops.vw_dashboard_review_distribution AS
SELECT date_trunc('month',issued_date)::date AS month,permit_type,review_days,count(*) AS records
FROM permitops.vw_issued_review_metrics GROUP BY 1,2,3;

CREATE OR REPLACE VIEW permitops.vw_dashboard_active_distribution AS
SELECT permit_type,active_age_days,count(*) AS records,
 count(*) FILTER(WHERE active_unissued_eligible) AS unissued,
 count(*) FILTER(WHERE issued_date IS NOT NULL) AS with_issue_date
FROM permitops.vw_active_workload GROUP BY 1,2;

CREATE OR REPLACE VIEW permitops.vw_new_houses_revision_analysis AS
WITH cases AS (
 SELECT *,CASE WHEN issued_date >= date_trunc('month',as_of_date)-interval '12 months'
 THEN 'Recent' ELSE 'Prior' END AS period,
 CASE WHEN revision_num='0' THEN 'Original (0)'
 WHEN revision_num='1' THEN 'Revision 1' ELSE 'Revision 2+' END AS revision_group
 FROM permitops.vw_issued_review_metrics WHERE permit_type='New Houses'
 AND issued_date>=date_trunc('month',as_of_date)-interval '24 months'
)
SELECT period,revision_group,count(*) AS issued,
 percentile_cont(.5) WITHIN GROUP(ORDER BY review_days) AS median_days,
 percentile_cont(.9) WITHIN GROUP(ORDER BY review_days) AS p90_days,
 count(*) FILTER(WHERE review_days>365) AS over_365,
 max(review_days) AS max_days
FROM cases GROUP BY 1,2;

CREATE OR REPLACE VIEW permitops.vw_new_houses_quarter_analysis AS
SELECT date_trunc('quarter',issued_date)::date AS quarter,count(*) AS issued,
 percentile_cont(.5) WITHIN GROUP(ORDER BY review_days) AS median_days,
 percentile_cont(.9) WITHIN GROUP(ORDER BY review_days) AS p90_days,
 count(*) FILTER(WHERE review_days>365) AS over_365
FROM permitops.vw_issued_review_metrics WHERE permit_type='New Houses'
AND issued_date>=date_trunc('month',as_of_date)-interval '24 months'
GROUP BY 1;
