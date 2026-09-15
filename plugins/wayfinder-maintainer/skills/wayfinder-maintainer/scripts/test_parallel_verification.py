#!/usr/bin/env python3
"""Ordinary parallel-runner isolation, ordering and fail-closed regressions."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
CONFORMANCE = SCRIPTS / 'conformance/v1'
sys.path.insert(0, str(CONFORMANCE))
import run as runner

SPEC = importlib.util.spec_from_file_location('parallel_maintain', SCRIPTS / 'maintain.py')
maintain = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(maintain)
ROOT = SCRIPTS.parents[4]
SKILL = ROOT / 'plugins/wayfinder/skills/wayfinder'
ADAPTER = SKILL / 'scripts/adapters/wayfinder.py'


def fixture_worker(skill_root, adapter, case, differential_mode):
    with tempfile.TemporaryDirectory(prefix='parallel-case-') as name:
        target = Path(name) / 'same-name.txt'
        target.write_text(case['id'])
        time.sleep(case.get('delay', 0))
        if target.read_text() != case['id']:
            raise RuntimeError('workspace contaminated')
        if case['id'] == 'crash':
            os._exit(9)
        if case['id'] == 'missing':
            return None
        result = dict(id=case['id'], category=case['category'], rules=case['rules'], status='passed')
        if case['id'] == 'failure':
            result.update(status='failed', detail='ordinary failure')
        return result, dict(id=case['id'], seconds=0, adapterInvocations=0, workspace=name)


def cases(*ids):
    return [dict(id=name, category='harness', rules=[], delay=0.08 if i == 0 else 0) for i, name in enumerate(ids)]


class ParallelVerificationTests(unittest.TestCase):
    def test_spawn_orders_results_and_isolates_workspaces(self):
        selected = cases('slow', 'fast', 'third')
        results = list(runner.selected_results(SKILL, ADAPTER, selected, 2, False, fixture_worker))
        self.assertEqual([r['id'] for r, _ in results], ['slow', 'fast', 'third'])
        self.assertEqual([r['status'] for r, _ in results], ['passed'] * 3)
        workspaces = [t['workspace'] for _, t in results]
        self.assertEqual(len(set(workspaces)), 3)
        self.assertTrue(all(not Path(path).exists() for path in workspaces))

    def test_worker_crash_and_missing_result_fail_with_complete_case_set(self):
        for bad in ('crash', 'missing'):
            with self.subTest(bad=bad):
                selected = cases('first', bad, 'last')
                results = list(runner.selected_results(SKILL, ADAPTER, selected, 2, False, fixture_worker))
                self.assertEqual([r['id'] for r, _ in results], [c['id'] for c in selected])
                self.assertEqual(results[1][0]['status'], 'failed')
                self.assertIn('case worker failed', results[1][0]['detail'])

    def test_ordinary_failure_does_not_drop_other_cases(self):
        results = list(runner.selected_results(SKILL, ADAPTER, cases('first', 'failure', 'last'), 2, False, fixture_worker))
        self.assertEqual([r['status'] for r, _ in results], ['passed', 'failed', 'passed'])
        self.assertEqual(results[1][0]['detail'], 'ordinary failure')

    def test_pool_start_failure_and_submission_failure_are_complete(self):
        selected = cases('one', 'two')
        with mock.patch.object(runner.concurrent.futures, 'ProcessPoolExecutor', side_effect=OSError('start')):
            results = list(runner.selected_results(SKILL, ADAPTER, selected, 2, False))
        self.assertEqual([r['status'] for r, _ in results], ['failed', 'failed'])
        with mock.patch.object(runner.concurrent.futures, 'ProcessPoolExecutor') as pool:
            pool.return_value.__enter__.return_value.submit.side_effect = RuntimeError('submit')
            # selected_results uses the executor itself, rather than its __enter__ return.
            pool.return_value.submit.side_effect = RuntimeError('submit')
            results = list(runner.selected_results(SKILL, ADAPTER, selected, 2, False))
        self.assertEqual([r['status'] for r, _ in results], ['failed', 'failed'])

    def test_measured_case_resets_counts_and_case_globals(self):
        selected = cases('one', 'two')
        def execute(skill_root, adapter, case):
            self.assertIsNone(runner.OBSERVATION_ROOT)
            self.assertIsNone(runner.OBSERVATION_CASE)
            self.assertEqual(runner.INVOCATION_COUNT, 0)
            runner.INVOCATION_COUNT = 3
            runner.OBSERVATION_ROOT = Path('/stale')
            runner.OBSERVATION_CASE = 'stale'
        with mock.patch.object(runner, 'execute_case', side_effect=execute):
            results = list(runner.selected_results(SKILL, ADAPTER, selected, 1, False))
        self.assertEqual([t['adapterInvocations'] for _, t in results], [3, 3])
        self.assertIsNone(runner.OBSERVATION_ROOT)
        self.assertIsNone(runner.OBSERVATION_CASE)

    def test_adapter_timeout_remains_fifteen_seconds_and_fails_case(self):
        case = dict(id='package-valid', category='package', rules=[])
        with mock.patch.object(runner.subprocess, 'run', side_effect=subprocess.TimeoutExpired('adapter', 15)) as invoke:
            result, timing = runner.measured_case(SKILL, ADAPTER, case, False)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('timed out', result['detail'])
        self.assertEqual(invoke.call_args.kwargs['timeout'], 15)
        self.assertEqual(timing['adapterInvocations'], 1)

    def test_jobs_validation_before_preflight_and_cli_execution(self):
        for jobs in ('0', '-1', 'abc'):
            for script in (SCRIPTS / 'maintain.py', CONFORMANCE / 'run.py'):
                command = [sys.executable, '-B', str(script)]
                if script.name == 'maintain.py':
                    command += ['test']
                command += ['--jobs', jobs]
                completed = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2)
                self.assertIn('positive integer', completed.stderr)
        with mock.patch.object(maintain, 'doctor') as doctor, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(maintain.test_command([], [], 'python-reference-v1', jobs=0), 2)
        doctor.assert_not_called()

    def test_parallel_governed_modes_are_rejected_before_execution(self):
        for extra in (['--write-evidence'], ['--observations', '/unused']):
            with mock.patch.object(runner, 'selected_results') as run, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(runner.main(['--jobs', '2', *extra]), 2)
            run.assert_not_called()

    def test_filtered_cli_serial_parallel_results_and_separate_timings(self):
        with tempfile.TemporaryDirectory() as name:
            documents = []
            for jobs in (1, 2):
                timing = Path(name) / f'timing-{jobs}.json'
                command = [sys.executable, '-B', str(SCRIPTS / 'maintain.py'), 'test', '--adapter', 'python-reference-v1',
                           '--case', 'json-valid-realistic', '--case', 'package-valid', '--jobs', str(jobs),
                           '--format', 'json', '--timings', str(timing)]
                completed = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                document = json.loads(completed.stdout)
                documents.append(document['data'])
                measured = json.loads(timing.read_text())
                self.assertEqual(measured['jobs'], jobs)
                self.assertEqual([t['id'] for t in measured['cases']], [r['id'] for r in document['data']['results']])
                self.assertTrue(all(t['adapterInvocations'] == 1 for t in measured['cases']))
                # Existing reports are never overwritten and no check starts for this invalid target.
                again = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(again.returncode, 2)
                self.assertIn('timing target already exists', again.stderr)
            self.assertEqual(documents[0], documents[1])

    def test_serial_observation_collection_preserves_all_cases(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / 'observations.json'
            completed = subprocess.run([sys.executable, '-B', str(CONFORMANCE / 'run.py'), '--adapter', str(ADAPTER),
                '--case', 'package-valid', '--case', 'json-valid-realistic', '--output', 'json', '--observations', str(path)],
                capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            observed = json.loads(path.read_text())
            self.assertEqual(len(observed['invocations']), 2)
            self.assertEqual([i['case'] for i in observed['invocations']], [r['id'] for r in observed['results']])
            self.assertEqual([i['invocation'] for i in observed['invocations']], [1, 1])


class VerificationDriverTests(unittest.TestCase):
    def test_full_coverage_rejects_missing_duplicate_reordered_and_failed_results(self):
        spec = importlib.util.spec_from_file_location('verification_driver_test', ROOT / 'scripts/run_repository_verification.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        expected = cases('one', 'two')
        results = [dict(id=c['id'], category=c['category'], rules=c['rules'], status='passed') for c in expected]
        def document(items):
            return json.dumps(dict(complete=True, truncated=False, data=dict(ok=True, results=items,
                              summary=dict(passed=2, failed=0, total=2))))
        self.assertEqual(driver.complete_results(document(results), expected)['passed'], 2)
        invalid = [results[:1], results + results[:1], results[::-1], [results[0], results[0]],
                   [results[0], dict(results[1], status='failed')], [results[0], dict(results[1], rules=['wrong'])]]
        for items in invalid:
            with self.subTest(items=items), self.assertRaises(ValueError):
                driver.complete_results(document(items), expected)
