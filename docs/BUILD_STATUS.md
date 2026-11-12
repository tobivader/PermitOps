# Build status — November 11, 2026

The Python/PostgreSQL project and the Mac-friendly, three-page web dashboard are implemented and verified. The manager dashboard is public at https://permitops-operations.smalliris16.chatgpt.site . The web report is separate from the optional Windows Power BI handoff; no PBIX or Power BI execution is claimed.

| Requested stage | Evidence | Status |
|---|---|---|
| Real data ingestion and inspection | src/ingest.py; both raw metadata files; data/raw/manifest.json; actual Python --download pipeline run | Complete |
| Date/missingness/identity cleaning | src/clean.py; local staging/quarantine/dedup/fact CSVs; outputs/data_quality.json | Complete |
| PostgreSQL tables/load/reporting views | sql/01–03; successfully loaded active/cleared staging and fact; repeated full pipeline execution | Complete |
| Volumes, median/P90, trends, active age, bottlenecks | SQL views; nine reporting CSVs; independent pandas comparisons | Complete |
| Power BI datasets, measures, three-page specification | dashboard/README.md; DAX and typed M templates; verified local ZIP with actual inputs | Complete handoff; M/DAX and visuals untested |
| Three-page Mac/browser dashboard | Live public Site; web-dashboard source; three genuine Chrome screenshots; date/category controls and CSV export | Complete |
| Manager case study and executive brief | Business-first README; docs/EXECUTIVE_SUMMARY.md; technical setup moved into docs/TECHNICAL_GUIDE.md | Complete |
| New Houses investigation | sql/06_dashboard.sql; docs/NEW_HOUSES_DEEP_DIVE.md; 15 independent SQL/pandas group checks | Complete |
| Three-minute manager tour | dashboard/recordings/PermitOps_3_Minute_Manager_Tour.mp4; outputs/tour_manifest.json; 180.02 seconds, six decoded sample frames and non-silent audio | Complete, screenshot-based with computer-generated narration |
| At least three findings and actions | docs/findings_recommendations.md contains four findings, scope, numbers, limitations and success measures | Complete |
| Pipeline/data-quality testing | Six pytest tests including isolated PostgreSQL regression; 41 SQL/pandas checks; six standalone SQL checks; nine byte-identical exports | Passed |
| Journal and post-build learning guide | Updated decisions/debug journal; docs/LEARN_AFTER_BUILD.md; dictionary, QA, KPI and business docs | Complete |

## Verified numbers

- Raw: 197,258 active + 452,118 cleared = 649,376 records.
- 10,730 conflicting-key rows quarantined; 25 redundant analytical rows removed; 638,621 unique fact records.
- Historical eligible issued-review population: 335,648; median 29 calendar days, P90 148 days. Applications from 2018 onward, issue dates before November 2026, with explicit KPI exclusions.
- Current eligible active workload: 194,325; active unissued: 13,580. All application years, snapshot only.

## Commands actually verified

```bash
.venv/bin/python -m src.pipeline --download --as-of 2026-11-11
.venv/bin/python -m src.pipeline --as-of 2026-11-11
.venv/bin/python -m pytest -q
/opt/homebrew/opt/postgresql@15/bin/psql -h 127.0.0.1 -p 55432 -d postgres -v ON_ERROR_STOP=1 -f sql/05_validate.sql -o outputs/sql_validation.txt
```

Full ingestion/pipeline runs and the updated pipeline with analysis charts succeeded. SHA-256 checksums for every reporting CSV matched across repeat exports, including explicit category/age-bucket ordering (`outputs/reproducibility.json`). `outputs/validation.json` records all 41 passed checks, and `outputs/sql_validation.txt` records six true standalone SQL checks. Final pytest with PERMITOPS_TEST_DSN targeting the isolated permitops_test database: six passed. Without that variable, the PostgreSQL regression test is skipped. Network/database steps required sandbox permission retries.

Three static analysis charts were generated from fingerprint-verified SQL exports and visually inspected (`docs/figures`). A local Windows-transfer ZIP includes 18 source files, including actual CSV inputs, typed M templates, DAX and report instructions. ZIP integrity and every included file hash passed readback checks (`outputs/handoff_package.json`). These checks do not execute Power Query, DAX or Power BI visuals.

## Remaining portfolio work and limits

- Build/import and verify an actual Power BI report in Windows: relationships, DAX filter behavior, slicers, drill-through, visuals and screenshots remain untested. No PBIX was produced.
- Source, SQL, tests, aggregate outputs, documentation and charts are published at https://github.com/tobivader/PermitOps on main. Initial source commit: 8cae142. GitHub's unauthenticated repository API confirmed public visibility and main as the default branch. Raw/cleaned CSVs, database, virtual environment, record-level reporting CSV and local ZIP remain excluded. See docs/PUBLICATION_CHECKLIST.md.
- Source-owner confirmation of conflicting identities and administrative-category exclusions is outstanding. Quarantine concentration, especially Conditional/Partial permits, limits comparisons. This does not block reproducing the defined MVP but does limit production interpretation.
- No geographic joins, business-day calendar, causal attribution, SLA assessment, historical backlog reconstruction or measured operational improvement is claimed.
- The isolated PostgreSQL server remains running on localhost:55432 for further exploration. Stop it with the command in docs/TECHNICAL_GUIDE.md when finished.

Start studying with README.md, then docs/LEARN_AFTER_BUILD.md and docs/findings_recommendations.md. Resume bullets and a five-minute walkthrough are in docs/demo_walkthrough.md.


## Manager-facing delivery verification

The refreshed full pipeline passed its original 41 metric checks and 15 additional SQL/pandas deep-dive group checks. Six Python/PostgreSQL tests passed. Sixteen JavaScript calculation/interface tests passed, including exact date/category percentiles, the no-issued/35-application month, active category age references, navigation, CSV creation and date validation/reset.

The public dashboard was opened in Chrome after access was approved. All three live pages were visually inspected and genuinely captured to dashboard/screenshots. The Mechanical workload filter changed unissued count to 2374, matching SQL, and Reset restored 13580. Desktop Chrome navigation and these filter/reset paths were observed; a real mobile viewport and Power BI runtime have not been tested.

The Sites deployment succeeded with public access, version 1, and source commit c6ec93cabdce0c5a7f880578efb0e4cc6cca426c. Hosting identity and UI source are in web-dashboard; the isolated hosting checkout and short-lived credentials are outside GitHub. The SQL reference distributions expose no individual record identifiers.


## Visual refresh — version 2

Published the Konrad-influenced editorial restyle to the existing public dashboard. The chart data and calculation engine are unchanged. Sixteen calculation/interface tests passed against the redesigned HTML; the local desktop preview was visually inspected. Browser control subsequently timed out during clean screenshot capture, so README imagery and the video are labeled as version 1. The live Site is the current visual reference.
