-- Q1: Applications and valid issued reviews in complete months.
SELECT * FROM permitops.vw_monthly_performance ORDER BY month,permit_type;
-- Q2/Q3: Typical and long reviews; counts and revisions qualify comparisons.
SELECT * FROM permitops.vw_category_performance ORDER BY median_review_days DESC;
-- Q4/Q6: Investigation candidates, not proven causes or measured staff performance.
SELECT * FROM permitops.vw_bottlenecks ORDER BY severity_rank;
-- Q5: Current snapshot. Issued active permits are construction/inspection workload,
-- not necessarily waiting for initial review.
SELECT * FROM permitops.vw_active_summary ORDER BY active_unissued DESC;
-- Optional: sensitivity to original revision only; never silently trim outliers.
SELECT permit_type,count(*) AS issued,
 percentile_cont(0.5) WITHIN GROUP(ORDER BY review_days) AS median_days,
 percentile_cont(0.9) WITHIN GROUP(ORDER BY review_days) AS p90_days
FROM permitops.vw_issued_review_metrics WHERE revision_num='0' GROUP BY 1;
