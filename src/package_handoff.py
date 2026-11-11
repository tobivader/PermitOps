"""Package actual Power BI inputs for transfer to Windows; never include raw sources."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED


def package_handoff():
    qa = json.loads(Path('outputs/data_quality.json').read_text())
    validation = json.loads(Path('outputs/validation.json').read_text())
    fingerprints = json.loads(Path('outputs/reporting/manifest.json').read_text())
    if not validation['all_passed'] or qa['as_of'] != validation['as_of']:
        raise ValueError('A passing validated snapshot is required for the handoff')
    inputs = [Path('outputs/reporting')/name for name in sorted(fingerprints)]
    inputs += [Path(name) for name in ['dashboard/README.md','dashboard/measures.dax',
               'dashboard/power_query.pq','docs/kpi_definitions.md','docs/data_dictionary.md',
               'docs/data_quality_report.md','docs/findings_recommendations.md',
               'outputs/validation.json','outputs/data_quality.json']]
    contents = {}
    manifest = {}
    for path in inputs:
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if path.parent == Path('outputs/reporting') and digest != fingerprints[path.name]['sha256']:
            raise ValueError(f'Reporting data changed since export: {path}')
        name = f'PermitOps/{path.as_posix()}'
        contents[name] = payload
        manifest[name] = {'sha256':digest,'bytes':len(payload)}
    instructions = f'''# PermitOps Power BI handoff — {qa['as_of']}

This bundle contains real reporting data and build templates. It does not contain a PBIX or a completed Power BI dashboard. Power Query and DAX have not been executed in Power BI.

1. Extract the PermitOps folder to C:\\ so that C:\\PermitOps\\outputs\\reporting exists, or edit DataFolder in the M templates to your extraction location.
2. Open Power BI Desktop on Windows. Follow dashboard/README.md to import fact_reporting, dim_date and dim_permit_type.
3. Use each separate expression in dashboard/power_query.pq as its own Blank Query. Add the relationships and individual DAX measures as documented.
4. Build the three pages and perform the SQL reconciliation checks before claiming the Power BI report works. Do not average aggregate medians or P90s.

The fact_reporting.csv file has {qa['fact_rows']:,} unique permit/revision records. It excludes street addresses, descriptions and builder names. Historical KPIs use a smaller eligible population as defined in docs/kpi_definitions.md. Active workload includes older application years.

HANDOFF_MANIFEST.json fingerprints every included source file. The parent project also saves the archive SHA-256 in outputs/handoff_package.json. Source: City of Toronto Open Data. Contains information licensed under the Open Government Licence – Toronto: https://open.toronto.ca/open-data-licence/ . No City endorsement is implied.
'''
    contents['PermitOps/START_HERE.md'] = instructions.encode()
    contents['PermitOps/HANDOFF_MANIFEST.json'] = json.dumps(
        {'as_of':qa['as_of'],'files':manifest},indent=2).encode()
    folder = Path('dist'); folder.mkdir(exist_ok=True)
    target = folder/'PermitOps_PowerBI_Handoff.zip'
    temp = target.with_suffix('.partial')
    year,month,day = map(int,qa['as_of'].split('-'))
    with ZipFile(temp,'w',compression=ZIP_DEFLATED,compresslevel=6) as archive:
        for name,payload in sorted(contents.items()):
            info = ZipInfo(name,date_time=(year,month,day,0,0,0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info,payload)
    temp.replace(target)
    with ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError('Handoff ZIP integrity check failed')
        for name,expected in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected['sha256']:
                raise ValueError(f'Handoff archive mismatch: {name}')
    with target.open('rb') as f:
        digest = hashlib.file_digest(f,'sha256').hexdigest()
    result = {'as_of':qa['as_of'],'archive':str(target),'bytes':target.stat().st_size,
              'sha256':digest,'source_files':len(manifest),'zip_integrity_passed':True,
              'all_included_files_hash_verified':True,
              'power_bi_runtime_tested':False}
    Path('outputs/handoff_package.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    print(json.dumps(package_handoff(),indent=2))
