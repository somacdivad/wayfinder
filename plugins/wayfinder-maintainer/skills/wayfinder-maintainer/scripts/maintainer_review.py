"""Local immutable review packets, delivery events, and verification reports.

Supplied observations/quotations are assertions, never authenticated authority.
No network, shell execution, Git mutation, or implicit owner decision occurs here.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tempfile
import uuid
from pathlib import Path

import maintainer_plans as plans
from maintainer_records import canonical_json, digest, read_regular, safe_path, strict_json
from maintainer_output import bounded_chunk, emit_json, make_cursor, read_cursor

PACKET = {'format', 'schemaVersion', 'id', 'planId', 'approvedPlanRevision', 'approvedPlanSha256', 'repository', 'owner', 'members', 'verificationIds', 'limitations', 'exclusions', 'requestedAuthority', 'observedAt'}
SUPERSEDE = {'format', 'schemaVersion', 'id', 'requestId', 'replacementRequestId', 'reason', 'at'}
EVENT = {'format', 'schemaVersion', 'id', 'requestId', 'memberNumber', 'headCommit', 'operationMarker', 'phase', 'at', 'reason', 'commentId', 'commentUrl'}
REPORT = {'format', 'schemaVersion', 'id', 'planId', 'provenance', 'results', 'suiteSuccessful', 'coverage', 'requiredCoverageComplete', 'readyForReview', 'bytecodeArtifacts'}
RESULTS = {'unit', 'testsRun', 'passed', 'skipped', 'expectedFailures', 'unexpectedSuccesses', 'caseFailures', 'caseErrors', 'subtestEvents', 'fixtureErrors', 'interrupted', 'skipReasons'}
PHASES = ('prepared', 'attempted', 'acknowledged', 'failed-with-known-no-effect', 'uncertain')


def shape(value, fields, optional=()):
    if not isinstance(value, dict) or not fields <= set(value) or set(value) - fields - set(optional):
        raise ValueError('unknown or missing JSON fields')


def text(value):
    if not isinstance(value, str) or not value.strip() or '\x00' in value or '\r' in value:
        raise ValueError('nonempty LF-only text required')


def identity(value, prefix):
    text(value)
    if not value.startswith(prefix + '-'):
        raise ValueError('wrong identity prefix')
    parsed = uuid.UUID(value[len(prefix) + 1:])
    if not parsed.int or str(parsed) != value[len(prefix) + 1:]:
        raise ValueError('nonzero canonical lowercase UUID required')


def sha(value, commit=False):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}' if commit else r'[0-9a-f]{64}', value):
        raise ValueError('invalid digest/commit identity')


def number(value):
    if type(value) is not int or value < 1:
        raise ValueError('positive integer required')


def when(value):
    text(value)
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return parsed


def strings(items):
    if not isinstance(items, list):
        raise ValueError('list required')
    for item in items:
        text(item)
    if len(items) != len(set(items)):
        raise ValueError('duplicate list members')


def flags(value, names):
    if any(type(value[key]) is not bool for key in names):
        raise ValueError('boolean required')


def result_valid(value):
    shape(value, RESULTS)
    if value['unit'] != 'test-case':
        raise ValueError('result accounting unit must be test-case')
    counters = ('testsRun', 'passed', 'skipped', 'expectedFailures', 'unexpectedSuccesses', 'caseFailures', 'caseErrors')
    if any(type(value[key]) is not int or value[key] < 0 for key in counters):
        raise ValueError('nonnegative integer result counters required')
    if any(value[key] > value['testsRun'] for key in counters[1:]):
        raise ValueError('case outcome count exceeds testsRun')
    flags(value, ['interrupted'])
    # Reasons may repeat for different skipped tests.
    if not isinstance(value['skipReasons'], list):
        raise ValueError('skip reasons must be a list')
    for reason in value['skipReasons']:
        text(reason)
    for key, unit in (('subtestEvents', 'subtest'), ('fixtureErrors', 'fixture')):
        if not isinstance(value[key], list):
            raise ValueError('event array required')
        for item in value[key]:
            shape(item, {'unit', 'id', 'outcome', 'detail'})
            text(item['id'])
            if item['unit'] != unit or item['outcome'] not in ('passed', 'failed', 'error', 'skipped'):
                raise ValueError('invalid event unit/outcome')


def coverage_complete(report):
    return bool(report['coverage']) and all(item['outcome'] == 'passed' or item['exception'] is not None or not item['required'] for item in report['coverage'])


def validate_artifact(value):
    kind = value.get('format') if isinstance(value, dict) else None
    if kind == 'wayfinder-review-packet':
        shape(value, PACKET, {'retainedApprovals'})
        identity(value['id'], 'rr'); identity(value['planId'], 'wp')
        number(value['approvedPlanRevision']); sha(value['approvedPlanSha256']); when(value['observedAt'])
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value['repository']):
            raise ValueError('repository must be owner/name')
        for key in ('owner', 'requestedAuthority'):
            text(value[key])
        for key in ('limitations', 'exclusions', 'verificationIds'):
            strings(value[key])
        for identifier in value['verificationIds']:
            identity(identifier, 'vr')
        if not value['members'] or not value['verificationIds']:
            raise ValueError('packet requires members and verification references')
        seen = set()
        for item in value['members']:
            shape(item, {'number', 'url', 'headCommit', 'baseCommit', 'mergeBaseCommit', 'reviewedDiffSha256', 'dependencies'})
            number(item['number'])
            if item['number'] in seen or item['url'] != f"https://github.com/{value['repository']}/pull/{item['number']}":
                raise ValueError('duplicate member or mismatched PR URL')
            for key in ('headCommit', 'baseCommit', 'mergeBaseCommit'):
                sha(item[key], True)
            sha(item['reviewedDiffSha256'])
            if not isinstance(item['dependencies'], list) or len(item['dependencies']) != len(set(item['dependencies'])):
                raise ValueError('dependencies must be unique prior members')
            if any(type(dep) is not int or dep not in seen for dep in item['dependencies']):
                raise ValueError('dependencies must precede member')
            seen.add(item['number'])
        retained = value.get('retainedApprovals', [])
        if not isinstance(retained, list):
            raise ValueError('retainedApprovals must be a list')
        prior = set()
        for item in retained:
            shape(item, {'memberNumber', 'requestId', 'recordId'})
            number(item['memberNumber']); identity(item['requestId'], 'rr')
            if item['memberNumber'] not in seen or item['memberNumber'] in prior or not re.fullmatch(r'wr-[0-9]{4,}', item['recordId']):
                raise ValueError('invalid retained decision reference')
            prior.add(item['memberNumber'])
    elif kind == 'wayfinder-review-supersession':
        shape(value, SUPERSEDE)
        identity(value['id'], 'rs'); identity(value['requestId'], 'rr'); identity(value['replacementRequestId'], 'rr')
        if value['requestId'] == value['replacementRequestId']:
            raise ValueError('self supersession')
        text(value['reason']); when(value['at'])
    elif kind == 'wayfinder-delivery-event':
        shape(value, EVENT, {'reconcilesEventId'})
        identity(value['id'], 'de'); identity(value['requestId'], 'rr'); number(value['memberNumber']); sha(value['headCommit'], True)
        text(value['reason']); when(value['at'])
        if value['operationMarker'] != f"{value['requestId']}/{value['memberNumber']}/{value['headCommit']}" or value['phase'] not in PHASES:
            raise ValueError('invalid delivery marker/phase')
        if value['phase'] == 'acknowledged':
            number(value['commentId']); text(value['commentUrl'])
        elif value['commentId'] is not None or value['commentUrl'] is not None:
            raise ValueError('only acknowledged events may carry receipts')
        if 'reconcilesEventId' in value:
            identity(value['reconcilesEventId'], 'de')
    elif kind == 'wayfinder-verification-report':
        shape(value, REPORT)
        identity(value['id'], 'vr'); identity(value['planId'], 'wp')
        shape(value['provenance'], {'command', 'selection', 'testedCommit', 'worktreeSha256', 'runtime', 'startedAt', 'finishedAt'})
        prov = value['provenance']
        for key in ('command', 'selection', 'runtime'):
            text(prov[key])
        sha(prov['testedCommit'], True); sha(prov['worktreeSha256'])
        if when(prov['finishedAt']) < when(prov['startedAt']):
            raise ValueError('finishedAt precedes startedAt')
        result_valid(value['results'])
        flags(value, ['suiteSuccessful', 'requiredCoverageComplete', 'readyForReview'])
        strings(value['bytecodeArtifacts'])
        if not isinstance(value['coverage'], list):
            raise ValueError('coverage must be a list')
        seen = set()
        for item in value['coverage']:
            shape(item, {'checkId', 'outcome', 'required', 'exception'})
            text(item['checkId']); flags(item, ['required'])
            if item['checkId'] in seen or item['outcome'] not in ('passed', 'failed', 'skipped', 'unavailable', 'pending', 'not-executed'):
                raise ValueError('duplicate check or invalid outcome')
            seen.add(item['checkId'])
            if item['exception'] is not None:
                shape(item['exception'], {'locator', 'reason'})
                text(item['exception']['locator']); text(item['exception']['reason'])
                if item['outcome'] not in ('unavailable', 'skipped'):
                    raise ValueError('exceptions apply only to disclosed unavailable/skipped checks')
        results = value['results']
        bad = results['unexpectedSuccesses'] or results['caseFailures'] or results['caseErrors'] or results['fixtureErrors'] or any(item['outcome'] in ('failed', 'error') for item in results['subtestEvents']) or results['interrupted']
        if value['suiteSuccessful'] and (bad or not results['testsRun']):
            raise ValueError('suite success contradicts accounting')
        if value['suiteSuccessful'] and results['passed'] + results['skipped'] + results['expectedFailures'] != results['testsRun']:
            raise ValueError('successful suite has incomplete case accounting')
        complete = coverage_complete(value) and not results['interrupted']
        ready = complete and value['suiteSuccessful'] and not value['bytecodeArtifacts']
        if value['requiredCoverageComplete'] != complete or value['readyForReview'] != ready:
            raise ValueError('coverage/readiness contradicts results')
    else:
        raise ValueError('unrecognized reliability artifact format')
    if type(value['schemaVersion']) is not int or value['schemaVersion'] != 1:
        raise ValueError('unsupported artifact schema version')


def artifact_path(value):
    kind = value['format']
    if kind == 'wayfinder-review-packet':
        return f"reviews/{value['id']}/packet.json"
    if kind == 'wayfinder-review-supersession':
        return f"reviews/{value['requestId']}/{value['id']}.json"
    if kind == 'wayfinder-delivery-event':
        return f"deliveries/{value['requestId']}/{value['id']}.json"
    return f"verification/{value['id']}.json"


def auxiliary_path(relative):
    parts = Path(relative).parts
    return any(part.startswith('wp-') and index + 1 < len(parts) and parts[index + 1] in ('reviews', 'deliveries', 'verification') for index, part in enumerate(parts))


def load_auxiliary(plan_folder):
    found = {}
    for name in ('reviews', 'deliveries', 'verification'):
        directory = safe_path(plan_folder, name)
        if not directory.exists():
            continue
        if not directory.is_dir():
            raise ValueError('artifact directory must be a directory')
        for current, folders, files in os.walk(directory, followlinks=False):
            for part in folders + files:
                if (Path(current) / part).is_symlink():
                    raise ValueError('symbolic reliability artifact path')
            for filename in files:
                path = Path(current) / filename
                relative = path.relative_to(plan_folder).as_posix()
                raw = read_regular(safe_path(plan_folder, relative))
                value = strict_json(raw)
                validate_artifact(value)
                if artifact_path(value) != relative or value['id'] in found:
                    raise ValueError('artifact identity/path mismatch or duplicate ID')
                found[value['id']] = {'value': value, 'raw': raw, 'path': relative, 'sha256': digest(raw)}
    return found


def reference(found, identifier, kind):
    if identifier not in found or found[identifier]['value']['format'] != kind:
        raise ValueError('missing or wrong artifact reference: ' + identifier)
    return found[identifier]['value']


def cross_validate(item, found, records=None):
    meta = item['metadata']
    packets = {key: entry['value'] for key, entry in found.items() if entry['value']['format'] == 'wayfinder-review-packet'}
    edges = {}
    for entry in found.values():
        value = entry['value']; kind = value['format']
        if kind in ('wayfinder-review-packet', 'wayfinder-verification-report') and value['planId'] != meta['id']:
            raise ValueError('artifact belongs to a different plan')
        if kind == 'wayfinder-review-packet':
            revision = value['approvedPlanRevision']
            if revision not in item['approvals'] or item['approvals'][revision]['sha256'] != value['approvedPlanSha256']:
                raise ValueError('packet approved snapshot binding differs')
            for identifier in value['verificationIds']:
                reference(found, identifier, 'wayfinder-verification-report')
            for retained in value.get('retainedApprovals', []):
                old = reference(found, retained['requestId'], 'wayfinder-review-packet')
                current = next(member for member in value['members'] if member['number'] == retained['memberNumber'])
                previous = next((member for member in old['members'] if member['number'] == retained['memberNumber']), None)
                if old['repository'] != value['repository'] or old['owner'] != value['owner'] or previous is None or any(previous[key] != current[key] for key in ('headCommit', 'reviewedDiffSha256')):
                    raise ValueError('retained approval refers to changed reviewed version')
                if records is not None:
                    decision = records.get(retained['recordId'])
                    if decision is None or decision['metadata']['kind'] != 'decision' or decision['metadata']['outcome'] != 'accepted' or not decision['metadata']['authorities'] or ('review-request:' + retained['requestId'] + '/member:' + str(retained['memberNumber'])) not in decision['metadata']['sources']:
                        raise ValueError('retained approval lacks explicit member-bound accepted decision')
        elif kind == 'wayfinder-review-supersession':
            reference(found, value['requestId'], 'wayfinder-review-packet'); reference(found, value['replacementRequestId'], 'wayfinder-review-packet')
            if value['requestId'] in edges:
                raise ValueError('request already superseded')
            edges[value['requestId']] = value['replacementRequestId']
        elif kind == 'wayfinder-delivery-event':
            packet = reference(found, value['requestId'], 'wayfinder-review-packet')
            member = next((member for member in packet['members'] if member['number'] == value['memberNumber']), None)
            if member is None or member['headCommit'] != value['headCommit']:
                raise ValueError('delivery member/version differs from packet')
            if value['phase'] == 'acknowledged' and value['commentUrl'] != f"https://github.com/{packet['repository']}/pull/{value['memberNumber']}#issuecomment-{value['commentId']}":
                raise ValueError('receipt URL does not match packet/comment')
            if 'reconcilesEventId' in value:
                prior = reference(found, value['reconcilesEventId'], 'wayfinder-delivery-event')
                if prior['phase'] != 'uncertain' or prior['operationMarker'] != value['operationMarker'] or when(prior['at']) >= when(value['at']):
                    raise ValueError('reconciliation must follow matching uncertain event')
    for start in edges:
        seen = set(); current = start
        while current in edges:
            if current in seen:
                raise ValueError('cyclic supersession')
            seen.add(current); current = edges[current]
    # Acknowledged delivery cannot be retried or contradicted. Uncertain delivery
    # blocks subsequent attempts until an explicit linked reconciliation.
    groups = {}
    for entry in found.values():
        value = entry['value']
        if value['format'] == 'wayfinder-delivery-event':
            groups.setdefault(value['operationMarker'], []).append(value)
    for values in groups.values():
        values.sort(key=lambda value: (when(value['at']), value['id']))
        state = None
        for value in values:
            phase = value['phase']
            if state == 'acknowledged':
                raise ValueError('acknowledged delivery cannot receive another event')
            if state == 'uncertain' and (value.get('reconcilesEventId') is None or phase not in ('acknowledged', 'failed-with-known-no-effect')):
                raise ValueError('uncertain delivery requires explicit reconciliation before retry')
            if phase == 'attempted' and state not in ('prepared', 'failed-with-known-no-effect'):
                raise ValueError('attempt requires prepared intent or known-no-effect reconciliation')
            if phase in ('uncertain', 'failed-with-known-no-effect') and state != 'attempted' and not value.get('reconcilesEventId'):
                raise ValueError('outcome requires an attempt')
            if phase == 'acknowledged' and state != 'attempted' and not value.get('reconcilesEventId'):
                raise ValueError('acknowledgment requires an attempt')
            state = phase


def integrity(repository, entries):
    for item in entries:
        folder = plans.store_root(repository) / Path(item['path']).parent
        found = load_auxiliary(folder)
        cross_validate(item, found)


def history(repository, plan_id, writer=False):
    entries = plans.load_store(repository, writer=writer)
    item = plans.find(entries, plan_id)
    folder = plans.store_root(repository) / Path(item['path']).parent
    found = load_auxiliary(folder)
    # Stored retained authority is always verified through the design record.
    import maintainer_records
    record_root = Path(__file__).resolve().parents[1] / 'references/design-record'
    records = {entry['metadata']['id']: entry for entry in maintainer_records.load_store(record_root)}
    cross_validate(item, found, records)
    binding = [{'path': 'plan.md', 'sha256': item['sha256']}] + [{'path': entry['path'], 'sha256': entry['sha256']} for entry in found.values()]
    return item, folder, found, digest(canonical_json(sorted(binding, key=lambda entry: entry['path'])).encode())


def review_status(packet, found, observations=None):
    inactive = {entry['value']['requestId'] for entry in found.values() if entry['value']['format'] == 'wayfinder-review-supersession'}
    active = [entry['value']['id'] for entry in found.values() if entry['value']['format'] == 'wayfinder-review-packet' and entry['value']['id'] not in inactive]
    superseded = packet['id'] in inactive
    reports = [reference(found, identifier, 'wayfinder-verification-report') for identifier in packet['verificationIds']]
    ready = not superseded and len(active) == 1 and all(report['readyForReview'] for report in reports)
    if any(not any(report['provenance']['testedCommit'] == member['headCommit'] for report in reports) for member in packet['members']):
        ready = False
    changed = []
    if observations is not None:
        shape(observations, {'repository', 'observedAt', 'members'})
        when(observations['observedAt'])
        if observations['repository'] != packet['repository'] or when(observations['observedAt']) < when(packet['observedAt']):
            raise ValueError('observations differ in repository or predate packet')
        if not isinstance(observations['members'], list) or len(observations['members']) != len(packet['members']):
            raise ValueError('observations must cover exact member set')
        seen = set()
        for observed in observations['members']:
            shape(observed, {'number', 'headCommit', 'baseCommit', 'mergeBaseCommit', 'reviewedDiffSha256'})
            if observed['number'] in seen:
                raise ValueError('duplicate observed member')
            seen.add(observed['number'])
            member = next((member for member in packet['members'] if member['number'] == observed['number']), None)
            if member is None:
                raise ValueError('unexpected observed member')
            for key in ('headCommit', 'baseCommit', 'mergeBaseCommit'):
                sha(observed[key], True)
            sha(observed['reviewedDiffSha256'])
            if observed['headCommit'] != member['headCommit'] or observed['reviewedDiffSha256'] != member['reviewedDiffSha256']:
                changed.append(member['number'])
        ready = ready and not changed
    retained = {member['memberNumber'] for member in packet.get('retainedApprovals', [])}
    requested = [member['number'] for member in packet['members'] if member['number'] not in retained]
    question = None if not requested else f"Do you approve request {packet['id']} for PRs {', '.join('#' + str(number) for number in requested)} in {packet['repository']} at the packet's identified commits and reviewed diffs, granting {packet['requestedAuthority']}, with these exclusions: {'; '.join(packet['exclusions'])}?"
    return {'packet': packet, 'readyForReview': ready, 'superseded': superseded, 'activeRequestIds': active, 'changedMembers': changed, 'observationsSupplied': observations is not None, 'approvalQuestion': question, 'ownerApprovalInferred': False, 'mergeEligibilityEstablished': False}


def delivery_state(request_id, found):
    reference(found, request_id, 'wayfinder-review-packet')
    events = [entry['value'] for entry in found.values() if entry['value']['format'] == 'wayfinder-delivery-event' and entry['value']['requestId'] == request_id]
    events.sort(key=lambda value: (when(value['at']), value['id']))
    states = {}
    for value in events:
        states[value['memberNumber']] = value['phase']
    return {'requestId': request_id, 'events': events, 'memberStates': {str(key): value for key, value in states.items()}, 'uncertain': sum(value == 'uncertain' for value in states.values()), 'acknowledged': sum(value == 'acknowledged' for value in states.values()), 'nextAction': 'stop-until-owner-return' if 'uncertain' in states.values() else 'follow-current-authority; no-auto-send'}


def human(data):
    if isinstance(data, dict) and 'written' in data:
        return f"PASS local artifact: {'preview' if data['dryRun'] else 'created'} {data['path']} sha256={data['sha256']}\nsummary written={str(data['written']).lower()} networkActions=0\n"
    if isinstance(data, dict) and 'memberStates' in data:
        lines = [f"{'PASS' if phase == 'acknowledged' else 'UNAVAILABLE'} delivery #{member}: {phase}" for member, phase in data['memberStates'].items()]
        lines.append(f"summary acknowledged={data['acknowledged']} uncertain={data['uncertain']} nextAction={data['nextAction']}")
        return '\n'.join(lines) + '\n'
    if isinstance(data, dict) and data.get('format') == 'wayfinder-verification-report':
        lines = []
        for item in data['coverage']:
            label = 'PASS' if item['outcome'] == 'passed' else 'UNAVAILABLE' if item['outcome'] in ('skipped', 'unavailable', 'pending', 'not-executed') else 'FAIL'
            lines.append(f"{label} {item['checkId']}: {item['outcome']}" + ('; explicit exception, not passed' if item['exception'] else ''))
        result = data['results']
        lines.append('summary ' + ' '.join(f'{key}={result[key]}' for key in ('testsRun', 'passed', 'skipped', 'expectedFailures', 'unexpectedSuccesses', 'caseFailures', 'caseErrors')) + f" suiteSuccessful={str(data['suiteSuccessful']).lower()} requiredCoverageComplete={str(data['requiredCoverageComplete']).lower()} readyForReview={str(data['readyForReview']).lower()}")
        return '\n'.join(lines) + '\n'
    if isinstance(data, dict) and 'packet' in data:
        lines = [f"{'PASS' if data['readyForReview'] else 'FAIL'} review: readyForReview={str(data['readyForReview']).lower()} superseded={str(data['superseded']).lower()}"]
        for member in data['packet']['members']:
            lines.append(f"PR #{member['number']} {member['url']} head={member['headCommit']} base={member['baseCommit']} mergeBase={member['mergeBaseCommit']} diff={member['reviewedDiffSha256']}")
        lines.extend(['UNAVAILABLE limitation: ' + item for item in data['packet']['limitations']])
        if data['approvalQuestion']:
            lines.append(data['approvalQuestion'])
        lines.append('summary ownerApprovalInferred=false mergeEligibilityEstablished=false')
        return '\n'.join(lines) + '\n'
    return canonical_json(data) + '\n'


def output(command, data, args, store_sha, status=0):
    source = (canonical_json(data) + '\n').encode() if args.format == 'json' else human(data).encode()
    maximum = args.max_bytes or 65536
    binding = {'command': command, 'planId': args.plan_id, 'id': getattr(args, 'id', None), 'requestId': getattr(args, 'request_id', None), 'format': args.format, 'storeSha256': store_sha, 'sourceSha256': digest(source), 'maxBytes': maximum}
    start = 0
    if args.cursor:
        cursor = read_cursor(args.cursor)
        if {key: value for key, value in cursor.items() if key != 'offset'} != binding:
            raise ValueError('stale or mismatched output cursor')
        start = cursor['offset']
        boundaries = {0}
        position = 0
        while position < len(source):
            _, position = bounded_chunk(source, position, maximum)
            boundaries.add(position)
        if type(start) is not int or start not in boundaries or start == len(source):
            raise ValueError('invalid continuation boundary')
    chunk, end = bounded_chunk(source, start, maximum)
    complete = end == len(source)
    next_cursor = None if complete else make_cursor({**binding, 'offset': end})
    if args.format == 'json':
        payload = data if start == 0 and complete else {'text': chunk.decode(), 'startByte': start, 'endByte': end, 'reconstructionRequired': True}
        emit_json(command=command, response_class='complete-evidence', scope={'kind': args.command, 'id': getattr(args, 'id', None) or getattr(args, 'request_id', None) or args.plan_id}, data=payload, complete=complete, truncated=not complete, returned_items=1, total_items=1, returned_bytes=len(chunk), source_bytes=len(source), source_sha256=digest(source), next_cursor=next_cursor)
    else:
        print(f'response-class=complete-evidence complete={str(complete).lower()} bytes={start}:{end}/{len(source)} sha256={digest(source)}')
        sys.stdout.write(chunk.decode())
        if next_cursor:
            print('next-cursor=' + next_cursor)
    return status if complete else 2


def command(repository, args):
    action = getattr(args, args.command + '_command')
    name = args.command + ' ' + action
    lock = pending = None
    staged = success = False
    lock_identity = None
    try:
        item, folder, found, store_sha = history(repository, args.plan_id)
        writing = action in ('create', 'supersede', 'append', 'capture')
        if writing:
            value = strict_json(read_regular(args.input)); validate_artifact(value)
            expected_kind = {'create': 'wayfinder-review-packet', 'supersede': 'wayfinder-review-supersession', 'append': 'wayfinder-delivery-event', 'capture': 'wayfinder-verification-report'}[action]
            if value['format'] != expected_kind or ('planId' in value and value['planId'] != args.plan_id) or (action == 'supersede' and value['requestId'] != args.id) or (action == 'append' and value['requestId'] != args.request_id):
                raise ValueError('input selector/format mismatch')
            if value['id'] in found:
                raise ValueError('artifact ID already exists; reconcile before retry')
            if found and args.expected_store_sha256 is None:
                raise ValueError('existing history requires --expected-store-sha256 from complete read')
            if args.expected_store_sha256 is not None and args.expected_store_sha256 != store_sha:
                raise ValueError('history digest changed; re-read and reconcile')
            raw = (canonical_json(value) + '\n').encode()
            relative = artifact_path(value)
            candidate = {**found, value['id']: {'value': value, 'raw': raw, 'path': relative, 'sha256': digest(raw)}}
            cross_validate(item, candidate)
            # Validate retained authority before any artifact publication.
            if value['format'] == 'wayfinder-review-packet' and value.get('retainedApprovals'):
                import maintainer_records
                records = {entry['metadata']['id']: entry for entry in maintainer_records.load_store(Path(__file__).resolve().parents[1] / 'references/design-record')}
                cross_validate(item, candidate, records)
            target = safe_path(folder, relative, absent=True)
            data = {'id': value['id'], 'path': str(target.relative_to(repository)), 'sha256': digest(raw), 'storeSha256': store_sha, 'dryRun': args.dry_run, 'written': not args.dry_run}
            if args.dry_run:
                data['artifact'] = value
            if len(canonical_json(data).encode()) > (args.max_bytes or 65536):
                raise ValueError('write result cannot fit budget; increase --max-bytes')
            if not args.dry_run:
                root = plans.store_root(repository)
                lock = safe_path(root, '.plan-write.lock', absent=True)
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                lock_identity = os.fstat(fd)
                with os.fdopen(fd, 'w') as stream:
                    stream.write(canonical_json({'pid': os.getpid(), 'command': name}) + '\n'); stream.flush(); os.fsync(stream.fileno())
                _, _, _, fresh_sha = history(repository, args.plan_id, writer=True)
                if fresh_sha != store_sha:
                    raise ValueError('history changed before locked write')
                target.parent.mkdir(parents=True, exist_ok=True)
                safe_path(folder, relative, absent=True)
                fd, filename = tempfile.mkstemp(prefix='.pending-', dir=root)
                pending = Path(filename); staged = True
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                if read_regular(pending) != raw:
                    raise ValueError('staged bytes differ')
                os.link(pending, target)
                if read_regular(target) != raw:
                    raise ValueError('published bytes differ; inspect writer state')
            success = True
            return output(name, data, args, store_sha)
        observations = strict_json(read_regular(args.observations)) if getattr(args, 'observations', None) else None
        if args.command == 'review':
            packet = reference(found, args.id, 'wayfinder-review-packet')
            data = review_status(packet, found, observations)
            status = 1 if action == 'validate' and not data['readyForReview'] else 0
        elif args.command == 'delivery':
            data = delivery_state(args.request_id, found); status = 0
        else:
            data = reference(found, args.id, 'wayfinder-verification-report'); status = 0
        data = {**data, 'storeSha256': store_sha}
        return output(name, data, args, store_sha, status)
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as exc:
        if args.format == 'json':
            emit_json(command=name, response_class='complete-evidence', scope={'kind': args.command, 'id': args.plan_id}, data=None, complete=False, error={'code': 'reliability.invalid', 'message': str(exc)})
        else:
            print('FAIL ' + name + ': ' + str(exc))
        return 2
    finally:
        if success or not staged:
            if pending is not None:
                pending.unlink()
            if lock is not None and lock_identity is not None and lock.exists():
                actual = lock.lstat()
                if (actual.st_dev, actual.st_ino) == (lock_identity.st_dev, lock_identity.st_ino):
                    lock.unlink()
