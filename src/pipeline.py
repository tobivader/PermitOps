import argparse
import json
from pathlib import Path
from .ingest import ingest
from .clean import clean
from .database import load, export


def main():
    p = argparse.ArgumentParser(description='Real Toronto permit ingestion, QA, PostgreSQL, exports')
    p.add_argument('--download', action='store_true')
    p.add_argument('--as-of', required=True, help='ISO snapshot date, not a historical backlog date')
    args = p.parse_args()
    if args.download:
        ingest()
    manifest = json.loads(Path('data/raw/manifest.json').read_text())
    import hashlib
    for source, info in manifest.items():
        with open(f'data/raw/{source}.csv','rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest() != info['sha256']:
                raise ValueError(f'{source}: raw checksum mismatch; retrieve a consistent snapshot')
        if args.as_of < info['retrieved_at'][:10]:
            raise ValueError('As-of precedes extract date; historical snapshot would be misleading')
    fact, qa = clean(args.as_of)
    load(fact,qa)
    from .validate import validate
    result = validate(fact,qa)
    export()
    from .report import report
    report()
    from .charts import charts
    charts()
    from .build_dashboard import build
    build()
    from .portfolio_report import write_reports
    write_reports()
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
