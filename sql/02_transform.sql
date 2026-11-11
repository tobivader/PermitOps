CREATE OR REPLACE VIEW permitops.dim_permit_type AS
SELECT DISTINCT permit_type FROM permitops.fact_permit_lifecycle;
CREATE OR REPLACE VIEW permitops.dim_date AS
SELECT d::date AS calendar_date, extract(year FROM d)::int AS year,
       extract(month FROM d)::int AS month, date_trunc('month',d)::date AS month_start
FROM permitops.run_metadata r,
     LATERAL generate_series(date '2018-01-01', r.as_of_date, interval '1 day') d;

-- Retain every revision as a separate complete permit identifier.
-- Do not interpret these rows as unique construction projects or staff tasks.
CREATE OR REPLACE VIEW permitops.vw_study_permits AS
SELECT f.* FROM permitops.fact_permit_lifecycle f
WHERE application_date >= date '2018-01-01';
