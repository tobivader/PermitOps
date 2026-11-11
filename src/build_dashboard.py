"""Build anonymous aggregate dashboard data and independent SQL reference cases."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import pandas as pd
from .database import connect


def build():
    destination=Path('web-dashboard/dist'); destination.mkdir(parents=True,exist_ok=True)
    qa=json.loads(Path('outputs/data_quality.json').read_text())
    end=pd.Timestamp(qa['as_of']).replace(day=1)
    last_month=(end-pd.DateOffset(months=1)).strftime('%Y-%m')
    recent=(end-pd.DateOffset(months=12)).strftime('%Y-%m')
    with connect() as conn:
        conn.execute(Path('sql/06_dashboard.sql').read_text())
        categories=[r[0] for r in conn.execute('''SELECT DISTINCT permit_type FROM permitops.fact_permit_lifecycle
          WHERE application_eligible OR review_eligible OR active_eligible ORDER BY 1''')]
        ids={name:i for i,name in enumerate(categories)}
        reviews=[[str(m)[:7],ids[c],d,int(n)] for m,c,d,n in conn.execute(
            'SELECT * FROM permitops.vw_dashboard_review_distribution ORDER BY 1,2,3')]
        apps=[[str(m)[:7],ids[c],int(n)] for m,c,n in conn.execute('''SELECT date_trunc('month',application_date)::date,
          permit_type,count(*) FROM permitops.vw_study_permits WHERE application_eligible
          AND application_date<date_trunc('month',as_of_date) GROUP BY 1,2 ORDER BY 1,2''')]
        active=[[ids[c],a,int(n),int(u),int(i)] for c,a,n,u,i in conn.execute(
            'SELECT * FROM permitops.vw_dashboard_active_distribution ORDER BY 1,2')]
        def objects(query):
            cur=conn.execute(query)
            return [dict(zip([d.name for d in cur.description],row)) for row in cur]
        revisions=objects('SELECT * FROM permitops.vw_new_houses_revision_analysis ORDER BY 1,2')
        quarters=objects('SELECT * FROM permitops.vw_new_houses_quarter_analysis ORDER BY 1')
        references=[]
        for start,finish,category in [(recent,last_month,None),(recent,last_month,'New Houses'),
              (recent,last_month,'New Building'),(last_month,last_month,None),('2024-12','2024-12','AS Alternative Solution'),
              ('2018-01',last_month,None)]:
            dates=(start+'-01',str(pd.Timestamp(finish+'-01')+pd.DateOffset(months=1))[:10])
            params=(*dates,category,category)
            n,m,p=conn.execute('''SELECT count(*),percentile_cont(.5) WITHIN GROUP(ORDER BY review_days),
              percentile_cont(.9) WITHIN GROUP(ORDER BY review_days) FROM permitops.vw_issued_review_metrics
              WHERE issued_date>=%s AND issued_date<%s AND (%s::text IS NULL OR permit_type=%s)''',params).fetchone()
            applications=conn.execute('''SELECT count(*) FROM permitops.vw_study_permits WHERE application_eligible
              AND application_date>=%s AND application_date<%s AND (%s::text IS NULL OR permit_type=%s)''',params).fetchone()[0]
            references.append({'start':start,'end':finish,'category':category,'issued':n,'median':m,'p90':p,'applications':applications})
        active_references=objects('''SELECT permit_type,count(*) AS active,count(*) FILTER(WHERE active_unissued_eligible) AS unissued,
          percentile_cont(.5) WITHIN GROUP(ORDER BY active_age_days) FILTER(WHERE active_unissued_eligible) AS median_age,
          percentile_cont(.9) WITHIN GROUP(ORDER BY active_age_days) FILTER(WHERE active_unissued_eligible) AS p90_age,
          max(active_age_days) FILTER(WHERE active_unissued_eligible) AS oldest
          FROM permitops.vw_active_workload GROUP BY 1 ORDER BY 1''')
    # Independent pandas validation of each SQL deep-dive group from the local fact.
    fact=pd.read_csv('outputs/reporting/fact_reporting.csv',dtype={'revision_num':str},parse_dates=['application_date','issued_date'])
    houses=fact[fact.permit_type.eq('New Houses') & fact.review_eligible & fact.application_date.ge('2018-01-01') &
                fact.issued_date.ge(end-pd.DateOffset(months=24)) & fact.issued_date.lt(end)].copy()
    houses['period']=houses.issued_date.ge(end-pd.DateOffset(months=12)).map({True:'Recent',False:'Prior'})
    if not houses.revision_num.str.fullmatch(r'[0-9]+').all():
        raise ValueError('Non-numeric New Houses revisions need an explicit group before publishing this deep dive')
    houses['revision_group']=houses.revision_num.map(lambda v:'Original (0)' if v=='0' else 'Revision 1' if v=='1' else 'Revision 2+')
    for group in revisions:
        values=houses.loc[houses.period.eq(group['period']) & houses.revision_group.eq(group['revision_group']),'review_days']
        assert len(values)==group['issued']
        assert abs(values.median()-group['median_days'])<1e-8
        assert abs(values.quantile(.9)-group['p90_days'])<1e-8
        assert int(values.gt(365).sum())==group['over_365']
    for group in quarters:
        values=houses.loc[houses.issued_date.dt.to_period('Q').eq(pd.Period(group['quarter'],freq='Q')),'review_days']
        assert len(values)==group['issued'] and abs(values.median()-group['median_days'])<1e-8
        assert abs(values.quantile(.9)-group['p90_days'])<1e-8
    data={'meta':{'asOf':qa['as_of'],'start':'2018-01','end':last_month,'recentStart':recent,
          'rawRows':qa['input_rows'],'quarantined':qa['quarantined_rows'],'factRows':qa['fact_rows'],
          'sources':'City of Toronto Open Data','grain':'One non-conflicting permit/revision record'},
          'categories':categories,'reviews':reviews,'applications':apps,'active':active,
          'revisions':revisions,'quarters':quarters,'activeReference':active_references}
    payload=json.dumps(data,separators=(',',':'),default=str,allow_nan=False)
    (destination/'data.js').write_text('window.PERMITOPS_DATA='+payload+';\n')
    (Path('web-dashboard')/'data.js').write_text('window.PERMITOPS_DATA='+payload+';\n')
    for name in ['index.html','styles.css','engine.js','app.js']:
        if (Path('web-dashboard')/name).exists(): shutil.copyfile(Path('web-dashboard')/name,destination/name)
    Path('outputs/dashboard_sql_reference.json').write_text(json.dumps(references,indent=2))
    Path('outputs/new_houses_deep_dive.json').write_text(json.dumps({'as_of':qa['as_of'],'revisions':revisions,'quarters':quarters,
                'sql_pandas_groups_checked':len(revisions)+len(quarters),'all_passed':True},indent=2,default=str))
    Path('outputs/dashboard_data_manifest.json').write_text(json.dumps({'as_of':qa['as_of'],'bytes':len(payload.encode()),
           'sha256':hashlib.sha256(payload.encode()).hexdigest(),'review_frequency_rows':len(reviews),
           'active_frequency_rows':len(active),'contains_individual_identifiers':False},indent=2))
    print(f'Built dashboard data: {len(payload):,} bytes; {len(revisions)+len(quarters)} SQL/pandas deep-dive checks passed')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
