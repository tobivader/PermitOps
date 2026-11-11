# KPI contract

Grain: one non-conflicting normalized permit number + revision. Numeric revisions `00` and `0` normalize to `0`. Revisions remain separate. Conflicting analytical payloads across or within sources are quarantined, not arbitrarily assigned. Matching analytical payloads are deduplicated, preferring cleared. See `outputs/data_quality.json` for impact.

Terminal cancellations, refusals, withdrawals, revocations, abandonment, superseded/not-accepted records are excluded from lifecycle KPIs. Pending cancellation/revocation remains distinguishable active work. Non-permit administrative categories are excluded using the explicit list in `src/clean.py`; this classification needs data-owner review. All records remain traceable in local raw/staging tables.

| KPI | Eligibility / time basis | SQL |
|---|---|---|
| Applications | Valid non-future application date, nonterminal permit category; application month from 2018 through last complete month | vw_monthly_performance |
| Issued permits | Valid application and issued date; issued >= application, nonterminal category; application >= 2018; issued before current month | vw_issued_review_metrics |
| Median/P90 review days | Issued population above; issued minus application in calendar days; continuous percentile interpolation | vw_category_performance, vw_monthly_performance |
| Trend | Same issued population; last 12 complete issue months versus preceding 12; minimum 100 each | vw_bottlenecks |
| Active permits | Active-source, nonterminal/nonadministrative, excluding closed status; all application years; extract snapshot | vw_active_workload |
| Active unissued | Active above with missing issue date (not a parsing failure), valid nonfuture application date | vw_active_summary |
| Unissued age | As-of minus application; calendar days, not final review duration | vw_active_summary |
| Completion days | Valid review record plus completion >= issue/application and <= as-of | fact completion_eligible |

No outliers are winsorized or removed for being large. Impossible intervals are flagged; they do not enter the affected duration. A future completion date excludes completion duration but does not invalidate a valid application-to-issue interval. Missing issue dates are excluded from review durations, retained for active workload.

All counts are counts of complete permit/revision identifiers, not unique initial applications or buildings. "Issued permits" means issued records with computable valid review duration; missing/invalid-date issued records are not included. Denominators and exclusions are in the QA JSON. Monthly percentile values cannot be averaged into a larger period percentile. SQL and Power BI must recompute from eligible fact rows.

Current active extracts cannot reconstruct historical backlog. Current terminal status filters can also change historical issuance cohorts on refresh. Sources may refresh at different times; overlaps are measured, but the extract is not an atomic City database snapshot.
