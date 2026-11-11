# Data dictionary

Observed input headers are identical in both downloaded CSVs (32 columns). Dates are ISO `YYYY-MM-DD`; empty strings represent missing values. All fields initially load as text to preserve identifiers. Exact field inventory and observed missing counts: `outputs/data_quality.json`. Category/status labels are source text, trimmed for analysis. No unsupported category merging is performed.

| Raw column | Treatment / meaning used |
|---|---|
| _id | Resource-local row identifier; not a stable cross-source permit key |
| PERMIT_NUM | Complete base identifier text, including suffix; never cast to a number |
| REVISION_NUM | Revision identifier; digit strings normalize leading zeros, nonnumeric values retained |
| PERMIT_TYPE | Source category; administrative categories explicitly flagged |
| STRUCTURE_TYPE | Source structural classification; retained in staging, unused in MVP KPIs |
| WORK | Source work classification; retained, suitable for later case-mix checks |
| STREET_NUM, STREET_NAME, STREET_TYPE, STREET_DIRECTION | Address components, retained locally in staging; not in report exports |
| POSTAL | Source postal fragment; unused, not geocoded |
| GEO_ID | Source geographic identifier; not validated for joins in this build |
| WARD_GRID | Source ward/grid field; unused pending geographic validation |
| APPLICATION_DATE | Start of elapsed review interval and active age |
| ISSUED_DATE | End of elapsed review interval; missing differs from invalid |
| COMPLETED_DATE | Cleared lifecycle date; not proof of a successful project for every status |
| STATUS | Source workflow status; cancellations and other terminal exclusions are explicit in clean.py |
| DESCRIPTION, CURRENT_USE, PROPOSED_USE | Source descriptive fields; retained locally, not parsed or published in exports |
| DWELLING_UNITS_CREATED, DWELLING_UNITS_LOST | Source unit fields, unused; no totals claimed |
| EST_CONST_COST | Source estimated cost field, unused; not an actual expenditure measure |
| ASSEMBLY, INSTITUTIONAL, RESIDENTIAL, BUSINESS_AND_PERSONAL_SERVICES, MERCANTILE, INDUSTRIAL, INTERIOR_ALTERATIONS, DEMOLITION | Source classification/area fields; retained as text; units and completeness not independently validated |
| BUILDER_NAME | Retained locally only; excluded from reporting output |

The City’s [source explanation](https://open.toronto.ca/exploring-cleared-building-permits/) describes permit plus revision identity, lifecycle intervals, and historical classification changes. Current raw resource metadata is saved under `data/raw/*_metadata.json`. The current cleared datastore covers completions since 2017; an older 2000–2016 resource exists but is not combined with this MVP.

## Derived fact fields

`permit_key` = trimmed permit number + `|` + normalized revision. `source_dataset`, `source_row_id`, and manifest hashes provide lineage. `as_of_date` is the snapshot reference, not proof of row-level freshness.

`*_invalid`, `*_future`, `negative_review`, `negative_completion`, `conflicting_key` and `invalid_key` remain in local cleaned audit outputs. Fact eligibility flags determine application, review, active, active-unissued and completion inclusion independently. Review days = issue minus application; active age = snapshot minus application; completion days = completion minus issue, each only populated for its valid eligible population.

`dim_date` is one row per date from 2018 to snapshot. `dim_permit_type` has one row per fact category. `vw_monthly_performance` has one row per full month/category, including zeros; its medians/P90 are nullable when no cases qualify. Active summary grain is category/age bucket. Bottleneck grain is category across two fixed issue windows with at least 100 records in each.
