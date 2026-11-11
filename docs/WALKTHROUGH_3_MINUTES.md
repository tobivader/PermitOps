# Three-minute manager walkthrough

This is the narration and shot plan for the actual web dashboard. A three-minute narrated, screenshot-based tour is provided at `dashboard/recordings/PermitOps_3_Minute_Manager_Tour.mp4`. It uses genuine live-dashboard captures and computer-generated narration; it is not a continuous screen recording or the project owner's recorded voice. The reproducible video builder and duration/decode checks are in `src/build_tour.py` and `outputs/tour_manifest.json`. Use this script to practice and record your own explanation afterward.

## 0:00–0:25 | Decision and source

Show Executive overview with all categories and the default period.

"PermitOps answers one operational question: which Toronto permit categories merit investigation? I used 649,376 real City of Toronto records, built a Python and PostgreSQL pipeline, and created this browser dashboard so it runs on a Mac. The reporting window here is November 2025 through October 2026."

## 0:25–0:55 | Executive performance

Point to the four cards, then the two trend charts.

"There are 37,074 eligible applications in their application-month cohort and 35,876 issues in their issue-month cohort. Those are different populations, so this is not a conversion rate. The issue cohort has a 28-day median and a 141-day P90. I show both because a typical case can look stable while the slow tail changes. All durations are calendar days."

## 0:55–1:30 | Category investigation

Open Bottleneck analysis. Show category median comparisons and volume-versus-duration scatter. Select New Houses, then reset if needed.

"New Building has a high median and a long tail, but its median decreased versus the prior issue-year. I would not label it worsening without that context. For New Houses, the recent cohort contains 1,446 issues, a 52-day median and a 419.5-day P90. Date/category filters recompute percentiles from frequency distributions, not averages of monthly medians."

## 1:30–2:10 | New Houses deep dive

Scroll to the revision spotlight; show the three revision groups. Refer to the deep-dive document for the issue-quarter table.

"Original permits are about 53% of recent New Houses issues, but account for 131 of the 151 reviews over a year, about 87%. Their median stayed at 71 days while P90 rose from 428.8 to 876 days. Q1 2026 contains 119 of those 151 long reviews. That suggests a focused case audit, not a proven explanation. These are issuance cohorts: the delay may have accumulated earlier."

## 2:10–2:40 | Active workload

Open Active workload, point to the issuance-state chart and unissued-age buckets, then the oldest-category table.

"There are 194,325 eligible active permits, but only 13,580 are unissued. An issued active permit can still be in construction or inspection. The date controls are disabled here because this is one snapshot across all application years. I would validate very old statuses and applicant response history before calling this city review backlog."

## 2:40–3:00 | Trust and action

Open Metric definitions & data quality.

"I quarantined conflicting identities, documented exclusions and checked the metrics against SQL. The recommendation is to audit original New Houses cases and the Q1 issuance concentration, then monitor P90 and unresolved ages together. I have not claimed a cause, a legal SLA or an operational improvement that was never measured."

## Practice before recording your own narration

Explain median versus mean, continuous P90 interpolation, permit/revision grain, quarantine trade-offs, complete-month windows, unresolved-case censoring and the difference between issued active and unissued. Be able to change one filter and reproduce its answer in SQL.
