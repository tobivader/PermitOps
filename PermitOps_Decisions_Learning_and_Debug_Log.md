# PermitOps — Project Journal, Decisions & Debugging Log

> **Purpose:** A living companion to [`PermitOps_Project_Plan.md`](./PermitOps_Project_Plan.md). Use the **plan** to decide what to build; use **this journal** to explain what you did, why you did it, what went wrong, how you fixed it, and what you learned. Update it throughout the project—not only at the end.
>
> **Project status:** Working Python/PostgreSQL MVP implemented; see actual build entries at the end and outputs/validation.json for evidence. The original planning templates below remain illustrative. Power BI execution remains unfinished; GitHub publication is now complete (see latest entry).

## Quick navigation

1. [Project at a glance](#1-project-at-a-glance)
2. [Stage-by-stage learning journal](#2-stage-by-stage-learning-journal)
3. [Decision log](#3-decision-log)
4. [Error and troubleshooting log](#4-error-and-troubleshooting-log)
5. [Data quality and metric validation record](#5-data-quality-and-metric-validation-record)
6. [Analysis findings and recommendations](#6-analysis-findings-and-recommendations)
7. [Weekly review and interview evidence](#7-weekly-review-and-interview-evidence)
8. [Completion checklist](#8-completion-checklist)

---

## 1. Project at a glance

**Project:** PermitOps — Toronto Building Permit Operations Analytics  
**Goal:** Understand permit volumes, application-to-issue durations, and active permit workload; identify permit categories for further operational investigation.  
**Audience:** Hypothetical municipal operations manager.  
**Key decision:** Which permit categories show the largest or worsening delays, with enough supporting data to justify further investigation?  
**Sources:** [Active permits](https://open.toronto.ca/dataset/building-permits-active-permits/) and [Cleared permits](https://open.toronto.ca/dataset/building-permits-cleared-permits/).  
**Stack:** Python/pandas → PostgreSQL/SQL → Power BI → findings report.  
**Project start date:** TBD  
**Current stage:** Implementation and verification  
**Most recent journal update:** 2026-11-11

### How to use this journal

- **After each work session (5 minutes):** Fill in the short session note in the relevant stage, and record any error or important decision in its own log.
- **For every major choice:** Add a `DEC-###` entry explaining options, trade-offs, and evidence.
- **For every meaningful problem:** Add an `ERR-###` entry, including the exact message, cause, fix, and validation—not merely "fixed it."
- **Before building a metric:** Document its numerator, denominator, filters, time frame, and key assumptions.
- **Before publishing a finding:** Link the SQL query or notebook, result, caveat, and recommended action.
- **Keep raw evidence:** Point to relative repository paths, SQL files, screenshots, or small query excerpts. Never paste passwords, tokens, personal information, or sensitive data into logs or screenshots.

### Stage map: what each part is for

| Stage | What you are trying to prove | Output | Key decision to document |
|---|---|---|---|
| 1. Understand the problem | You can translate a stakeholder question into measurable questions | Business brief | Which questions and KPIs are feasible? |
| 2. Inspect source data | You understand what the rows actually mean | Data dictionary and quality profile | What makes a unique permit? |
| 3. Clean/model data | You can produce reliable reusable data | Python pipeline + SQL tables | How will you handle revisions, duplicates, missing dates? |
| 4. Analyze with SQL | You can compute and check operational measures | SQL views + analysis | Which rows belong in each metric? |
| 5. Build dashboard | You can make findings easy for a manager to explore | Three Power BI pages | Which chart helps answer each business question? |
| 6. Recommend actions | You can move from evidence to a decision | Findings report | What can and cannot be concluded? |

---

## 2. Stage-by-stage learning journal

### Stage 1 — Business understanding (Week 1)

**In simple language:** Before touching the data, decide what a permit operations manager needs to know. A good analysis answers a real question rather than displaying every available column.

**Guiding questions**
- What is the difference between an *application*, an *issued permit*, and a *completed/cleared permit*?
- What does "review time" mean? Is the interval from application to issuance available?
- Which comparisons are fair across different permit categories or years?
- What decisions could a manager make from the report—and what information is missing?

**Actions and evidence**
- [ ] Draft `docs/business_brief.md` with audience, key decision, scope, and exclusions.
- [ ] Choose 4–6 main questions.
- [ ] Draft metric definitions in `docs/kpi_definitions.md`.
- [ ] Record assumptions that require validation.

**Session note template (copy per work session)**

```markdown
#### Session: YYYY-MM-DD — Short description
Goal:
What I did:
What I learned (in simple terms):
Evidence (file/query/screenshot):
Decision ID(s):
Error ID(s):
Next step:
```

**Stage exit test:** Explain the central business question and what each metric measures without mentioning Power BI first.

### Stage 2 — Source data exploration (Week 1)

**In simple language:** Real datasets can contain missing dates, repeated permits, and unexpected status values. First find out what each row represents. If you count rows incorrectly, even a beautiful dashboard will give a wrong answer.

**Guiding questions**
- What are the exact names and types of the downloaded fields?
- Is a permit identified by permit number alone, or by permit number plus revision?
- Do active and cleared datasets overlap?
- Are application, issue, and completion dates available, valid, and in a sensible order?
- What study period and categories are comparable?

**Actions and evidence**
- [ ] Record source download URL, retrieval date, file version if available, row count, and date range.
- [ ] Profile nulls, duplicates, categories, and key uniqueness.
- [ ] Compare active and cleared keys without assuming they can simply be appended.
- [ ] Save observations to `docs/data_dictionary.md` and `docs/data_quality_report.md`.

**Decision checkpoint:** Choose the analytical grain (one row per what?) *only after* checking revisions and overlap. Log it as a decision.

**Stage exit test:** Clearly explain what one analytical row represents and how missing/invalid records will affect metrics.

### Stage 3 — Python cleaning and SQL data model (Week 2)

**In simple language:** Turn source files into clean, consistent tables that can be refreshed. The same input should produce the same output, and questionable records should be reported rather than silently hidden.

**Guiding questions**
- Which fields need type conversions or category standardization?
- What should happen when a date cannot be parsed?
- How do I make the pipeline repeatable rather than editing a spreadsheet manually?
- What table structure avoids double-counting?

**Actions and evidence**
- [ ] Create `src/ingest.py`, `src/clean.py`, and `src/validate.py`.
- [ ] Build staging and analytical tables using `sql/01_schema.sql` and `sql/02_transform.sql`.
- [ ] Track input, accepted, excluded, and flagged record counts.
- [ ] Add simple automated tests in `tests/test_data_quality.py`.

**Decision checkpoint:** Log how invalid dates, revisions, cancelled records, and active/cleared overlap are handled.

**Stage exit test:** Run the pipeline again and reproduce row counts and checks without manual fixes.

### Stage 4 — SQL analysis and KPI validation (Week 2)

**In simple language:** Write queries that answer questions, not just return data. For example, median review time answers "what is typical?" while the 90th percentile shows how long the slowest portion of cases can take.

**Guiding questions**
- How many permits were issued each month?
- Which permit categories have high median or P90 application-to-issue times?
- How does the active, unissued workload differ from past issued cases?
- Are slow categories also high-volume or worsening over time?

**Actions and evidence**
- [ ] Build metric definitions and views in `sql/03_metrics.sql`.
- [ ] Build analysis queries in `sql/04_analysis.sql`.
- [ ] Use joins, CTEs, window functions, and percentiles where useful.
- [ ] Reconcile counts and summary results against source/staging data.

**Decision checkpoint:** Record filters, date logic, groupings, and treatment of outliers. Do **not** label application-to-issue calendar days as an official SLA without an applicable documented standard.

**Stage exit test:** Explain the denominator and filters for each KPI, then reproduce its number directly with SQL.

### Stage 5 — Power BI dashboard (Week 3)

**In simple language:** A dashboard helps managers find answers quickly. Every visual should serve a business question. Avoid adding a map or chart only because it looks impressive.

**Report pages**
1. **Executive Performance:** volumes, median/P90 review times, trends, categories.
2. **Review Bottlenecks:** category comparisons, distributions, outliers, drill-through.
3. **Active Workload:** current permit ages, categories, and investigation priorities.

**Actions and evidence**
- [ ] Create relationships, measures, and filters in Power BI.
- [ ] Add definitions and date coverage to visuals/tooltips.
- [ ] Confirm Power BI values match SQL for selected filters.
- [ ] Capture screenshots in `dashboard/screenshots/`.

**Decision checkpoint:** Document why each chart type was chosen and which user question it answers.

**Stage exit test:** Walk through the report as a manager and answer six questions without needing to open SQL or a spreadsheet.

### Stage 6 — Findings, recommendations, and publication (Week 4)

**In simple language:** A finding is what the data shows; a recommendation is what someone could do because of it. Do not claim that the data proves a specific cause when it only reveals an association or pattern.

**Actions and evidence**
- [ ] Document three findings with supporting metric values and query links.
- [ ] Include limitations and plausible alternative explanations.
- [ ] Recommend specific investigations or process changes, with a measure of success.
- [ ] Publish project structure, reproducibility steps, and screenshots.
- [ ] Prepare a 3–5 minute demonstration and a conversational CAR interview story.

**Stage exit test:** Explain what the manager should investigate, why, and how the team would know whether an intervention helped.

---

## 3. Decision log

**Why it matters:** Interviewers may ask *"Why did you use a median instead of an average?"* or *"How did you prevent double counting?"* This section records your reasoning when it actually happens.

### Decision index

| ID | Date | Decision | Reason | Status | Evidence |
|---|---|---|---|---|---|
| DEC-001 | TBD | TBD — analytical grain | Pending data profiling | Open | TBD |

### Decision entry template — copy below for each new decision

```markdown
### DEC-002 — Short decision title
Date:
Stage:
Question/problem:
Options considered:
- Option A:
- Option B:
Chosen approach:
Why I chose it:
Trade-off or limitation:
Evidence or test performed:
Files/queries affected:
When to revisit:
Status: Proposed / Confirmed / Reversed
```

**Example only — not a completed decision**

> **DEC-EXAMPLE — Median versus average review time**  
> Option A: Average days, which is easy to understand but can be pulled upward by extreme cases.  
> Option B: Median days, which better reflects a typical case in a skewed distribution.  
> Proposed approach: Show median as the headline measure, P90 for long-duration cases, and volume alongside both.  
> Validation needed: Examine the actual review-time distribution before confirming this choice.

---

## 4. Error and troubleshooting log

**Rule:** Log **meaningful** technical and analytical errors. A useful log explains the *symptom → cause → fix → verification*. The debugging process matters as much as the final solution.

### Error index

| ID | Date | Type | Symptom | Root cause | Fix verified? | Evidence |
|---|---|---|---|---|---|---|
| ERR-001 | TBD | TBD | TBD | TBD | No | TBD |

### Error entry template — copy below whenever needed

```markdown
### ERR-002 — Short issue title
Date and stage:
Type: Python / SQL / Data quality / Power BI / Git / Business logic
Severity: Blocker / Major / Minor
What I was trying to do:
What I expected:
What actually happened:
Exact error message (or description of incorrect result):
How I reproduced it:
My first hypothesis:
Steps I took to investigate:
1.
2.
3.
Confirmed root cause:
Fix applied:
Files or queries changed:
How I verified the fix (test/result):
What I learned:
How I will prevent this next time:
Status: Open / Resolved / Monitoring
```

**Example only — hypothetical issue, not encountered yet**

> **ERR-EXAMPLE — Monthly issued permit count is unexpectedly high**  
> Expected: One count for each unique permit at the chosen analytical grain.  
> Observed: Count increases after combining active and cleared data.  
> Possible cause: Overlapping permit identifiers or multiple revisions.  
> Debug approach: Count records per candidate permit key in each dataset; inspect duplicate groups; compare source overlap; check the join/union logic.  
> Potential fix: Adopt the correct validated key, precedence, and status rules.  
> Verification: Query counts of distinct keys before and after transformation, and inspect a sample of duplicates.  
> **Do not mark resolved until the data confirms the cause and the checks pass.**

### Helpful quick debugging questions

- **Python:** Is the input type what I expect? Are nulls, dates and column names handled? Did the transformation change row counts unexpectedly?
- **SQL:** Is the join one-to-one or one-to-many? Am I unintentionally counting revisions? Is the `WHERE` filter applied at the correct stage?
- **Power BI:** Does the relationship duplicate rows? Is the measure affected by the intended filter context? Does the visual match a SQL reconciliation query?
- **Data quality:** Is an anomalous value an actual record, a source error, or a transformation bug?
- **Git:** Which file changed, what did the diff show, and can the previous working state be reproduced?

---

## 5. Data quality and metric validation record

### Dataset profile (complete for each extract)

| Field | Active permits | Cleared permits |
|---|---|---|
| Retrieval date | TBD | TBD |
| Source URL/version | TBD | TBD |
| Raw row count | TBD | TBD |
| Selected analysis period | TBD | TBD |
| Candidate unique key | TBD | TBD |
| Duplicate key count | TBD | TBD |
| Missing application date | TBD | TBD |
| Missing issue date | TBD | TBD |
| Invalid date sequences | TBD | TBD |
| Records excluded from each KPI | TBD | TBD |

### KPI validation template

```markdown
### KPI: [metric name]
Business question:
Definition in plain English:
Formula / SQL logic:
Unit:
Date field and time window:
Denominator / eligible records:
Filters / exclusions:
Treatment of nulls and outliers:
SQL view or query path:
Power BI measure:
Cross-check query and result:
Known limitation:
Validated on:
```

**Important guardrails**
- A current active-permit extract is not a complete historical snapshot of daily backlog.
- Incomplete cases cannot be used as if their final review duration were already known.
- Permit number and revision must be validated before grouping or joining.
- Timestamps alone cannot prove *why* a permit took longer.
- Write down all rejected or adjusted observations and their impact on metrics.

---

## 6. Analysis findings and recommendations

Use one record per claim. Keep findings separate from guesses about the cause.

```markdown
### FIND-001 — Clear, specific finding
Question answered:
Population and period:
Observed result (real number):
Comparison / baseline:
Source SQL query or notebook:
Data checks performed:
What the evidence supports:
What the evidence does NOT prove:
Recommended next action:
How success would be measured:
Confidence / limitations:
Status: Draft / Validated / Published
```

**Example only (invented numbers, not project findings):**

> A permit category has a 65-day median review duration versus 38 days for another category. This **does not prove** staff performance is worse; category complexity, revisions, and case mix could differ. A reasonable next step is to investigate workflow stages or application completeness, then track change in median/P90 duration after any intervention.

---

## 7. Weekly review and interview evidence

### Weekly review template

```markdown
## Week [1/2/3/4] review — YYYY-MM-DD
Goal for the week:
What I completed (links to files/commits):
New concepts I can explain without notes:
Decisions made (DEC IDs):
Errors fixed (ERR IDs):
Unresolved problems or assumptions:
Most important analytical insight so far:
What I would do differently:
Next week's top three priorities:
```

### CAR story builder (complete when the work is real)

**Challenge:** What was the business question, and why was reliable reporting difficult?  
**Action:** What did *you* do to profile, clean, model, query, validate, visualize, and communicate the data? Include one actual decision and one actual debug story.  
**Result:** What deliverables and verified findings did you produce? What *recommendation* did you make? Avoid claiming operational improvement unless it was implemented and measured.

### Five interview questions this journal should help you answer

1. How did you decide which KPIs mattered?
2. How did you validate the accuracy of your SQL and Power BI outputs?
3. Tell me about a mistake or unexpected data problem and how you fixed it.
4. Why did you make a particular modeling or technical choice?
5. How did your analysis lead to a useful operational recommendation?

---

## 8. Completion checklist

- [ ] Every main KPI has a documented definition and SQL validation.
- [ ] The dataset grain, revision handling, and active/cleared overlap are explained.
- [ ] Source records and excluded rows are traceable.
- [ ] Significant decisions have evidence and trade-offs.
- [ ] At least one **real** solved issue has a reproducible error log and tested fix (if an issue occurs).
- [ ] All reported findings link to analysis evidence.
- [ ] Findings clearly distinguish observed facts from hypothesized causes.
- [ ] Recommendations include a follow-up action and success metric.
- [ ] A recruiter can understand the project in 2 minutes.
- [ ] You can explain the project and a genuine challenge using CAR in 3–5 minutes.

**Reminder:** Document what actually happens. A smaller, accurate project journal is better than a polished log full of invented problems or results.


## Actual build session — 2026-11-11

### DEC-001 — Preserve planning documents before implementation
The workspace was empty. Copied the plan and journal from Downloads. The two downloaded journal copies are byte-identical (cmp exit 0). The required PermitOps_Codex_Overnight_Goal.md was not found in Downloads, Documents, Desktop, Dev, or connected Drive search. Requested it from the user; its required build order remains unknown. Do not substitute a fabricated goal file.

### ERR-001 — Public API network access
Symptom: curl exited 6, Could not resolve host, while requesting Toronto CKAN package metadata.
Root cause: sandbox network access could not resolve the public API host; unrestricted retry requested to distinguish restriction from host availability.
Fix: pending authorized network retry.
Verification: pending.

### Environment checks
Python 3.13.1, psql and docker executables exist. PostgreSQL default socket /tmp:5432 returned no response; this does not prove no other server is configured. pandas, requests, psycopg and pytest are absent from the default Python interpreter. No pipeline, metrics, dashboard or findings have been claimed tested.


## Implementation journal — actual work, 2026-11-11

### DEC-002 — Build order authorized
The newly added goal.txt referenced the missing overnight document. The user explicitly authorized using the Project Plan order: ingestion, cleaning, PostgreSQL, analytics, Power BI handoff, findings, testing, documentation. This supersedes the missing-file dependency.

### DEC-003 — Conservative identity handling
Observed repeated permit/revision keys with differing category, status or dates. Normalize numeric revisions (00 and 0), retain revisions as separate records, quarantine all conflicting analytical payloads. Deduplicate only agreeing analytical payloads; source row IDs break ties and cleared has precedence. Trade-off: affected records are excluded; do not claim keys necessarily represent erroneous source records. Evidence: src/clean.py, data/clean/quarantine.csv, outputs/data_quality.json.

### DEC-004 — Study cohorts and active workload
Use applications >=2018 because the current cleared resource starts with completions in 2017; exclude the incomplete issue month. Active workload spans all application years. Equal 12-month issue windows with >=100 each support comparison. No arbitrary impact score, SLA, causal claims or outlier trimming. Evidence: sql/03_metrics.sql, docs/kpi_definitions.md.

### DEC-005 — Power BI handoff on macOS
Power BI Desktop is unavailable in this environment. Deliver CSV fact/dimensions, SQL aggregate references, DAX and a three-page build specification. DAX, visuals, slicers and drill-through require verification in Power BI. Do not present specification as a completed dashboard.

### ERR-001 update — Network restriction resolved
Unrestricted curl downloads succeeded for both public resources after sandbox DNS failure. Dependency pip install hit the same restriction; authorized retry installed pinned packages in .venv. Hashes, bytes, timestamps and URLs are saved in data/raw/manifest.json.

### ERR-002 — PostgreSQL initialization/connection blocked
Symptom: initdb failed at shmget with Operation not permitted; later psycopg connection to localhost also returned Operation not permitted. Root cause: execution sandbox restrictions, verified by successful authorized retries. Fix: isolated UTF-8 cluster under .local/postgres on port 55432, authorized startup and connection. Verification: staging and fact loads completed and independent SQL checks passed. No existing database was replaced.

### ERR-003 — Nullable durations serialized as floats
Symptom: psycopg.errors.InvalidTextRepresentation: invalid input syntax for type integer: 1282.0 during COPY review_days. Root cause: pandas map inferred float when results contained integers and None. Fix: directly construct an object Series from Python integers/None. Verification: PostgreSQL COPY completed and SQL/pandas duration percentiles agreed. Failed load rolled back transactionally. File: src/database.py.

### ERR-004 — Single-column dimension export sort
Symptom: psycopg.errors.InvalidColumnReference: ORDER BY position 2 is not in select list for dim_permit_type. Root cause: generic export assumed at least two columns. Fix: stable ORDER BY 1 for generic exports. Verification: all reporting CSV exports completed; end-to-end rerun underway at this journal entry.

### ERR-005 — Invalid chronology in real source data
Observed 36 raw negative review intervals, three negative completion sequences and one future completion. No date parsing failures observed. Root cause of source values is unknown; do not invent an explanation. Fix: retain flags and exclude only affected duration calculations. Verification: src.clean eligibility rules, synthetic edge-case tests and SQL nonnegative duration checks. Status: source-owner clarification remains open.


### Final verified session record — 2026-11-11
The complete Python --download pipeline passed, followed by a retained-input repeat run. All nine reporting CSV hashes were byte-identical (outputs/reproducibility.json). All 41 SQL/pandas checks passed, all six standalone SQL checks returned true (outputs/sql_validation.txt), and final pytest was 5 passed. Input counts: 649376; fact: 638621; quarantine: 10730; redundant analytical rows removed: 25. Four findings and recommendations were generated from verified SQL exports. Data dictionary, QA report, KPI definitions, Power BI handoff, learning guide and five-minute walkthrough are present. ERR-004 end-to-end verification is now resolved.

### DEC-006 — Keep local data outside version control
Initialized Git; git check-ignore verified exclusion of .venv, .local PostgreSQL, raw CSVs, cleaned/quarantine CSVs and the large record-level report CSV. No commit or remote publication was made. GitHub CLI is unavailable. The first git init was sandbox-blocked; authorized retry succeeded.

### Outstanding work
Actual Power BI report/DAX/visual validation and public GitHub publication are not complete. No screenshots or PBIX are claimed. Source identity conflicts and non-permit category exclusions require data-owner review. The working core MVP and its limitations are documented in docs/BUILD_STATUS.md.


## Continuation — portfolio handoff and regression checks, 2026-11-11

### DEC-007 — Reproducible analysis charts
Added matplotlib PNG/SVG charts for volumes, category median/P90 comparisons and active/unissued workload. Charts read verified SQL export fingerprints, separate lifecycle cohorts, reconcile workload totals, and are explicitly not Power BI screenshots. All three were visually inspected for legibility and clipping. The complete pipeline including chart generation passed its 41 SQL/pandas checks. A project-local font/cache directory resolved initial Fontconfig no-writable-cache warnings; chart rerun completed without those warnings.

### ERR-006 — Snapshot cutoff depended on issue-date filter context (static review)
Original DAX As Of Date used MAX on filtered fact rows. Static review found that an empty issue-date selection could yield a blank cutoff before the Applications measure switches date relationships. Real-data example: AS Alternative Solution, December 2024 has 35 eligible applications but no issued-date fact rows that month. Fix: CALCULATE(MAX(as_of_date), REMOVEFILTERS()) makes the snapshot global. Verification: Microsoft REMOVEFILTERS/USERELATIONSHIP documentation and the CSV counterexample support the correction; Power BI execution is still untested and the regression scenario is in dashboard/README.md. Do not describe this as a runtime-verified DAX fix.

### DEC-008 — Deterministic export ordering and exact bytes
Multi-column reporting views now sort by their two grouping keys; the one-column category dimension sorts by its sole column. This makes category/age-bucket peer ordering explicit. Two successive exports matched byte-for-byte for all nine CSVs; outputs/reproducibility.json records the current checksums. Git attributes preserve generated CSV line endings to avoid invalidating fingerprints after checkout. Git whitespace checks on source/SQL/tests/dashboard passed; expected CSV CRLF and Markdown hard line breaks are not data errors.

### DEC-009 — Windows-transfer handoff
Added typed Power Query M templates and a generated local Power BI ZIP. The ZIP includes actual fact/dimension/aggregate CSVs and 18 source files total, with internal file fingerprints and CRC/hash readback checks. It excludes raw addresses/descriptions/builder names and stays ignored by Git. Power Query/DAX runtime verification still requires Power BI Desktop. Package evidence: outputs/handoff_package.json.

### Verification — SQL regression test
Created a separate permitops_test database. Five cleaning tests plus a PostgreSQL integration regression test all passed (6 passed). Explicitly synthetic test rows prove the known median=20, P90=76, age=41 and monthly applications=1/issues=5. Test code refuses to load into a database not named permitops_test. These fixtures never enter the real analytics database or findings.

### Publication state
GitHub discovery found an available but uninstalled/unconnected GitHub plugin; a connection was suggested. GitHub CLI is absent and the browser tool reported No browser is available. Publication therefore remains external work. Local source/aggregate/chart staging was reviewed; raw files, database and local handoff ZIP remain excluded.


## GitHub publication — 2026-11-11
The user supplied https://github.com/tobivader/PermitOps.git. git ls-remote returned no refs, confirming the destination was empty. Added origin and pushed main successfully. Existing Git authentication worked without inspecting credentials or needing a plugin/browser. Initial source commit: 8cae14230b54644dc6195c69bd8363ad0af44696. GitHub public API readback returned private=false and default_branch=main. Earlier connection-blocker entries are historical and superseded. README and publication/build status now reflect the repository. Actual Power BI runtime verification remains unfinished under the environment-limited handoff scope.


## Manager-facing portfolio upgrade — 2026-11-11

### DEC-010 — Mac-friendly browser dashboard
The user requested the three-page manager dashboard, actual screenshots, a business-first README, executive summary, New Houses investigation and walkthrough. Built a dependency-free production HTML/CSS/JavaScript/SVG report with exact frequency-weighted percentiles. Python generates only anonymous SQL aggregates. Sixteen calculation/interface tests passed; the full pipeline also passed 41 original metrics checks and 15 new SQL/pandas group checks. All three live pages were visually inspected and captured in Chrome after user approval. Real mobile behavior and Power BI remain untested.

### ERR-007 — Nullable category parameter had indeterminate SQL type
Dashboard generation failed with psycopg.errors.IndeterminateDatatype: could not determine data type of parameter $3. The all-category filter passed None to an isolated IS NULL placeholder, which PostgreSQL could not type from another parameter. Fixed with %s::text IS NULL. Verification: six independent SQL reference cohorts generated, 15 deep-dive checks passed and all browser calculation comparisons matched.

### ERR-008 — Local preview and browser access restrictions
The sandbox blocked HTTP server binding and localhost readiness requests. Authorized retries served the actual page successfully. Chrome initially returned Computer Use was not approved to use Google Chrome; the user explicitly allowed it. Later user/window changes invalidated accessibility controls, so actions were refreshed against current state and Chrome was left idle for QA. Genuine screenshots and Mechanical category/reset checks succeeded. No screenshots were fabricated. The native Screenshot app did not expose a usable recording interface (timeout), so the reproducible tour uses real captures rather than claiming a continuous screen recording.

### ERR-009 — Expired Sites source credential
The initial source helper rejected an expired credential. Renewed access for the same persisted project, kept credentials only in session memory and passed them through hidden stdin. The hosting checkout is isolated under .local/permitops-site so nested Git metadata cannot replace the GitHub project source. Packaging/push succeeded, then version 1 deployed. The user explicitly requested public manager access, which was applied and read back before public deployment.

### DEC-011 — New Houses investigation uses counts AND rates
Recent original permits: 766 issues, median 71 days, P90 876 days, 131 over-year reviews (17.1%). Revisions: 680 issues and 20 over-year reviews. Originals are 53.0% of issues but 86.8% of the long tail. Q1 2026 has 364 issues and 119 over-year reviews, about 78.8% of recent over-year cases. Evidence: sql/06_dashboard.sql and outputs/new_houses_deep_dive.json. Do not infer that delay accumulated within Q1 or that revision status caused duration; compare case complexity and stage timestamps. Partial edge quarters are labeled in the deep dive.

### ERR-010 — Narration and segment timing
macOS speech synthesis inside the sandbox produced no usable audio. Authorized retry generated narration. Duration guards then rejected segments that would exceed their allotted windows (30.4 seconds in a 30-second segment and 20.85 seconds in a 20-second segment). Shortened the narration rather than cutting off speech. The final media builder checks total duration and decodes six sample frames; outputs/tour_manifest.json records successful completion once produced. The tour is explicitly computer-narrated and screenshot-based, not the owner's voice or live interaction recording.


### Final manager-delivery verification
The refreshed full pipeline passed 41 original metrics checks and 15 New Houses checks. Final test runs: 16 JavaScript calculation/interface tests and 6 Python/PostgreSQL tests passed. Three genuine desktop Chrome screenshots were visually inspected; native Mechanical filtering and reset matched SQL values. Video completed at 180.02 seconds (2,899,775 bytes), six sample frames decoded and first/middle/last frames were visually checked. Audio volume analysis confirmed non-silent narration (mean -19.8 dB, peak -0.7 dB). The public Site deployment succeeded and the root was anonymously reachable through curl; an automated urllib index.html probe received 403, so no blanket automated asset-readback success is claimed. Browser QA/public access mode and deployment success remain the authoritative hosting evidence.
