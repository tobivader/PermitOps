"""Generate dated evidence-backed findings after SQL validation succeeds."""
import json
from pathlib import Path
import pandas as pd


def report():
    qa=json.loads(Path('outputs/data_quality.json').read_text())
    validation=json.loads(Path('outputs/validation.json').read_text())
    if not validation['all_passed'] or validation['as_of'] != qa['as_of']:
        raise ValueError('Findings require a passing validation for this extract')
    quality=f'''# Data quality report

As-of {qa['as_of']}. Authoritative counts: `outputs/data_quality.json`; source fingerprints and retrieval times: `data/raw/manifest.json`.

| Reconciliation | Rows |
|---|---:|
| Raw active | {qa['sources']['active']['input_rows']:,} |
| Raw cleared | {qa['sources']['cleared']['input_rows']:,} |
| Combined input | {qa['input_rows']:,} |
| Conflicting/invalid key quarantine | {qa['quarantined_rows']:,} |
| Analytically redundant rows removed | {qa['duplicate_rows_removed']:,} |
| Unique analytical fact | {qa['fact_rows']:,} |

Every input row is accounted for. There are {qa['conflicting_keys']:,} conflicting normalized keys and {qa['cross_source_overlap_keys']:,} normalized keys present in both sources. Cross-source overlaps are not blindly added; conflicting payloads are quarantined. Identical analytical payloads are deduplicated deterministically. No exact full-row duplicate claim is made.

| Date/identity flag | Raw rows (may overlap) |
|---|---:|
'''
    quality+='\n'.join(f'| {k} | {v:,} |' for k,v in qa['flags'].items())
    quality+='\n\n| Eligible population (before historical study filter) | Fact records |\n|---|---:|\n'
    quality+='\n'.join(f'| {k} | {v:,} |' for k,v in qa['eligibility'].items())
    quarantine=pd.read_csv('data/clean/quarantine.csv',dtype=str)
    concentration=quarantine.groupby(['source_dataset','permit_type']).size().sort_values(ascending=False)
    quality+='\n\n## Quarantine concentration\n\nCounts below are raw rows, not unique permits or the historical study denominator.\n\n| Source | Category | Quarantined raw rows |\n|---|---|---:|\n'
    quality+='\n'.join(f'| {source} | {category} | {count:,} |' for (source,category),count in concentration.head(10).items())
    quality+='''

Missing application/issue/completion counts by source and observed date ranges are retained in the JSON. Active completion dates are all blank in this extract, as expected for a current open resource. Cleared records include cancellations and other statuses; cleared does not automatically mean a successful construction completion. A future completion date is excluded from completion duration, while a valid review interval can remain eligible.

Historical analysis excludes pre-2018 applications, incomplete issue months, invalid review chronology and explicit terminal/non-permit populations. No outlier duration is removed solely because it is large. This is not a complete history of all Toronto applications: the cleared resource begins in 2017, current extracts can be corrected, and active workload is a single snapshot. Quarantine may be concentrated in particular categories and distort comparisons; resolve it with source owners before production use. Administrative-category exclusions are analytical judgments requiring review.

Verification: source→staging counts, input→quarantine/dedup/fact reconciliation, unique keys, eligible review totals, overall/category/month-category median/P90, equal-window trends, active/unissued totals and age arithmetic are checked against SQL. Passing checks validate implemented definitions, not the truth of every source record or causal interpretations.
'''
    Path('docs/data_quality_report.md').write_text(quality)
    p=Path('outputs/reporting')
    b=pd.read_csv(p/'vw_bottlenecks.csv').set_index('permit_type')
    a=pd.read_csv(p/'vw_active_summary.csv')
    totals=a.groupby('permit_type')[['active_permits','active_unissued']].sum()
    top=totals.sort_values('active_unissued',ascending=False).iloc[0]
    top_name=totals.active_unissued.idxmax()
    end=pd.Timestamp(qa['as_of']).replace(day=1)
    window=f"{(end-pd.DateOffset(months=12)).date()} to {(end-pd.Timedelta(days=1)).date()}"
    prior=f"{(end-pd.DateOffset(months=24)).date()} to {(end-pd.DateOffset(months=12)-pd.Timedelta(days=1)).date()}"
    sections=[f'''# Findings and recommendations

Extract as-of: {qa['as_of']}. Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/). Source: City of Toronto active permits and cleared permits since 2017.

Population: non-conflicting permit/revision records, application date from 2018 onward for historical review metrics. Current workload includes all application years. Recent issue window: {window}; prior: {prior}. Counts below are eligible issued records, not all applications. Timestamps cannot identify causes or measure staff productivity.

Validation: {len(validation['checks'])} checks passed in `outputs/validation.json`. Full study issued review population: {validation['study_review_rows']:,}; median {validation['median_review_days']:g} days; P90 {validation['p90_review_days']:g} days. This is a pooled cohort, not a target or fair like-for-like category comparison.
''']
    for i,name in enumerate(['New Building','New Houses','Building Additions/Alterations'],1):
        r=b.loc[name]
        sections.append(f'''## FIND-{i:03d} — {name}

Recent: **{int(r.recent_issued):,} issued records**, median **{r.recent_median_days:g} calendar days**, P90 **{r.recent_p90_days:g} days**. Prior: {int(r.prior_issued):,} records, median {r.prior_median_days:g} days. Median change: {r.median_change_days:+g} days.

Evidence: `sql/03_metrics.sql` → `vw_bottlenecks`, exported to `outputs/reporting/vw_bottlenecks.csv`; recent/prior group counts and percentiles cross-checked against pandas.
''')
        if name=='New Building':
            direction = ('Its median decreased; do not describe the median as worsening.' if r.median_change_days < 0
                         else 'Its median increased; investigate whether case mix explains the change.' if r.median_change_days > 0
                         else 'Its median was unchanged between the two windows.')
            sections.append(f'Recommendation: investigate the long-duration tail first. {direction} Audit a sample near/above P90 for application completeness, applicant response cycles and project complexity. Track median/P90 and the age of unresolved cases in subsequent equal-length issue windows. Limitation: modest volume, changing case mix and unresolved-case censoring could explain differences; no causal improvement is established.\n')
        elif name=='New Houses':
            sections.append('Recommendation: investigate long reviews alongside the larger case volume. Sample slow cases across revision levels before proposing workflow changes. Success measure: lower P90 in a comparable cohort without a rise in active-unissued ages. Limitation: elapsed days include applicant time; a change in median alone does not demonstrate operational improvement.\n')
        else:
            sections.append(f'Recommendation: monitor this high-volume category; the observed median change is {r.median_change_days:+g} calendar days, with no established causal explanation. Compare work subtypes and revision mix, then review handoff steps if an adverse shift persists. Success measure: stable or lower median/P90 across subsequent comparable windows. Limitation: no significance test or case-complexity adjustment has been performed.\n')
    sections.append(f'''## FIND-004 — Most active permits are already issued

There are **{int(a.active_permits.sum()):,} eligible active permits**, including **{int(a.active_unissued.sum()):,} unissued** ({a.active_unissued.sum()/a.active_permits.sum():.1%}). {top_name} has the largest unissued count, **{int(top.active_unissued):,}**. Evidence: `vw_active_summary` and `outputs/reporting/vw_active_summary.csv`; totals and unissued age arithmetic independently checked.

Recommendation: separate the pre-issuance queue from construction/inspection workload in management reporting. Investigate the oldest unissued cases within high-volume categories rather than treating all open permits as review backlog. Track unissued count and median/P90 age at future snapshots. Limitation: this single extract cannot show historical backlog change; open status does not prove city staff are currently acting on a case.

## Confidence and next investigations

{qa['quarantined_rows']:,} rows covering {qa['conflicting_keys']:,} conflicting keys are excluded pending data-owner clarification; {qa['duplicate_rows_removed']} analytically redundant rows were removed. Quarantine and category exclusions may change rankings. {qa['flags']['completed_date_future']} future completion dates and {qa['flags']['negative_review']} negative review intervals are flagged in the QA report. Large valid durations are retained. `original_revision_sensitivity.csv` provides an original-only comparison; review it before attributing category differences to process performance. No recommendations have been implemented and no real-world performance gain is claimed.

Investigation priority is transparent judgment, not an invented weighted impact score: New Building for severity/tail; New Houses for tail plus volume; Building Additions/Alterations for high-volume monitoring. A manager should review case complexity, revision handling and quarantine concentration before adopting this shortlist.
''')
    Path('docs/findings_recommendations.md').write_text('\n'.join(sections))


if __name__=='__main__':
    report()
