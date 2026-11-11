"""Static analyst charts from validated SQL exports; not Power BI screenshots."""
import hashlib
import json
import os
from pathlib import Path

# Keep plotting caches within the project and run without a GUI.
os.environ.setdefault('MPLCONFIGDIR', str(Path('.local/matplotlib').resolve()))
cache = Path('.local/cache').resolve()
cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('XDG_CACHE_HOME', str(cache))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd

BLUE = '#235789'
TEAL = '#16817a'
AMBER = '#c77719'
GRAY = '#667584'


def charts():
    root = Path('outputs/reporting')
    destination = Path('docs/figures')
    destination.mkdir(parents=True, exist_ok=True)
    qa = json.loads(Path('outputs/data_quality.json').read_text())
    validation = json.loads(Path('outputs/validation.json').read_text())
    if not validation['all_passed'] or validation['as_of'] != qa['as_of']:
        raise ValueError('Charts require passing metric validation for this snapshot')
    fingerprints = json.loads((root/'manifest.json').read_text())
    used = ['vw_monthly_performance.csv','vw_bottlenecks.csv','vw_active_summary.csv']
    for filename in used:
        with (root/filename).open('rb') as f:
            actual = hashlib.file_digest(f,'sha256').hexdigest()
        if actual != fingerprints[filename]['sha256']:
            raise ValueError(f'Modified reporting input: {filename}')

    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'axes.titleweight':'bold','axes.labelcolor':GRAY,
                         'text.color':'#182b3a','svg.hashsalt':'permitops'})
    end = pd.Timestamp(qa['as_of']).replace(day=1)
    start = end-pd.DateOffset(months=12)
    prior_start = end-pd.DateOffset(months=24)
    recent_label = f'{start:%b %Y}–{end-pd.Timedelta(days=1):%b %Y}'
    prior_label = f'{prior_start:%b %Y}–{start-pd.Timedelta(days=1):%b %Y}'
    attribution = (f'City of Toronto Open Data | Snapshot {qa["as_of"]} | '
                   'Static SQL analysis; not a Power BI screenshot')

    def save(fig, name, caption):
        fig.text(.03,.055,caption,fontsize=9,color=GRAY,va='bottom')
        fig.text(.03,.015,attribution,fontsize=8,color=GRAY,va='bottom')
        fig.tight_layout(rect=(.01,.13,.99,.98))
        fig.savefig(destination/f'{name}.png',dpi=160,facecolor='white')
        fig.savefig(destination/f'{name}.svg',metadata={'Date':None},facecolor='white')
        plt.close(fig)

    # Counts can be summed across categories; monthly medians cannot.
    monthly = pd.read_csv(root/used[0],parse_dates=['month'])
    monthly = monthly[monthly.month.ge(prior_start)].groupby('month')[['applications','issued']].sum()
    fig,ax = plt.subplots(figsize=(11,5.7))
    ax.plot(monthly.index,monthly.applications,color=TEAL,marker='o',markersize=3,label='Applications (application month)')
    ax.plot(monthly.index,monthly.issued,color=BLUE,marker='o',markersize=3,label='Valid issued reviews (issue month)')
    ax.set(title='Monthly permit volumes',ylabel='Eligible permit/revision records',xlabel='Complete calendar month')
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y',alpha=.18); ax.legend(frameon=False,loc='best')
    save(fig,'monthly_volumes','Applications from 2018 onward; terminal/non-permit exclusions apply.\nThe two lines are different lifecycle cohorts, not a conversion-rate calculation.')

    bottlenecks = pd.read_csv(root/used[1]).sort_values('recent_median_days')
    fig,(left,right) = plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[2.1,1]})
    y = list(range(len(bottlenecks)))
    left.barh([v-.17 for v in y],bottlenecks.prior_median_days,height=.30,color='#a7b8c6',label=prior_label)
    left.barh([v+.17 for v in y],bottlenecks.recent_median_days,height=.30,color=BLUE,label=recent_label)
    left.set_yticks(y,bottlenecks.permit_type)
    left.set(title='Median review time by category',xlabel='Calendar days: application to issuance')
    left.legend(frameon=False,loc='lower right',fontsize=8)
    left.grid(axis='x',alpha=.18)
    right.barh(y,bottlenecks.recent_p90_days,color=AMBER,height=.55)
    right.set_yticks(y,[f'n={n:,}' for n in bottlenecks.recent_issued])
    right.set(title='Recent P90 and volume',xlabel='Calendar days (separate scale)')
    right.grid(axis='x',alpha=.18)
    save(fig,'category_review_times','Both windows require at least 100 eligible issues; application dates from 2018 onward.\nElapsed days include applicant time. Different case mix and unresolved cases limit interpretation.')

    active = pd.read_csv(root/used[2])
    active_total = int(active.active_permits.sum())
    unissued = int(active.active_unissued.sum())
    with_issue = int(active.active_with_issue_date.sum())
    other = active_total-unissued-with_issue
    buckets = ['0–30','31–90','91–180','181–365','366+','Unknown']
    age = active.groupby('age_bucket').active_unissued.sum().reindex(buckets,fill_value=0)
    if (active_total != qa['eligibility']['active_eligible'] or
            unissued != qa['eligibility']['active_unissued_eligible'] or int(age.sum()) != unissued):
        raise ValueError('Workload chart does not reconcile to the validated QA populations')
    fig,(left,right) = plt.subplots(1,2,figsize=(11,5.7),gridspec_kw={'width_ratios':[1,1.4]})
    labels = ['With issue date','Unissued, valid age','Other/invalid age']
    values = [with_issue,unissued,other]
    bars = left.barh(labels,values,color=[BLUE,TEAL,GRAY])
    left.bar_label(bars,labels=[f'{n:,}' for n in values],padding=4,fontsize=9)
    left.set_xlim(0,max(values)*1.22)
    left.set(title=f'Active workload: {active_total:,}',xlabel='Permit/revision records')
    left.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    bars = right.bar(buckets,age,color=TEAL)
    right.bar_label(bars,labels=[f'{int(n):,}' for n in age],padding=3,fontsize=9)
    right.set_ylim(0,max(age)*1.18)
    right.set(title=f'Unissued age: {unissued:,} records',xlabel='Calendar days since application',ylabel='Records')
    right.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    right.grid(axis='y',alpha=.18)
    save(fig,'active_workload','All application years; current snapshot only. Active issued cases are not initial-review backlog.\nAge is elapsed time so far, not a completed review duration; conflicting keys are excluded.')

    evidence = {'as_of':qa['as_of'],'input_fingerprints':{name:fingerprints[name] for name in used},
                'active_total':active_total,'active_unissued':unissued,
                'chart_names':['monthly_volumes','category_review_times','active_workload']}
    (destination/'provenance.json').write_text(json.dumps(evidence,indent=2))
    return evidence


if __name__=='__main__':
    print(json.dumps(charts(),indent=2))
