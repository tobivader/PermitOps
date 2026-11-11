import pandas as pd
import pytest
from src.clean import normalize, clean


def row(**overrides):
    d={'_id':'1','PERMIT_NUM':' 26 123 BLD ','REVISION_NUM':'00','PERMIT_TYPE':'New Building',
       'STATUS':'Under Review ','APPLICATION_DATE':'2026-01-01','ISSUED_DATE':'', 'COMPLETED_DATE':''}
    return d | overrides


def test_zero_revision_and_whitespace():
    d=normalize(pd.DataFrame([row(),row(REVISION_NUM='0')]),'active','2026-11-11')
    assert d.permit_key.nunique()==1
    assert d.status.iloc[0]=='Under Review'


def test_missing_invalid_and_future_dates_remain_distinct():
    d=normalize(pd.DataFrame([row(),row(ISSUED_DATE='not-a-date'),row(ISSUED_DATE='2028-01-01')]),'active','2026-11-11')
    assert d.issued_date_invalid.tolist()==[False,True,False]
    assert d.issued_date_future.tolist()==[False,False,True]


def test_negative_chronology():
    d=normalize(pd.DataFrame([row(ISSUED_DATE='2025-12-31',COMPLETED_DATE='2025-12-30')]),'cleared','2026-11-11')
    assert d.negative_review.iloc[0] and d.negative_completion.iloc[0]


def test_schema_drift_fails_loudly():
    with pytest.raises(ValueError,match='missing required columns'):
        normalize(pd.DataFrame([{'PERMIT_NUM':'x'}]),'active','2026-11-11')


def test_conflicts_dedup_and_metric_exclusions(tmp_path,monkeypatch):
    # Explicit synthetic test fixtures, never used as project findings.
    monkeypatch.chdir(tmp_path)
    raw=tmp_path/'raw'; raw.mkdir()
    active=[row(),row(_id='2'),
            row(_id='3',PERMIT_NUM='conflict',ISSUED_DATE='2026-02-01'),
            row(_id='4',PERMIT_NUM='negative',ISSUED_DATE='2025-01-01'),
            row(_id='5',PERMIT_NUM='cancelled',STATUS='Cancelled'),
            row(_id='6',PERMIT_NUM='bad-date',ISSUED_DATE='bad'),
            row(_id='7',PERMIT_NUM='future-completion',ISSUED_DATE='2026-02-01',COMPLETED_DATE='2028-01-01')]
    cleared=[row(_id='1',PERMIT_NUM='conflict',ISSUED_DATE='2026-03-01',STATUS='Closed')]
    pd.DataFrame(active).to_csv(raw/'active.csv',index=False)
    pd.DataFrame(cleared).to_csv(raw/'cleared.csv',index=False)
    fact,qa=clean('2026-11-11',raw,tmp_path/'clean')
    assert qa['input_rows']==8 and qa['quarantined_rows']==2 and qa['duplicate_rows_removed']==1
    assert 'conflict|0' not in set(fact.permit_key)
    f=fact.set_index('permit_num')
    assert not f.loc['negative','review_eligible']
    assert not f.loc['cancelled','active_eligible']
    assert not f.loc['bad-date','active_unissued_eligible']
    assert f.loc['future-completion','review_eligible']
    assert not f.loc['future-completion','completion_eligible']
    assert f.loc['26 123 BLD','active_unissued_eligible']
