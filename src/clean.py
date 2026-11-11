"""Validate dates and identities without silently discarding questionable records."""
import json
from pathlib import Path
import pandas as pd

FIELDS = ['PERMIT_NUM', 'REVISION_NUM', 'PERMIT_TYPE', 'STATUS',
          'APPLICATION_DATE', 'ISSUED_DATE', 'COMPLETED_DATE']
TERMINAL = {'cancelled', 'refused', 'revoked', 'permit revoked', 'application withdrawn',
            'abandoned', 'superseded', 'not accepted'}
NON_PERMIT_TYPES = {'DCs DeferredFees', 'Toronto Buildings Contacts',
                    'Site Inspection(Scarborough)', 'Building Historical data - Converted',
                    'Toronto Building Standard Attachments', 'Rental Renovation Licence'}


def normalize(frame, source, as_of):
    missing = set(FIELDS + ['_id']) - set(frame.columns)
    if missing:
        raise ValueError(f'{source}: missing required columns {sorted(missing)}')
    d = frame[FIELDS + ['_id']].copy().fillna('')
    for c in d:
        d[c] = d[c].astype(str).str.strip()
    d.columns = d.columns.str.lower()
    d = d.rename(columns={'_id': 'source_row_id'})
    d['source_dataset'] = source
    d['revision_num'] = d.revision_num.str.replace(r'^0+(?=\d)', '', regex=True)
    d['permit_key'] = d.permit_num + '|' + d.revision_num
    d['invalid_key'] = d.permit_num.eq('') | d.revision_num.eq('')
    for c in ['application_date', 'issued_date', 'completed_date']:
        raw = d[c]
        parsed = pd.to_datetime(raw, format='%Y-%m-%d', errors='coerce')
        d[c + '_invalid'] = raw.ne('') & parsed.isna()
        d[c + '_future'] = parsed.gt(pd.Timestamp(as_of))
        d[c] = parsed
    d['negative_review'] = d.issued_date.lt(d.application_date)
    d['negative_completion'] = d.completed_date.lt(d.issued_date) | d.completed_date.lt(d.application_date)
    d['excluded_status'] = d.status.str.lower().isin(TERMINAL)
    d['non_permit_type'] = d.permit_type.isin(NON_PERMIT_TYPES) | d.permit_type.eq('')
    d['as_of_date'] = pd.Timestamp(as_of)
    return d


def clean(as_of, raw=Path('data/raw'), output=Path('data/clean')):
    frames, profiles = [], {}
    for source in ['active', 'cleared']:
        original = pd.read_csv(raw / f'{source}.csv', dtype=str, keep_default_na=False)
        d = normalize(original, source, as_of)
        profiles[source] = {'input_rows': len(d), 'fields': original.columns.tolist(),
                            'statuses': d.status.value_counts().to_dict(),
                            'missing_dates': {c: int(d[c].isna().sum()) for c in
                                              ['application_date', 'issued_date', 'completed_date']},
                            'duplicate_key_rows': int(d.permit_key.duplicated().sum())}
        frames.append(d)
    all_rows = pd.concat(frames, ignore_index=True)
    relevant = ['permit_type', 'status', 'application_date', 'issued_date', 'completed_date']
    # Include nulls: missing versus populated dates are conflicting evidence, too.
    conflicts = all_rows.groupby('permit_key')[relevant].nunique(dropna=False).max(axis=1).gt(1)
    all_rows['conflicting_key'] = all_rows.permit_key.isin(conflicts[conflicts].index)
    quarantine = all_rows.invalid_key | all_rows.conflicting_key
    eligible = all_rows.loc[~quarantine].copy()
    # Identical analytical payload: cleared takes precedence; stable source ID breaks ties.
    eligible['source_priority'] = eligible.source_dataset.map({'cleared': 0, 'active': 1})
    eligible = eligible.sort_values(['permit_key', 'source_priority', 'source_row_id'])
    dedup = eligible.duplicated('permit_key')
    dropped = eligible.loc[dedup].copy()
    fact = eligible.loc[~dedup].drop(columns='source_priority').copy()
    valid_app = fact.application_date.notna() & ~fact.application_date_future
    fact['review_eligible'] = (valid_app & fact.issued_date.notna() & ~fact.issued_date_future
                               & ~fact.negative_review & ~fact.excluded_status & ~fact.non_permit_type)
    fact['application_eligible'] = valid_app & ~fact.excluded_status & ~fact.non_permit_type
    fact['active_eligible'] = (fact.source_dataset.eq('active') & ~fact.excluded_status
                                & ~fact.non_permit_type
                                & ~fact.status.str.lower().isin({'closed', 'file closed', 'permit issued/close file'}))
    fact['active_unissued_eligible'] = fact.active_eligible & valid_app & fact.issued_date.isna() & ~fact.issued_date_invalid
    fact['review_days'] = (fact.issued_date - fact.application_date).dt.days.where(fact.review_eligible)
    fact['active_age_days'] = (fact.as_of_date - fact.application_date).dt.days.where(fact.active_eligible & valid_app)
    fact['completion_eligible'] = (fact.review_eligible & fact.completed_date.notna()
                                     & ~fact.completed_date_future & ~fact.negative_completion)
    fact['completion_days'] = (fact.completed_date - fact.issued_date).dt.days.where(fact.completion_eligible)
    output.mkdir(parents=True, exist_ok=True)
    all_rows.to_csv(output / 'staging.csv', index=False, date_format='%Y-%m-%d')
    all_rows.loc[quarantine].to_csv(output / 'quarantine.csv', index=False, date_format='%Y-%m-%d')
    dropped.to_csv(output / 'duplicate_rows.csv', index=False, date_format='%Y-%m-%d')
    fact.to_csv(output / 'fact_permit_lifecycle.csv', index=False, date_format='%Y-%m-%d')
    qa = {'as_of': str(as_of), 'sources': profiles, 'input_rows': len(all_rows),
          'quarantined_rows': int(quarantine.sum()), 'conflicting_keys': int(conflicts.sum()),
          'duplicate_rows_removed': int(dedup.sum()), 'fact_rows': len(fact),
          'cross_source_overlap_keys': len(set(frames[0].permit_key) & set(frames[1].permit_key)),
          'flags': {c: int(all_rows[c].sum()) for c in all_rows if
                    c.endswith(('_invalid', '_future')) or c in ['negative_review', 'negative_completion', 'invalid_key']},
          'eligibility': {c: int(fact[c].sum()) for c in fact if c.endswith('_eligible')},
          'date_ranges': {c: {'min': str(fact[c].min()), 'max': str(fact[c].max())}
                          for c in ['application_date', 'issued_date', 'completed_date']}}
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/data_quality.json').write_text(json.dumps(qa, indent=2))
    assert qa['input_rows'] == qa['quarantined_rows'] + qa['duplicate_rows_removed'] + qa['fact_rows']
    assert fact.permit_key.is_unique
    return fact, qa
