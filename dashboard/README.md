# Power BI report build specification

For the completed Mac-friendly report, open https://permitops-operations.smalliris16.chatgpt.site . Actual web-dashboard screenshots and its three-minute screenshot-based tour are in this folder. The instructions below are the separate, optional Power BI handoff.

Status: import datasets and measures provided; no PBIX or rendered Power BI report has been built or tested. This machine runs macOS; [Power BI Desktop requires Windows](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop#minimum-requirements). This is a specification, not dashboard screenshots.

## Import and model

Run the pipeline first. Import `outputs/reporting/fact_reporting.csv`, `dim_date.csv`, and `dim_permit_type.csv` using Get Data → Text/CSV. Prefer the fact table for interactive percentiles: monthly medians must never be averaged into a period median. The aggregated exports are SQL reference results, not additional fact tables to join.

Set permit_key, permit_type and revision_num to Text (preserve leading zeros in raw IDs). Set date fields to Date, eligibility flags to True/False and durations to Whole Number. Relate dim_permit_type[permit_type] 1:* to fact_reporting[permit_type]. Relate dim_date[calendar_date] 1:* to fact_reporting[issued_date], active, with single direction filtering. Add an inactive application_date relationship. Mark dim_date as the date table.

`power_query.pq` provides named M query templates for typed imports. Create each expression as its own Blank Query, starting with the DataFolder parameter and loader function. Edit DataFolder for Windows; the Mac project path will not work in Power BI Desktop. Templates were checked against exported headers and Microsoft function documentation but have not run inside Power BI. The file is a collection of expressions, not a single query to paste whole.

For the Active Workload page, disable date slicer interaction with its visuals: dim_date starts in 2018 but active workload includes older applications. A category slicer may apply to all pages. Do not use the active issued-date relationship to filter application volume: use the provided measure. As-of date is fixed to the extract and is not a historical backlog selector.

## Page 1 — Executive Performance

Question: How much work was applied for and issued, and how long were issued reviews?

- Cards: applications, issued permits, median review days, P90 review days.
- Line chart: month_start against issuance volume. Second separate chart: median/P90 by month; show eligible count in tooltip.
- Category bar: issuance volume, sorted descending.
- Date and category slicers. Default date range: last 12 complete months; all study applications must be 2018 or later.
- Tooltip: calendar days from application to issuance; issued cohort; revisions counted separately; no official SLA implied.

## Page 2 — Review Bottlenecks

Question: Which categories merit investigation given duration, scale and trend?

- Scatter: category, issued count (X), median review days (Y), P90 tooltip.
- Table: `vw_bottlenecks.csv`, showing recent/prior issuance counts, medians, median change, P90; order by severity rank. This fixed-window SQL table is a reference panel: label its fixed dates and do not imply the date slicer recalculates it.
- Matrix or histogram of fact review_days by category; show extreme values rather than silently trimming them.
- Drill-through page or detail table: permit_key, revision_num, dates, status, review_days; category drill-through filter.
- Minimum comparative count is 100 issued records in each 12-month window, a practical stability rule rather than a statistical confidence guarantee.

## Page 3 — Active Workload

Question: What remains open, and what is waiting for issuance?

- Cards: active permits; active unissued; median age of active unissued.
- Stacked bars: age buckets by permit category; distinguish unissued and issued active permits.
- Table: active unissued IDs, application date, age and status for investigation.
- Use `vw_active_summary.csv` for a fixed snapshot reference chart, or create a calculated age-bucket column on the fact for interactive categories.
- Label: current snapshot, all application years, not historical backlog and not completed review duration. Missing ages appear as Unknown.

## Reconciliation before claiming completion

1. Clear filters; compare cards to `outputs/validation.json`, respecting the study scope.
2. Filter one month/category and compare applications, issued, median and P90 to `vw_monthly_performance.csv`.
3. Check full-period medians against `vw_category_performance.csv`; never sum or average its percentile columns.
4. Check active/unissued totals against `vw_active_summary.csv` with no issued-date filters.
5. Confirm drill-through, slicer interactions and no-data months. Export screenshots only after these checks in Power BI.
6. Test a category/month with applications but no valid issues. As Of Date must remain the global snapshot; Applications must still match SQL even when the active issue-date relationship selects no fact rows. The snapshot measure removes filter context before calculating the cutoff.

M references: [Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document), [Table.TransformColumnTypes](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes). DAX references: [REMOVEFILTERS](https://learn.microsoft.com/en-us/dax/removefilters-function-dax), [USERELATIONSHIP](https://learn.microsoft.com/en-us/dax/userelationship-function-dax).
