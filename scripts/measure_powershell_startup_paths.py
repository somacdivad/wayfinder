#!/usr/bin/env python3
"""Serial module-loading diagnostics, separate from governed conformance results."""
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
import importlib.util
_spec = importlib.util.spec_from_file_location('startup_component_validation', ROOT / 'scripts/measure_powershell_components.py')
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
WRAPPER = ROOT / 'scripts/measure_powershell_startup_paths.ps1'
MANAGEMENT = _base.MANAGEMENT
SCENARIOS = (
    ('empty-process', 'empty-process', 'original'),
    ('minimal-original', 'minimal', 'original'),
    ('minimal-dotnet', 'minimal', 'dotnet'),
    ('probe-original', 'probe', 'original'),
    ('probe-dotnet', 'probe', 'dotnet'),
)
ASSIGNMENTS = (
    ("$script:SkillRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent",
     "$script:SkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($PSScriptRoot))"),
    ("$script:ContractRoot = Join-Path $script:SkillRoot 'assets/contract-v1'",
     "$script:ContractRoot = [IO.Path]::Combine($script:SkillRoot,'assets/contract-v1')"),
)

def expected_prefix(source: str) -> int:
    return _base.expected_prefix(source)


def prototype_prefix(source: str, variant: str) -> str:
    expected_prefix(source)
    if variant not in ('original', 'dotnet'):
        raise ValueError('unsupported startup variant')
    for original, _ in ASSIGNMENTS:
        if source.count(original) != 1:
            raise ValueError('startup assignment missing or duplicated')
    prefix = source[:-len('Invoke-WfMain $args\nexit $script:ExitCode\n')]
    if variant == 'dotnet':
        for original, replacement in ASSIGNMENTS:
            prefix = prefix.replace(original, replacement)
    return prefix


def validate_observation(report: dict, scenario: str, digest: str, source: str,
                         mode: str = 'original') -> None:
    extra = {'variant', 'diagnosticCounterfactual', 'prefixSha256', 'contractRoot',
             'modulesAfterProbe', 'modulesAfterFormatting'}
    fields = (_base.FIELDS - {'managementMode', 'modulesAfterImport'}) | extra
    prefix = prototype_prefix(source, mode)
    if (not isinstance(report, dict) or set(report) != fields
            or report['format'] != 'wayfinder-powershell-startup-prototype-observation'
            or type(report['schemaVersion']) is not int or report['schemaVersion'] != 1
            or report['variant'] != mode
            or report['diagnosticCounterfactual'] is not (mode == 'dotnet')
            or report['prefixSha256'] != hashlib.sha256(prefix.encode()).hexdigest()
            or report['contractRoot'] != str(SKILL / 'assets/contract-v1')
            or report['prefixLength'] != len(prefix.encode('utf-16-le')) // 2):
        raise ValueError('startup prototype report/provenance differs')
    labels = _base.TIMERS - ({'probeWork'} if scenario == 'minimal' else set())
    labels |= {'startupTransformation'} if mode == 'dotnet' else set()
    if not isinstance(report['times'], dict) or set(report['times']) != labels:
        raise ValueError('startup prototype timer labels differ')
    for value in report['times'].values():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('invalid startup prototype time')
    after_load = [] if mode == 'dotnet' else MANAGEMENT
    # Probe invokes unchanged package checks using Management commands; minimal does not.
    after_work = MANAGEMENT if scenario == 'probe' else after_load
    if (report['modulesBefore'] != [] or report['modulesBeforeLoad'] != []
            or report['modulesAfter'] != after_load
            or report['modulesAfterProbe'] != after_work
            or report['modulesAfterFormatting'] != after_work):
        raise ValueError('startup prototype module transitions differ')
    # Reuse established source/path/runtime/payload/formatter validation without
    # publishing synthetic component fields in the prototype observation.
    normalized = {k: v for k, v in report.items() if k not in extra}
    normalized.update(format='wayfinder-powershell-component-observation', schemaVersion=2,
                      managementMode='natural', modulesAfterImport=None,
                      modulesAfter=MANAGEMENT, prefixLength=expected_prefix(source))
    normalized['times'] = {k: v for k, v in report['times'].items() if k != 'startupTransformation'}
    if scenario == 'minimal':
        normalized['times']['probeWork'] = 0
    _base.ADAPTER, _base.SKILL = ADAPTER, SKILL
    _base.validate_observation(normalized, scenario, digest, source)


def measure_one(command: list[str], scenario: str, digest: str, source: str,
                mode: str = 'original') -> dict:
    before = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    started = time.perf_counter()
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=15, check=False)
    wall = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    if result.returncode or result.stderr:
        raise ValueError(f'diagnostic process failed: exit={result.returncode}; '
                         f'stderr={result.stderr.decode("utf-8", errors="replace")[:3000]}')
    observation = None
    if scenario == 'empty-process':
        if result.stdout:
            raise ValueError('empty baseline produced output')
    else:
        if not result.stdout.endswith(b'\n') or len(result.stdout.splitlines()) != 1:
            raise ValueError('expected exactly one diagnostic JSON line')
        observation = json.loads(result.stdout.decode('utf-8'))
        validate_observation(observation, scenario, digest, source, mode)
    return {'wallSeconds': wall, 'childUserSeconds': after.ru_utime-before.ru_utime if after else None,
            'childSystemSeconds': after.ru_stime-before.ru_stime if after else None,
            'exit': result.returncode, 'components': observation}


