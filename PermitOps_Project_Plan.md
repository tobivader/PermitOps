# PermitOps — Toronto Building Permit Operations Analytics

**Project type:** End-to-end Data Analyst portfolio case study  
**Duration:** 4 weeks  
**Primary tools:** Python (pandas), PostgreSQL, SQL, Power BI, Git/GitHub  
**Stakeholder:** Hypothetical municipal operations manager  
**Status:** Planning; conclusions and dataset assumptions must be validated with real data.

## 1. Executive Brief

### Business problem
A municipal operations team needs a reliable way to monitor building permit volumes, application-to-issuance review times, active workload, and differences across permit categories. The team wants to identify persistent process bottlenecks and prioritize workflow investigations based on evidence.

### Decision to support
**Which permit categories show unusually long or worsening processing times, and which should operations investigate first?**

### Deliverables
1. Reproducible data-cleaning/validation pipeline in Python.
2. PostgreSQL analytical tables and documented SQL metric views.
3. A three-page interactive Power BI report.
4. A one-to-two-page findings and recommendations report.
5. Public GitHub repository containing scripts, documentation, SQL and dashboard screenshots (not confidential or unnecessary raw files).

## 2. Verified public data sources

- Active permits: https://open.toronto.ca/dataset/building-permits-active-permits/
- Cleared permits: https://open.toronto.ca/dataset/building-permits-cleared-permits/
- City's analysis and feature explanations: https://open.toronto.ca/exploring-cleared-building-permits/
- Optional geographic reference: Toronto Open Data Address Points / ward boundaries, only if location analysis is practical.

**Source note:** The City explains that active permits are not yet closed, while cleared permits are completed/closed. Application Date, Issued Date and Completed Date can support different lifecycle intervals. Permit Num plus Revision Num identifies the complete permit number. The City also notes historical classification changes, so avoid naive cross-era comparisons.

## 3. Research Questions (prioritized)

### Must answer
1. How many permits are applied for and issued each month, by permit type?
2. What is the median and 90th percentile number of days between application and issuance?
3. Which permit types have the longest review times after accounting for volume and outliers?
4. Are review times improving or worsening over time within comparable categories?
5. How old is the active permit workload, and which categories dominate it?
6. Which 2–3 categories should a manager investigate first, and why?

### Optional if data and time allow
7. How does issuance-to-completion time differ by permit type?
8. Are there meaningful geographic differences once locations are validated?
9. How sensitive are conclusions to revision handling, outliers and the chosen date range?

### Out of scope
- Claiming a specific cause of municipal delays from timestamps alone.
- Measuring staff productivity without staffing/case assignment data.
- Calling application-to-issue elapsed time a legal SLA without a documented standard.
- Treating active permits as if their final review/inspection times are known.
- Building an ML prediction system or complex web application.

## 4. Initial KPI Definitions (validate against source dictionary)

| Metric | Draft formula | Important caveat |
|---|---|---|
| Permit volume | Count of distinct complete permit IDs | Determine whether revision is part of analytical grain. |
| Median review days | Median(Issued Date - Application Date) | Issued cases only; missing/invalid dates excluded and counted in QA. |
| P90 review days | 90th percentile of review days | Clarify time window and sample size. |
| Review-age of active unissued permits | As-of date - Application Date | Separate from issued review duration. |
| Active permit count | Count of currently active distinct permit IDs | Snapshot-based, not historical backlog reconstruction. |
| Inspection/completion days | Completed Date - Issued Date | Only for valid completed cases. |
| Monthly issuance trend | Permits issued per month | Compare months with similar completeness. |

Use **calendar days** unless a business-day calendar is explicitly implemented and documented. Store extract timestamp and metric definitions.

## 5. Source Validation: first milestone before any dashboard

- [ ] Obtain source files or accessible API data and record retrieval date.
- [ ] Confirm exact field names, types and status values.
- [ ] Profile row counts, date range, unique permit identifiers, missingness and duplicate records.
- [ ] Examine whether permit revisions create multiple rows for one application.
- [ ] Identify impossible date sequences and anomalous durations.
- [ ] Decide how cancelled permits and missing dates affect each KPI.
- [ ] Check overlap between active and cleared sources and define precedence.
- [ ] Select a comparable study period; document category/classification changes.
- [ ] Produce `docs/data_dictionary.md` and `docs/data_quality_report.md`.

**Go/no-go rule:** Do not implement the planned KPIs until the columns and case grain have been validated. If the source structure changes, revise the metric plan rather than inventing fields.

## 6. Suggested Data Model

Raw/staging tables:
- `stg_active_permits`
- `stg_cleared_permits`

Analytics tables/views (final names depend on the source):
- `dim_permit_type` — normalized type/category labels
- `dim_date` — calendar/date attributes
- `fact_permit_lifecycle` — one validated record per chosen permit/revision grain
- `vw_issued_review_metrics` — review metrics for issued records
- `vw_active_workload` — current open permit profile
- `vw_monthly_performance` — monthly aggregations

Keep a `source_dataset`, `extract_date` and stable permit key to maintain lineage. Avoid joining active and cleared sources without verifying key semantics.

## 7. Technical Implementation

