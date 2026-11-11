# Learn after the build

This file explains the implementation. For tested results, read `outputs/validation.json` and the build status; written code alone does not prove a successful run.

## Architecture

Toronto CKAN → immutable local CSV downloads + manifest → pandas cleaning and QA → PostgreSQL staging and permit lifecycle fact → SQL reporting views → CSV imports for Power BI.

`src/ingest.py` discovers the current datastore resource from metadata rather than relying on a hard-coded annual CSV link. It saves file size, SHA-256 hash, URL and extraction time. A hash is a fingerprint: the pipeline checks that the raw file still matches its manifest. The initial session used curl downloads; their manifest timestamps come from completed file modification times. Later downloads use the Python ingestion command.

`src/clean.py` checks required columns, trims whitespace, standardizes numeric revisions, parses dates and reports impossible intervals. It keeps invalid-date flags separate from missing dates. A blank issue date can mean waiting for issuance; an unparseable date should not be treated as evidence of an unissued permit.

## Why identity mattered

A permit number and revision should form a complete permit identifier, but the actual source contains conflicting repeated keys. A tempting approach is to keep the first row, but row order does not establish which version is correct. This build quarantines every key with a disagreement in the analytical fields: category, status or lifecycle dates. It removes repeated analytical payloads only when those fields agree. This protects against arbitrary category assignments but undercounts the affected population. Quarantine is a visible limitation, not proof the source rows are wrong. Differences in address or description are not silently described as exact full-row duplicates.

Revisions count separately. Plumbing, mechanical and building permits may relate to the same construction project. The fact table therefore counts permit/revision records, not buildings or unique applicants.

## Database and SQL

`sql/01_schema.sql` defines source staging tables and one lifecycle fact. Staging JSON preserves every raw column locally. The fact contains only fields needed for metrics. `src/database.py` loads both with PostgreSQL COPY, a bulk-transfer operation. The replacement happens in one transaction: if a load fails, PostgreSQL rolls it back instead of leaving half-loaded tables.

`02_transform.sql` builds date/category dimensions and the study view. Applications from 2018 onward are used for historical reporting because the current cleared resource starts at completions in 2017. An earlier application cohort would omit cases closed before that resource begins. Active workload keeps older applications because old open cases matter to current workload.

`03_metrics.sql` builds reusable views. GROUP BY makes one row per month/category. A full grid of dates and categories keeps zero-volume months visible. LEFT JOIN combines application and issue aggregates without losing months present in only one. CASE produces readable age buckets. CTEs break comparison logic into named steps. ROW_NUMBER ranks candidates deterministically, and LAG compares each category with its previous calendar month.

`percentile_cont(.5)` is the median; `.9` is P90. PostgreSQL interpolates between adjacent values where necessary. A 10-day P90 means roughly 90% of the eligible records took at most that duration. It is not a legal target. A median describes the middle case and is less distorted by extreme durations than an average. Large valid durations are retained, and counts accompany comparisons.

The recent/prior comparison uses two equal 12-month windows ending before the extraction month. Requiring at least 100 records per window reduces very small-group comparisons but does not establish statistical significance. These are issuance cohorts: slower unresolved cases do not yet enter review durations. This is why the separate active-unissued-age measure matters.

## Power BI handoff

Use `dashboard/README.md` and `dashboard/measures.dax`. Date and category dimensions filter the fact. Application dates and issue dates answer different questions, so the model uses separate date relationships. Medians/P90 must be computed from eligible records after filters; averaging monthly medians gives a different and usually misleading statistic. Snapshot workload must ignore issuance-date slicers. Power BI formulas are supplied but cannot be claimed verified until run in Power BI.

## Debugging lessons

Network and PostgreSQL shared memory/socket access were restricted by the execution sandbox. Permission retries distinguished environment failures from missing data or broken SQL. Do not replace a failed real-data request with invented records.

The first database COPY failed because a nullable integer column became floating-point after a pandas map. PostgreSQL correctly rejected a string such as `1282.0` for an integer. Constructing an object Series directly from Python integers and None preserves the intended representation. The transaction protected the database from partial writes. The journal records the precise failure and final verification.

Tests use deliberately synthetic small fixtures to exercise edge cases. Findings use only downloaded Toronto records. Validation compares SQL totals and category percentiles against independently grouped pandas calculations. Matching global totals alone would not prove category joins are correct.

## How to study this project

`src/charts.py` plots the validated SQL exports with matplotlib and checks their saved hashes first. It sums counts across categories, but never averages their medians. The category comparison has separate scales for median and P90, and the workload chart separates issued active permits from the unissued population. The chart provenance file records exactly which SQL export hashes were used. These PNG/SVG files are analyst charts, not screenshots of a Power BI report.

Read the business brief, then KPI definitions, the QA JSON, clean.py, the SQL files and validation.py. Run a single category query and explain its denominator before opening Power BI. Read the findings last and ask whether each recommendation follows from an observed metric rather than an assumed cause.
