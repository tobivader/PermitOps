"""Retrieve authoritative CKAN CSV dumps with hashes and extract timestamps."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

BASE = 'https://ckan0.cf.opendata.inter.prod-toronto.ca'
PACKAGES = {'active': 'building-permits-active-permits',
            'cleared': 'building-permits-cleared-permits'}


def ingest(root=Path('data/raw')):
    root.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for source, package in PACKAGES.items():
        with urlopen(f'{BASE}/api/3/action/package_show?id={package}', timeout=60) as r:
            metadata = json.load(r)
        if not metadata.get('success'):
            raise RuntimeError(f'CKAN failed for {package}')
        resources = [r for r in metadata['result']['resources']
                     if '/datastore/dump/' in r['url'] and r['format'].upper() == 'CSV']
        if len(resources) != 1:
            raise ValueError(f'Expected one current datastore CSV for {package}')
        resource = resources[0]
        target = root / f'{source}.csv'
        temp = target.with_suffix('.partial')
        with urlopen(resource['url'], timeout=180) as response, temp.open('wb') as out:
            while block := response.read(1024 * 1024):
                out.write(block)
        temp.replace(target)
        (root / f'{source}_metadata.json').write_text(json.dumps(metadata, indent=2))
        manifest[source] = {'url': resource['url'], 'resource_id': resource['id'],
                            'retrieved_at': datetime.now(timezone.utc).isoformat(),
                            'sha256': hashlib.file_digest(target.open('rb'), 'sha256').hexdigest(),
                            'bytes': target.stat().st_size}
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    ingest()
