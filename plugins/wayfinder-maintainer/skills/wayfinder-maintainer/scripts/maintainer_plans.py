"""Repository-owned living plans; caller approval assertions are not authenticated."""
from __future__ import annotations

import contextlib
import datetime as dt
import os
import re
import shlex
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from maintainer_output import bounded_chunk, canonical_json, emit_json, make_cursor
import maintainer_records
from maintainer_records import cursor_offset, digest, read_regular, safe_path, strict_json, text_bytes

BEGIN = '<!-- WAYFINDER-PLAN:BEGIN -->\n```json\n'
END = '\n```\n<!-- WAYFINDER-PLAN:END -->\n\n'
STATUSES = ('draft', 'approved', 'implementing', 'awaiting-review', 'changes-requested', 'completed', 'abandoned')
FIELDS = {'id', 'subject', 'slug', 'title', 'summary', 'status', 'updated', 'body', 'records', 'approval'}
META_FIELDS = (FIELDS - {'body'}) | {'format', 'schemaVersion', 'revision', 'approvedRevision', 'approvedSha256', 'approvalHistory'}
SEGMENT = r'[a-z0-9]+(?:-[a-z0-9]+)*'


def store_root(repository: Path) -> Path:
    repository = Path(repository).absolute()
    safe_path(repository, 'docs/plans')
    return repository / 'docs/plans'


def validate(value: dict[str, Any]) -> None:
    identifier = value['id']
    if not isinstance(identifier, str) or not identifier.startswith('wp-'):
        raise ValueError('id must be wp- followed by a canonical lowercase UUID')
    try:
        parsed = uuid.UUID(identifier[3:])
    except ValueError as exc:
        raise ValueError('invalid plan UUID') from exc
    if str(parsed) != identifier[3:] or parsed.int == 0:
        raise ValueError('id must use a nonzero canonical lowercase UUID')
    if not isinstance(value['subject'], str) or not re.fullmatch(SEGMENT + r'(?:/' + SEGMENT + r')*', value['subject']):
        raise ValueError('subject must be a hierarchy of lowercase slug components')
    if not isinstance(value['slug'], str) or not re.fullmatch(SEGMENT, value['slug']) or len(value['slug']) > 80:
        raise ValueError('slug must be a lowercase slug of at most 80 characters')
    if value['status'] not in STATUSES:
        raise ValueError('unknown plan status')
    for key in ('title', 'summary', 'body'):
        text = value[key]
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f'{key} must be nonempty text')
        text_bytes(text.encode('utf-8'))
    for key, limit in (('title', 200), ('summary', 500)):
        if '\n' in value[key] or len(value[key]) > limit:
            raise ValueError(f'{key} must be single-line and at most {limit} characters')
    if not isinstance(value['updated'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value['updated']):
        raise ValueError('updated must be explicitly supplied as YYYY-MM-DD')
    dt.date.fromisoformat(value['updated'])
    records = value['records']
    if not isinstance(records, list) or any(not isinstance(item, str) or not re.fullmatch(r'wr-[0-9]{4,}', item) for item in records) or len(records) != len(set(records)):
        raise ValueError('records must contain unique design-record IDs')
    approval = value['approval']
    if approval is not None:
        if not isinstance(approval, dict) or set(approval) != {'locator', 'quotation'} or any(not isinstance(item, str) or not item.strip() for item in approval.values()):
            raise ValueError('approval requires an exact quotation and source locator')
        for item in approval.values():
            text_bytes(item.encode('utf-8'))
        if '\n' in approval['locator']:
            raise ValueError('approval locator must be single-line')


def render(metadata: dict[str, Any], body: str) -> bytes:
    return (BEGIN + canonical_json(metadata) + END + body.rstrip('\n') + '\n').encode('utf-8')


def parse(raw: bytes) -> dict[str, Any]:
    text = text_bytes(raw)
    if not text.startswith(BEGIN) or END not in text[len(BEGIN):]:
        raise ValueError('missing plan metadata block')
    header, body = text[len(BEGIN):].split(END, 1)
    metadata = strict_json(header.encode('utf-8'))
    if not isinstance(metadata, dict) or set(metadata) != META_FIELDS or metadata['format'] != 'wayfinder-plan' or type(metadata['schemaVersion']) is not int or metadata['schemaVersion'] != 1:
        raise ValueError('unsupported plan metadata fields/format/version')
    validate({**metadata, 'body': body})
    revision, approved = metadata['revision'], metadata['approvedRevision']
    if type(revision) is not int or revision < 1 or (approved is not None and (type(approved) is not int or not 1 <= approved <= revision)):
        raise ValueError('invalid plan revision/approvedRevision')
    approval_digest = metadata['approvedSha256']
    if approved is None or approved == revision:
        if approval_digest is not None:
            raise ValueError('self/unapproved revision must have null approvedSha256')
    elif not isinstance(approval_digest, str) or not re.fullmatch(r'[0-9a-f]{64}', approval_digest):
        raise ValueError('current progress requires exact approved snapshot SHA-256')
    history = metadata['approvalHistory']
    if not isinstance(history, dict) or any(not isinstance(key, str) or not re.fullmatch(r'[1-9][0-9]*', key) or int(key) >= revision or not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value) for key, value in history.items()):
        raise ValueError('invalid approvalHistory digest bindings')
    if (approved is None) != (metadata['approval'] is None):
        raise ValueError('approval provenance and approvedRevision must agree')
    if metadata['status'] in {'approved', 'implementing', 'awaiting-review', 'completed'} and approved is None:
        raise ValueError('execution status requires an approved revision')
    if not body.endswith('\n'):
        raise ValueError('plan must end with LF')
    return metadata


