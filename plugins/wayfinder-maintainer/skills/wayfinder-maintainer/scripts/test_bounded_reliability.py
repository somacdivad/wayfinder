"""Focused proof for the bounded-context and claim-integrity tranche."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import maintain
import maintainer_checkpoint as checkpoints
import maintainer_records as records
import maintainer_output as output
import maintainer_status as status_tools


def capture(function, *args):
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = function(*args)
    return code, stdout.getvalue(), stderr.getvalue()


class OutputTests(unittest.TestCase):
    def test_fixed_envelope_and_cursor_integrity(self):
        value = output.envelope(command="x", response_class="complete-evidence", scope={"kind": "x", "id": "x"}, data={})
        self.assertEqual(set(value), {"format", "schemaVersion", "command", "responseClass", "scope", "complete", "truncated", "returnedItems", "totalItems", "returnedBytes", "sourceBytes", "sourceSha256", "nextCursor", "error", "data"})
        cursor = output.make_cursor({"offset": 12, "sourceSha256": "a" * 64})
        self.assertEqual(output.read_cursor(cursor)["offset"], 12)
        with self.assertRaises(ValueError):
            output.read_cursor(cursor + "x")

    def test_utf8_chunks_reconstruct_exactly(self):
        source = ("αβγ\n" * 17 + "🙂" * 9).encode()
        position, chunks = 0, []
        while position < len(source):
            chunk, position = output.bounded_chunk(source, position, 13)
            chunk.decode("utf-8", "strict")
            chunks.append(chunk)
        self.assertEqual(b"".join(chunks), source)

    def test_section_chunk_sequence_and_stale_cursor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            store = root / "references/design-record"
            (store / "foundation").mkdir(parents=True)
            metadata = {"format": "wayfinder-design-record", "schemaVersion": 1, "id": "wr-0001",
                        "topic": "foundation", "candidateRevision": None, "title": "Example", "kind": "context",
                        "outcome": "recorded", "date": "2026-09-15", "summary": "Exact UTF-8 source.",
                        "predecessors": [], "sources": [], "authorities": [], "legacy": None}
            path = store / "foundation/wr-0001-example.md"
            body = ("## Example\n\n" + "αβγ content\n" * 12 + "\n").encode()
            source = records.render(metadata, body)
            path.write_bytes(source)
            chunks, cursor, digest, indexes = [], None, None, []
            with mock.patch.object(maintain, "COMPANION_ROOT", root):
                while True:
                    code, raw, diagnostic = capture(maintain.record_section_command, "Example", "json", "complete-evidence", 40, cursor)
                    value = json.loads(raw)
                    chunks.append(value["data"]["text"].encode())
                    indexes.append(value["data"]["chunkIndex"])
                    digest = value["sourceSha256"]
                    cursor = value["nextCursor"]
                    self.assertEqual(code, 0 if cursor is None else 2)
                    if cursor is None:
                        break
                reconstructed = b"".join(chunks)
                self.assertEqual(reconstructed, source)
                self.assertEqual(hashlib.sha256(reconstructed).hexdigest(), digest)
                self.assertEqual(indexes, list(range(len(chunks))))
                _, raw, _ = capture(maintain.record_section_command, "Example", "json", "discovery-preview", 40, None)
                first = json.loads(raw)
                self.assertFalse(first["complete"])
                path.write_bytes(records.render(metadata, body + b"changed\n"))
                code, _, diagnostic = capture(maintain.record_section_command, "Example", "json", "complete-evidence", 40, first["nextCursor"])
                self.assertEqual(code, 2)
                self.assertIn("stale", diagnostic)

    def test_complete_bound_fails_without_partial_result(self):
        code, raw, diagnostic = capture(maintain.main, ["describe", "--format", "json", "--response-class", "complete-evidence", "--max-bytes", "100"])
        self.assertEqual(code, 2)
        value = json.loads(raw)
        self.assertFalse(value["complete"])
        self.assertTrue(value["truncated"])
        self.assertIn("--max-bytes", diagnostic)
        code, raw, _ = capture(maintain.main, ["describe", "--format", "json", "--field", "id", "--field", "path", "--field", "nextCommand"])
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(raw)["complete"])
        self.assertFalse(json.loads(raw)["truncated"])


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.status = status_tools.parse_status(maintain.CURRENT_STATE_PATH)

    def copy_targets(self, root):
        for path in status_tools.rendered_targets(maintain.REPOSITORY_ROOT, self.status):
            destination = root / path.relative_to(maintain.REPOSITORY_ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)

    def test_projection_tamper_idempotence_and_narrow_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_targets(root)
            readme = root / "README.md"
            before = readme.read_text()
            readme.write_text(before.replace("v1-candidate-revision-10", "v1-candidate-revision-99", 1))
            self.assertEqual(status_tools.projection_drift(root, self.status), ["README.md"])
            self.assertEqual(status_tools.write_targets(root, self.status), ["README.md"])
            self.assertEqual(readme.read_text(), before)
            self.assertEqual(status_tools.write_targets(root, self.status), [])
            transitioned = copy.deepcopy(self.status)
            transitioned["candidate"]["activation"] = "enabled"
            rendered = status_tools.rendered_targets(root, transitioned)
            self.assertIn(b"Current candidate is activated", rendered[root / "plugins/wayfinder/plugin.json"])
            self.assertEqual(readme.read_text(), before)

    def test_missing_marker_and_failed_write_preserve_every_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_targets(root)
            changed = copy.deepcopy(self.status)
            changed["candidate"]["activation"] = "enabled"
            originals = {path: path.read_bytes() for path in status_tools.rendered_targets(root, self.status)}
            real_replace = status_tools.os.replace
            count = 0
            def fail_second(source, destination):
                nonlocal count
                count += 1
                if count == 2:
                    raise OSError("injected write failure")
                return real_replace(source, destination)
            with mock.patch.object(status_tools.os, "replace", side_effect=fail_second):
                with self.assertRaises(OSError):
                    status_tools.write_targets(root, changed)
            self.assertEqual({path: path.read_bytes() for path in originals}, originals)
            readme = root / "README.md"
            readme.write_text(readme.read_text().replace("WAYFINDER-GENERATED:README-BANNER:BEGIN", "missing"))
            with self.assertRaises(ValueError):
                status_tools.write_targets(root, changed)

    def test_authority_cross_validation_and_bound_before_write(self):
        changed = copy.deepcopy(self.status)
        changed["candidate"]["releaseId"] = "v1-candidate-revision-99"
        self.assertIn("candidate.releaseId differs", maintain.status_issues(changed))
        with mock.patch.object(maintain, "write_targets") as writes:
            code, _, _ = capture(maintain.status_command, "json", True, 1)
        self.assertEqual(code, 2)
        writes.assert_not_called()

    def test_unsafe_target_and_duplicate_authority_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_targets(root)
            path = root / "plugins/wayfinder/plugin.json"
            path.write_text('{"name":"wrong","version":"x","description":"x"}\n')
            with self.assertRaises(ValueError):
                status_tools.write_targets(root, self.status)
            state = root / "state.md"
            text = maintain.CURRENT_STATE_PATH.read_text()
            state.write_text(text.replace('"schemaVersion": 1,', '"schemaVersion": 1, "schemaVersion": 1,', 1))
            with self.assertRaises(ValueError):
                status_tools.parse_status(state)


class CheckpointTests(unittest.TestCase):
    def make_repository(self, root):
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "state.md").write_text("state\n")
        subprocess.run(["git", "add", "state.md"], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline"], cwd=root, check=True)

    def supplied(self):
        return {"objective": "test", "tranche": "bounded", "exclusions": ["network"], "sources": [{"path": "state.md", "scope": "complete"}], "validations": [], "mutations": [], "failures": [], "unresolved": [], "nextSafeAction": "read state", "cursor": None}

    def test_fingerprint_and_stale_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repository(root)
            checkpoint = checkpoints.create_checkpoint(root, self.supplied(), root / "state.md")
            self.assertEqual(checkpoints.verify_checkpoint(root, checkpoint, root / "state.md"), [])
            (root / "untracked.txt").write_text("one")
            first = checkpoints.fingerprint(root)
            (root / "untracked.txt").write_text("two")
            self.assertNotEqual(first["sha256"], checkpoints.fingerprint(root)["sha256"])
            self.assertIn("worktree changed", checkpoints.verify_checkpoint(root, checkpoint, root / "state.md"))
            (root / "state.md").write_text("changed\n")
            issues = checkpoints.verify_checkpoint(root, checkpoint, root / "state.md")
            self.assertIn("current state changed", issues)
            self.assertIn("source changed: state.md", issues)

    def test_source_confinement_external_locator_and_output_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repository(root)
            (root / "link.md").symlink_to(root / "state.md")
            supplied = self.supplied()
            supplied["sources"] = [{"path": "link.md", "scope": "complete"}]
            with self.assertRaises(ValueError):
                checkpoints.create_checkpoint(root, supplied, root / "state.md")
            supplied["sources"] = [{"locator": "opaque-external", "scope": "citation", "sha256": "a" * 64}]
            checkpoint = checkpoints.create_checkpoint(root, supplied, root / "state.md")
            self.assertEqual(checkpoint["sources"][0]["locator"], "opaque-external")
            with mock.patch.object(maintain, "REPOSITORY_ROOT", root):
                with self.assertRaises(ValueError):
                    maintain._checkpoint_output_path(root / "checkpoint.json")
                with self.assertRaises(ValueError):
                    maintain._checkpoint_output_path(root / "state.md")

    def test_checkpoint_file_is_exclusive_and_complete_before_write(self):
        with tempfile.TemporaryDirectory() as repository, tempfile.TemporaryDirectory() as external:
            root, outside = Path(repository), Path(external)
            self.make_repository(root)
            input_path = outside / "input.json"
            input_path.write_text(json.dumps(self.supplied()))
            destination = outside / "checkpoint.json"
            with mock.patch.object(maintain, "REPOSITORY_ROOT", root), mock.patch.object(maintain, "CURRENT_STATE_PATH", root / "state.md"):
                code, _, _ = capture(maintain.checkpoint_create_command, str(input_path), destination, "json", 4)
                self.assertEqual(code, 2)
                self.assertFalse(destination.exists())
                code, raw, _ = capture(maintain.checkpoint_create_command, str(input_path), destination, "json")
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(raw)["complete"])
                checkpoint = json.loads(destination.read_text())
                self.assertEqual(checkpoints.verify_checkpoint(root, checkpoint, root / "state.md"), [])
                code, _, _ = capture(maintain.checkpoint_create_command, str(input_path), destination, "json")
                self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