def validate_cohorts(entries: list[dict], digest: str, source: str) -> None:
    if [e['scenario'] for e in entries] != [s[0] for s in SCENARIOS]:
        raise ValueError('diagnostic scenarios missing or reordered')
    seen = set()
    for entry, (name, scenario, mode) in zip(entries, SCENARIOS):
        if set(entry) != {'scenario', 'firstObservation', 'samples'} or len(entry['samples']) != 8:
            raise ValueError('invalid cohort shape or sample count')
        for observation, round_number in zip([entry['firstObservation'], *entry['samples']], range(9)):
            if set(observation) != {'wallSeconds', 'childUserSeconds', 'childSystemSeconds',
                                    'exit', 'components', 'round', 'order'}:
                raise ValueError('invalid process observation shape')
            order = list(SCENARIOS if round_number % 2 else reversed(SCENARIOS)) if round_number else list(SCENARIOS)
            if (type(observation['round']) is not int or observation['round'] != round_number
                    or type(observation['order']) is not int
                    or observation['order'] != [s[0] for s in order].index(name)
                    or observation['exit'] != 0):
                raise ValueError('invalid round/order/exit binding')
            binding = (round_number, observation['order'])
            if binding in seen:
                raise ValueError('duplicate observation binding')
            seen.add(binding)
            for key in ('wallSeconds', 'childUserSeconds', 'childSystemSeconds'):
                value = observation[key]
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    raise ValueError('invalid process duration or CPU')
            if scenario == 'empty-process':
                if observation['components'] is not None:
                    raise ValueError('empty process unexpectedly has components')
            else:
                validate_observation(observation['components'], scenario, digest, source, mode)
    for start in (1, 3):
        natural, preloaded = entries[start:start+2]
        left = [natural['firstObservation'], *natural['samples']]
        right = [preloaded['firstObservation'], *preloaded['samples']]
        reference = left[0]['components']
        for observation in [*left, *right]:
            component = observation['components']
            if (component['payload'] != reference['payload']
                    or component['formattedText'] != reference['formattedText']):
                raise ValueError('original/dotnet payload or formatter disagreement')


def summarize_cohort(entry: dict) -> dict:
    samples = entry['samples']
    summary = {'medianWallSeconds': statistics.median(o['wallSeconds'] for o in samples),
               'minWallSeconds': min(o['wallSeconds'] for o in samples),
               'maxWallSeconds': max(o['wallSeconds'] for o in samples), 'medianComponents': {}}
    if samples[0]['components']:
        labels = samples[0]['components']['times']
        summary['medianComponents'] = {k: statistics.median(o['components']['times'][k] for o in samples)
                                       for k in sorted(labels)}
        if 'loadInitialization' in labels:
            combined = [o['components']['times']['loadInitialization'] +
                        o['components']['times'].get('managementImport', 0) for o in samples]
            summary['medianInitializationSeconds'] = statistics.median(combined)
    return summary


