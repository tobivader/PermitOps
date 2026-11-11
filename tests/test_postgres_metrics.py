"""Small synthetic regression dataset: never an input to portfolio findings.

Requires an explicitly selected disposable database named permitops_test.
The normal development PostgreSQL database is never selected implicitly.
"""
import json
import os
from pathlib import Path
import shutil

import pandas as pd
import psycopg
import pytest

from src.clean import clean
from src.database import load
from src.validate import validate


@pytest.mark.skipif(not os.environ.get('PERMITOPS_TEST_DSN'),reason='PERMITOPS_TEST_DSN not configured')
def test_postgres_metrics_match_known_calendar_intervals(tmp_path,monkeypatch):
    dsn=os.environ['PERMITOPS_TEST_DSN']
    with psycopg.connect(dsn) as conn:
        if conn.execute('SELECT current_database()').fetchone()[0] != 'permitops_test':
            pytest.fail('Refusing to replace project tables outside the permitops_test database')
    monkeypatch.setenv('PERMITOPS_DSN',dsn)
    shutil.copytree(Path(__file__).resolve().parents[1]/'sql',tmp_path/'sql')
    monkeypatch.chdir(tmp_path)
    raw=Path('data/raw'); raw.mkdir(parents=True)
    base={'PERMIT_TYPE':'Test Permit','REVISION_NUM':'00','STATUS':'Closed',
          'ISSUED_DATE':'2025-11-01','COMPLETED_DATE':'2026-01-01'}
    # Application→issue intervals are exactly 0, 10, 20, 40, 100 calendar days.
    dates=['2025-11-01','2025-10-22','2025-10-12','2025-09-22','2025-07-24']
    cleared=[base|{'_id':str(i),'PERMIT_NUM':f'SYNTHETIC-{i}','APPLICATION_DATE':date}
             for i,date in enumerate(dates,1)]
    active=[base|{'_id':'1','PERMIT_NUM':'SYNTHETIC-UNISSUED','STATUS':'Under Review',
                   'APPLICATION_DATE':'2026-10-01','ISSUED_DATE':'','COMPLETED_DATE':''}]
    pd.DataFrame(active).to_csv(raw/'active.csv',index=False)
    pd.DataFrame(cleared).to_csv(raw/'cleared.csv',index=False)
    (raw/'manifest.json').write_text(json.dumps({'test_fixture':'synthetic, not real findings'}))
    fact,qa=clean('2026-11-11')
    load(fact,qa)
    with psycopg.connect(dsn) as conn:
        result=conn.execute('SELECT issued,median_review_days,p90_review_days FROM permitops.vw_category_performance').fetchone()
        assert result==pytest.approx((5,20,76))
        age=conn.execute('SELECT active_age_days FROM permitops.vw_active_workload').fetchone()[0]
        assert age==41
        month=conn.execute("SELECT applications,issued FROM permitops.vw_monthly_performance WHERE month=date '2025-11-01'").fetchone()
        assert month==(1,5)
    assert validate(fact,qa)['all_passed']
