CREATE OR REPLACE VIEW permitops.vw_issued_review_metrics AS
SELECT * FROM permitops.vw_study_permits
WHERE review_eligible AND issued_date < date_trunc('month', as_of_date);

CREATE OR REPLACE VIEW permitops.vw_monthly_performance AS
WITH applications AS (
 SELECT date_trunc('month',application_date)::date AS month, permit_type, count(*) AS applications
 FROM permitops.vw_study_permits
 WHERE application_eligible AND application_date < date_trunc('month',as_of_date)
 GROUP BY 1,2
), issued AS (
 SELECT date_trunc('month',issued_date)::date AS month, permit_type, count(*) AS issued,
 percentile_cont(0.5) WITHIN GROUP (ORDER BY review_days) AS median_review_days,
 percentile_cont(0.9) WITHIN GROUP (ORDER BY review_days) AS p90_review_days
 FROM permitops.vw_issued_review_metrics GROUP BY 1,2
), months AS (
 SELECT DISTINCT month_start AS month FROM permitops.dim_date, permitops.run_metadata
 WHERE month_start < date_trunc('month',as_of_date)
), grid AS (SELECT month,permit_type FROM months CROSS JOIN permitops.dim_permit_type)
SELECT g.month,g.permit_type,coalesce(a.applications,0) AS applications,
       coalesce(i.issued,0) AS issued, i.median_review_days,i.p90_review_days
FROM grid g LEFT JOIN applications a USING(month,permit_type)
LEFT JOIN issued i USING(month,permit_type);

CREATE OR REPLACE VIEW permitops.vw_category_performance AS
SELECT permit_type, count(*) AS issued,
 percentile_cont(0.5) WITHIN GROUP (ORDER BY review_days) AS median_review_days,
 percentile_cont(0.9) WITHIN GROUP (ORDER BY review_days) AS p90_review_days,
 count(*) FILTER(WHERE revision_num <> '0') AS revision_records,
 count(*) FILTER(WHERE review_days > 365) AS over_365_days
FROM permitops.vw_issued_review_metrics GROUP BY 1;

CREATE OR REPLACE VIEW permitops.vw_active_workload AS
SELECT *, CASE WHEN active_age_days IS NULL THEN 'Unknown'
 WHEN active_age_days < 31 THEN '0–30'
 WHEN active_age_days < 91 THEN '31–90'
 WHEN active_age_days < 181 THEN '91–180'
 WHEN active_age_days < 366 THEN '181–365' ELSE '366+' END AS age_bucket
FROM permitops.fact_permit_lifecycle WHERE active_eligible;

CREATE OR REPLACE VIEW permitops.vw_active_summary AS
SELECT permit_type,age_bucket,count(*) AS active_permits,
 count(*) FILTER(WHERE active_unissued_eligible) AS active_unissued,
 count(*) FILTER(WHERE issued_date IS NOT NULL) AS active_with_issue_date,
 percentile_cont(0.5) WITHIN GROUP (ORDER BY active_age_days)
 FILTER(WHERE active_unissued_eligible) AS median_unissued_age_days
FROM permitops.vw_active_workload GROUP BY 1,2;

-- Equal length windows ending on last complete month. Issue cohorts, not application cohorts.
CREATE OR REPLACE VIEW permitops.vw_bottlenecks AS
WITH periods AS (
 SELECT f.*, CASE WHEN issued_date >= date_trunc('month',as_of_date)-interval '12 months'
 THEN 'recent' ELSE 'prior' END AS period
 FROM permitops.vw_issued_review_metrics f
 WHERE issued_date >= date_trunc('month',as_of_date)-interval '24 months'
), stats AS (
 SELECT permit_type,period,count(*) AS issued,
 percentile_cont(0.5) WITHIN GROUP (ORDER BY review_days) AS median_days,
 percentile_cont(0.9) WITHIN GROUP (ORDER BY review_days) AS p90_days
 FROM periods GROUP BY 1,2
), comparisons AS (
 SELECT a.permit_type,a.issued AS recent_issued,b.issued AS prior_issued,
 a.median_days AS recent_median_days,b.median_days AS prior_median_days,
 a.p90_days AS recent_p90_days,a.median_days-b.median_days AS median_change_days
 FROM stats a JOIN stats b USING(permit_type)
 WHERE a.period='recent' AND b.period='prior'
)
SELECT *, row_number() OVER(ORDER BY recent_median_days DESC, recent_issued DESC,permit_type) AS severity_rank
FROM comparisons WHERE recent_issued >= 100 AND prior_issued >= 100;

CREATE OR REPLACE VIEW permitops.vw_monthly_trend AS
SELECT *, lag(median_review_days) OVER (PARTITION BY permit_type ORDER BY month) AS prior_month_median,
 median_review_days-lag(median_review_days) OVER(PARTITION BY permit_type ORDER BY month) AS median_change_days
FROM permitops.vw_monthly_performance;
