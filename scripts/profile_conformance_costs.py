#!/usr/bin/env python3
"""Run bounded, non-certification process-boundary profiles for costly fixtures."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/run.py'
SKILL = ROOT / 'plugins/wayfinder/skills/wayfinder'
CASES = (
    'apply-failure-boundary-matrix', 'apply-rollback-boundary-matrix',
    'apply-seeded-target-races', 'property-catalog-repeat-bytes',
    'property-record-seeded-id', 'initialize-seeded-candidate-boundaries',
    'property-path-boundaries',
)
ADAPTERS = ('wayfinder.py', 'wayfinder-node.mjs', 'wayfinder-powershell.ps1')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit('profile output already exists')
    args.output.mkdir(parents=True)
    reports = []
    for name in ADAPTERS:
        adapter = SKILL / 'scripts/adapters' / name
        profile = args.output / f'{adapter.stem}-profile.json'
        command = [sys.executable, str(RUNNER), '--adapter', str(adapter), '--output', 'json', '--profile', str(profile)]
        for case in CASES:
            command.extend(['--case', case])
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        if completed.returncode:
            raise SystemExit(f'{adapter.name} profile failed: {completed.stderr or completed.stdout}')
        result = json.loads(completed.stdout)
        profile_data = json.loads(profile.read_text(encoding='utf-8'))
        if (not result['ok'] or [item['id'] for item in profile_data['cases']] != list(CASES)
                or any(item['adapterInvocations'] is None for item in profile_data['cases'])):
            raise SystemExit(f'{adapter.name} profile is incomplete')
        reports.append({'adapter': name, 'profile': profile.name,
                        'adapterProcessSeconds': sum(item['adapterProcessSeconds'] for item in profile_data['cases']),
                        'harnessSeconds': sum(item['harnessSeconds'] for item in profile_data['cases'])})
    (args.output / 'summary.json').write_text(json.dumps({'format': 'wayfinder-conformance-cost-profile',
        'schemaVersion': 1, 'cases': list(CASES), 'reports': reports}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'reports': reports}, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