### Python
- Load source data through repeatable scripts.
- Normalize dates and category labels.
- Report invalid/missing records rather than silently dropping them.
- Check duplicates, bad chronology and key validity.
- Write cleaned staging outputs to PostgreSQL.
- Log input row count, accepted row count and rejected row count.

### SQL
Show evidence of:
- `JOIN`, `GROUP BY`, `CASE`, `CTE`, `ROW_NUMBER`, date arithmetic.
- Window functions for category trends or rankings.
- PostgreSQL `percentile_cont` for median/P90.
- A reusable metric view, rather than calculations only embedded inside charts.
- Reconciliation queries to validate totals.

### Power BI
Page 1 — **Executive Performance**
- Issuance volume, median review days, P90 review days, trend by month, period/category slicers.

Page 2 — **Review Bottlenecks**
- Review-time distributions by permit category, volume vs duration comparison, top categories, drill-through.

Page 3 — **Active Workload**
- Current active permits, age buckets, category distribution, records needing review/investigation.

Each page should answer a stakeholder question. Provide definitions/tooltips and clear labeling of filters, units and time coverage.

## 8. Decision Framework

Choose candidate investigation priorities using a transparent combination of:
- **Severity:** long median or P90 review duration.
- **Scale:** sufficient case count to matter.
- **Trend:** worsening performance over comparable recent periods.
- **Confidence:** sample size, missingness and stability of the findings.

No arbitrary single "impact score" unless the weights are clearly explained and tested. Show actual metric values before offering a ranking.

Each recommendation must follow: **finding → supporting metric → limitation/possible explanation → suggested action → success metric**.

Example (illustrative, not a real finding): "Category X's median review time rose from A to B days while comparable categories remained stable. Audit the category workflow and check revision frequency; monitor median and P90 review time in the following quarter."

## 9. Four-Week Delivery Plan

### Week 1 — Data understanding and KPI specification
- [ ] Download/profile the two datasets.
- [ ] Validate identifiers, dates, case status, overlap and revision semantics.
- [ ] Select analysis period and define inclusion/exclusion rules.
- [ ] Create data dictionary, business question brief and KPI specification.
**Exit criterion:** Can explain exactly what each row and every KPI means.

### Week 2 — Reproducible Python + SQL
- [ ] Build cleaning and validation scripts.
- [ ] Load PostgreSQL staging/analytics tables.
- [ ] Write SQL views for six core questions.
- [ ] Add validation checks and sample SQL test queries.
**Exit criterion:** Data pipeline runs repeatably and totals reconcile.

### Week 3 — Power BI and exploration
- [ ] Create a simple documented model and measures.
- [ ] Build three report pages and slicers.
- [ ] Check visuals against SQL results.
- [ ] Investigate outliers and comparison fairness.
**Exit criterion:** Dashboard answers the six core questions without manual spreadsheet calculations.

### Week 4 — Findings and portfolio publication
- [ ] Write three evidence-backed findings and prioritized recommendations.
- [ ] Include uncertainty, data limitations and follow-up questions.
- [ ] Add screenshots, architecture diagram and reproducibility instructions.
- [ ] Publish GitHub README and demo walkthrough.
- [ ] Draft 2–3 resume bullets describing *actual work completed*; do not claim measured operational improvements without implementation evidence.
**Exit criterion:** Can give a five-minute stakeholder walkthrough and defend KPI definitions and limitations.

## 10. Repository Layout

```text
permitops/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
├── data/
│   └── README.md
├── src/
│   ├── ingest.py
│   ├── clean.py
│   └── validate.py
├── sql/
│   ├── 01_schema.sql
│   ├── 02_transform.sql
│   ├── 03_metrics.sql
│   └── 04_analysis.sql
├── tests/
│   └── test_data_quality.py
├── dashboard/
│   └── screenshots/
└── docs/
    ├── business_brief.md
    ├── data_dictionary.md
    ├── kpi_definitions.md
    ├── data_quality_report.md
    └── findings_recommendations.md
```

## 11. Hiring Signal / Evaluation Rubric

| Category | Points | What to demonstrate |
|---|---:|---|
| Business framing | 20 | Specific stakeholder and decision, well-scoped questions |
| SQL & modeling | 20 | Correct grain, joins, windows, meaningful reusable metrics |
| Python & data quality | 20 | Reproducible processing, validation, logged exclusions |
| Dashboard | 20 | Accurate charts, drill-down, understandable self-service reporting |
| Recommendations | 20 | Defensible findings, caveats, practical next steps |

**Goal:** at least 85/100 under this self-imposed quality rubric. It is not an industry certification.

## 12. Interview Story to Prepare

- **Challenge:** Leadership lacks a consolidated, trustworthy view of permit volume and processing time.
- **Action:** Defined KPIs, reconciled active and cleared permit records, created Python/SQL transformations, and delivered a Power BI dashboard.
- **Result:** Describe what the completed analysis actually revealed and how it would inform prioritization; don't invent a process-improvement percentage.

## 13. Source / licensing notes

Public Toronto Open Data content is subject to the portal's stated licence and individual dataset conditions. Attribute the City of Toronto and the exact datasets/refresh dates used. Verify the licence before publishing raw data or derivative products.

---

**First work session:** Download a small sample from each permit dataset and produce a field inventory. Stop if record identity, active/cleared overlap or date semantics cannot be explained yet.
