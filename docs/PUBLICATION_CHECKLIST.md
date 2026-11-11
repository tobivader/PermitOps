# Publication verification

Published repository: https://github.com/tobivader/PermitOps . The user supplied this destination. The empty remote was checked before the first push, and local main was pushed successfully. GitHub's unauthenticated repository API confirmed private=false and default_branch=main. Initial source commit: 8cae14230b54644dc6195c69bd8363ad0af44696.

Git push worked with the existing Git authentication environment. No GitHub CLI, plugin or browser connection was needed, and no credentials were inspected. Earlier journal entries describing a missing publication connection are historical; this successful publication supersedes that blocker.

## Repository contents

- Python pipeline, SQL schema/views, cleaning and PostgreSQL regression tests.
- README, business/KPI/data-quality documentation, learning guide and findings.
- Aggregated reporting CSVs, validation/reproducibility evidence and analysis PNG/SVG charts.
- Power BI instructions, DAX and typed Power Query templates, explicitly marked untested in Power BI.

Raw/cleaned records, PostgreSQL files, virtual environment, record-level reporting CSV and Windows handoff ZIP are ignored and were checked absent from the tracked snapshot. Generated CSV hashes match committed blobs. City attribution and the Toronto licence link are retained; no City endorsement is implied.

## Follow-up

Actual Power BI Desktop execution, visuals, drill-through, slicers and screenshots remain future work on Windows. Static analysis figures are not dashboard screenshots. Verify Power BI values against SQL reference outputs before describing that report as complete. Source-owner review of conflicting keys and administrative exclusions remains an analytical limitation.
