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
import sys
sys.dont_write_bytecode = True
import importlib.util
_spec = importlib.util.spec_from_file_location('startup_component_validation', ROOT / 'scripts/measure_powershell_components.py')
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
WRAPPER = ROOT / 'scripts/measure_powershell_probe_paths.ps1'
MANAGEMENT = _base.MANAGEMENT
SCENARIOS = (
    ('empty-process','empty-process','original'),
    ('probe-original','probe','original'),
    ('probe-startup','probe','startup'),
    ('probe-paths','probe','paths'),
    ('probe-full','probe','full'),
)
PROBE_REPLACEMENTS = (
    ("Join-Path $script:ContractRoot 'release.json'", "[IO.Path]::Combine($script:ContractRoot,'release.json')"),
    ("Join-Path $script:SkillRoot $release.contractManifest.path", "[IO.Path]::Combine($script:SkillRoot,$release.contractManifest.path)"),
    ("Join-Path $script:ContractRoot 'schemas/release.schema.json'", "[IO.Path]::Combine($script:ContractRoot,'schemas/release.schema.json')"),
    ("Join-Path $script:SkillRoot $adapter.path", "[IO.Path]::Combine($script:SkillRoot,$adapter.path)"),
    ("Join-Path $script:SkillRoot $resource.path", "[IO.Path]::Combine($script:SkillRoot,$resource.path)"),
    ("Join-Path $script:SkillRoot $scope.path", "[IO.Path]::Combine($script:SkillRoot,$scope.path)"),
    ("Join-Path $script:ContractRoot 'known-answer.json'", "[IO.Path]::Combine($script:ContractRoot,'known-answer.json')"),
    ("Get-ChildItem -LiteralPath $path -Recurse -File", "Get-DiagnosticProbeFiles $path"),
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
    if variant not in ('original', 'startup', 'paths', 'full'):
        raise ValueError('unsupported startup variant')
    for original, _ in ASSIGNMENTS:
        if source.count(original) != 1:
            raise ValueError('startup assignment missing or duplicated')
    prefix = source[:-len('Invoke-WfMain $args\nexit $script:ExitCode\n')]
    if source.count('function Invoke-WfProbe {') != 1 or 'Get-DiagnosticProbeFiles' in source:
        raise ValueError('unsupported probe/helper source')
    start = prefix.index('function Invoke-WfProbe {')
    end = prefix.index('\nfunction Parse-WfOptions', start)
    probe = prefix[start:end]
    for original, _ in PROBE_REPLACEMENTS:
        if probe.count(original) != 1:
            raise ValueError('probe command missing or duplicated')
    if variant in ('paths', 'full'):
        for original, replacement in PROBE_REPLACEMENTS[:7 if variant == 'paths' else 8]:
            probe = probe.replace(original, replacement)
        prefix = prefix[:start] + probe + prefix[end:]
    if variant != 'original':
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
            or report['format'] != 'wayfinder-powershell-probe-prototype-observation'
            or type(report['schemaVersion']) is not int or report['schemaVersion'] != 1
            or report['variant'] != mode
            or report['diagnosticCounterfactual'] is not (mode != 'original')
            or report['prefixSha256'] != hashlib.sha256(prefix.encode()).hexdigest()
            or report['contractRoot'] != str(SKILL / 'assets/contract-v1')
            or report['prefixLength'] != len(prefix.encode('utf-16-le')) // 2):
        raise ValueError('startup prototype report/provenance differs')
    labels = _base.TIMERS - ({'probeWork'} if scenario == 'minimal' else set())
    labels |= {'startupTransformation'} if mode != 'original' else set()
    if not isinstance(report['times'], dict) or set(report['times']) != labels:
        raise ValueError('startup prototype timer labels differ')
    for value in report['times'].values():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('invalid startup prototype time')
    after_load = [] if mode != 'original' else MANAGEMENT
    # Probe invokes unchanged package checks using Management commands; minimal does not.
    after_work = [] if mode == 'full' else MANAGEMENT
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
    for start in (1,):
        natural = entries[start]
        preloaded = entries[-1]
        left = [natural['firstObservation'], *natural['samples']]
        right = [o for entry in entries[2:] for o in [entry['firstObservation'], *entry['samples']]]
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


CONTROL_FIELDS = {'format','schemaVersion','complete','adapterSha256','adapterPath','skillRoot',
                  'runtimeVersion','fixtures','recursiveScopes','permissionStatus'}

def validate_compatibility(report: dict, digest: str) -> None:
    if (not isinstance(report, dict) or set(report) != CONTROL_FIELDS
            or report['format'] != 'wayfinder-powershell-probe-compatibility'
            or type(report['schemaVersion']) is not int or report['schemaVersion'] != 1
            or report['complete'] is not True or report['adapterSha256'] != digest
            or report['adapterPath'] != str(ADAPTER) or report['skillRoot'] != str(SKILL)
            or report['runtimeVersion'] != '7.6.6'
            or report['permissionStatus'] not in ('passed','unavailable')):
        raise ValueError('compatibility control binding differs')
    fixtures = report['fixtures']
    if (not isinstance(fixtures, list) or len(fixtures) != 3
            or [f.get('name') for f in fixtures] != ['empty','nested-hidden-literal-unicode-links-cycle','missing-root']
            or fixtures[0] != {'name':'empty','rows':[]}
            or fixtures[2] != {'name':'missing-root','failureEquality':True}
            or set(fixtures[1]) != {'name','rows'}):
        raise ValueError('compatibility fixture coverage differs')
    def valid_rows(rows):
        return (isinstance(rows,list) and all(isinstance(r,str) and '|' in r for r in rows)
                and rows == sorted(set(rows)))
    if not valid_rows(fixtures[1]['rows']):
        raise ValueError('compatibility fixture rows differ')
    contract = json.loads((SKILL/'assets/contract-v1/contract.json').read_text())
    expected = [scope['path'] for scope in contract['governedScopes'] if scope['recursive']]
    scopes = report['recursiveScopes']
    if (not isinstance(scopes,list) or [scope.get('path') for scope in scopes] != expected
            or any(set(scope) != {'path','rows'} or not valid_rows(scope['rows']) for scope in scopes)):
        raise ValueError('real recursive scope coverage differs')


def compatibility_preflight(command: list[str], digest: str) -> dict:
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=15, check=False)
    if result.returncode or result.stderr or not result.stdout.endswith(b'\n') or len(result.stdout.splitlines()) != 1:
        raise ValueError(f'compatibility control failed: exit={result.returncode}; stderr={result.stderr.decode(errors="replace")[:3000]}')
    report = json.loads(result.stdout.decode('utf-8'))
    validate_compatibility(report,digest)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or resource is None:
        parser.error('startup-path diagnostics require the existing Linux runner')
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write('{"complete":false}\n'); output.flush()
        raw = ADAPTER.read_bytes(); source = raw.decode('utf-8'); prototype_prefix(source, 'full')
        digest = hashlib.sha256(raw).hexdigest()
        release = json.loads((SKILL / 'assets/contract-v1/release.json').read_text())
        entries = [a for a in release['adapters'] if a['id'] == 'powershell-v1']
        if len(entries) != 1 or entries[0]['sha256'] != digest or entries[0]['path'] != 'scripts/adapters/wayfinder-powershell.ps1':
            raise ValueError('registered adapter digest or identity differs')
        base = [os.environ.get('WAYFINDER_POWERSHELL_RUNTIME', 'pwsh'), '-NoLogo', '-NoProfile', '-NonInteractive']
        wrapper_raw = WRAPPER.read_bytes()
        binding = {'sourceCommit': os.environ.get('GITHUB_SHA'), 'runId': os.environ.get('GITHUB_RUN_ID'),
                   'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'adapterSha256': digest,
                   'wrapperSha256': hashlib.sha256(wrapper_raw).hexdigest(), 'expectedObservations': 45, 'expectedCompatibilityControls': 1, 'diagnosticOnly': True}
        print('POWERSHELL-PROBE-PATH-BINDING ' + json.dumps(binding, separators=(',', ':')), flush=True)
        control = compatibility_preflight(base + ['-File',str(WRAPPER),'-AdapterPath',str(ADAPTER),
                                                 '-Scenario','probe','-Variant','control'],digest)
        print('POWERSHELL-PROBE-PATH-COMPATIBILITY ' + json.dumps(control,separators=(',',':')),flush=True)
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
                print('POWERSHELL-PROBE-PATH-OBSERVATION ' + json.dumps(
                    {'scenario': name, 'observation': observation}, separators=(',', ':')), flush=True)
        ordered = list(cohorts.values())
        validate_cohorts(ordered, digest, source)
        summaries = [{'scenario': e['scenario'], **summarize_cohort(e)} for e in ordered]
        pairs = [{'comparison': ordered[i]['scenario'] + '-versus-' + ordered[i+1]['scenario'],
                  'roundDifferences': paired_differences(ordered[i], ordered[i+1])} for i in (1, 2, 3)]
        if ADAPTER.read_bytes() != raw:
            raise ValueError('adapter bytes changed during diagnostics')
        if WRAPPER.read_bytes() != wrapper_raw:
            raise ValueError('wrapper bytes changed during diagnostics')
        report = {'format': 'wayfinder-powershell-probe-path-diagnostics', 'schemaVersion': 1, 'complete': True,
                  'sourceCommit': os.environ.get('GITHUB_SHA'), 'runId': os.environ.get('GITHUB_RUN_ID'),
                  'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'adapterSha256': digest,
                  'wrapperSha256': binding['wrapperSha256'],
                  'compatibility': control, 'scenarios': ordered, 'summaries': summaries, 'pairedDifferences': pairs}
        output.seek(0); output.truncate(); json.dump(report, output, indent=2); output.write('\n')
    print('POWERSHELL-PROBE-PATH-SUMMARY ' + json.dumps(
        {'summaries': summaries, 'pairedDifferences': pairs}, separators=(',', ':')), flush=True)
    print('PowerShell probe-path report complete; 45 observations; adapter bytes unchanged.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
