CREATE SCHEMA IF NOT EXISTS permitops;
CREATE TABLE IF NOT EXISTS permitops.run_metadata (
    singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
    as_of_date date NOT NULL, manifest jsonb NOT NULL, qa jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS permitops.stg_active_permits (
    source_dataset text NOT NULL, source_row_id text NOT NULL,
    permit_key text NOT NULL, payload jsonb NOT NULL,
    PRIMARY KEY (source_dataset, source_row_id)
);
CREATE TABLE IF NOT EXISTS permitops.stg_cleared_permits
    (LIKE permitops.stg_active_permits INCLUDING ALL);
CREATE TABLE IF NOT EXISTS permitops.fact_permit_lifecycle (
    permit_key text PRIMARY KEY, permit_num text NOT NULL, revision_num text NOT NULL,
    permit_type text NOT NULL, status text NOT NULL, source_dataset text NOT NULL,
    source_row_id text NOT NULL, application_date date, issued_date date, completed_date date,
    as_of_date date NOT NULL, application_eligible boolean NOT NULL,
    review_eligible boolean NOT NULL, active_eligible boolean NOT NULL,
    active_unissued_eligible boolean NOT NULL, completion_eligible boolean NOT NULL,
    review_days integer, active_age_days integer, completion_days integer,
    CHECK (NOT review_eligible OR review_days >= 0),
    CHECK (NOT active_unissued_eligible OR issued_date IS NULL)
);
