import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[5]
SPEC = importlib.util.spec_from_file_location('startup_diagnostics', ROOT / 'scripts/measure_powershell_startup.py')
diagnostics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnostics)


class StartupDiagnosticTests(unittest.TestCase):
    @unittest.skipIf(diagnostics.resource is None, 'Unix child resource counters unavailable')
    def test_group_measures_real_child_processes_and_preserves_sample_count(self):
        group = diagnostics.measure_group([sys.executable, '-c', 'sum(range(100000))'], (0, None, None), 4, 2)
        self.assertEqual(len(group['samples']), 4)
        self.assertTrue(all(item['exit'] == 0 and item['seconds'] > 0 for item in group['samples']))
        self.assertGreater(group['wallSeconds'], 0)
        self.assertGreaterEqual(group['childUserSeconds'], 0)
        self.assertGreaterEqual(group['p95InvocationSeconds'], group['medianInvocationSeconds'])

    def test_expected_adapter_rejection_is_a_measurement_but_wrong_code_fails(self):
        envelope = dict(format='wayfinder-command-result', schemaVersion=1, command='unknown', code='command.unknown', ok=False)
        command = [sys.executable, '-c', f'import sys; print({json.dumps(envelope)!r}); print("rejected", file=sys.stderr); sys.exit(2)']
        self.assertEqual(diagnostics.measure_one(command, (2, 'unknown', 'command.unknown'))['exit'], 2)
        with self.assertRaises(ValueError):
            diagnostics.measure_one(command, (2, 'unknown', 'wrong.code'))

    def test_invocation_timeout_is_not_reported_successful(self):
        with mock.patch.object(diagnostics.subprocess, 'run', side_effect=subprocess.TimeoutExpired('pwsh', 15)) as run:
            with self.assertRaises(subprocess.TimeoutExpired):
                diagnostics.measure_one(['pwsh'], (0, None, None))
        self.assertEqual(run.call_args.kwargs['timeout'], 15)

    def test_existing_report_is_refused_before_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report.json'
            output.write_text('original\n')
            with mock.patch.object(sys, 'argv', ['diagnostic', '--output', str(output)]), mock.patch.object(diagnostics.platform, 'system', return_value='Linux'), mock.patch.object(diagnostics, 'measure_group') as group:
                with self.assertRaises(FileExistsError):
                    diagnostics.main()
                group.assert_not_called()
            self.assertEqual(output.read_text(), 'original\n')
