# PermitOps | Executive findings brief

**Decision:** Which Toronto permit categories should an operations manager investigate first?

**Reporting period:** November 2025–October 2026. Active workload: November 11, 2026 snapshot, all application years. Historical review metrics use applications from 2018 onward. One record represents a permit and revision, not a building project.

## The operating picture

35,876 eligible issued records · **28-day median review** · **141-day P90**. Current active workload is 194,325 records; 13,580 are unissued. Calendar days include applicant response time.

## Three findings and actions

1. **New Building has the longest typical review among categories meeting the volume rule.** 231 recent issues; median 79 days; P90 866 days. Its median decreased from 155.5 days in the prior issue-year. **Action:** audit the long-duration tail for application completeness and case complexity; track median/P90 alongside unresolved age.

2. **New Houses needs a targeted original-permit investigation.** 1,446 recent issues; median 52 days; P90 419.5 days. 131 of 151 reviews over 365 days (86.8%) were original permits, which comprised 53.0% of issues. **Action:** sample original cases over one year, compare applicant/city handoff dates and review the Q1 2026 issuance concentration. Timestamps alone do not explain the pattern.

3. **Active permits and waiting-for-issuance workload answer different questions.** Only 7.0% of eligible active records are unissued. **Action:** manage the unissued queue separately from construction/inspection activity, validate very old statuses, and track median/P90 unissued age at future snapshots.

## Confidence and follow-through

10,730 conflicting-key source rows are quarantined. Terminal/administrative exclusions and unresolved-case censoring limit interpretation. Comparisons are descriptive, not case-mix adjusted; 365 days is an investigation threshold, not an SLA. No staffing or causal improvement is claimed.

Use the three-page web dashboard for date/category exploration, then inspect the [New Houses evidence](NEW_HOUSES_DEEP_DIVE.md). Keep an initial case-review log and evaluate subsequent comparable cohorts before proposing a process intervention.

Source: City of Toronto Open Data. Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/). Independent portfolio case study; no City endorsement.
