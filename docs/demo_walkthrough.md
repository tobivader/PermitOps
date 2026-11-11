# Five-minute portfolio walkthrough

1. **Decision (30 seconds):** A hypothetical permit operations manager needs to decide which categories merit workflow investigation. Calendar days measure elapsed lifecycle time, not staff effort or legal compliance.
2. **Data trust (60 seconds):** Show the City source URLs, manifest hashes, QA report and conflicting-key quarantine. Explain why permit revisions are separate records and why keeping an arbitrary repeated row would distort categories.
3. **Pipeline (60 seconds):** Show `src/pipeline.py`, the clean eligibility flags, PostgreSQL staging/fact tables and one reusable percentile query. Show `outputs/validation.json` and the edge-case test command.
4. **Decision evidence (90 seconds):** Open findings and the bottleneck CSV. Explain the New Building long tail alongside its improved median, New Houses volume/tail, and high-volume Additions/Alterations monitoring. Show that most active permits have already been issued, so open count is not synonymous with initial-review backlog.
5. **Limits and next step (60 seconds):** Open the public three-page web dashboard and explain its snapshot scope. Distinguish it from the optional Power BI handoff, whose runtime remains untested. Describe source-owner review of conflicting keys and administrative classifications. Do not claim an operational improvement or a completed PBIX.

## Truthful resume bullet drafts

- Built a Python/PostgreSQL analytics pipeline for 649,376 Toronto building-permit records, with source fingerprinting, conflicting-key quarantine and explicit lifecycle eligibility rules.
- Developed reusable SQL views for permit volumes, median/P90 review time, equal-window category comparisons and current active workload; reconciled calculations against independent pandas checks.
- Published a three-page browser dashboard with date/category filters and SQL-validated percentiles; investigated New Houses revision groups and issue-quarter concentration, with 16 calculation/interface tests and genuine dashboard screenshots.

Numbers describe the November 11, 2026 extract and should be updated if refreshed.