def relative_path(metadata: dict[str, Any]) -> str:
    return f"{metadata['subject']}/{metadata['id']}-{metadata['slug']}/plan.md"


def load_store(repository: Path, *, writer: bool = False) -> list[dict[str, Any]]:
    root = store_root(repository)
    if not root.exists():
        return []
    if not root.is_dir():
        raise ValueError('plan store is not a directory')
    if list(root.glob('.pending-*')):
        raise ValueError('unfinished plan writer artifact; inspect before explicit cleanup')
    if not writer and (root / '.plan-write.lock').exists():
        raise ValueError('unfinished or active plan writer; inspect the lock before explicit cleanup')
    entries = []
    auxiliary_files = []
    snapshots: dict[str, dict[int, dict[str, Any]]] = {}
    for directory, folders, files in os.walk(root, followlinks=False):
        for name in folders + files:
            if (Path(directory) / name).is_symlink():
                raise ValueError('symbolic path in plan store')
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if name == '.plan-write.lock' and path.parent == root and writer:
                continue
            if name == 'README.md' and path.parent == root:
                read_regular(path)
                continue
            if name.startswith('.pending-'):
                raise ValueError('unfinished plan writer artifact; inspect before explicit cleanup')
            import maintainer_review
            if maintainer_review.auxiliary_path(relative):
                auxiliary_files.append(relative)
                continue
            if name != 'plan.md' and not re.fullmatch(r'revision-[1-9][0-9]*\.md', name):
                raise ValueError(f'unrecognized file in plan store: {relative}')
            raw = read_regular(safe_path(root, relative))
            metadata = parse(raw)
            item = {'metadata': metadata, 'raw': raw, 'sha256': digest(raw), 'path': relative}
            expected = relative_path(metadata)
            if name == 'plan.md':
                if relative != expected:
                    raise ValueError(f'plan path/metadata mismatch: {relative}')
                entries.append(item)
            else:
                revision = int(name[9:-3])
                expected = str(Path(expected).parent / 'approvals' / name)
                if relative != expected or metadata['revision'] != revision or metadata['approvedRevision'] != revision or metadata['status'] != 'approved' or metadata['approval'] is None:
                    raise ValueError('approval snapshot path or metadata differs')
                versions = snapshots.setdefault(metadata['id'], {})
                if revision in versions:
                    raise ValueError('duplicate approved revision')
                versions[revision] = item
    entries.sort(key=lambda item: item['metadata']['id'])
    ids = [item['metadata']['id'] for item in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate plan ID')
    if set(snapshots) - set(ids):
        raise ValueError('orphan approved snapshot')
    for item in entries:
        metadata = item['metadata']
        versions = snapshots.get(metadata['id'], {})
        approved = metadata['approvedRevision']
        if approved is not None:
            if approved not in versions or max(versions) != approved or metadata['approval'] != versions[approved]['metadata']['approval']:
                raise ValueError('current plan approval binding differs from snapshots')
            if approved != metadata['revision'] and metadata['approvedSha256'] != versions[approved]['sha256']:
                raise ValueError('approved snapshot SHA-256 differs')
        elif versions:
            raise ValueError('snapshot exists without current approval binding')
        expected_history = {str(key): snapshot['sha256'] for key, snapshot in versions.items() if key < metadata['revision']}
        if metadata['approvalHistory'] != expected_history:
            raise ValueError('approval history SHA-256 differs')
        for revision, snapshot in versions.items():
            prior = {str(key): member['sha256'] for key, member in versions.items() if key < revision}
            if snapshot['metadata']['approvalHistory'] != prior:
                raise ValueError('snapshot approval history differs')
            if revision > metadata['revision'] or any(snapshot['metadata'][key] != metadata[key] for key in ('id', 'subject', 'slug')):
                raise ValueError('snapshot identity/revision differs')
        if approved == metadata['revision'] and item['raw'] != versions[approved]['raw']:
            raise ValueError('current approved revision differs from exact snapshot')
        item['approvals'] = versions
    for relative in auxiliary_files:
        if not any(relative.startswith(str(Path(item['path']).parent) + '/' + category + '/') for item in entries for category in ('reviews', 'deliveries', 'verification')):
            raise ValueError('orphan reliability artifact')
    import maintainer_review
    maintainer_review.integrity(repository, entries)
    return entries


def find(entries: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
    matches = [item for item in entries if item['metadata']['id'] == identifier]
    if len(matches) != 1:
        raise ValueError('plan not found; use plan list')
    return matches[0]


def store_digest(entries: list[dict[str, Any]]) -> str:
    members = []
    for item in entries:
        for member in [item, *item['approvals'].values()]:
            members.append({'path': member['path'], 'sha256': member['sha256']})
    return digest(canonical_json(sorted(members, key=lambda item: item['path'])).encode('utf-8'))


def error(command: str, exc: Exception, output_format: str) -> int:
    message = str(exc)
    print(message, file=sys.stderr)
    if output_format == 'json':
        emit_json(command=command, response_class='complete-evidence', scope={'kind': 'plan', 'id': command}, data=None, complete=False, error={'code': 'plan.invalid', 'message': message})
    return 2


def read_command(root: Path, identifier: str, revision: int | None, include_history: bool, output_format: str, response_class: str, max_bytes: int, cursor: str | None) -> int:
    try:
        if max_bytes < 4 or revision is not None and include_history:
            raise ValueError('budget must be at least four; revision and history are exclusive')
        entries = load_store(root)
        item = find(entries, identifier)
        versions = item['approvals']
        if revision is not None:
            if revision not in versions:
                raise ValueError('revision is not an approved snapshot')
            selected = [versions[revision]]
        elif include_history:
            selected = [versions[key] for key in sorted(versions) if key != item['metadata']['revision']] + [item]
        else:
            selected = [item]
        source = b'\n'.join(member['raw'] for member in selected)
        binding = {'command': 'plan read', 'id': identifier, 'revision': revision, 'history': include_history, 'sourceSha256': digest(source), 'storeSha256': store_digest(entries), 'maxBytes': max_bytes, 'responseClass': response_class}
        boundaries = [0]
        while boundaries[-1] < len(source):
            _, end = bounded_chunk(source, boundaries[-1], max_bytes)
            boundaries.append(end)
        start = cursor_offset(cursor, binding, boundaries[:-1])
        chunk, end = bounded_chunk(source, start, max_bytes)
        exhausted = end == len(source)
        continuation = None if exhausted else make_cursor({**binding, 'offset': end})
        position, spans = 0, []
        for member in selected:
            stop = position + len(member['raw'])
            spans.append({'revision': member['metadata']['revision'], 'path': member['path'], 'sha256': member['sha256'], 'startByte': position, 'endByte': stop})
            position = stop + 1
        data = {'id': identifier, 'startByte': start, 'endByte': end, 'text': chunk.decode('utf-8'), 'chunkIndex': boundaries.index(start), 'chunkCount': len(boundaries) - 1, 'reconstructionRequired': len(boundaries) > 2, 'sequenceExhausted': exhausted, 'storeSha256': binding['storeSha256'], 'plans': spans}
        if output_format == 'json':
            emit_json(command='plan read', response_class=response_class, scope={'kind': 'plan-history' if include_history else 'plan', 'id': identifier, 'revision': revision}, data=data, complete=exhausted and response_class == 'complete-evidence', truncated=not exhausted, returned_items=len(selected), total_items=len(selected), returned_bytes=len(chunk), source_bytes=len(source), source_sha256=digest(source), next_cursor=continuation, error=None if exhausted or response_class == 'discovery-preview' else {'code': 'output.incomplete', 'message': 'continue with --cursor'})
        else:
            print(f'response-class={response_class} complete={str(exhausted and response_class == "complete-evidence").lower()} bytes={start}:{end}/{len(source)} sha256={digest(source)}')
            sys.stdout.write(chunk.decode('utf-8'))
        if continuation:
            extra = ' --history' if include_history else (f' --revision {revision}' if revision is not None else '')
            print(f'next-command: maintain.py plan read --id {identifier}{extra} --format {output_format} --response-class {response_class} --max-bytes {max_bytes} --cursor {continuation}', file=sys.stderr)
        return 0 if exhausted or response_class == 'discovery-preview' else 2
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return error('plan read', exc, output_format)


def list_command(root: Path, subject: str | None, status: str | None, output_format: str, response_class: str, max_bytes: int, cursor: str | None) -> int:
    try:
        if max_bytes < 4 or status is not None and status not in STATUSES:
            raise ValueError('invalid budget or status')
        if subject is not None and not re.fullmatch(SEGMENT + r'(?:/' + SEGMENT + r')*', subject):
            raise ValueError('unsafe subject')
        entries = load_store(root)
        items = []
        for item in entries:
            meta = item['metadata']
            if subject is not None and not (meta['subject'] == subject or meta['subject'].startswith(subject + '/')) or status is not None and meta['status'] != status:
                continue
            items.append({**{key: meta[key] for key in ('id', 'title', 'summary', 'subject', 'status', 'updated', 'revision', 'approvedRevision')}, 'path': 'docs/plans/' + item['path'], 'bytes': len(item['raw']), 'sha256': item['sha256'], 'nextCommand': 'maintain.py plan read --id ' + meta['id']})
        source = canonical_json(items).encode('utf-8')
        binding = {'command': 'plan list', 'subject': subject, 'status': status, 'sourceSha256': digest(source), 'storeSha256': store_digest(entries), 'maxBytes': max_bytes, 'responseClass': response_class}
        if not items and cursor:
            raise ValueError('stale cursor: selected listing now empty')
        start = cursor_offset(cursor, binding, list(range(len(items)))) if items else 0
        page, end = [], start
        while end < len(items) and len(canonical_json(page + [items[end]]).encode('utf-8')) <= max_bytes:
            page.append(items[end])
            end += 1
        if items and not page:
            raise ValueError('budget cannot contain an inventory item; increase --max-bytes or read one plan')
        exhausted = end == len(items)
        continuation = None if exhausted else make_cursor({**binding, 'offset': end})
        data = {'items': page, 'startItem': start, 'endItem': end, 'sequenceExhausted': exhausted, 'storeSha256': binding['storeSha256']}
        if output_format == 'json':
            emit_json(command='plan list', response_class=response_class, scope={'kind': 'plan-inventory', 'id': subject or 'all', 'status': status}, data=data, complete=exhausted and response_class == 'complete-evidence', truncated=not exhausted, returned_items=len(page), total_items=len(items), returned_bytes=len(canonical_json(page).encode('utf-8')), source_bytes=len(source), source_sha256=digest(source), next_cursor=continuation, error=None if exhausted or response_class == 'discovery-preview' else {'code': 'output.incomplete', 'message': 'continue with --cursor'})
        else:
            print(f'response-class={response_class} complete={str(exhausted and response_class == "complete-evidence").lower()} items={start}:{end}/{len(items)} sha256={digest(source)}')
            for item in page:
                print(canonical_json(item) if output_format == 'full' else f"{item['id']} {item['subject']} {item['status']} revision={item['revision']}: {item['title']}\n  {item['nextCommand']}")
        if continuation:
            selectors = (f' --subject {shlex.quote(subject)}' if subject else '') + (f' --status {status}' if status else '')
            print(f'next-command: maintain.py plan list{selectors} --format {output_format} --response-class {response_class} --max-bytes {max_bytes} --cursor {continuation}', file=sys.stderr)
        return 0 if exhausted or response_class == 'discovery-preview' else 2
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return error('plan list', exc, output_format)


def prepare(repository: Path, supplied: Any, identifier: str | None = None) -> tuple[bytes, dict[str, Any], dict[str, Any] | None]:
    expected = FIELDS if identifier is None else FIELDS | {'changeKind'}
    if not isinstance(supplied, dict) or set(supplied) != expected:
        raise ValueError('plan input fields differ; see the plan-management guide')
    validate(supplied)
    if supplied['records']:
        record_root = Path(repository) / 'plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/design-record'
        known = {item['metadata']['id'] for item in maintainer_records.load_store(record_root)}
        if any(identifier not in known for identifier in supplied['records']):
            raise ValueError('plan references an unknown design-record ID')
    entries = load_store(repository, writer=True)
    old = None if identifier is None else find(entries, identifier)
    meta = {key: supplied[key] for key in FIELDS - {'body'}}
    if old is None:
        if any(item['metadata']['id'] == supplied['id'] for item in entries):
            raise ValueError('plan ID already exists')
        if supplied['status'] != 'draft' or supplied['approval'] is not None:
            raise ValueError('create requires draft status and null approval; use approval update afterwards')
        revision, approved = 1, None
    else:
        previous = old['metadata']
        if identifier != supplied['id'] or any(previous[key] != supplied[key] for key in ('id', 'subject', 'slug')):
            raise ValueError('updates cannot move or rename plan identity/path')
        if supplied['updated'] < previous['updated']:
            raise ValueError('updated date cannot move backwards')
        revision, approved = previous['revision'] + 1, previous['approvedRevision']
        kind = supplied['changeKind']
        if kind == 'approval':
            if supplied['approval'] is None or supplied['status'] != 'approved':
                raise ValueError('approval update requires approved status and explicit provenance')
            approved = revision
        elif kind in ('progress', 'material'):
            if supplied['approval'] is not None and supplied['approval'] != previous['approval']:
                raise ValueError('non-approval update must preserve prior approval provenance')
            meta['approval'] = previous['approval']
            if kind == 'material' and supplied['status'] != 'changes-requested':
                raise ValueError('material update requires changes-requested status')
            if kind == 'progress':
                transitions = {
                    'draft': {'draft', 'abandoned'},
                    'changes-requested': {'changes-requested', 'abandoned'},
                    'approved': {'approved', 'implementing', 'awaiting-review', 'completed', 'abandoned'},
                    'implementing': {'implementing', 'awaiting-review', 'completed', 'abandoned'},
                    'awaiting-review': {'awaiting-review', 'implementing', 'completed', 'abandoned'},
                    'completed': {'completed'}, 'abandoned': {'abandoned'},
                }
                if supplied['status'] not in transitions[previous['status']]:
                    raise ValueError('progress cannot reopen or approve a plan; use material/approval update')
        else:
            raise ValueError('changeKind must be progress, material, or approval')
    approved_digest = None if approved is None or approved == revision else old['approvals'][approved]['sha256']
    meta.update(format='wayfinder-plan', schemaVersion=1, revision=revision, approvedRevision=approved, approvedSha256=approved_digest, approvalHistory={} if old is None else {str(key): member['sha256'] for key, member in old['approvals'].items()})
    raw = render(meta, supplied['body'])
    parse(raw)
    return raw, meta, old


def write_command(repository: Path, input_path: Path, dry_run: bool, output_format: str, max_bytes: int, identifier: str | None = None, expected_sha256: str | None = None) -> int:
    command = 'plan create' if identifier is None else 'plan update'
    lock = pending = None
    lock_identity = None
    success = False
    staged = False
    try:
        supplied = strict_json(read_regular(Path(input_path)))
        root = store_root(repository)
        # Dry runs do not create the store or acquire a lock, but reject active writers.
        load_store(repository)
        if not dry_run:
            root.mkdir(parents=True, exist_ok=True)
            safe_path(Path(repository).absolute(), 'docs/plans')
            lock = safe_path(root, '.plan-write.lock', absent=True)
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
                lock_identity = os.fstat(stream.fileno())
                stream.write(canonical_json({'pid': os.getpid()}) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
        raw, meta, old = prepare(repository, supplied, identifier)
        target = safe_path(root, relative_path(meta), absent=identifier is None)
        if old is not None and (not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256) or old['sha256'] != expected_sha256):
            raise ValueError('current SHA-256 differs; re-read before updating')
        data = {'id': meta['id'], 'path': 'docs/plans/' + relative_path(meta), 'revision': meta['revision'], 'approvedRevision': meta['approvedRevision'], 'bytes': len(raw), 'sha256': digest(raw), 'dryRun': dry_run, 'written': not dry_run, 'currentStateUpdated': False, 'designRecordUpdated': False}
        if dry_run:
            data['text'] = raw.decode('utf-8')
        if len(canonical_json(data).encode('utf-8')) > max_bytes:
            raise ValueError('budget cannot describe the complete write; increase --max-bytes')
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            safe_path(root, relative_path(meta), absent=identifier is None)
            descriptor, name = tempfile.mkstemp(prefix='.pending-', dir=root)
            pending = Path(name)
            staged = True
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            if read_regular(pending) != raw:
                raise ValueError('staged bytes differ')
            snapshot = None
            if meta['approvedRevision'] == meta['revision']:
                relative = str(Path(relative_path(meta)).parent / 'approvals' / f"revision-{meta['revision']}.md")
                snapshot = safe_path(root, relative, absent=True)
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                safe_path(root, relative, absent=True)
                os.link(pending, snapshot)
            if old is None:
                os.link(pending, target)
            else:
                if digest(read_regular(safe_path(root, relative_path(meta)))) != expected_sha256:
                    raise ValueError('current plan changed before replacement')
                os.replace(pending, target)
                pending = None
            if read_regular(target) != raw or snapshot is not None and read_regular(snapshot) != raw:
                raise ValueError('published bytes differ; inspect writer artifacts')
        success = True
        if output_format == 'json':
            emit_json(command=command, response_class='complete-evidence', scope={'kind': 'plan', 'id': meta['id']}, data=data, returned_items=1, total_items=1, returned_bytes=len(canonical_json(data).encode('utf-8')), source_bytes=len(raw), source_sha256=digest(raw))
        elif dry_run:
            print(f"dry-run {data['path']} sha256={data['sha256']}")
            sys.stdout.write(raw.decode('utf-8'))
        else:
            print(f"wrote {data['path']} revision={meta['revision']} sha256={data['sha256']}; current state and records unchanged")
        return 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return error(command, exc, output_format)
    finally:
        # Once staging begins a failure leaves evidence for explicit inspection.
        # Never delete a lock we did not create or silently clean interrupted work.
        if success or not staged:
            if pending is not None:
                with contextlib.suppress(OSError):
                    pending.unlink()
            if lock is not None and lock_identity is not None:
                with contextlib.suppress(OSError):
                    actual = lock.lstat()
                    if (actual.st_dev, actual.st_ino) == (lock_identity.st_dev, lock_identity.st_ino):
                        lock.unlink()


def create_command(root: Path, input_path: Path, dry_run: bool, output_format: str, max_bytes: int) -> int:
    return write_command(root, input_path, dry_run, output_format, max_bytes)


def update_command(root: Path, identifier: str, input_path: Path, expected_sha256: str, dry_run: bool, output_format: str, max_bytes: int) -> int:
    return write_command(root, input_path, dry_run, output_format, max_bytes, identifier, expected_sha256)


def integrity_issues(root: Path) -> list[str]:
    try:
        load_store(root)
        return []
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return [str(exc)]
