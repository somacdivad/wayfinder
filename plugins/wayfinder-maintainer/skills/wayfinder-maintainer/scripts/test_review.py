"""Behavioral regressions for local review, recovery and result accounting."""
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import maintainer_plans as plans
import maintainer_review as review
import maintainer_unittest as runner


def identifier(prefix):
    return prefix + '-' + str(uuid.uuid4())


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'repository'
        self.root.mkdir()
        self.input = self.root.parent / 'input.json'
        self.plan_id = identifier('wp')
        value = dict(id=self.plan_id, subject='development', slug='example', title='Example', summary='Review example', status='draft', updated='2026-09-15', body='# Example\n\nOutcome\n', records=[], approval=None)
        self.input.write_text(json.dumps(value))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(plans.create_command(self.root, self.input, False, 'json', 65536), 0)
            item = plans.load_store(self.root)[0]
            value.update(status='approved', changeKind='approval', approval=dict(locator='conversation:owner', quotation='yes'))
            self.input.write_text(json.dumps(value))
            self.assertEqual(plans.update_command(self.root, self.plan_id, self.input, item['sha256'], False, 'json', 65536), 0)
        self.snapshot = plans.load_store(self.root)[0]['approvals'][2]['sha256']
        self.report = self.result()
        self.assertEqual(self.call('verification', 'capture', self.report)[0], 0)
        self.packet = dict(format='wayfinder-review-packet', schemaVersion=1, id=identifier('rr'), planId=self.plan_id, approvedPlanRevision=2, approvedPlanSha256=self.snapshot, repository='example/demo', owner='owner', members=[dict(number=4, url='https://github.com/example/demo/pull/4', headCommit='a'*40, baseCommit='b'*40, mergeBaseCommit='b'*40, reviewedDiffSha256='c'*64, dependencies=[])], verificationIds=[self.report['id']], limitations=[], exclusions=['No publication'], requestedAuthority='eligible merging under protections', observedAt='2026-09-15T15:00:00Z')
        self.assertEqual(self.call('review', 'create', self.packet)[0], 0)

    def result(self):
        return dict(format='wayfinder-verification-report', schemaVersion=1, id=identifier('vr'), planId=self.plan_id, provenance=dict(command='maintain.py self-test', selection='all', testedCommit='a'*40, worktreeSha256='d'*64, runtime='CPython 3.12', startedAt='2026-09-15T14:00:00Z', finishedAt='2026-09-15T14:00:01Z'), results=dict(unit='test-case', testsRun=1, passed=1, skipped=0, expectedFailures=0, unexpectedSuccesses=0, caseFailures=0, caseErrors=0, subtestEvents=[], fixtureErrors=[], interrupted=False, skipReasons=[]), suiteSuccessful=True, coverage=[dict(checkId='recovery', outcome='passed', required=True, exception=None)], requiredCoverageComplete=True, readyForReview=True, bytecodeArtifacts=[])

    def call(self, group, action, value=None, **kwargs):
        if value is not None:
            self.input.write_text(json.dumps(value))
        digest = review.history(self.root, self.plan_id)[3]
        args = SimpleNamespace(command=group, plan_id=self.plan_id, input=self.input, id=getattr(self, 'packet', {}).get('id'), request_id=getattr(self, 'packet', {}).get('id'), dry_run=False, expected_store_sha256=digest, format='json', max_bytes=65536, cursor=None, observations=None, **{group + '_command': action})
        for key, item in kwargs.items():
            setattr(args, key, item)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = review.command(self.root, args)
        return code, json.loads(stream.getvalue())

    def event(self, phase, second, **extra):
        return dict(format='wayfinder-delivery-event', schemaVersion=1, id=identifier('de'), requestId=self.packet['id'], memberNumber=4, headCommit='a'*40, operationMarker=self.packet['id']+'/4/'+'a'*40, phase=phase, at=f'2026-09-15T15:00:{second:02d}Z', reason=phase, commentId=None, commentUrl=None, **extra)

    def test_single_request_question_and_no_inferred_approval(self):
        code, response = self.call('review', 'validate')
        self.assertEqual(code, 0)
        self.assertEqual(response['format'], 'wayfinder-maintainer-response')
        self.assertFalse(response['data']['ownerApprovalInferred'])
        self.assertFalse(response['data']['mergeEligibilityEstablished'])
        self.assertEqual(response['data']['approvalQuestion'].count('?'), 1)

    def test_changed_diff_same_head_requires_review(self):
        observed = dict(repository='example/demo', observedAt='2026-09-15T16:00:00Z', members=[{key: val for key, val in self.packet['members'][0].items() if key not in ('url', 'dependencies')}])
        observed['members'][0]['reviewedDiffSha256'] = 'e'*64
        path = self.root.parent / 'observations.json'; path.write_text(json.dumps(observed))
        code, data = self.call('review', 'validate', observations=path)
        self.assertEqual(code, 1)
        self.assertEqual(data['data']['changedMembers'], [4])

    def test_base_movement_with_identical_diff_preserves_version(self):
        observed = dict(repository='example/demo', observedAt='2026-09-15T16:00:00Z', members=[{key: val for key, val in self.packet['members'][0].items() if key not in ('url', 'dependencies')}])
        observed['members'][0]['baseCommit'] = 'e'*40
        path = self.root.parent / 'observations.json'; path.write_text(json.dumps(observed))
        self.assertEqual(self.call('review', 'validate', observations=path)[0], 0)

    def test_supersession_is_immutable_and_not_approval(self):
        replacement = {**self.packet, 'id': identifier('rr')}
        self.assertEqual(self.call('review', 'create', replacement)[0], 0)
        self.assertEqual(self.call('review', 'validate')[0], 1)
        value = dict(format='wayfinder-review-supersession', schemaVersion=1, id=identifier('rs'), requestId=self.packet['id'], replacementRequestId=replacement['id'], reason='revision', at='2026-09-15T16:00:00Z')
        self.assertEqual(self.call('review', 'supersede', value)[0], 0)
        self.assertEqual(self.call('review', 'validate')[0], 1)
        self.assertEqual(self.call('review', 'validate', id=replacement['id'])[0], 0)
        self.assertEqual(self.call('review', 'supersede', {**value, 'id': identifier('rs')})[0], 2)

    def test_false_retained_approval_and_subset_members_are_rejected(self):
        value = {**self.packet, 'id': identifier('rr'), 'retainedApprovals': [dict(memberNumber=4, requestId=self.packet['id'], recordId='wr-0037')]}
        # Plan approval is not an explicit member-bound PR approval.
        self.assertEqual(self.call('review', 'create', value)[0], 2)
        value['retainedApprovals'][0]['memberNumber'] = 5
        self.assertEqual(self.call('review', 'create', value)[0], 2)

    def test_explicit_unchanged_subset_provenance_excludes_member_from_question(self):
        replacement = copy.deepcopy(self.packet)
        replacement['id'] = identifier('rr')
        report = self.result(); report['provenance']['testedCommit'] = 'e'*40
        self.assertEqual(self.call('verification', 'capture', report)[0], 0)
        member = {**replacement['members'][0], 'number': 5, 'url': 'https://github.com/example/demo/pull/5', 'headCommit': 'e'*40, 'dependencies': [4]}
        replacement['members'].append(member)
        replacement['verificationIds'].append(report['id'])
        replacement['retainedApprovals'] = [dict(memberNumber=4, requestId=self.packet['id'], recordId='wr-0099')]
        decision = {'metadata': {'id': 'wr-0099', 'kind': 'decision', 'outcome': 'accepted', 'authorities': [{'locator': 'conversation:owner', 'quotation': 'Approve #4 only'}], 'sources': ['review-request:' + self.packet['id'] + '/member:4']}}
        import maintainer_records
        with patch.object(maintainer_records, 'load_store', return_value=[decision]):
            self.assertEqual(self.call('review', 'create', replacement)[0], 0)
            data = self.call('review', 'read', id=replacement['id'])[1]['data']
        self.assertIn('PRs #5 ', data['approvalQuestion'])
        self.assertNotIn('PRs #4', data['approvalQuestion'])
        self.assertFalse(data['ownerApprovalInferred'])

    def test_uncertain_delivery_stops_and_reconciles_without_resend(self):
        self.assertEqual(self.call('delivery', 'append', self.event('prepared', 1))[0], 0)
        self.assertEqual(self.call('delivery', 'append', self.event('attempted', 2))[0], 0)
        uncertain = self.event('uncertain', 3)
        self.assertEqual(self.call('delivery', 'append', uncertain)[0], 0)
        self.assertEqual(self.call('delivery', 'read')[1]['data']['nextAction'], 'stop-until-owner-return')
        self.assertEqual(self.call('delivery', 'append', self.event('attempted', 4))[0], 2)
        ack = self.event('acknowledged', 5, reconcilesEventId=uncertain['id'])
        ack.update(commentId=123, commentUrl='https://github.com/example/demo/pull/4#issuecomment-123')
        self.assertEqual(self.call('delivery', 'append', ack)[0], 0)
        state = self.call('delivery', 'read')[1]['data']
        self.assertEqual((state['acknowledged'], state['uncertain']), (1, 0))
        self.assertEqual(len(state['events']), 4)
        self.assertEqual(self.call('delivery', 'append', self.event('attempted', 6))[0], 2)

    def test_undiscovered_comment_needs_known_no_effect_before_retry(self):
        for phase, second in [('prepared', 1), ('attempted', 2)]:
            self.call('delivery', 'append', self.event(phase, second))
        uncertain = self.event('uncertain', 3); self.call('delivery', 'append', uncertain)
        reconciled = self.event('failed-with-known-no-effect', 4, reconcilesEventId=uncertain['id'])
        self.assertEqual(self.call('delivery', 'append', reconciled)[0], 0)
        self.assertEqual(self.call('delivery', 'append', self.event('attempted', 5))[0], 0)

    def test_duplicate_receipt_and_wrong_version_are_rejected(self):
        value = self.event('prepared', 1)
        self.assertEqual(self.call('delivery', 'append', value)[0], 0)
        self.assertEqual(self.call('delivery', 'append', value)[0], 2)
        value = self.event('attempted', 2); value['headCommit'] = 'f'*40
        self.assertEqual(self.call('delivery', 'append', value)[0], 2)

    def test_stale_digest_dry_run_and_lock_failure_have_no_effect(self):
        report = {**self.report, 'id': identifier('vr')}
        before = review.history(self.root, self.plan_id)[3]
        self.assertEqual(self.call('verification', 'capture', report, dry_run=True)[0], 0)
        self.assertEqual(review.history(self.root, self.plan_id)[3], before)
        self.assertEqual(self.call('verification', 'capture', report, expected_store_sha256='0'*64)[0], 2)
        with patch.object(review.os, 'link', side_effect=OSError('interrupted publication')):
            self.assertEqual(self.call('verification', 'capture', report)[0], 2)
        self.assertTrue((self.root/'docs/plans/.plan-write.lock').exists())
        self.assertTrue(plans.integrity_issues(self.root))

    def test_linked_report_missing_and_snapshot_mismatch_fail(self):
        value = {**self.packet, 'id': identifier('rr'), 'approvedPlanSha256': '0'*64}
        self.assertEqual(self.call('review', 'create', value)[0], 2)
        value['approvedPlanSha256'] = self.snapshot
        value['verificationIds'] = [identifier('vr')]
        self.assertEqual(self.call('review', 'create', value)[0], 2)

    def test_unknown_fields_and_incomplete_success_fail(self):
        value = {**self.report, 'id': identifier('vr'), 'guess': True}
        self.assertEqual(self.call('verification', 'capture', value)[0], 2)
        value.pop('guess'); value['results'] = {**value['results'], 'testsRun': 2}
        self.assertEqual(self.call('verification', 'capture', value)[0], 2)

    def test_missing_coverage_blocks_and_explicit_exception_is_visible(self):
        value = copy.deepcopy(self.report); value['id'] = identifier('vr')
        value['coverage'][0]['outcome'] = 'unavailable'
        value.update(requiredCoverageComplete=False, readyForReview=False)
        self.assertEqual(self.call('verification', 'capture', value)[0], 0)
        rendered = self.call('verification', 'render', id=value['id'])[1]['data']
        self.assertFalse(rendered['readyForReview'])
        self.assertIn('UNAVAILABLE recovery', review.human(rendered))
        value['id'] = identifier('vr')
        value['coverage'][0]['exception'] = dict(locator='approved-plan:2', reason='Owner explicitly accepted unavailable baseline')
        value.update(requiredCoverageComplete=True, readyForReview=True)
        self.assertEqual(self.call('verification', 'capture', value)[0], 0)
        self.assertIn('not passed', review.human(value))

    def test_bytecode_and_interruption_block_readiness(self):
        value = copy.deepcopy(self.report); value['id'] = identifier('vr')
        value['bytecodeArtifacts'] = ['__pycache__']; value['readyForReview'] = False
        self.assertEqual(self.call('verification', 'capture', value)[0], 0)
        value['id'] = identifier('vr'); value['results']['interrupted'] = True
        value.update(suiteSuccessful=False, requiredCoverageComplete=False)
        self.assertEqual(self.call('verification', 'capture', value)[0], 0)

    def test_chunk_reconstruction_and_changed_history_cursor(self):
        chunks = []; cursor = None
        while True:
            code, response = self.call('review', 'read', max_bytes=101, cursor=cursor)
            self.assertEqual(code, 2 if response['nextCursor'] else 0)
            chunks.append(response['data']['text'])
            cursor = response['nextCursor']
            if cursor is None:
                break
        reconstructed = ''.join(chunks).encode()
        self.assertEqual(review.digest(reconstructed), response['sourceSha256'])
        self.assertEqual(json.loads(reconstructed)['packet']['id'], self.packet['id'])
        cursor = self.call('review', 'read', max_bytes=101)[1]['nextCursor']
        self.call('delivery', 'append', self.event('prepared', 1))
        self.assertEqual(self.call('review', 'read', max_bytes=101, cursor=cursor)[0], 2)

    def test_unsafe_or_orphan_auxiliary_files_rejected(self):
        item, folder, _, _ = review.history(self.root, self.plan_id)
        extra = folder/'verification/other.json'; extra.write_text('{}')
        self.assertTrue(plans.integrity_issues(self.root))
        extra.unlink()
        symlink = folder/'verification/link.json'
        try:
            symlink.symlink_to(self.input)
        except OSError:
            self.skipTest('symlink creation unavailable')
        self.assertTrue(plans.integrity_issues(self.root))


