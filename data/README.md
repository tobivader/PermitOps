# Data provenance

Contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/). Data provider: City of Toronto. This project is independent and is not endorsed by the City.

- [Active permits](https://open.toronto.ca/dataset/building-permits-active-permits/)
- [Cleared permits](https://open.toronto.ca/dataset/building-permits-cleared-permits/)

`raw/manifest.json` records retrieval times, resource URLs, byte sizes and SHA-256 hashes. Saved CKAN metadata identifies resources and available refresh fields. The two downloads are separate extracts, not an atomic transaction. Dataset records currently extend through November 9, 2026 in several lifecycle fields even though extraction is November 11.

Large raw/cleaned CSVs, database files and record-level reporting CSV are ignored by Git. They include unnecessary descriptive/address/builder fields; keep them local. Aggregated reporting CSVs omit those fields. The pipeline retrieves real records; fixtures in tests are synthetic and are never used for findings.

Regenerate raw data with `.venv/bin/python -m src.ingest` or the pipeline's `--download` option. Regenerating retrieves the current snapshot, so results can change. To reproduce this session's exact numbers, retain the original local CSVs and matching manifest. Source-side corrections can also change historical results.
