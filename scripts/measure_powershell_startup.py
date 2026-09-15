#!/usr/bin/env python3
"""Bounded, Linux-only PowerShell diagnostics; never certification evidence."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import resource
except ImportError:  # Keep maintainer test discovery portable to Windows.
    resource = None

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/wayfinder/skills/wayfinder'
ADAPTER = SKILL / 'scripts/adapters/wayfinder-powershell.ps1'


def measure_one(command: list[str], expected: tuple[int, str | None, str | None]) -> dict:
    started = time.perf_counter()
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=15, check=False)
    elapsed = time.perf_counter() - started
    exit_code, command_name, code = expected
    if result.returncode != exit_code:
        raise ValueError(f'unexpected exit {result.returncode}; expected {exit_code}')
    if command_name is None:
        if result.stdout or result.stderr:
            raise ValueError('empty-process baseline produced output')
    else:
        envelope = json.loads(result.stdout.decode('utf-8'))
        if (not result.stdout.endswith(b'\n') or len(result.stdout.splitlines()) != 1
                or envelope['format'] != 'wayfinder-command-result'
                or envelope['schemaVersion'] != 1 or envelope['command'] != command_name
                or envelope['code'] != code or envelope['ok'] != (exit_code == 0)
                or bool(result.stderr) != (exit_code != 0)):
            raise ValueError('adapter result disagrees with the diagnostic expectation')
    return {'seconds': elapsed, 'exit': result.returncode}


def measure_group(command: list[str], expected: tuple, samples: int, jobs: int) -> dict:
    if resource is None:
        raise RuntimeError('child resource counters are unavailable on this platform')
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(measure_one, command, expected) for _ in range(samples)]
        observations = [future.result() for future in futures]
    wall = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    seconds = sorted(item['seconds'] for item in observations)
    return {'jobs': jobs, 'samples': observations, 'wallSeconds': wall,
            'medianInvocationSeconds': statistics.median(seconds),
            'p95InvocationSeconds': seconds[max(0, (95 * len(seconds) + 99) // 100 - 1)],
            'childUserSeconds': after.ru_utime - before.ru_utime,
            'childSystemSeconds': after.ru_stime - before.ru_stime,
            'childMajorFaults': after.ru_majflt - before.ru_majflt,
            'childBlockInputs': after.ru_inblock - before.ru_inblock,
            'childBlockOutputs': after.ru_oublock - before.ru_oublock,
            'childVoluntaryContextSwitches': after.ru_nvcsw - before.ru_nvcsw,
            'childInvoluntaryContextSwitches': after.ru_nivcsw - before.ru_nivcsw}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=16, choices=range(4, 33))
    args = parser.parse_args()
    if platform.system() != 'Linux':
        parser.error('this diagnostic requires the existing Linux runner')
    # Reserve exclusively before any measurement; an interrupted report stays visible.
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write('{"complete":false}\n')
        output.flush()
        raw = ADAPTER.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        pwsh = os.environ.get('WAYFINDER_POWERSHELL_RUNTIME', 'pwsh')
        base = [pwsh, '-NoLogo', '-NoProfile', '-NonInteractive']
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(ROOT / 'plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1'))
        import run as conformance
        with tempfile.TemporaryDirectory(prefix='wayfinder-startup-') as temporary:
            workspace = Path(temporary)
            conformance.materialize(workspace, conformance.load_manifest(SKILL))
            scenarios = [
                ('empty-process', base + ['-Command', 'exit 0'], (0, None, None)),
                ('adapter-invalid-command', base + ['-File', str(ADAPTER), 'initialize-activate'],
                 (2, 'unknown', 'command.unknown')),
                ('adapter-probe', base + ['-File', str(ADAPTER), 'probe'], (0, 'probe', 'ok')),
                ('adapter-discover', base + ['-File', str(ADAPTER), 'discover', '--workspace-root', str(workspace)],
                 (0, 'discover', 'ok')),
            ]
            report = {'format': 'wayfinder-powershell-startup-diagnostics', 'schemaVersion': 1,
                      'complete': False, 'sourceCommit': os.environ.get('GITHUB_SHA'),
                      'runId': os.environ.get('GITHUB_RUN_ID'), 'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
                      'adapterSha256': digest, 'cpuCount': os.cpu_count(), 'platform': platform.platform(),
                      'sampleCountPerGroup': args.samples, 'scenarios': []}
            for name, command, expected in scenarios:
                first = measure_group(command, expected, 1, 1)
                # First observation is separate; repeated calls still launch fresh processes.
                groups = [measure_group(command, expected, args.samples, jobs) for jobs in (1, 2, 4)]
                entry = {'scenario': name, 'firstObservation': first, 'groups': groups}
                report['scenarios'].append(entry)
                print('POWERSHELL-DIAGNOSTIC ' + json.dumps(entry, separators=(',', ':')), flush=True)
            if ADAPTER.read_bytes() != raw:
                raise ValueError('adapter bytes changed during diagnostics')
            report['complete'] = True
            output.seek(0)
            output.truncate()
            json.dump(report, output, indent=2)
            output.write('\n')
        print('PowerShell diagnostic report complete; adapter bytes unchanged.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
