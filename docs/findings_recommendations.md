# Findings and recommendations

Extract as-of: 2026-11-11. Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/). Source: City of Toronto active permits and cleared permits since 2017.

Population: non-conflicting permit/revision records, application date from 2018 onward for historical review metrics. Current workload includes all application years. Recent issue window: 2025-11-01 to 2026-10-31; prior: 2024-11-01 to 2025-10-31. Counts below are eligible issued records, not all applications. Timestamps cannot identify causes or measure staff productivity.

Validation: 41 checks passed in `outputs/validation.json`. Full study issued review population: 335,648; median 29 days; P90 148 days. This is a pooled cohort, not a target or fair like-for-like category comparison.

## FIND-001 — New Building

Recent: **231 issued records**, median **79 calendar days**, P90 **866 days**. Prior: 262 records, median 155.5 days. Median change: -76.5 days.

Evidence: `sql/03_metrics.sql` → `vw_bottlenecks`, exported to `outputs/reporting/vw_bottlenecks.csv`; recent/prior group counts and percentiles cross-checked against pandas.

Recommendation: investigate the long-duration tail first. Its median decreased; do not describe the median as worsening. Audit a sample near/above P90 for application completeness, applicant response cycles and project complexity. Track median/P90 and the age of unresolved cases in subsequent equal-length issue windows. Limitation: modest volume, changing case mix and unresolved-case censoring could explain differences; no causal improvement is established.

## FIND-002 — New Houses

Recent: **1,446 issued records**, median **52 calendar days**, P90 **419.5 days**. Prior: 1,392 records, median 54 days. Median change: -2 days.

Evidence: `sql/03_metrics.sql` → `vw_bottlenecks`, exported to `outputs/reporting/vw_bottlenecks.csv`; recent/prior group counts and percentiles cross-checked against pandas.

Recommendation: investigate long reviews alongside the larger case volume. Sample slow cases across revision levels before proposing workflow changes. Success measure: lower P90 in a comparable cohort without a rise in active-unissued ages. Limitation: elapsed days include applicant time; a change in median alone does not demonstrate operational improvement.

## FIND-003 — Building Additions/Alterations

Recent: **4,676 issued records**, median **33 calendar days**, P90 **99 days**. Prior: 4,742 records, median 32 days. Median change: +1 days.

Evidence: `sql/03_metrics.sql` → `vw_bottlenecks`, exported to `outputs/reporting/vw_bottlenecks.csv`; recent/prior group counts and percentiles cross-checked against pandas.

Recommendation: monitor this high-volume category; the observed median change is +1 calendar days, with no established causal explanation. Compare work subtypes and revision mix, then review handoff steps if an adverse shift persists. Success measure: stable or lower median/P90 across subsequent comparable windows. Limitation: no significance test or case-complexity adjustment has been performed.

## FIND-004 — Most active permits are already issued

There are **194,325 eligible active permits**, including **13,580 unissued** (7.0%). Mechanical(MS) has the largest unissued count, **2,374**. Evidence: `vw_active_summary` and `outputs/reporting/vw_active_summary.csv`; totals and unissued age arithmetic independently checked.

Recommendation: separate the pre-issuance queue from construction/inspection workload in management reporting. Investigate the oldest unissued cases within high-volume categories rather than treating all open permits as review backlog. Track unissued count and median/P90 age at future snapshots. Limitation: this single extract cannot show historical backlog change; open status does not prove city staff are currently acting on a case.

## Confidence and next investigations

10,730 rows covering 5,360 conflicting keys are excluded pending data-owner clarification; 25 analytically redundant rows were removed. Quarantine and category exclusions may change rankings. 1 future completion dates and 36 negative review intervals are flagged in the QA report. Large valid durations are retained. `original_revision_sensitivity.csv` provides an original-only comparison; review it before attributing category differences to process performance. No recommendations have been implemented and no real-world performance gain is claimed.

Investigation priority is transparent judgment, not an invented weighted impact score: New Building for severity/tail; New Houses for tail plus volume; Building Additions/Alterations for high-volume monitoring. A manager should review case complexity, revision handling and quarantine concentration before adopting this shortlist.
