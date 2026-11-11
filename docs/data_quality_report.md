# Data quality report

As-of 2026-11-11. Authoritative counts: `outputs/data_quality.json`; source fingerprints and retrieval times: `data/raw/manifest.json`.

| Reconciliation | Rows |
|---|---:|
| Raw active | 197,258 |
| Raw cleared | 452,118 |
| Combined input | 649,376 |
| Conflicting/invalid key quarantine | 10,730 |
| Analytically redundant rows removed | 25 |
| Unique analytical fact | 638,621 |

Every input row is accounted for. There are 5,360 conflicting normalized keys and 1,337 normalized keys present in both sources. Cross-source overlaps are not blindly added; conflicting payloads are quarantined. Identical analytical payloads are deduplicated deterministically. No exact full-row duplicate claim is made.

| Date/identity flag | Raw rows (may overlap) |
|---|---:|
| invalid_key | 0 |
| application_date_invalid | 0 |
| application_date_future | 0 |
| issued_date_invalid | 0 |
| issued_date_future | 0 |
| completed_date_invalid | 0 |
| completed_date_future | 1 |
| negative_review | 36 |
| negative_completion | 3 |

| Eligible population (before historical study filter) | Fact records |
|---|---:|
| review_eligible | 579,801 |
| application_eligible | 596,682 |
| active_eligible | 194,325 |
| active_unissued_eligible | 13,580 |
| completion_eligible | 399,056 |

## Quarantine concentration

Counts below are raw rows, not unique permits or the historical study denominator.

| Source | Category | Quarantined raw rows |
|---|---|---:|
| cleared | Conditional Permit | 4,821 |
| cleared | Partial Permit | 1,689 |
| cleared | New Houses | 1,427 |
| active | New Houses | 983 |
| active | New Building | 311 |
| active | DCs DeferredFees | 270 |
| active | Conditional Permit | 263 |
| cleared | New Building | 204 |
| cleared | Building Additions/Alterations | 156 |
| active | Partial Permit | 149 |

Missing application/issue/completion counts by source and observed date ranges are retained in the JSON. Active completion dates are all blank in this extract, as expected for a current open resource. Cleared records include cancellations and other statuses; cleared does not automatically mean a successful construction completion. A future completion date is excluded from completion duration, while a valid review interval can remain eligible.

Historical analysis excludes pre-2018 applications, incomplete issue months, invalid review chronology and explicit terminal/non-permit populations. No outlier duration is removed solely because it is large. This is not a complete history of all Toronto applications: the cleared resource begins in 2017, current extracts can be corrected, and active workload is a single snapshot. Quarantine may be concentrated in particular categories and distort comparisons; resolve it with source owners before production use. Administrative-category exclusions are analytical judgments requiring review.

Verification: source→staging counts, input→quarantine/dedup/fact reconciliation, unique keys, eligible review totals, overall/category/month-category median/P90, equal-window trends, active/unissued totals and age arithmetic are checked against SQL. Passing checks validate implemented definitions, not the truth of every source record or causal interpretations.
