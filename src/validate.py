"""Independent pandas-versus-PostgreSQL checks, persisted as evidence."""
import json
import math
from pathlib import Path
import pandas as pd
from .database import connect


def validate(fact,qa):
    checks = {}
    def check(name,condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(f'Validation failed: {name}')
    check('row_accounting',qa['input_rows']==qa['fact_rows']+qa['quarantined_rows']+qa['duplicate_rows_removed'])
    check('unique_fact_key',fact.permit_key.is_unique)
    end = pd.Timestamp(qa['as_of']).replace(day=1)
    r = fact[fact.review_eligible & fact.application_date.ge('2018-01-01') & fact.issued_date.lt(end)]
    with connect() as conn:
        for source in ['active','cleared']:
            count = conn.execute(f'SELECT count(*) FROM permitops.stg_{source}_permits').fetchone()[0]
            check(source+'_staging_count',count==qa['sources'][source]['input_rows'])
        check('sql_fact_count',conn.execute('SELECT count(*) FROM permitops.fact_permit_lifecycle').fetchone()[0]==len(fact))
        n,med,p90 = conn.execute('''SELECT count(*),percentile_cont(.5) WITHIN GROUP(ORDER BY review_days),
             percentile_cont(.9) WITHIN GROUP(ORDER BY review_days) FROM permitops.vw_issued_review_metrics''').fetchone()
        check('review_count',n==len(r))
        check('review_median',math.isclose(float(med),float(r.review_days.median()),abs_tol=1e-8))
        check('review_p90',math.isclose(float(p90),float(r.review_days.quantile(.9)),abs_tol=1e-8))
        monthly = conn.execute('SELECT sum(issued),sum(applications) FROM permitops.vw_monthly_performance').fetchone()
        a = fact[fact.application_eligible & fact.application_date.ge('2018-01-01') & fact.application_date.lt(end)]
        check('monthly_issued_reconciliation',monthly[0]==len(r))
        check('monthly_applications_reconciliation',monthly[1]==len(a))
        sql_groups = conn.execute('SELECT permit_type,issued,median_review_days,p90_review_days FROM permitops.vw_category_performance').fetchall()
        for category,count,m,p in sql_groups:
            values = r.loc[r.permit_type.eq(category),'review_days']
            check(f'category:{category}',count==len(values) and math.isclose(m,values.median(),abs_tol=1e-8)
                  and math.isclose(p,values.quantile(.9),abs_tol=1e-8))
        grouped=r.groupby([r.issued_date.dt.to_period('M'),'permit_type']).review_days
        independently_grouped={(str(month),category):(len(v),v.median(),v.quantile(.9))
                               for (month,category),v in grouped}
        for month,category,count,m,p in conn.execute('SELECT month,permit_type,issued,median_review_days,p90_review_days FROM permitops.vw_monthly_performance'):
            n_expected,m_expected,p_expected=independently_grouped.get((str(pd.Period(month,freq='M')),category),(0,None,None))
            if count != n_expected or (count and (not math.isclose(m,m_expected,abs_tol=1e-8)
                                                   or not math.isclose(p,p_expected,abs_tol=1e-8))):
                raise AssertionError(f'Month/category mismatch: {month} {category}')
        check('all_month_category_percentiles',True)
        for category,n_recent,n_prior,median_recent,median_prior,p90_recent,change,_ in conn.execute('SELECT * FROM permitops.vw_bottlenecks'):
            recent=r.loc[r.permit_type.eq(category) & r.issued_date.ge(end-pd.DateOffset(months=12)),'review_days']
            prior=r.loc[r.permit_type.eq(category) & r.issued_date.ge(end-pd.DateOffset(months=24)) & r.issued_date.lt(end-pd.DateOffset(months=12)),'review_days']
            check('trend:'+category,len(recent)==n_recent and len(prior)==n_prior
                  and math.isclose(median_recent,recent.median(),abs_tol=1e-8)
                  and math.isclose(median_prior,prior.median(),abs_tol=1e-8)
                  and math.isclose(p90_recent,recent.quantile(.9),abs_tol=1e-8)
                  and math.isclose(change,recent.median()-prior.median(),abs_tol=1e-8))
        active,unissued = conn.execute('SELECT sum(active_permits),sum(active_unissued) FROM permitops.vw_active_summary').fetchone()
        check('active_count',active==int(fact.active_eligible.sum()))
        check('unissued_count',unissued==int(fact.active_unissued_eligible.sum()))
        unissued_rows=fact.loc[fact.active_unissued_eligible]
        recomputed=(pd.Timestamp(qa['as_of'])-unissued_rows.application_date).dt.days
        check('unissued_age_arithmetic',recomputed.eq(unissued_rows.active_age_days).all())
        check('review_nonnegative',bool(r.review_days.ge(0).all()))
        check('active_unissued_has_no_issue_date',fact.loc[fact.active_unissued_eligible,'issued_date'].isna().all())
    result={'as_of':qa['as_of'],'checks':checks,'all_passed':all(checks.values()),
            'study_review_rows':len(r),'median_review_days':float(r.review_days.median()),
            'p90_review_days':float(r.review_days.quantile(.9))}
    Path('outputs/validation.json').write_text(json.dumps(result,indent=2))
    return result
