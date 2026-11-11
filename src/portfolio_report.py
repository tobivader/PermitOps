"""Produce a concise executive brief and a reproducible New Houses investigation."""
import json
from pathlib import Path


def write_reports():
    dive=json.loads(Path('outputs/new_houses_deep_dive.json').read_text())
    refs=json.loads(Path('outputs/dashboard_sql_reference.json').read_text())
    all_recent=refs[0]; houses=refs[1]; building=refs[2]
    recent=[r for r in dive['revisions'] if r['period']=='Recent']
    prior=[r for r in dive['revisions'] if r['period']=='Prior']
    original=next(r for r in recent if r['revision_group']=='Original (0)')
    old_original=next(r for r in prior if r['revision_group']=='Original (0)')
    count=sum(r['issued'] for r in recent);tail=sum(r['over_365'] for r in recent)
    first_quarter=next(r for r in dive['quarters'] if r['quarter']=='2026-01-01')
    summary=f'''# PermitOps | Executive findings brief

**Decision:** Which Toronto permit categories should an operations manager investigate first?

**Reporting period:** November 2025–October 2026. Active workload: November 11, 2026 snapshot, all application years. Historical review metrics use applications from 2018 onward. One record represents a permit and revision, not a building project.

## The operating picture

{all_recent['issued']:,} eligible issued records · **{all_recent['median']:g}-day median review** · **{all_recent['p90']:g}-day P90**. Current active workload is 194,325 records; 13,580 are unissued. Calendar days include applicant response time.

## Three findings and actions

1. **New Building has the longest typical review among categories meeting the volume rule.** {building['issued']:,} recent issues; median {building['median']:g} days; P90 {building['p90']:g} days. Its median decreased from 155.5 days in the prior issue-year. **Action:** audit the long-duration tail for application completeness and case complexity; track median/P90 alongside unresolved age.

2. **New Houses needs a targeted original-permit investigation.** {count:,} recent issues; median {houses['median']:g} days; P90 {houses['p90']:.1f} days. {original['over_365']} of {tail} reviews over 365 days ({original['over_365']/tail:.1%}) were original permits, which comprised {original['issued']/count:.1%} of issues. **Action:** sample original cases over one year, compare applicant/city handoff dates and review the Q1 2026 issuance concentration. Timestamps alone do not explain the pattern.

3. **Active permits and waiting-for-issuance workload answer different questions.** Only 7.0% of eligible active records are unissued. **Action:** manage the unissued queue separately from construction/inspection activity, validate very old statuses, and track median/P90 unissued age at future snapshots.

## Confidence and follow-through

10,730 conflicting-key source rows are quarantined. Terminal/administrative exclusions and unresolved-case censoring limit interpretation. Comparisons are descriptive, not case-mix adjusted; 365 days is an investigation threshold, not an SLA. No staffing or causal improvement is claimed.

Use the three-page web dashboard for date/category exploration, then inspect the [New Houses evidence](NEW_HOUSES_DEEP_DIVE.md). Keep an initial case-review log and evaluate subsequent comparable cohorts before proposing a process intervention.

Source: City of Toronto Open Data. Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/). Independent portfolio case study; no City endorsement.
'''
    Path('docs/EXECUTIVE_SUMMARY.md').write_text(summary)
    lines=[f'''# New Houses | Where is the long review-time tail?

**Question:** Are unusually long review durations concentrated in revision groups or issuance periods?

**Recent issue window:** November 2025–October 2026. **Prior:** November 2024–October 2025. Eligible application dates start in 2018; revisions count separately. "Over 365 days" is a transparent analytical flag, not a legal service standard.

## 1. The tail is concentrated in original permits

There are {count:,} recent eligible issues and {tail} reviews over 365 days ({tail/count:.1%}). Original permits account for {original['issued']/count:.1%} of issues but {original['over_365']/tail:.1%} of long reviews. This is a within-category investigation, not just a cross-category average.

| Revision group | Recent n | Median days | P90 days | Over 365 | Within-group rate |
|---|---:|---:|---:|---:|---:|''']
    for r in recent:
        lines.append(f"| {r['revision_group']} | {r['issued']:,} | {r['median_days']:g} | {r['p90_days']:.1f} | {r['over_365']} | {r['over_365']/r['issued']:.1%} |")
    lines.append(f'''
The original-permit median remained **{original['median_days']:g} days**, while its P90 rose from **{old_original['p90_days']:.1f} to {original['p90_days']:g} days**. Its over-year rate changed from **{old_original['over_365']/old_original['issued']:.1%} to {original['over_365']/original['issued']:.1%}**. A stable median can coexist with a worsening long-duration tail. Different case mixes may explain the change; it is not proof of a process cause.

## 2. Long reviews cluster in Q1 2026 issuance

Q1 2026 has **{first_quarter['issued']:,} issues**, including **{first_quarter['over_365']} over-year reviews** ({first_quarter['over_365']/first_quarter['issued']:.1%} within the quarter). It represents {first_quarter['issued']/count:.1%} of recent issued volume but {first_quarter['over_365']/tail:.1%} of recent over-year reviews. This is an issuance cohort: cases may have started years earlier. It does not mean all delay happened in Q1.

| Issue quarter | Eligible n | Median days | P90 days | Over 365 |
|---|---:|---:|---:|---:|''')
    for r in dive['quarters']:
        lines.append(f"| {r['quarter']} | {r['issued']:,} | {r['median_days']:g} | {r['p90_days']:.1f} | {r['over_365']} |")
    lines.append('''
**Quarter coverage:** Q4 2024 contains November–December only; Q4 2026 contains October only. Do not compare those partial quarters as full-quarter volumes. Q1 2026 is complete. Q4 2025 crosses the boundary between the prior and recent 12-month windows; the recent-tail share above uses the complete Q1 2026 subset within the recent window.

## 3. What a manager should investigate

1. Sample original New Houses permits with over-year reviews, stratifying Q1 2026 and other issue quarters; include a sample below the threshold for comparison.
2. Ask the data owner for stage timestamps: application completeness, city review, applicant response, resubmission and issue entry/corrections. Look for case complexity or batch issuance of old applications; these are hypotheses to investigate, not observed causes.
3. Validate the revision interpretation and any status/date corrections. An original/revision record is not a randomized comparison, and the same building may appear across separate permits.
4. Track the original-permit P90 and over-year rate alongside issuance volume and unissued-age percentiles. A shorter completed duration without checking unresolved ages may hide displacement into the open queue.

## Evidence and limits

- `sql/06_dashboard.sql`: reusable revision and issue-quarter views.
- `outputs/new_houses_deep_dive.json`: source results and 15 SQL-versus-pandas group checks, all passed.
- `src/build_dashboard.py`: regenerates SQL data and verifies group counts, medians, P90s and revision-group long-review counts independently from the local fact CSV.
- Conflicting-key rows remain quarantined, including 2,410 raw New Houses rows across both full extracts. This count is not the recent cohort's exclusion denominator. No sensitivity that resolves these ambiguous identities is claimed.
- Current terminal-status filters, separate extracts, issue-cohort censoring, classification/case mix and application-year restrictions may change the comparison. No cause, statistical significance or operational improvement is established.
''')
    Path('docs/NEW_HOUSES_DEEP_DIVE.md').write_text('\n'.join(lines))


if __name__=='__main__':write_reports()