def paired_differences(natural: dict, preloaded: dict) -> list[dict]:
    return [{'round': left['round'],
             'initializationDifferenceSeconds': left['components']['times']['loadInitialization'] -
                                                right['components']['times']['loadInitialization'],
             'wallDifferenceSeconds': left['wallSeconds'] - right['wallSeconds']}
            for left, right in zip(natural['samples'], preloaded['samples'])]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or resource is None:
        parser.error('startup-path diagnostics require the existing Linux runner')
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write('{"complete":false}\n'); output.flush()
        raw = ADAPTER.read_bytes(); source = raw.decode('utf-8'); prototype_prefix(source, 'dotnet')
        digest = hashlib.sha256(raw).hexdigest()
        release = json.loads((SKILL / 'assets/contract-v1/release.json').read_text())
        entries = [a for a in release['adapters'] if a['id'] == 'powershell-v1']
        if len(entries) != 1 or entries[0]['sha256'] != digest or entries[0]['path'] != 'scripts/adapters/wayfinder-powershell.ps1':
            raise ValueError('registered adapter digest or identity differs')
        base = [os.environ.get('WAYFINDER_POWERSHELL_RUNTIME', 'pwsh'), '-NoLogo', '-NoProfile', '-NonInteractive']
        wrapper_raw = WRAPPER.read_bytes()
        binding = {'sourceCommit': os.environ.get('GITHUB_SHA'), 'runId': os.environ.get('GITHUB_RUN_ID'),
                   'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'adapterSha256': digest,
                   'wrapperSha256': hashlib.sha256(wrapper_raw).hexdigest(), 'expectedObservations': 45, 'diagnosticOnly': True}
        print('POWERSHELL-STARTUP-PATH-BINDING ' + json.dumps(binding, separators=(',', ':')), flush=True)
        cohorts = {name: {'scenario': name, 'firstObservation': None, 'samples': []}
                   for name, _, _ in SCENARIOS}
        for round_number in range(9):
            order = SCENARIOS if round_number == 0 or round_number % 2 else tuple(reversed(SCENARIOS))
            for index, (name, scenario, mode) in enumerate(order):
                command = base + (['-Command', 'exit 0'] if scenario == 'empty-process' else
                                  ['-File', str(WRAPPER), '-AdapterPath', str(ADAPTER),
                                   '-Scenario', scenario, '-Variant', mode])
                observation = measure_one(command, scenario, digest, source, mode)
                observation.update(round=round_number, order=index)
                if round_number == 0:
                    cohorts[name]['firstObservation'] = observation
                else:
                    cohorts[name]['samples'].append(observation)
                print('POWERSHELL-STARTUP-PATH-OBSERVATION ' + json.dumps(
                    {'scenario': name, 'observation': observation}, separators=(',', ':')), flush=True)
        ordered = list(cohorts.values())
        validate_cohorts(ordered, digest, source)
        summaries = [{'scenario': e['scenario'], **summarize_cohort(e)} for e in ordered]
        pairs = [{'payload': ordered[i]['scenario'].split('-')[0],
                  'roundDifferences': paired_differences(ordered[i], ordered[i+1])} for i in (1, 3)]
        if ADAPTER.read_bytes() != raw:
            raise ValueError('adapter bytes changed during diagnostics')
        if WRAPPER.read_bytes() != wrapper_raw:
            raise ValueError('wrapper bytes changed during diagnostics')
        report = {'format': 'wayfinder-powershell-startup-path-diagnostics', 'schemaVersion': 1, 'complete': True,
                  'sourceCommit': os.environ.get('GITHUB_SHA'), 'runId': os.environ.get('GITHUB_RUN_ID'),
                  'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'adapterSha256': digest,
                  'wrapperSha256': binding['wrapperSha256'],
                  'scenarios': ordered, 'summaries': summaries, 'pairedDifferences': pairs}
        output.seek(0); output.truncate(); json.dump(report, output, indent=2); output.write('\n')
    print('POWERSHELL-STARTUP-PATH-SUMMARY ' + json.dumps(
        {'summaries': summaries, 'pairedDifferences': pairs}, separators=(',', ':')), flush=True)
    print('PowerShell startup-path report complete; 45 observations; adapter bytes unchanged.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