class AccountingTests(unittest.TestCase):
    def test_direct_callbacks_with_subtests_expected_failure_and_skip(self):
        class Cases(unittest.TestCase):
            def test_pass(self):
                self.assertTrue(True)
            @unittest.skip('unavailable')
            def test_skip(self):
                pass
            @unittest.expectedFailure
            def test_expected(self):
                self.fail('expected')
            def test_subtests(self):
                for value in (1, 2):
                    with self.subTest(value=value):
                        self.assertEqual(value, 0)
        result = runner.run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(Cases), io.StringIO())
        counts = result['results']
        self.assertEqual((counts['testsRun'], counts['passed'], counts['skipped'], counts['expectedFailures']), (4, 1, 1, 1))
        self.assertEqual(len(counts['subtestEvents']), 2)
        self.assertEqual(counts['caseFailures'], 0)
        self.assertFalse(result['suiteSuccessful'])

    def test_fixture_error_and_unexpected_success_are_distinct(self):
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError('fixture failed')
            def test_unused(self):
                pass
        class Unexpected(unittest.TestCase):
            @unittest.expectedFailure
            def test_unexpected(self):
                pass
        suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Broken), unittest.defaultTestLoader.loadTestsFromTestCase(Unexpected)])
        result = runner.run_suite(suite, io.StringIO())
        self.assertEqual(result['results']['testsRun'], 1)
        self.assertEqual(result['results']['unexpectedSuccesses'], 1)
        self.assertEqual(len(result['results']['fixtureErrors']), 1)
        self.assertEqual(result['results']['passed'], 0)
