-- Run after a successful pipeline. Each passed column should be true.
BEGIN TRANSACTION READ ONLY;
SELECT 'input_row_accounting' AS check_name,
 (SELECT count(*) FROM permitops.stg_active_permits) +
 (SELECT count(*) FROM permitops.stg_cleared_permits) =
 (SELECT (qa->>'quarantined_rows')::bigint + (qa->>'duplicate_rows_removed')::bigint +
         (qa->>'fact_rows')::bigint FROM permitops.run_metadata) AS passed;

SELECT 'fact_count' AS check_name, count(*) =
 (SELECT (qa->>'fact_rows')::bigint FROM permitops.run_metadata) AS passed
FROM permitops.fact_permit_lifecycle;

SELECT 'no_invalid_review_duration' AS check_name, count(*)=0 AS passed
FROM permitops.fact_permit_lifecycle
WHERE review_eligible AND (review_days IS NULL OR review_days<0 OR issued_date<application_date);

SELECT 'monthly_review_reconciliation' AS check_name,
 (SELECT sum(issued) FROM permitops.vw_monthly_performance) =
 (SELECT count(*) FROM permitops.vw_issued_review_metrics) AS passed;

SELECT 'active_workload_reconciliation' AS check_name,
 (SELECT sum(active_permits) FROM permitops.vw_active_summary) =
 (SELECT count(*) FROM permitops.fact_permit_lifecycle WHERE active_eligible) AS passed;

SELECT 'unissued_age_arithmetic' AS check_name,count(*)=0 AS passed
FROM permitops.fact_permit_lifecycle WHERE active_unissued_eligible
AND (issued_date IS NOT NULL OR active_age_days IS DISTINCT FROM as_of_date-application_date);
COMMIT;
