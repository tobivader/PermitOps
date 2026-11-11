# Publication handoff

The local project is ready for repository review. Public GitHub publication has not happened. GitHub CLI is absent, the GitHub plugin is unconnected, and the computer-use environment reported no available browser. No credentials were inspected and no remote was invented.

## Before publishing

- Review README, findings, definitions and BUILD_STATUS for accurate claims.
- Keep raw/cleaned records, PostgreSQL, virtual environment and the local Power BI ZIP outside Git. `.gitignore` covers these paths.
- Retain the City attribution and licence link; no City endorsement is implied.
- Keep actual Power BI/DAX execution and screenshot status explicit. The analysis figures are not Power BI screenshots.
- `git status --short` should show no accidental record-level data. Git attributes preserve CSV bytes so the saved export fingerprints remain meaningful after checkout.

## Remaining external step

Install/connect the GitHub plugin to continue publication through the account you choose. The candidate repository name is PermitOps; visibility and the final repository URL must come from a completed GitHub action, not a guessed link. Alternatively, use your own authenticated Git client to create a repository and push this local repository.

After publication, verify the remote default branch contains the source, SQL, tests, README, aggregate exports and figures. Check that README images render, links resolve and the excluded large/local files are absent. Only then add the observed public URL to the project status and portfolio.
