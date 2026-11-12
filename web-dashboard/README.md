# PermitOps manager dashboard

Public dashboard: https://permitops-operations.smalliris16.chatgpt.site

A buildless, three-page web report for macOS and modern browsers. No production JavaScript dependencies, external chart service, login or database connection are required for a manager to open it. Published data is a dated, anonymous aggregate snapshot, not a live feed.

## Run on a Mac

From the repository root:

```bash
node web-dashboard/build.mjs
python3 -m http.server 8765 --directory web-dashboard/dist
```

Open http://localhost:8765 . You can also open the generated index.html locally because the report loads a local data script rather than calling an API.

To refresh from a validated local PostgreSQL pipeline:

```bash
.venv/bin/python -m src.build_dashboard
.venv/bin/python -m src.portfolio_report
node web-dashboard/build.mjs
cd web-dashboard
npm ci
npm test
```

Publication is a separate, deliberate step; a local refresh does not silently change the public report. The Sites identity is recorded in `.openai/hosting.json`; source credentials are never stored in the repository. The managed hosting checkout is isolated under the root `.local/` folder, which is excluded from GitHub.

## Metric behavior

- Executive/Bottleneck date controls select complete issue months and application months independently. The default window is November 2025–October 2026. Prior comparison is an equally long preceding interval; if it starts before 2018, the baseline is unavailable.
- Category selectors and category-table buttons recalculate the distributions. Exact median/P90 use record ranks over frequency counts, matching PostgreSQL percentile_cont interpolation. Monthly medians are never averaged into period medians.
- Category severity charts require at least 100 selected-period issues; the comparison flag requires 100 in both windows. Small counts remain visible and qualified in the evidence table.
- Active workload keeps a November 11, 2026 snapshot across all application years. Historical date controls are disabled on that page; category filtering still applies.
- The New Houses revision spotlight is an explicitly labeled fixed reference cohort, independent of page filters. The full period/revision investigation is in `docs/NEW_HOUSES_DEEP_DIVE.md`.
- CSV export contains the current view's metrics and cohort labels, not individual records.

## Verification

`engine.test.cjs` compares six date/category selections and every active category to independent PostgreSQL references, plus known interpolation and period-boundary cases. `interface.test.cjs` executes the actual application in jsdom and checks navigation, exact New Houses cards, workload filters, empty cohorts, date validation/reset and CSV export construction.

Sixteen tests passed. Actual desktop Chrome inspection and screenshots are recorded in the build status: all three pages were inspected, the Mechanical workload filter matched SQL (2,374 unissued), and Reset restored 13,580. Responsive CSS is implemented, but mobile-device behavior has not been tested in a real narrow viewport.

The dataset builder also independently verifies 15 SQL revision/quarter groups against pandas. Source hashes, data sizes and anonymity are documented in `outputs/dashboard_data_manifest.json`. The frequency dataset contains no permit IDs, addresses, builder names or descriptions.


## Visual direction — version 2

The editorial field-report design takes inspiration from Konrad's current black/white palette, electric-blue accents and oversized typography (https://www.konrad.com/). PermitOps has its own cut-corner P monogram, architectural SVG illustration, warm paper canvas, numbered horizontal navigation, joined metric strip and restrained green analytical surfaces. The illustration is decorative, not geographic data. Motion respects prefers-reduced-motion. No Konrad logo, proprietary font or site assets were reused.

Sixteen existing dashboard tests passed after the structure/palette update. The desktop local preview was visually inspected. Subsequent native Chrome control timed out, so the existing screenshots and tour are explicitly retained as version 1 captures; no new screenshots were fabricated. Real mobile visual QA remains unperformed.
