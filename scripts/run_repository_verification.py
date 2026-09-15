#!/usr/bin/env python3
"""Ordinary repository checks with separate, non-certification timing output."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINTAIN = ROOT / 'plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py'


def complete_results(raw: str, expected: list[dict]) -> dict:
    envelope = json.loads(raw)
    data = envelope['data']
    results = data['results']
    summary = data['summary']
    if (not envelope['complete'] or envelope['truncated'] or not data['ok']
            or summary != {'passed': len(expected), 'failed': 0, 'total': len(expected)}
            or len(results) != len(expected)
            or any(result != dict(id=case['id'], category=case['category'], rules=case['rules'], status='passed')
                   for result, case in zip(results, expected))):
        raise ValueError('full passing fixture coverage is missing or mismatched')
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--powershell-jobs', type=int, default=2, choices=(1, 2, 4))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    checks = [
        ('repository', [sys.executable, str(ROOT / 'scripts/validate_repository.py')]),
        ('doctor', [sys.executable, str(MAINTAIN), 'doctor']),
        ('self-test', [sys.executable, str(MAINTAIN), 'self-test']),
    ]
    for adapter in ('python-reference-v1', 'node-v1', 'powershell-v1'):
        command = [sys.executable, str(MAINTAIN), 'test', '--adapter', adapter, '--format', 'json',
                   '--timings', str(args.output / f'{adapter}-timings.json')]
        if adapter == 'powershell-v1':
            command += ['--jobs', str(args.powershell_jobs)]
        checks.append((adapter, command))
    durations = []
    failed = False
    for name, command in checks:
        before = time.perf_counter()
        print(f'CHECK {name}', flush=True)
        # Capture full adapter JSON separately; summaries remain bounded in CI logs.
        adapter_check = name.endswith('-v1')
        completed = subprocess.run(command, cwd=ROOT, check=False,
                                   stdout=subprocess.PIPE if adapter_check else None, text=True)
        duration = time.perf_counter() - before
        if adapter_check:
            (args.output / f'{name}-results.json').write_text(completed.stdout, encoding='utf-8', newline='\n')
            try:
                cases_path = ROOT / 'plugins/wayfinder/skills/wayfinder/assets/contract-v1/conformance/v1/cases.json'
                expected = json.loads(cases_path.read_text(encoding='utf-8'))['cases']
                summary = complete_results(completed.stdout, expected)
                print(f'{name}: {summary}', flush=True)
                measured = json.loads((args.output / f'{name}-timings.json').read_text(encoding='utf-8'))
                invocations = [case['adapterInvocations'] for case in measured['cases']]
                print(f'TIMING {name} adapterInvocations={sum(invocations)}', flush=True)
                slowest = sorted(measured['cases'], key=lambda case: case['seconds'], reverse=True)[:10]
                print('CASE-TIMINGS ' + json.dumps({'adapter': name, 'slowest': slowest}, separators=(',', ':')), flush=True)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                failed = True
                print(f'FAIL {name}: incomplete results: {exc}', flush=True)
        failed |= completed.returncode != 0
        durations.append({'check': name, 'seconds': duration, 'exit': completed.returncode})
        print(f'TIMING {name} seconds={duration:.3f} exit={completed.returncode}', flush=True)
        if failed:
            break
    finished = time.time()
    setup_started = os.environ.get('WAYFINDER_VERIFICATION_STARTED')
    setup = started - float(setup_started) if setup_started else None
    report = {'format': 'wayfinder-repository-verification-timings', 'schemaVersion': 1,
              'sourceCommit': os.environ.get('GITHUB_SHA'), 'runId': os.environ.get('GITHUB_RUN_ID'),
              'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'powershellJobs': args.powershell_jobs,
              'setupSeconds': setup, 'checks': durations, 'checksSeconds': finished - started,
              'totalSeconds': finished - float(setup_started) if setup_started else finished - started,
              'ok': not failed}
    (args.output / 'verification-timings.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('VERIFICATION-TIMING ' + json.dumps(report, separators=(',', ':')), flush=True)
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8', newline='\n') as handle:
            handle.write('## Ordinary verification timings\n\n')
            handle.write(f"PowerShell workers: {args.powershell_jobs}; total seconds: {report['totalSeconds']:.3f}\n\n")
            handle.write('| Check | Seconds | Exit |\n| --- | ---: | ---: |\n')
            for check in durations:
                handle.write(f"| {check['check']} | {check['seconds']:.3f} | {check['exit']} |\n")
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
