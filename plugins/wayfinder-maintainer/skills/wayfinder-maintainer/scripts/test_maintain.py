#!/usr/bin/env python3
"""Dependency-free regression tests for maintainer-only tooling."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("maintain.py")
SPEC = importlib.util.spec_from_file_location("wayfinder_maintain", SCRIPT)
assert SPEC and SPEC.loader
maintain = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(maintain)

RUN_MATRIX_SCRIPT = maintain.REPOSITORY_ROOT / "scripts/run_matrix_entry.py"
RUN_MATRIX_SPEC = importlib.util.spec_from_file_location("wayfinder_run_matrix_entry", RUN_MATRIX_SCRIPT)
assert RUN_MATRIX_SPEC and RUN_MATRIX_SPEC.loader
run_matrix_entry = importlib.util.module_from_spec(RUN_MATRIX_SPEC)
RUN_MATRIX_SPEC.loader.exec_module(run_matrix_entry)

PREPARE_EVIDENCE_SCRIPT = maintain.REPOSITORY_ROOT / "scripts/prepare_evidence_release.py"
PREPARE_EVIDENCE_SPEC = importlib.util.spec_from_file_location("wayfinder_prepare_evidence", PREPARE_EVIDENCE_SCRIPT)
assert PREPARE_EVIDENCE_SPEC and PREPARE_EVIDENCE_SPEC.loader
prepare_evidence = importlib.util.module_from_spec(PREPARE_EVIDENCE_SPEC)
PREPARE_EVIDENCE_SPEC.loader.exec_module(prepare_evidence)


def capture(function, *args):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = function(*args)
    return result, stream.getvalue()


class DoctorTests(unittest.TestCase):
    def test_summary_verbose_json_and_failure(self) -> None:
        checks = [("one", True, "detail"), ("two", True, "")]
        code, summary = capture(maintain._emit_doctor, checks, "summary", False)
        self.assertEqual(code, 0)
        self.assertEqual(summary, "OK doctor passed=2 total=2\n")
        code, verbose = capture(maintain._emit_doctor, checks, "verbose", False)
        self.assertEqual(code, 0)
        self.assertIn("PASS one: detail", verbose)
        code, raw = capture(maintain._emit_doctor, checks, "json", False)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(raw)["data"]["summary"], {"passed": 2, "failed": 0, "total": 2})
        code, failure = capture(maintain._emit_doctor, [("broken", False, "why")], "summary", True)
        self.assertEqual(code, 1)
        self.assertEqual(failure, "FAIL broken: why\nsummary passed=0 failed=1 total=1\n")
        self.assertEqual(capture(maintain._emit_doctor, checks, "quiet", True), (0, ""))
        self.assertIn("FAIL broken", capture(maintain._emit_doctor, [("broken", False, "why")], "quiet", True)[1])

    def test_quiet_selected_adapter_preflight_and_multi_case_batch(self) -> None:
        completed = subprocess.CompletedProcess([], 0)
        with (
            mock.patch.object(maintain, "doctor", return_value=0) as doctor,
            mock.patch.object(maintain, "adapter_path", return_value=Path("adapter.py")),
            mock.patch.object(maintain, "run_python", return_value=completed) as run,
        ):
            code, output = capture(
                maintain.test_command,
                ["package-valid", "inventory-files-roots"],
                [],
                "python-reference-v1",
                "summary",
            )
        self.assertEqual((code, output), (0, ""))
        doctor.assert_called_once_with("quiet", selected_adapter="python-reference-v1")
        self.assertEqual(
            run.call_args.args[1],
            [
                "--adapter", "adapter.py", "--output", "summary",
                "--case", "package-valid", "--case", "inventory-files-roots",
            ],
        )

    def test_selected_adapter_is_not_blocked_by_unrelated_runtime(self) -> None:
        environment = os.environ.copy()
        environment["WAYFINDER_NODE_RUNTIME"] = "/definitely/unavailable/node"
        environment["WAYFINDER_POWERSHELL_RUNTIME"] = "/definitely/unavailable/pwsh"
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "test", "--adapter", "python-reference-v1", "--case", "harness-test-controls"],
            cwd=maintain.REPOSITORY_ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("summary passed=1 failed=0 total=1\n", completed.stdout)
        self.assertIn("response-class=complete-evidence", completed.stdout)

    def test_runtime_diagnostics_and_output_budgets(self) -> None:
        code, output = capture(maintain.doctor, "verbose", "python-reference-v1")
        self.assertEqual(code, 0, output)
        adapter_line = next(line for line in output.splitlines() if line.startswith("PASS adapter-probes:"))
        for token in ("request=", "resolved=", "observed=CPython", "required=CPython 3.14.7", "override=none; invoke maintain.py with the selected interpreter"):
            self.assertIn(token, adapter_line)
        code, summary = capture(maintain.doctor, "summary", "python-reference-v1")
        self.assertEqual(code, 0)
        self.assertLessEqual(len(summary.encode()), 80)
        self.assertLessEqual(len(adapter_line.encode()), 1024)


class ContextTests(unittest.TestCase):
    def test_context_markdown_and_json(self) -> None:
        code, markdown = capture(maintain.describe_command, "markdown")
        self.assertEqual(code, 0)
        self.assertIn("305", markdown)
        self.assertIn("activation `disabled`", markdown)
        code, raw = capture(maintain.describe_command, "json", "complete-evidence", 65536)
        self.assertEqual(code, 0)
        value = json.loads(raw)["data"]
        self.assertEqual(value["candidate"]["releaseId"], "v1-candidate-revision-11")
        self.assertEqual({item["id"] for item in value["adapterRegistry"]}, set(maintain.CURRENT_CANDIDATE_ADAPTER_DIGESTS))
        self.assertTrue(value["routing"])

    def test_current_state_is_exact_and_historical_evidence_is_preserved(self) -> None:
        self.assertEqual(maintain.status_issues(maintain.parse_status(maintain.CURRENT_STATE_PATH)), [])
        pinned = maintain.load_json(maintain.HISTORICAL_HASHES)["files"]
        for name, digest in pinned.items():
            self.assertEqual(maintain.sha256(maintain.CERTIFICATION_ROOT / name), digest)
        for collection in (maintain.ACCEPTED_PARITY_EVIDENCE_DIGESTS, maintain.ACCEPTED_MATRIX_EVIDENCE_DIGESTS):
            for name, digest in collection.items():
                self.assertEqual(maintain.sha256(maintain.CERTIFICATION_ROOT / name), digest)

    def test_exact_record_section_and_missing_heading(self) -> None:
        code, output = capture(maintain.record_section_command, "Candidate revision 9 Windows corrections — accepted")
        self.assertEqual(code, 0, output)
        self.assertIn("## Candidate revision 9 Windows corrections — accepted\n", output)
        self.assertNotIn("## Candidate revision 9 hosted certification execution", output)
        code, output = capture(maintain.record_section_command, "not a real heading")
        self.assertEqual(code, 2)
        self.assertIn("not found", output)


class OperationalEfficiencyTests(unittest.TestCase):
    def test_approval_response_routing_is_complete_and_progressive(self) -> None:
        companion = maintain.COMPANION_ROOT
        agents = (maintain.REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        skill = (companion / "SKILL.md").read_text(encoding="utf-8")
        approval = (companion / "references/approval-response.md").read_text(encoding="utf-8")
        workflow = (companion / "references/workflow.md").read_text(encoding="utf-8")
        self.assertIn("approval-response.md", agents)
        self.assertNotIn("v1-candidate-revision-", agents)
        for marker in ("Before asking the owner", "when processing the owner's response", "references/approval-response.md"):
            self.assertIn(marker, skill)
        for marker in (
            "## Explicit affirmative response",
            "## Explicit rejection or revision request",
            "## Conditional response",
            "## Ambiguous response",
        ):
            self.assertIn(marker, approval)
        self.assertIn("[approval-response protocol](approval-response.md) is mandatory", workflow)

    def test_self_test_discovers_all_modules_without_bytecode(self) -> None:
        accounting = dict(unit='test-case', testsRun=21, passed=20, skipped=1, expectedFailures=0, unexpectedSuccesses=0, caseFailures=0, caseErrors=0, subtestEvents=[], fixtureErrors=[], interrupted=False, skipReasons=['unavailable runtime'])
        completed = subprocess.CompletedProcess([], 0, stdout=json.dumps({'results': accounting, 'suiteSuccessful': True, 'events': []}), stderr='ordinary test logs')
        with (
            mock.patch.object(maintain, "repository_bytecode_artifacts", side_effect=[[], []]),
            mock.patch.object(maintain, 'fingerprint', return_value={'head': 'a' * 40, 'sha256': 'b' * 64}),
            mock.patch.object(maintain.subprocess, "run", return_value=completed) as run,
        ):
            code, output = capture(maintain.self_test_command, "json")
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(output)["data"]["tests"], 21)
        command = run.call_args.args[0]
        self.assertTrue(command[1].endswith('maintainer_unittest.py'))
        self.assertEqual(json.loads(output)['data']['passed'], 20)
        self.assertEqual(json.loads(output)['data']['skipped'], 1)
        self.assertEqual(run.call_args.kwargs["env"]["PYTHONDONTWRITEBYTECODE"], "1")

    def test_self_test_refuses_preexisting_bytecode(self) -> None:
        with mock.patch.object(maintain, "repository_bytecode_artifacts", return_value=["scripts/__pycache__"]):
            code, output = capture(maintain.self_test_command, "summary")
        self.assertEqual(code, 1)
        self.assertIn("bytecode-present", output)

    def test_failure_summary_is_exact_and_bounded(self) -> None:
        results = [
            {"id": f"case-{index}", "category": "inventory", "rules": ["WF-INV-003"], "status": "failed", "detail": "x" * 600}
            for index in range(30)
        ]
        value = maintain._matrix_failure_summary(results)
        self.assertEqual(value["failedCaseIds"], [f"case-{index}" for index in range(30)])
        self.assertEqual(len(value["failedCases"]), 25)
        self.assertEqual(value["failureDetailsTruncated"], 5)
        self.assertEqual(len(value["failedCases"][0]["detail"]), 512)

    def test_mode_aware_handoff_omits_mutating_commands_for_investigation(self) -> None:
        with mock.patch.object(maintain, "doctor", return_value=0):
            code, output = capture(maintain.handoff_command, "investigation", "Inspect a failure", [])
        self.assertEqual(code, 0, output)
        self.assertIn("Kind: `investigation`", output)
        for command in ("maintain.py evidence", "maintain.py freeze", "maintain.py parity"):
            self.assertNotIn(command, output)

    def test_all_handoff_kinds_include_common_approval_response_contract(self) -> None:
        for kind in ("investigation", "implementation", "hosted-review", "acceptance-record"):
            with self.subTest(kind=kind), mock.patch.object(maintain, "doctor", return_value=0):
                code, output = capture(maintain.handoff_command, kind, "Bounded objective", ["Deferred action"])
            self.assertEqual(code, 0, output)
            self.assertIn("Approval response", output)
            self.assertIn("references/approval-response.md", output)
            self.assertIn("detailed copy-ready prompt", output)
            self.assertIn("new session", output)
            self.assertIn("stop without beginning that task", output)
            for target in ("reason for rejection", "required correction", "needed evidence", "acceptance criteria"):
                self.assertIn(target, output)

    def test_handoff_output_remains_bounded_and_deterministic(self) -> None:
        with mock.patch.object(maintain, "doctor", return_value=0):
            first_code, first = capture(maintain.handoff_command, "implementation", "Bounded objective", ["Deferred action"])
            second_code, second = capture(maintain.handoff_command, "implementation", "Bounded objective", ["Deferred action"])
        self.assertEqual((first_code, first), (second_code, second))
        self.assertLess(len(first.splitlines()), 50)
        self.assertEqual(first.count("Approval response"), 1)
        self.assertIn("Do not infer authorization for later work", first)

    def test_plan_handoff_reconciles_approved_scope_and_review_stop(self) -> None:
        identifier = 'wp-01234567-89ab-4cde-8f01-23456789abcd'
        with tempfile.TemporaryDirectory() as raw:
            state = Path(raw) / 'current-state.md'
            state.write_text('Current plan: ' + identifier, encoding='utf-8')
            for status in ('approved', 'implementing', 'awaiting-review'):
                plan = {'metadata': {'id': identifier, 'revision': 3, 'approvedRevision': 2, 'status': status}}
                with self.subTest(status=status), mock.patch.object(maintain, 'doctor', return_value=0), mock.patch.object(maintain, 'CURRENT_STATE_PATH', state), mock.patch.object(maintain.plans, 'load_store', return_value=[plan]):
                    code, output = capture(maintain.handoff_command, 'implementation', 'Deliver this plan', [], identifier)
                self.assertEqual(code, 0, output)
                self.assertIn('plan read --id ' + identifier + ' --history', output)
                self.assertIn('Continue only the approved plan', output)
                self.assertIn('no polling', output)
                self.assertNotIn('stop without beginning that task', output)

    def test_plan_handoff_rejects_missing_unapproved_or_unrouted_plan(self) -> None:
        identifier = 'wp-01234567-89ab-4cde-8f01-23456789abcd'
        with tempfile.TemporaryDirectory() as raw:
            state = Path(raw) / 'current-state.md'
            state.write_text('No active plan', encoding='utf-8')
            for candidates in ([], [{'metadata': {'id': identifier, 'approvedRevision': None}}], [{'metadata': {'id': identifier, 'approvedRevision': 2, 'status': 'changes-requested'}}], [{'metadata': {'id': identifier, 'approvedRevision': 2, 'status': 'approved'}}]):
                with self.subTest(candidates=candidates), mock.patch.object(maintain, 'CURRENT_STATE_PATH', state), mock.patch.object(maintain.plans, 'load_store', return_value=candidates):
                    code, output = capture(maintain.handoff_command, 'implementation', 'Deliver this plan', [], identifier)
                self.assertEqual(code, 1, output)
                self.assertNotIn('Continue maintaining', output)

    def test_installed_plugin_requires_explicit_external_plan_repository(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw).resolve()
            repository = base / 'source'
            repository.mkdir()
            (repository / '.git').mkdir()
            (repository / 'AGENTS.md').write_text('# Instructions\n', encoding='utf-8')
            installation = base / 'installed-maintainer'
            installation.mkdir()
            with mock.patch.object(maintain, 'COMPANION_ROOT', installation), mock.patch.object(maintain, 'REPOSITORY_ROOT', repository), mock.patch.dict(os.environ):
                os.environ.pop('WAYFINDER_REPOSITORY_ROOT', None)
                with self.assertRaises(ValueError):
                    maintain.plan_repository_root()
                os.environ['WAYFINDER_REPOSITORY_ROOT'] = str(repository)
                self.assertEqual(maintain.plan_repository_root(), repository)
                os.environ['WAYFINDER_REPOSITORY_ROOT'] = str(installation)
                with self.assertRaises(ValueError):
                    maintain.plan_repository_root()

    def test_github_failure_annotations_and_summary(self) -> None:
        result = {
            "ok": False,
            "code": "matrix.entry-failed",
            "data": {
                "failedCaseIds": ["inventory-special-file"],
                "failedCases": [{"id": "inventory-special-file", "category": "inventory", "rules": ["WF-INV-003"], "detail": "socket unavailable"}],
                "failureDetailsTruncated": 0,
            },
        }
        with tempfile.TemporaryDirectory() as raw:
            summary = Path(raw) / "summary.md"
            with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}):
                code, output = capture(run_matrix_entry.report_failures, result, "python-windows")
            self.assertIsNone(code)
            text = summary.read_text(encoding="utf-8")
        self.assertIn("::error title=Wayfinder case inventory-special-file::socket unavailable", output)
        self.assertIn("`inventory-special-file`", text)
        self.assertIn("WF-INV-003", text)

    def test_certification_workflow_has_identity_summary_and_artifact_digests(self) -> None:
        workflow = (maintain.REPOSITORY_ROOT / ".github/workflows/certify.yml").read_text(encoding="utf-8")
        for token in ("run-name:", "GITHUB_STEP_SUMMARY", "artifact-digest", "cancel-in-progress: false"):
            self.assertIn(token, workflow)

    def test_evidence_publication_workflow_requires_exact_revision_10_identity(self) -> None:
        workflow = (maintain.REPOSITORY_ROOT / ".github/workflows/publish-evidence.yml").read_text(encoding="utf-8")
        for token in (
            "34921918384", "run_attempt", "82a2bb994e7ef8d2ffda7317e0687b0c7230aa54",
            "2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0",
            "evidence-v1-candidate-revision-10", "Wayfinder candidate revision 10 bounded matrix evidence",
        ):
            self.assertIn(token, workflow)


class MatrixReviewTests(unittest.TestCase):
    def _write_artifacts(self, root: Path, failing_target: tuple[str, str, str, str] | None = None) -> None:
        case_index = maintain.load_json(maintain.CONFORMANCE_ROOT / "cases.json")["cases"]
        expected_negative = [case["id"] for case in case_index if case["exit"] != 0]
        interruption_ids = ("apply-failure-boundary-matrix", "apply-rollback-boundary-matrix", "apply-rollback-interrupted")
        source = {"sourceRepository": "somacdivad/wayfinder", "sourceCommit": "a" * 40, "workflowRunId": "123", "workflowRunAttempt": "1"}
        release = maintain.load_json(maintain.SKILL_ROOT / "assets/contract-v1/release.json")
        adapter_paths = {item["id"]: item["path"] for item in release["adapters"]}
        for index, target in enumerate(maintain.MATRIX_TARGETS):
            results = [
                {"id": case["id"], "category": case["category"], "rules": case["rules"], "status": "passed"}
                for case in case_index
            ]
            if target == failing_target:
                results[0]["status"] = "failed"
                results[0]["detail"] = "synthetic regression"
            package = {
                **maintain.ACCEPTED_MATRIX_BINDINGS,
                "adapterId": target[0],
                "adapterPath": adapter_paths[target[0]],
                "adapterSha256": maintain.ACCEPTED_ADAPTER_DIGESTS[target[0]],
            }
            passed = sum(item["status"] == "passed" for item in results)
            result_by_id = {item["id"]: item["status"] for item in results}
            report = {
                "format": "wayfinder-environment-certification-evidence",
                "schemaVersion": 1,
                "target": {"adapterId": target[0], "runtimeImplementation": target[1], "runtimeVersion": target[2], "operatingSystemFamily": target[3]},
                "package": package,
                "executionProvenance": {**source, "unavailableObservations": []},
                "summary": {
                    "total": 305,
                    "passed": passed,
                    "failed": 305 - passed,
                    "completeRegisteredSuite": True,
                    "byCategory": dict(sorted(Counter(case["category"] for case in case_index).items())),
                    "negativeAndMutationCases": {
                        "required": len(expected_negative),
                        "passed": sum(item["id"] in set(expected_negative) and item["status"] == "passed" for item in results),
                        "caseIdsSha256": maintain.canonical_sha256(expected_negative),
                    },
                    "interruptionBoundaryCases": {case_id: result_by_id[case_id] for case_id in interruption_ids},
                },
                "results": results,
                "invocations": {"count": 300, "sha256": hashlib.sha256(f"invocations-{index}".encode()).hexdigest()},
            }
            report["resultSetSha256"] = maintain._matrix_result_set_sha256(package, results)
            stem = f"entry-{index}"
            report_path = root / f"{stem}.json"
            markdown_path = root / f"{stem}.md"
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
            markdown_path.write_text(f"# Review-only {stem}\n", encoding="utf-8", newline="\n")
            command_result = {
                "ok": not (target == failing_target),
                "code": "matrix.entry-failed" if target == failing_target else "ok",
                "data": {
                    "json": str(report_path), "jsonSha256": maintain.sha256(report_path),
                    "markdown": str(markdown_path), "markdownSha256": maintain.sha256(markdown_path),
                },
            }
            execution = {
                "format": "wayfinder-matrix-execution-status", "schemaVersion": 1,
                "entryId": stem, "adapterId": target[0], "operatingSystemFamily": target[3],
                "sourceCommit": source["sourceCommit"], "workflowRunId": source["workflowRunId"],
                "workflowRunAttempt": source["workflowRunAttempt"], "exitCode": 1 if target == failing_target else 0,
                "stdout": json.dumps(command_result, sort_keys=True, separators=(",", ":")) + "\n", "stderr": "",
            }
            (root / f"execution-{stem}.json").write_text(json.dumps(execution, indent=2) + "\n", encoding="utf-8", newline="\n")

    def test_offline_review_verifies_failing_environment_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            failing = maintain.MATRIX_TARGETS[2]
            self._write_artifacts(root, failing)
            before = {path.name: maintain.sha256(path) for path in root.iterdir()}
            code, output = capture(maintain.matrix_review_command, root, "json")
            after = {path.name: maintain.sha256(path) for path in root.iterdir()}
        self.assertEqual(code, 0, output)
        value = json.loads(output)["data"]
        self.assertIn(maintain._matrix_target_id(failing), value["failingCasesByEnvironment"])
        self.assertEqual(value["classification"], "GitHub Actions material; review-only; not accepted evidence")
        self.assertEqual(before, after)

    def _rewrite_recorded_paths(self, root: Path, render) -> None:
        for status_path in root.glob("execution-*.json"):
            status = json.loads(status_path.read_text(encoding="utf-8"))
            command = json.loads(status["stdout"])
            command["data"]["json"] = render(Path(command["data"]["json"]).name)
            command["data"]["markdown"] = render(Path(command["data"]["markdown"]).name)
            status["stdout"] = json.dumps(command, sort_keys=True, separators=(",", ":")) + "\n"
            status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    def test_offline_review_accepts_host_independent_report_basenames(self) -> None:
        renderings = (
            lambda name: f"/home/runner/work/output/{name}",
            lambda name: f"D:\\a\\wayfinder\\output\\{name}",
            lambda name: f"\\\\server\\share\\output\\{name}",
            lambda name: f"D:\\a/wayfinder\\output/{name}",
        )
        for render in renderings:
            with self.subTest(render=render("entry.json")), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                self._write_artifacts(root)
                self._rewrite_recorded_paths(root, render)
                code, output = capture(maintain.matrix_review_command, root, "json")
                self.assertEqual(code, 0, output)

    def test_offline_review_rejects_missing_ambiguous_and_malformed_paths(self) -> None:
        for mode in ("missing", "ambiguous", "malformed"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                self._write_artifacts(root)
                status_path = root / "execution-entry-0.json"
                status = json.loads(status_path.read_text(encoding="utf-8"))
                command = json.loads(status["stdout"])
                markdown = Path(command["data"]["markdown"])
                if mode == "missing":
                    markdown.unlink()
                elif mode == "ambiguous":
                    duplicate = root / "duplicate" / markdown.name
                    duplicate.parent.mkdir()
                    duplicate.write_bytes(markdown.read_bytes())
                else:
                    command["data"]["markdown"] = ""
                    status["stdout"] = json.dumps(command, sort_keys=True, separators=(",", ":")) + "\n"
                    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
                code, output = capture(maintain.matrix_review_command, root, "json")
                self.assertEqual(code, 2)
                issues = json.loads(output)["data"]["issues"]
                self.assertTrue(any("Markdown report" in issue for issue in issues), issues)

    def test_offline_review_rejects_report_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._write_artifacts(root)
            status_path = root / "execution-entry-0.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            command = json.loads(status["stdout"])
            command["data"]["markdownSha256"] = "0" * 64
            status["stdout"] = json.dumps(command, sort_keys=True, separators=(",", ":")) + "\n"
            status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
            code, output = capture(maintain.matrix_review_command, root, "json")
        self.assertEqual(code, 2)
        self.assertTrue(any("Markdown report hash differs" in issue for issue in json.loads(output)["data"]["issues"]))


class EvidenceTests(unittest.TestCase):
    def test_revision_10_publication_preparation_verifies_exact_promoted_set(self) -> None:
        evidence = maintain.PROMOTED_REVISION_10_EVIDENCE_ROOT
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "publication"
            argv = [
                str(PREPARE_EVIDENCE_SCRIPT), "--input", str(evidence),
                "--expected-commit", prepare_evidence.SOURCE_COMMIT,
                "--expected-run-id", prepare_evidence.RUN_ID,
                "--expected-attempt", prepare_evidence.RUN_ATTEMPT,
                "--expected-matrix-sha256", prepare_evidence.MATRIX_SHA256,
                "--output", str(output),
            ]
            with mock.patch.object(sys, "argv", argv):
                code, emitted = capture(prepare_evidence.main)
            manifest = json.loads((output / "publication-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, emitted)
        self.assertEqual(manifest["candidate"], "v1-candidate-revision-10")
        self.assertEqual(manifest["workflowRunId"], "34921918384")
        self.assertEqual(manifest["workflowRunAttempt"], "1")
        self.assertEqual(len(manifest["files"]), 27)

    def test_revision_10_publication_preparation_fails_closed(self) -> None:
        source = maintain.PROMOTED_REVISION_10_EVIDENCE_ROOT
        for mode in ("missing", "extra", "ambiguous", "symlink", "digest"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as raw:
                root = Path(raw) / "evidence"
                shutil.copytree(source, root)
                target = root / "artifact-inventory.json"
                if mode == "missing":
                    target.unlink()
                elif mode == "extra":
                    (root / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
                elif mode == "ambiguous":
                    duplicate = root / "duplicate"
                    duplicate.mkdir()
                    shutil.copyfile(target, duplicate / target.name)
                elif mode == "symlink":
                    target.unlink()
                    target.symlink_to(root / "execution-node-linux.json")
                else:
                    target.write_bytes(target.read_bytes() + b"\n")
                with self.assertRaises(ValueError):
                    prepare_evidence.verified_files(root)

    def test_revision_10_publication_preparation_rejects_unapproved_identity(self) -> None:
        files = prepare_evidence.verified_files(maintain.PROMOTED_REVISION_10_EVIDENCE_ROOT)
        with self.assertRaisesRegex(ValueError, "not the approved revision-10"):
            prepare_evidence.verify_bindings(
                files, prepare_evidence.SOURCE_COMMIT, "0", prepare_evidence.RUN_ATTEMPT, prepare_evidence.MATRIX_SHA256
            )

    def test_evidence_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "candidate-revision-11-local.json"
            target.write_text("preserve\n", encoding="utf-8")
            with mock.patch.object(maintain, "doctor", return_value=0):
                code, output = capture(maintain.evidence_command, root)
            self.assertEqual(code, 2)
            self.assertEqual(target.read_text(encoding="utf-8"), "preserve\n")
            self.assertIn("already exists", output)

    def test_freeze_proposal_requires_revision_scoped_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with mock.patch.object(maintain, "doctor", return_value=0), mock.patch.object(
                maintain, "CERTIFICATION_ROOT", root
            ):
                code, output = capture(maintain.freeze_proposal_command, root)
            self.assertEqual(code, 1)
            self.assertIn("candidate and parity reports are required", output)
            self.assertEqual(list(root.iterdir()), [])

    def test_freeze_acceptance_requires_explicit_option_and_revision_scoped_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with mock.patch.object(maintain, "doctor", return_value=0):
                code, output = capture(maintain.freeze_acceptance_command, root, False)
            self.assertEqual(code, 2)
            self.assertIn("requires --accept-option-a", output)
            self.assertEqual(list(root.iterdir()), [])
            with mock.patch.object(maintain, "doctor", return_value=0), mock.patch.object(
                maintain, "CERTIFICATION_ROOT", root
            ):
                code, output = capture(maintain.freeze_acceptance_command, root, True)
            self.assertEqual(code, 1)
            self.assertIn("freeze proposal is required", output)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
