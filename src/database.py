"""Transactional PostgreSQL load and reporting exports."""
import csv
import json
import os
import hashlib
from pathlib import Path
import pandas as pd
import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

DEFAULT_DSN = 'host=127.0.0.1 port=55432 dbname=postgres'
FACT_COLUMNS = ['permit_key','permit_num','revision_num','permit_type','status','source_dataset',
 'source_row_id','application_date','issued_date','completed_date','as_of_date',
 'application_eligible','review_eligible','active_eligible','active_unissued_eligible',
 'completion_eligible','review_days','active_age_days','completion_days']


def connect():
    return psycopg.connect(os.environ.get('PERMITOPS_DSN', DEFAULT_DSN))


def load(fact, qa):
    manifest = json.loads(Path('data/raw/manifest.json').read_text())
    with connect() as conn:
        conn.execute(Path('sql/01_schema.sql').read_text())
        # Dedicated project schema only; one transaction preserves prior run on failure.
        conn.execute('TRUNCATE permitops.fact_permit_lifecycle, permitops.stg_active_permits, '
                     'permitops.stg_cleared_permits, permitops.run_metadata')
        conn.execute('INSERT INTO permitops.run_metadata(as_of_date,manifest,qa) VALUES (%s,%s,%s)',
                     (qa['as_of'], Jsonb(manifest), Jsonb(qa)))
        for source in ['active','cleared']:
            d = pd.read_csv(f'data/raw/{source}.csv', dtype=str, keep_default_na=False)
            with conn.cursor().copy(sql.SQL('COPY permitops.{} (source_dataset,source_row_id,permit_key,payload) FROM STDIN').format(
                    sql.Identifier(f'stg_{source}_permits'))) as cp:
                for row in d.to_dict('records'):
                    revision = row['REVISION_NUM'].lstrip('0') or '0'
                    cp.write_row((source,row['_id'],row['PERMIT_NUM'].strip()+'|'+revision,Jsonb(row)))
        safe = fact[FACT_COLUMNS].astype(object).where(pd.notna(fact[FACT_COLUMNS]), None)
        for col in ['application_date','issued_date','completed_date','as_of_date']:
            safe[col] = safe[col].map(lambda v: v.date() if v is not None else None)
        for col in ['review_days','active_age_days','completion_days']:
            # Construct object dtype directly: map would coerce int+None back to float.
            safe[col] = pd.Series([int(v) if v is not None else None for v in safe[col]],
                                  index=safe.index, dtype=object)
        statement = sql.SQL('COPY permitops.fact_permit_lifecycle ({}) FROM STDIN').format(
            sql.SQL(',').join(map(sql.Identifier, FACT_COLUMNS)))
        with conn.cursor().copy(statement) as cp:
            for row in safe.itertuples(index=False, name=None):
                cp.write_row(row)
        for filename in ['02_transform.sql','03_metrics.sql']:
            conn.execute((Path('sql')/filename).read_text())


def export():
    dest = Path('outputs/reporting')
    dest.mkdir(parents=True, exist_ok=True)
    # Every multi-column export has a unique (first, second) grouping key.
    # Resolve peer order explicitly; dim_permit_type is the single-column exception.
    queries = {name: f'SELECT * FROM permitops.{name} ORDER BY '
               + ('1' if name == 'dim_permit_type' else '1,2') for name in
               ['dim_date','dim_permit_type','vw_monthly_performance','vw_category_performance',
                'vw_active_summary','vw_bottlenecks','vw_monthly_trend']}
    queries['fact_reporting'] = '''SELECT permit_key,permit_type,revision_num,application_date,
     issued_date,completed_date,source_dataset,status,as_of_date,application_eligible,
     review_eligible,active_eligible,active_unissued_eligible,review_days,active_age_days,
     completion_days FROM permitops.fact_permit_lifecycle ORDER BY permit_key'''
    queries['original_revision_sensitivity'] = '''SELECT permit_type,count(*) AS issued,
     percentile_cont(0.5) WITHIN GROUP(ORDER BY review_days) AS median_days,
     percentile_cont(0.9) WITHIN GROUP(ORDER BY review_days) AS p90_days
     FROM permitops.vw_issued_review_metrics WHERE revision_num='0' GROUP BY 1 ORDER BY 1'''
    with connect() as conn:
        for name, query in queries.items():
            cur = conn.execute(query)
            temp = dest/f'{name}.partial'
            with temp.open('w') as f:
                w = csv.writer(f); w.writerow([c.name for c in cur.description]); w.writerows(cur)
            temp.replace(dest/f'{name}.csv')
    manifest = {}
    for path in sorted(dest.glob('*.csv')):
        with path.open('rb') as f:
            manifest[path.name] = {'sha256':hashlib.file_digest(f,'sha256').hexdigest(),
                                    'bytes':path.stat().st_size}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return dest
