"""Migration fidelity, authority visibility, and record-store failure boundaries."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import maintain
import maintainer_records as records
from maintainer_output import canonical_json, make_cursor


STORE = maintain.COMPANION_ROOT / 'references/design-record'


def capture(function, *args, **kwargs):
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = function(*args, **kwargs)
    return code, stdout.getvalue(), stderr.getvalue()


class RecordStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='wayfinder-record-test-')
        self.parent = Path(self.temporary.name).resolve()
        self.store = self.parent / 'references/design-record'
        shutil.copytree(STORE, self.store)
        self.initial = records.load_store(self.store)
        self.next_id = f'wr-{len(self.initial) + 1:04d}'

    def tearDown(self):
        self.temporary.cleanup()

    def supplied(self, **changes):
        value = {'topic': 'governance', 'candidateRevision': None, 'title': 'Synthetic proposal', 'kind': 'proposal', 'outcome': 'pending',
                 'date': '2026-09-15', 'summary': 'A synthetic pending decision for record-store tests.',
                 'body': 'A substantive synthetic proposal with αβγ and 🙂.\n\nNo external actions are authorized.',
                 'predecessors': [], 'authorities': [], 'sources': []}
        value.update(changes)
        return value

    def add(self, value=None, dry_run=False, maximum=65536):
        path = self.parent / 'input.json'
        path.write_text(json.dumps(value or self.supplied(), ensure_ascii=False) + '\n', encoding='utf-8')
        return capture(records.add_command, self.store, path, dry_run, 'json', maximum)

    def snapshot(self):
        return {path.relative_to(self.store).as_posix(): path.read_bytes() for path in self.store.rglob('*') if path.is_file()}

    def test_migration_reconstructs_entire_original_and_pins_legacy_records(self):
        self.assertEqual(records.integrity_issues(self.store), [])
        manifest = json.loads((self.store / 'migration.json').read_text())
        self.assertEqual(len(manifest['sections']), 31)
        self.assertEqual(manifest['sourceBytes'], 131495)
        self.assertEqual(manifest['sourceSha256'], 'd34cfefdff357f7c3511eb3efe632921f9be76dedfdd298fc1dd42395b0ebadf')
        self.assertEqual(sum(len(entry['linkAdjustments']) for entry in manifest['sections']), 24)
        for title in ('Governing brief', 'Accepted choices', 'Workflow progress', 'Stub state', 'Next decision'):
            item = records.find_record(self.initial, heading=title)
            self.assertIsNone(item['metadata']['date'])
        path = self.store / self.initial[0]['path']
        path.write_bytes(path.read_bytes() + b'Unreviewed alteration.\n')
        self.assertTrue(records.integrity_issues(self.store))
        before = self.snapshot()
        code, raw, _ = self.add()
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(raw)['complete'])
        self.assertEqual(self.snapshot(), before)

    def test_inverse_link_adjustments_are_checked_not_just_file_hashes(self):
        manifest_path = self.store / 'migration.json'
        manifest = json.loads(manifest_path.read_text())
        entry = next(item for item in manifest['sections'] if item['linkAdjustments'])
        entry['linkAdjustments'][0]['before'] = 'wrong-original-destination'
        manifest_path.write_text(json.dumps(manifest) + '\n')
        issues = records.integrity_issues(self.store, expected_migration_digest=None)
        self.assertTrue(issues)
        self.assertIn('historical section', issues[0])

    def test_legacy_links_and_anchors_resolve(self):
        entrypoint = maintain.COMPANION_ROOT / 'references/design-record.md'
        text = entrypoint.read_text()
        manifest = json.loads((self.store / 'migration.json').read_text())
        for entry in manifest['sections']:
            self.assertIn('## ' + entry['title'] + '\n', text)
            self.assertIn('(design-record/' + entry['path'] + ')', text)
        for item in records.load_store(STORE):
            for destination in re.findall(r'\]\(([^\s()]+)\)', item['body'].decode()):
                if destination.startswith(('#', '/')) or re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', destination):
                    continue
                path = destination.partition('#')[0]
                self.assertTrue((STORE / item['path']).parent.joinpath(path).resolve().exists(), (item['metadata']['id'], destination))

    def test_add_is_one_complete_file_and_preserves_existing_bytes_and_current_state(self):
        before = self.snapshot()
        current_state = maintain.CURRENT_STATE_PATH.read_bytes()
        code, raw, diagnostics = self.add()
        self.assertEqual(code, 0, diagnostics)
        result = json.loads(raw)
        self.assertTrue(result['complete'])
        self.assertFalse(result['data']['currentStateUpdated'])
        self.assertEqual(result['data']['id'], self.next_id)
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {result['data']['path']})
        self.assertTrue(all(after[name] == content for name, content in before.items()))
        self.assertEqual(maintain.CURRENT_STATE_PATH.read_bytes(), current_state)
        self.assertEqual(records.digest(after[result['data']['path']]), result['sourceSha256'])
        self.assertEqual(records.integrity_issues(self.store), [])

    def test_dry_run_matches_created_bytes_without_managed_writes(self):
        before = self.snapshot()
        code, raw, diagnostics = self.add(dry_run=True)
        self.assertEqual(code, 0, diagnostics)
        preview = json.loads(raw)['data']
        self.assertFalse(preview['written'])
        self.assertEqual(self.snapshot(), before)
        code, raw, diagnostics = self.add()
        self.assertEqual(code, 0, diagnostics)
        created = json.loads(raw)['data']
        self.assertEqual(created['id'], preview['id'])
        self.assertEqual(created['sha256'], preview['sha256'])
        self.assertEqual((self.store / created['path']).read_bytes(), preview['text'].encode())

    def test_invalid_inputs_never_write_managed_files(self):
        invalid = [self.supplied(topic='../../outside'), self.supplied(candidateRevision=9),
                   self.supplied(date=None), self.supplied(date='2026-02-30'), self.supplied(title='Two\nlines'),
                   self.supplied(kind='decision', outcome='accepted'), self.supplied(kind='closure', outcome='accepted'),
                   self.supplied(kind='proposal', outcome='accepted'), self.supplied(body='bad\r\ntext'),
                   self.supplied(sources=['record:wr-9999']), self.supplied(predecessors=['wr-9999']),
                   self.supplied(authorities=[{'locator': 'test:owner'}])]
        for value in invalid:
            with self.subTest(value=value):
                before = self.snapshot()
                code, raw, _ = self.add(value)
                self.assertEqual(code, 2)
                self.assertFalse(json.loads(raw)['complete'])
                self.assertEqual(self.snapshot(), before)
        path = self.parent / 'duplicate.json'
        path.write_text('{"topic":"governance","topic":"initialize"}\n')
        code, raw, _ = capture(records.add_command, self.store, path, False, 'json', 65536)
        self.assertEqual(code, 2)
        self.assertIn('duplicate', json.loads(raw)['error']['message'])

    def test_accepted_closure_keeps_explicit_authority_and_later_outcomes_visible(self):
        self.assertEqual(self.add()[0], 0)
        second = f'wr-{len(self.initial) + 2:04d}'
        value = self.supplied(title='Synthetic closure', kind='closure', outcome='accepted', predecessors=[self.next_id],
                              authorities=[{'locator': 'test:explicit-owner-decision', 'quotation': 'Close the synthetic proposal.'}])
        code, _, diagnostics = self.add(value)
        self.assertEqual(code, 0, diagnostics)
        store = records.load_store(self.store)
        chain = records.history(store, self.next_id)
        self.assertEqual([item['metadata']['id'] for item in chain], [self.next_id, second])
        self.assertEqual(chain[-1]['metadata']['authorities'][0]['quotation'], 'Close the synthetic proposal.')
        self.assertEqual(records.history(store, second), chain)

    def test_authority_and_source_links_are_followed_without_inbound_citation_fanout(self):
        self.assertEqual(self.add()[0], 0)
        source_id = f'wr-{len(self.initial) + 2:04d}'
        self.assertEqual(self.add(self.supplied(title='Source citation', sources=['record:' + self.next_id]))[0], 0)
        store = records.load_store(self.store)
        self.assertEqual([item['metadata']['id'] for item in records.history(store, self.next_id)], [self.next_id])
        self.assertEqual([item['metadata']['id'] for item in records.history(store, source_id)], [self.next_id, source_id])

    def test_read_chunks_reconstruct_exact_bytes_and_refuse_stale_or_wrong_scope_cursors(self):
        self.assertEqual(self.add()[0], 0)
        item = records.find_record(records.load_store(self.store), identifier=self.next_id)
        cursor, chunks, indexes = None, [], []
        before = self.snapshot()
        while True:
            code, raw, diagnostics = capture(records.read_command, self.store, self.next_id, None, False, 'json', 'complete-evidence', 93, cursor)
            result = json.loads(raw)
            self.assertIsNone(result['data'].get('items'))
            chunks.append(result['data']['text'].encode())
            indexes.append(result['data']['chunkIndex'])
            self.assertEqual(result['data']['startByte'], sum(map(len, chunks[:-1])))
            cursor = result['nextCursor']
            self.assertEqual(code, 2 if cursor else 0, diagnostics)
            self.assertEqual(result['complete'], cursor is None)
            if cursor is None:
                break
        self.assertEqual(b''.join(chunks), item['raw'])
        self.assertEqual(records.digest(b''.join(chunks)), result['sourceSha256'])
        self.assertEqual(indexes, list(range(result['data']['chunkCount'])))
        self.assertEqual(self.snapshot(), before)
        _, raw, _ = capture(records.read_command, self.store, self.next_id, None, False, 'json', 'complete-evidence', 93, None)
        cursor = json.loads(raw)['nextCursor']
        for identifier, budget, klass, include_history in ((self.next_id, 94, 'complete-evidence', False),
                                                         ('wr-0001', 93, 'complete-evidence', False),
                                                         (self.next_id, 93, 'discovery-preview', False),
                                                         (self.next_id, 93, 'complete-evidence', True)):
            code, _, diagnostic = capture(records.read_command, self.store, identifier, None, include_history, 'json', klass, budget, cursor)
            self.assertEqual(code, 2)
            self.assertIn('stale', diagnostic)
        self.assertEqual(self.add(self.supplied(title='Another record'))[0], 0)
        code, _, diagnostics = capture(records.read_command, self.store, self.next_id, None, False, 'json', 'complete-evidence', 93, cursor)
        self.assertEqual(code, 2)
        self.assertIn('stale', diagnostics)

    def test_history_chunk_metadata_stays_scoped_to_returned_bytes(self):
        code, raw, _ = capture(records.read_command, self.store, 'wr-0031', None, True, 'json', 'complete-evidence', 40, None)
        result = json.loads(raw)
        self.assertEqual(code, 2)
        self.assertGreater(result['data']['recordCount'], 1)
        self.assertEqual(len(result['data']['records']), 1)
        self.assertNotIn('summary', result['data']['records'][0])
        self.assertLessEqual(result['returnedBytes'], 40)

    def test_inventory_pages_reconstruct_full_metadata_and_detect_store_changes(self):
        expected = [records.inventory_item(item) for item in self.initial]
        cursor, pages = None, []
        while True:
            code, raw, diagnostics = capture(records.list_command, self.store, None, 'json', 'complete-evidence', 1800, cursor)
            result = json.loads(raw)
            self.assertEqual(result['data']['startItem'], len(pages))
            pages.extend(result['data']['items'])
            self.assertLessEqual(result['returnedBytes'], 1800)
            cursor = result['nextCursor']
            self.assertEqual(code, 2 if cursor else 0, diagnostics)
            if not cursor:
                break
        self.assertEqual(pages, expected)
        self.assertEqual(records.digest(canonical_json(pages).encode()), result['sourceSha256'])
        _, raw, _ = capture(records.list_command, self.store, None, 'json', 'complete-evidence', 1800, None)
        cursor = json.loads(raw)['nextCursor']
        self.assertEqual(self.add()[0], 0)
        code, _, diagnostics = capture(records.list_command, self.store, None, 'json', 'complete-evidence', 1800, cursor)
        self.assertEqual(code, 2)
        self.assertIn('stale', diagnostics)
        code, raw, _ = capture(records.list_command, self.store, None, 'json', 'discovery-preview', 1800, None)
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(raw)['complete'])
        self.assertEqual(capture(records.list_command, self.store, None, 'json', 'complete-evidence', 4, None)[0], 2)

    def test_legacy_alias_resolves_exact_record_and_rejects_old_cursors_or_ambiguous_titles(self):
        with mock.patch.object(maintain, 'COMPANION_ROOT', self.parent):
            code, raw, diagnostics = capture(maintain.main, ['record-section', '--heading', 'Governing brief', '--format', 'json'])
            self.assertEqual(code, 0, diagnostics)
            result = json.loads(raw)
            self.assertEqual(result['data']['id'], 'wr-0001')
            self.assertEqual(result['data']['text'].encode(), self.initial[0]['raw'])
            cursor = make_cursor({'command': 'record-section', 'scope': '## Governing brief', 'sourceSha256': records.digest(self.initial[0]['body']), 'maxBytes': 40, 'offset': 40})
            code, _, diagnostics = capture(maintain.main, ['record-section', '--heading', 'Governing brief', '--format', 'json', '--max-bytes', '40', '--cursor', cursor])
            self.assertEqual(code, 2)
            self.assertIn('stale', diagnostics)
            self.assertEqual(self.add(self.supplied(title='Governing brief'))[0], 0)
            code, _, diagnostics = capture(maintain.record_section_command, 'Governing brief')
            self.assertEqual(code, 2)
            self.assertIn('ambiguous', diagnostics)

    def test_ordinal_gaps_and_duplicate_ids_fail_closed(self):
        item = self.initial[-1]
        path = self.store / item['path']
        # Removing an interior record cannot be hidden by reassigning the next ID.
        (self.store / self.initial[3]['path']).unlink()
        with self.assertRaisesRegex(ValueError, 'gap'):
            records.load_store(self.store)
        shutil.copyfile(STORE / self.initial[3]['path'], self.store / self.initial[3]['path'])
        duplicate = path.with_name(item['metadata']['id'] + '-duplicate.md')
        duplicate.write_bytes(item['raw'])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            records.load_store(self.store)

    def test_unsafe_symlinks_and_existing_nonrecord_targets_are_not_overwritten(self):
        outside = self.parent / 'outside'
        outside.mkdir()
        symlink = self.store / 'governance/linked'
        symlink.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        self.assertEqual(self.add()[0], 2)
        self.assertEqual(self.snapshot(), before)
        symlink.unlink()
        target = self.store / 'governance' / (self.next_id + '-synthetic-proposal.md')
        target.write_text('Unowned existing content.\n')
        self.assertEqual(self.add()[0], 2)
        self.assertEqual(target.read_text(), 'Unowned existing content.\n')

    def test_failed_publication_cleans_owned_artifacts_without_partial_record(self):
        before = self.snapshot()
        with mock.patch.object(records.os, 'link', side_effect=OSError('hard links unavailable')):
            code, _, diagnostics = self.add()
        self.assertEqual(code, 2)
        self.assertIn('hard links unavailable', diagnostics)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(records.integrity_issues(self.store), [])

    def test_failure_after_publication_retains_the_completed_record_for_inspection(self):
        original_read = records.read_regular
        def fail_verification(path):
            if path.name.startswith(self.next_id + '-'):
                raise OSError('post-publication inspection failed')
            return original_read(path)
        with mock.patch.object(records, 'read_regular', side_effect=fail_verification):
            code, _, diagnostics = self.add()
        self.assertEqual(code, 2)
        self.assertIn('post-publication', diagnostics)
        self.assertEqual(len(records.load_store(self.store)), len(self.initial) + 1)
        self.assertEqual(records.integrity_issues(self.store), [])

    def test_stale_lock_and_pending_artifacts_require_explicit_inspection(self):
        lock = self.store / '.record-add.lock'
        lock.write_text('{"pid":0,"host":"unknown"}\n')
        before = self.snapshot()
        self.assertEqual(self.add()[0], 2)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(records.integrity_issues(self.store))
        lock.unlink()
        staging = self.store / '.pending-interrupted'
        staging.write_text('partial staging\n')
        before = self.snapshot()
        self.assertEqual(self.add()[0], 2)
        self.assertEqual(self.snapshot(), before)

    def test_output_budget_failure_happens_before_publication(self):
        before = self.snapshot()
        self.assertEqual(self.add(maximum=4)[0], 2)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.add(dry_run=True, maximum=4)[0], 2)
        self.assertEqual(self.snapshot(), before)

    def test_parallel_processes_never_allocate_duplicate_ordinals_or_overwrite(self):
        source = self.parent / 'parallel.json'
        source.write_text(json.dumps(self.supplied()) + '\n')
        script_root = str(maintain.COMPANION_ROOT / 'scripts')
        code = 'import sys; sys.dont_write_bytecode=True; sys.path.insert(0,sys.argv[1]); from pathlib import Path; import maintainer_records as r; raise SystemExit(r.add_command(Path(sys.argv[2]),Path(sys.argv[3]),False,"json",65536))'
        command = [sys.executable, '-B', '-c', code, script_root, str(self.store), str(source)]
        children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        results = [(child, child.communicate(timeout=30)) for child in children]
        self.assertTrue(all(child.returncode in (0, 2) for child, _ in results))
        successful = [json.loads(output[0])['data']['id'] for child, output in results if child.returncode == 0]
        self.assertGreaterEqual(len(successful), 1)
        self.assertEqual(len(successful), len(set(successful)))
        self.assertEqual(len(records.load_store(self.store)), len(self.initial) + len(successful))
        self.assertEqual(records.integrity_issues(self.store), [])


class RecordRoutingTests(unittest.TestCase):
    def test_current_context_routes_to_individual_records_and_commands(self):
        context = maintain.current_context()
        routes = [item for item in context['routing'] if item['id'].startswith('design-record:')]
        self.assertTrue(routes)
        for item in routes:
            self.assertIn('/references/design-record/', item['path'])
            self.assertIn('record read --id wr-', item['nextCommand'])
            self.assertIn('--history', item['nextCommand'])
        self.assertIn('designRecordStore', context['paths'])
        for mode in ('investigation', 'implementation', 'hosted-review', 'acceptance-record'):
            with mock.patch.object(maintain, 'doctor', return_value=0):
                code, text, _ = capture(maintain.handoff_command, mode, 'Synthetic bounded objective', [])
            self.assertEqual(code, 0)
            for marker in ('record list', 'record read --id ID --history', 'record add --input FILE', 'current-state routing'):
                self.assertIn(marker, text)
