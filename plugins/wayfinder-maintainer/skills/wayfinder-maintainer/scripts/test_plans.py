"""Regression scenarios for repository plans and exact approval history."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch

import maintainer_plans as plans
from maintainer_output import canonical_json
from maintainer_records import digest


class PlansTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / 'repository'
        self.root.mkdir()
        self.input = Path(self.tmp.name).resolve() / 'input.json'
        self.value = {'id': 'wp-' + str(uuid.uuid4()), 'subject': 'maintainer/development', 'slug': 'example', 'title': 'Example plan', 'summary': 'A coherent change', 'status': 'draft', 'updated': '2026-09-15', 'body': '# Example plan\n\nOutcome: café 🧭\n', 'records': [], 'approval': None}

    def invoke(self, function, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = function(*args)
        # JSON commands never append next-command text to stdout.
        result = json.loads(out.getvalue())
        return code, result, err.getvalue()

    def supplied(self, value):
        self.input.write_text(canonical_json(value), encoding='utf-8')
        return self.input

    def create(self, value=None, dry=False):
        return self.invoke(plans.create_command, self.root, self.supplied(value or self.value), dry, 'json', 65536)

    def item(self):
        return plans.load_store(self.root)[0]

    def update(self, kind, status, approval=None, body=None, sha=None):
        value = {**self.value, 'changeKind': kind, 'status': status, 'approval': approval}
        if body is not None:
            value['body'] = body
        return self.invoke(plans.update_command, self.root, self.value['id'], self.supplied(value), sha or self.item()['sha256'], False, 'json', 65536)

    def approve(self):
        return self.update('approval', 'approved', {'locator': 'conversation:owner-message', 'quotation': 'Implement the proposed plan.'})

    def test_create_dry_run_is_exact_and_does_not_create_store(self):
        code, response, _ = self.create(dry=True)
        self.assertEqual(code, 0)
        raw = response['data']['text'].encode('utf-8')
        self.assertEqual(digest(raw), response['sourceSha256'])
        self.assertFalse((self.root / 'docs').exists())
        code, response, _ = self.create()
        self.assertEqual(code, 0)
        self.assertEqual(self.item()['raw'], raw)
        self.assertEqual(plans.integrity_issues(self.root), [])
        self.assertEqual(self.create()[0], 2)

    def test_exact_approval_snapshot_progress_material_and_reapproval(self):
        self.create()
        self.assertEqual(self.approve()[0], 0)
        item = self.item()
        raw = item['raw']
        self.assertEqual(item['approvals'][2]['raw'], raw)
        self.assertEqual(self.update('progress', 'implementing', body='# Updated progress\n')[0], 0)
        item = self.item()
        self.assertEqual(item['metadata']['approvedRevision'], 2)
        self.assertEqual(item['approvals'][2]['raw'], raw)
        self.assertEqual(item['metadata']['approval']['quotation'], 'Implement the proposed plan.')
        self.assertEqual(self.update('material', 'changes-requested', body='# Revised scope\n')[0], 0)
        self.assertEqual(self.update('progress', 'implementing')[0], 2)
        self.assertEqual(self.approve()[0], 0)
        self.assertEqual(sorted(self.item()['approvals']), [2, 5])
        code, response, _ = self.invoke(plans.read_command, self.root, self.value['id'], 2, False, 'json', 'complete-evidence', 65536, None)
        self.assertEqual(code, 0)
        self.assertEqual(response['data']['text'].encode('utf-8'), raw)

    def test_unapproved_and_terminal_status_cannot_advance(self):
        self.create()
        for status in ('implementing', 'awaiting-review', 'completed', 'approved'):
            self.assertEqual(self.update('progress', status)[0], 2)
        self.approve()
        self.assertEqual(self.update('progress', 'abandoned')[0], 0)
        self.assertEqual(self.update('progress', 'implementing')[0], 2)
        self.assertEqual(self.update('material', 'changes-requested')[0], 0)

    def test_unknown_linked_record_is_rejected_before_write(self):
        self.assertEqual(self.create({**self.value, 'records': ['wr-9999']})[0], 2)
        self.assertEqual(plans.load_store(self.root), [])

    def test_expected_digest_and_no_approval_fabrication(self):
        self.create()
        old = self.item()['raw']
        self.assertEqual(self.update('progress', 'draft', sha='0' * 64)[0], 2)
        self.assertEqual(self.item()['raw'], old)
        self.assertEqual(self.update('progress', 'draft', {'locator': 'x', 'quotation': 'Yes'})[0], 2)
        self.assertEqual(self.approve()[0], 0)
        self.assertEqual(self.update('approval', 'approved')[0], 2)

    def test_unicode_chunks_reconstruct_exact_history_and_stale_cursor(self):
        self.value['body'] += ('Long café 🧭 line\n' * 35)
        self.create()
        self.approve()
        self.update('progress', 'implementing')
        chunks, cursor, position = [], None, 0
        while True:
            code, result, stderr = self.invoke(plans.read_command, self.root, self.value['id'], None, True, 'json', 'complete-evidence', 91, cursor)
            data = result['data']
            self.assertEqual(data['startByte'], position)
            raw = data['text'].encode('utf-8')
            self.assertLessEqual(len(raw), 91)
            self.assertEqual(len(raw), data['endByte'] - position)
            chunks.append(raw)
            position = data['endByte']
            cursor = result['nextCursor']
            if cursor is None:
                self.assertEqual(code, 0)
                break
            self.assertEqual(code, 2)
            self.assertIn('next-command:', stderr)
        self.assertEqual(digest(b''.join(chunks)), result['sourceSha256'])
        item = self.item()
        self.assertEqual(b''.join(chunks), item['approvals'][2]['raw'] + b'\n' + item['raw'])
        _, first, _ = self.invoke(plans.read_command, self.root, self.value['id'], None, False, 'json', 'complete-evidence', 91, None)
        self.update('progress', 'implementing', body='# changed\n')
        self.assertEqual(self.invoke(plans.read_command, self.root, self.value['id'], None, False, 'json', 'complete-evidence', 91, first['nextCursor'])[0], 2)

    def test_listing_pages_subject_hierarchy_and_store_binding(self):
        for number in range(3):
            value = {**self.value, 'id': 'wp-' + str(uuid.uuid4()), 'slug': f'example-{number}'}
            self.assertEqual(self.create(value)[0], 0)
        cursor, ids = None, []
        while True:
            code, result, _ = self.invoke(plans.list_command, self.root, 'maintainer', 'draft', 'json', 'discovery-preview', 800, cursor)
            self.assertEqual(code, 0)
            ids.extend(item['id'] for item in result['data']['items'])
            cursor = result['nextCursor']
            if cursor is None:
                break
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(result['totalItems'], 3)
        self.assertEqual(self.invoke(plans.list_command, self.root, None, None, 'json', 'complete-evidence', 4, None)[0], 2)

    def test_unsafe_paths_invalid_json_and_duplicate_identity(self):
        for key, value in (('subject', '../escape'), ('slug', 'a/b'), ('id', 'wp-NOT-UUID'), ('body', 'CR\rLF'), ('updated', '2026-02-30')):
            self.assertEqual(self.create({**self.value, key: value})[0], 2)
        self.input.write_text('{"id":"one","id":"two"}', encoding='utf-8')
        self.assertEqual(self.invoke(plans.create_command, self.root, self.input, False, 'json', 65536)[0], 2)
        self.create()
        item = self.item()
        folder = self.root / 'docs/plans/other' / Path(item['path']).parent.name
        folder.mkdir(parents=True)
        meta = {**item['metadata'], 'subject': 'other'}
        (folder / 'plan.md').write_bytes(plans.render(meta, '# Duplicate\n'))
        self.assertIn('duplicate plan ID', plans.integrity_issues(self.root)[0])

    def test_symlink_ancestor_and_snapshot_tampering_fail_closed(self):
        outside = Path(self.tmp.name).resolve() / 'outside'
        outside.mkdir()
        (self.root / 'docs').symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.create()[0], 2)
        self.assertEqual(list(outside.iterdir()), [])
        (self.root / 'docs').unlink()
        self.create()
        self.approve()
        self.update('progress', 'implementing')
        current = self.item()
        snapshot = self.root / 'docs/plans' / current['approvals'][2]['path']
        snapshot.write_bytes(snapshot.read_bytes() + b'Tampered\n')
        self.assertTrue(plans.integrity_issues(self.root))
        self.assertEqual(self.update('progress', 'implementing', sha=current['sha256'])[0], 2)

    def test_older_snapshot_is_bound_after_reapproval(self):
        self.create()
        self.approve()
        self.update('material', 'changes-requested')
        self.approve()
        item = self.item()
        oldest = self.root / 'docs/plans' / item['approvals'][2]['path']
        oldest.write_bytes(oldest.read_bytes() + b'Changed older approval\n')
        self.assertTrue(plans.integrity_issues(self.root))

    def test_digest_is_rechecked_immediately_before_replacement(self):
        self.create()
        old = self.item()
        value = {**self.value, 'changeKind': 'progress'}
        source = self.supplied(value)
        original_read = plans.read_regular
        reads = 0

        def changed_read(path):
            nonlocal reads
            raw = original_read(path)
            if path.name == 'plan.md':
                reads += 1
                if reads == 3:
                    return raw + b'Concurrent writer\n'
            return raw

        with patch.object(plans, 'read_regular', side_effect=changed_read):
            code, response, _ = self.invoke(plans.update_command, self.root, self.value['id'], source, old['sha256'], False, 'json', 65536)
        self.assertEqual(code, 2)
        self.assertIn('changed before replacement', response['error']['message'])
        self.assertEqual((self.root / 'docs/plans' / old['path']).read_bytes(), old['raw'])

    def test_lock_owned_elsewhere_is_not_removed(self):
        self.create()
        lock = self.root / 'docs/plans/.plan-write.lock'
        lock.write_text('owner data\n', encoding='utf-8')
        self.assertEqual(self.create()[0], 2)
        self.assertEqual(lock.read_text(), 'owner data\n')

    def test_interruption_after_snapshot_preserves_fail_closed_artifacts(self):
        self.create()
        old = self.item()['raw']
        with patch.object(plans.os, 'replace', side_effect=OSError('simulated interruption')):
            self.assertEqual(self.approve()[0], 2)
        root = self.root / 'docs/plans'
        self.assertTrue((root / '.plan-write.lock').exists())
        self.assertTrue(list(root.glob('.pending-*')))
        self.assertEqual((root / plans.relative_path(plans.parse(old))).read_bytes(), old)
        self.assertTrue(plans.integrity_issues(self.root))

    def test_budget_failure_writes_no_plan_and_leaves_no_lock(self):
        self.assertEqual(self.invoke(plans.create_command, self.root, self.supplied(self.value), False, 'json', 4)[0], 2)
        self.assertEqual(plans.load_store(self.root), [])
        self.assertFalse((self.root / 'docs/plans/.plan-write.lock').exists())


if __name__ == '__main__':
    unittest.main()
