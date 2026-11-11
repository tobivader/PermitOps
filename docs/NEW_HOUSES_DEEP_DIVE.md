# New Houses | Where is the long review-time tail?

**Question:** Are unusually long review durations concentrated in revision groups or issuance periods?

**Recent issue window:** November 2025–October 2026. **Prior:** November 2024–October 2025. Eligible application dates start in 2018; revisions count separately. "Over 365 days" is a transparent analytical flag, not a legal service standard.

## 1. The tail is concentrated in original permits

There are 1,446 recent eligible issues and 151 reviews over 365 days (10.4%). Original permits account for 53.0% of issues but 86.8% of long reviews. This is a within-category investigation, not just a cross-category average.

| Revision group | Recent n | Median days | P90 days | Over 365 | Within-group rate |
|---|---:|---:|---:|---:|---:|
| Original (0) | 766 | 71 | 876.0 | 131 | 17.1% |
| Revision 1 | 446 | 44.5 | 125.0 | 13 | 2.9% |
| Revision 2+ | 234 | 51 | 94.4 | 7 | 3.0% |

The original-permit median remained **71 days**, while its P90 rose from **428.8 to 876 days**. Its over-year rate changed from **11.3% to 17.1%**. A stable median can coexist with a worsening long-duration tail. Different case mixes may explain the change; it is not proof of a process cause.

## 2. Long reviews cluster in Q1 2026 issuance

Q1 2026 has **364 issues**, including **119 over-year reviews** (32.7% within the quarter). It represents 25.2% of recent issued volume but 78.8% of recent over-year reviews. This is an issuance cohort: cases may have started years earlier. It does not mean all delay happened in Q1.

| Issue quarter | Eligible n | Median days | P90 days | Over 365 |
|---|---:|---:|---:|---:|
| 2024-10-01 | 165 | 51 | 285.4 | 11 |
| 2025-01-01 | 325 | 66 | 589.0 | 57 |
| 2025-04-01 | 361 | 43 | 234.0 | 28 |
| 2025-07-01 | 366 | 49 | 208.5 | 19 |
| 2025-10-01 | 352 | 61 | 233.0 | 7 |
| 2026-01-01 | 364 | 107 | 883.0 | 119 |
| 2026-04-01 | 429 | 55 | 157.0 | 13 |
| 2026-07-01 | 304 | 44 | 192.6 | 14 |
| 2026-10-01 | 172 | 51 | 117.0 | 1 |

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
