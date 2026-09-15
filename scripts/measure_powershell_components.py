#!/usr/bin/env python3
"""Serial component diagnostics, separate from governed conformance results."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import time
from pathlib import Path
try:
    import resource
except ImportError:
    resource = None

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/wayfinder/skills/wayfinder'
ADAPTER = SKILL / 'scripts/adapters/wayfinder-powershell.ps1'
WRAPPER = ROOT / 'scripts/measure_powershell_components.ps1'
TIMERS = {'sourceReadDecode', 'fullSourceParse', 'diagnosticPrefixParse',
          'scriptBlockCreation', 'loadInitialization', 'probeWork', 'formatFirst',
          'formatRepeat1', 'formatRepeat2', 'formatRepeat3', 'privateFileWrite'}
FIELDS = {'format', 'schemaVersion', 'scenario', 'adapterSha256', 'adapterPath',
          'skillRoot', 'prefixLength', 'sourceLength', 'runtimeVersion', 'times',
          'modulesBefore', 'modulesAfter', 'payload', 'formattedText',
          'repeatedTexts', 'outputByteEquality'}


def expected_prefix(source: str) -> int:
    """Parent boundary check complements the wrapper's authoritative AST guard."""
    suffix = 'Invoke-WfMain $args\nexit $script:ExitCode\n'
    if not source.endswith(suffix):
        raise ValueError('unexpected adapter dispatch boundary')
    # PowerShell AST offsets are UTF-16 code units.
    return len(source[:-len(suffix)].encode('utf-16-le')) // 2


def validate_observation(report: dict, scenario: str, digest: str, source: str) -> None:
    if (not isinstance(report, dict) or set(report) != FIELDS
            or report['format'] != 'wayfinder-powershell-component-observation'
            or report['schemaVersion'] != 1 or report['scenario'] != scenario
            or report['adapterSha256'] != digest or report['adapterPath'] != str(ADAPTER)
            or report['skillRoot'] != str(SKILL)
            or report['prefixLength'] != expected_prefix(source)
            or report['sourceLength'] != len(source.encode('utf-16-le')) // 2
            or not isinstance(report['runtimeVersion'], str) or not report['runtimeVersion']
            or report['outputByteEquality'] is not True):
        raise ValueError('component report binding or shape differs')
    if not isinstance(report['times'], dict) or set(report['times']) != TIMERS:
        raise ValueError('component timer labels differ')
    for value in report['times'].values():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('component times must be finite and nonnegative')
    for modules in (report['modulesBefore'], report['modulesAfter']):
        if not isinstance(modules, list) or any(not isinstance(m, dict) or set(m) != {'name', 'version'}
                or not all(isinstance(v, str) and v for v in m.values()) for m in modules):
            raise ValueError('invalid module inventory')
    payload = report['payload']
    if (not isinstance(payload, dict) or set(payload) != {'format','schemaVersion','ok','command','code','data','diagnostics'}
            or payload['format'] != 'wayfinder-command-result' or payload['schemaVersion'] != 1
            or payload['ok'] is not True or payload['command'] != 'probe' or payload['code'] != 'ok'
            or payload['diagnostics'] != [] or not isinstance(payload['data'], dict)):
        raise ValueError('invalid component payload')
    if scenario == 'minimal':
        if payload['data'] != {} or report['times']['probeWork'] != 0:
            raise ValueError('minimal scenario performed probe work')
    else:
        if payload['data'].get('adapter') != {'id':'powershell-v1','path':'scripts/adapters/wayfinder-powershell.ps1','sha256':digest}:
            raise ValueError('probe adapter identity differs')
        if payload['data'].get('environment', {}).get('version') != report['runtimeVersion']:
            raise ValueError('probe runtime identity differs')
    text = report['formattedText']
    if (not isinstance(text, str) or json.loads(text) != payload
            or report['repeatedTexts'] != [text] * 3):
        raise ValueError('formatter output disagrees across calls or with payload')


def measure_one(command: list[str], scenario: str, digest: str, source: str) -> dict:
    before = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    started = time.perf_counter()
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=15, check=False)
    wall = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    if result.returncode or result.stderr:
        raise ValueError(f'component process failed: exit={result.returncode}; stderr={result.stderr.decode("utf-8", errors="replace")[:3000]}')
    observation = None
    if scenario == 'empty-process':
        if result.stdout:
            raise ValueError('empty baseline produced output')
    else:
        if not result.stdout.endswith(b'\n') or len(result.stdout.splitlines()) != 1:
            raise ValueError('expected exactly one component JSON line')
        observation = json.loads(result.stdout.decode('utf-8'))
        validate_observation(observation, scenario, digest, source)
    return {'wallSeconds':wall, 'childUserSeconds':after.ru_utime-before.ru_utime if after else None,
            'childSystemSeconds':after.ru_stime-before.ru_stime if after else None,
            'exit':result.returncode, 'components':observation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or resource is None:
        parser.error('component diagnostics require the existing Linux runner')
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write('{"complete":false}\n'); output.flush()
        raw = ADAPTER.read_bytes(); source = raw.decode('utf-8'); expected_prefix(source)
        digest = hashlib.sha256(raw).hexdigest()
        release = json.loads((SKILL / 'assets/contract-v1/release.json').read_text())
        entries = [a for a in release['adapters'] if a['id'] == 'powershell-v1']
        if len(entries) != 1 or entries[0]['sha256'] != digest or entries[0]['path'] != 'scripts/adapters/wayfinder-powershell.ps1':
            raise ValueError('registered adapter digest or identity differs')
        base = [os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh'),'-NoLogo','-NoProfile','-NonInteractive']
        report = {'format':'wayfinder-powershell-component-diagnostics','schemaVersion':1,'complete':False,
                  'sourceCommit':os.environ.get('GITHUB_SHA'),'runId':os.environ.get('GITHUB_RUN_ID'),
                  'attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),'adapterSha256':digest,
                  'wrapperSha256':hashlib.sha256(WRAPPER.read_bytes()).hexdigest(), 'scenarios':[]}
        for scenario in ('empty-process','minimal','probe'):
            command = base + (['-Command','exit 0'] if scenario == 'empty-process' else
                              ['-File',str(WRAPPER),'-AdapterPath',str(ADAPTER),'-Scenario',scenario])
            observations = [measure_one(command,scenario,digest,source) for _ in range(9)]
            versions = {o['components']['runtimeVersion'] for o in observations if o['components']}
            if len(versions) > 1:
                raise ValueError('runtime version changed within scenario')
            entry = {'scenario':scenario,'firstObservation':observations[0],'samples':observations[1:],
                     'medianWallSeconds':statistics.median(o['wallSeconds'] for o in observations[1:]),
                     'medianComponents':{key:statistics.median(o['components']['times'][key] for o in observations[1:])
                                         for key in sorted(TIMERS)} if scenario != 'empty-process' else {}}
            report['scenarios'].append(entry)
            print('POWERSHELL-COMPONENT ' + json.dumps(entry,separators=(',',':')),flush=True)
        if ADAPTER.read_bytes() != raw:
            raise ValueError('adapter bytes changed during diagnostics')
        report['complete'] = True
        output.seek(0); output.truncate(); json.dump(report,output,indent=2); output.write('\n')
    print('PowerShell component report complete; 27 observations; adapter bytes unchanged.',flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
