"""Isolated unittest runner with explicit callback accounting, never log parsing."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True


class Results(unittest.TextTestResult):
    def __init__(self, *args):
        super().__init__(*args)
        self.events = []

    def event(self, outcome, test, detail=None, unit='test-case'):
        self.events.append({'unit': unit, 'id': test.id(), 'outcome': outcome, 'detail': detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.event('passed', test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.event('skipped', test, reason, unit='test-case' if isinstance(test, unittest.TestCase) else 'fixture')

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.event('expected-failure', test)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.event('unexpected-success', test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.event('failed', test)

    def addError(self, test, err):
        super().addError(test, err)
        self.event('error', test, unit='test-case' if isinstance(test, unittest.TestCase) else 'fixture')

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        outcome = 'passed' if err is None else 'failed' if issubclass(err[0], test.failureException) else 'error'
        self.event(outcome, subtest, unit='subtest')


def accounting(result, interrupted=False):
    cases = [item for item in result.events if item['unit'] == 'test-case']
    count = lambda name: sum(item['outcome'] == name for item in cases)
    return {
        'unit': 'test-case', 'testsRun': result.testsRun, 'passed': count('passed'),
        'skipped': count('skipped'), 'expectedFailures': count('expected-failure'),
        'unexpectedSuccesses': count('unexpected-success'), 'caseFailures': count('failed'),
        'caseErrors': count('error'), 'subtestEvents': [item for item in result.events if item['unit'] == 'subtest'],
        'fixtureErrors': [item for item in result.events if item['unit'] == 'fixture' and item['outcome'] == 'error'],
        'interrupted': interrupted, 'skipReasons': [('fixture skipped: ' if item['unit'] == 'fixture' else '') + item['detail'] for item in result.events if item['outcome'] == 'skipped'],
    }


def run_suite(suite, stream=None):
    runner = unittest.TextTestRunner(stream=stream or sys.stderr, verbosity=2, resultclass=Results)
    # Keep incidental test stdout out of the structured response.
    with contextlib.redirect_stdout(sys.stderr):
        result = runner.run(suite)
    return {'results': accounting(result), 'suiteSuccessful': result.wasSuccessful(), 'events': result.events}


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(Path(sys.argv[1])), pattern='test_*.py')
    result = run_suite(suite)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['suiteSuccessful'] else 1)
