"""Maintainer-only, append-only design history and bounded record interfaces.

Record assertions are supplied by the caller, not authenticated or inferred here.
The current-state file remains the authority for current facts and permissions.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shlex
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

from maintainer_output import bounded_chunk, canonical_json, emit_json, make_cursor, read_cursor


BEGIN = '<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->\n```json\n'
END = '\n```\n<!-- WAYFINDER-DESIGN-RECORD:END -->\n\n'
TOPICS = ('foundation', 'initialize', 'governance', 'distribution')
KINDS = ('context', 'proposal', 'decision', 'verification', 'closure')
OUTCOMES = ('historical', 'pending', 'accepted', 'rejected', 'changes-requested', 'recorded', 'passed', 'failed')
ID_PATTERN = r'wr-[0-9]{4,}'
FIELDS = {'topic', 'candidateRevision', 'title', 'kind', 'outcome', 'date', 'summary', 'body', 'predecessors', 'authorities', 'sources'}
META_FIELDS = (FIELDS - {'body'}) | {'format', 'schemaVersion', 'id', 'legacy'}
# Bound once at migration; changing the migrated history requires explicit authority.
MIGRATION_SHA256 = '3ee0e8a8908a405e567afb238e3bc200858f74b8f07b95d9cda9e51f37aa3a59'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def text_bytes(raw: bytes) -> str:
    if raw.startswith(b'\xef\xbb\xbf') or b'\r' in raw or b'\x00' in raw:
        raise ValueError('records require UTF-8 without BOM, LF-only text, and no NUL')
    return raw.decode('utf-8', 'strict')


def strict_json(raw: bytes) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON member: {key}')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f'invalid JSON constant: {value}')

    return json.loads(text_bytes(raw), object_pairs_hook=pairs, parse_constant=invalid_constant)


def safe_path(root: Path, relative: str, *, absent: bool = False) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or '\\' in relative or any(part in ('.', '..') for part in relative.split('/')):
        raise ValueError(f'unsafe record path: {relative}')
    # Also inspect the ancestors of the store itself, before resolving any links.
    for parent in (*reversed(root.parents), root):
        if parent.is_symlink():
            raise ValueError(f'symbolic record-store ancestor: {parent}')
    target = root
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError(f'symbolic record path: {relative}')
        if target.exists() and target != root / path and not target.is_dir():
            raise ValueError(f'non-directory record ancestor: {relative}')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'record path escapes store: {relative}')
    if absent and target.exists():
        raise ValueError(f'record target already exists: {relative}')
    return target


def read_regular(path: Path) -> bytes:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f'not a regular record file: {path}')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError(f'record changed before opening: {path}')
        raw = stream.read()
        after = os.fstat(stream.fileno())
    final = path.lstat()
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    if identity(before) != identity(after) or identity(after) != identity(final):
        raise ValueError(f'record changed during reading: {path}')
    text_bytes(raw)
    return raw


def validate_fields(value: dict[str, Any], *, migrated: bool = False) -> None:
    if value['topic'] not in TOPICS or value['kind'] not in KINDS or value['outcome'] not in OUTCOMES:
        raise ValueError('unknown record topic, kind, or outcome')
    revision = value['candidateRevision']
    if revision is not None and (type(revision) is not int or revision < 1 or value['topic'] != 'initialize'):
        raise ValueError('candidateRevision must be null or a positive Initialize revision')
    for field in ('title', 'summary', 'body'):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValueError(f'{field} must be nonempty text')
        text_bytes(value[field].encode('utf-8', 'strict'))
    if '\n' in value['title'] or '\n' in value['summary']:
        raise ValueError('title and summary must be single-line text')
    if len(value['title']) > 200 or len(value['summary']) > 500:
        raise ValueError('title/summary exceed 200/500 characters')
    date = value['date']
    if date is None and migrated:
        pass  # Undated history is not assigned an invented date.
    elif not isinstance(date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
        raise ValueError('date must be explicitly supplied as YYYY-MM-DD')
    else:
        dt.date.fromisoformat(date)
    for field in ('predecessors', 'sources'):
        items = value[field]
        if not isinstance(items, list) or not all(isinstance(item, str) and item.strip() for item in items) or len(items) != len(set(items)):
            raise ValueError(f'{field} must contain unique nonempty strings')
        for item in items:
            text_bytes(item.encode('utf-8', 'strict'))
            if '\n' in item:
                raise ValueError(f'{field} entries must be single-line')
    if any(not re.fullmatch(ID_PATTERN, item) for item in value['predecessors']):
        raise ValueError('predecessors must name record IDs')
    authorities = value['authorities']
    if not isinstance(authorities, list):
        raise ValueError('authorities must be an array')
    for item in authorities:
        if not isinstance(item, dict) or set(item) != {'locator', 'quotation'} or not all(isinstance(text, str) and text.strip() for text in item.values()):
            raise ValueError('each authority requires a locator and exact quotation')
        for text in item.values():
            text_bytes(text.encode('utf-8', 'strict'))
        if '\n' in item['locator']:
            raise ValueError('authority locator must be single-line')
    if not migrated:
        allowed = {
            'context': {'recorded'}, 'proposal': {'pending'},
            'decision': {'pending', 'accepted', 'rejected', 'changes-requested'},
            'verification': {'passed', 'failed', 'recorded'},
            'closure': {'accepted'},
        }
        if value['outcome'] not in allowed[value['kind']]:
            raise ValueError('outcome does not match record kind')
        if value['outcome'] in {'accepted', 'rejected'} and not authorities:
            raise ValueError('accepted/rejected decisions and closures require an authority locator and quotation')


def render(metadata: dict[str, Any], body: bytes) -> bytes:
    return (BEGIN + canonical_json(metadata) + END).encode('utf-8') + body


def parse(raw: bytes) -> tuple[dict[str, Any], bytes]:
    text = text_bytes(raw)
    if not text.startswith(BEGIN) or END not in text[len(BEGIN):]:
        raise ValueError('missing design-record metadata block')
    header, body = text[len(BEGIN):].split(END, 1)
    metadata = strict_json(header.encode('utf-8'))
    if not isinstance(metadata, dict) or set(metadata) != META_FIELDS:
        raise ValueError('design-record metadata fields differ')
    if metadata['format'] != 'wayfinder-design-record' or type(metadata['schemaVersion']) is not int or metadata['schemaVersion'] != 1:
        raise ValueError('unsupported design-record format/version')
    if not isinstance(metadata['id'], str) or not re.fullmatch(ID_PATTERN, metadata['id']) or int(metadata['id'][3:]) < 1:
        raise ValueError('invalid design-record ID')
    legacy = metadata['legacy']
    if legacy is not None and (not isinstance(legacy, dict) or set(legacy) != {'sourceSectionSha256'} or not isinstance(legacy['sourceSectionSha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', legacy['sourceSectionSha256'])):
        raise ValueError('invalid legacy provenance')
    validate_fields({**metadata, 'body': body}, migrated=legacy is not None)
    if not body.startswith('## ' + metadata['title'] + '\n') or not body.endswith('\n'):
        raise ValueError('record body must start with its exact level-two title and end with LF')
    return metadata, body.encode('utf-8')


def links(metadata: dict[str, Any]) -> list[str]:
    references = metadata['sources'] + [item['locator'] for item in metadata['authorities']]
    return metadata['predecessors'] + [value[7:] for value in references if value.startswith('record:')]


def load_store(root: Path) -> list[dict[str, Any]]:
    safe_path(root.parent, root.name)
    if not root.is_dir():
        raise ValueError(f'design record store missing: {root}')
    records = []
    for directory, folders, files in os.walk(root, followlinks=False):
        for name in folders + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError(f'symbolic path in record store: {path}')
        for name in sorted(files):
            if name == 'README.md' or name == 'migration.json' or name.startswith('.pending-') or name == '.record-add.lock':
                continue
            if not name.endswith('.md'):
                raise ValueError(f'unrecognized file in record store: {name}')
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            raw = read_regular(safe_path(root, relative))
            metadata, body = parse(raw)
            expected_folder = folder(metadata)
            if path.parent.relative_to(root).as_posix() != expected_folder or not name.startswith(metadata['id'] + '-'):
                raise ValueError(f'record path/metadata mismatch: {relative}')
            records.append({'metadata': metadata, 'body': body, 'raw': raw, 'path': relative, 'sha256': digest(raw)})
    records.sort(key=lambda item: int(item['metadata']['id'][3:]))
    ids = [item['metadata']['id'] for item in records]
    if len(ids) != len(set(ids)) or len({int(value[3:]) for value in ids}) != len(ids):
        raise ValueError('duplicate record ID/ordinal')
    if [int(value[3:]) for value in ids] != list(range(1, len(ids) + 1)):
        raise ValueError('record ordinal gap: missing history')
    by_id = {item['metadata']['id']: item for item in records}
    for item in records:
        identifier = item['metadata']['id']
        for target in links(item['metadata']):
            if target not in by_id or int(target[3:]) >= int(identifier[3:]):
                raise ValueError(f'missing, self, or forward record reference: {identifier} -> {target}')
    return records


def folder(metadata: dict[str, Any]) -> str:
    if metadata['topic'] == 'initialize':
        suffix = 'policy' if metadata['candidateRevision'] is None else f"candidate-revision-{metadata['candidateRevision']}"
        return 'initialize/' + suffix
    return metadata['topic']


def store_digest(records: list[dict[str, Any]]) -> str:
    return digest(canonical_json([{'id': item['metadata']['id'], 'path': item['path'], 'sha256': item['sha256']} for item in records]).encode('utf-8'))


def find_record(records: list[dict[str, Any]], *, identifier: str | None = None, heading: str | None = None) -> dict[str, Any]:
    title = heading.removeprefix('## ') if heading else None
    matches = [item for item in records if item['metadata']['id'] == identifier] if identifier else [item for item in records if item['metadata']['title'] == title]
    if len(matches) != 1:
        reason = 'not found' if not matches else 'ambiguous'
        raise ValueError(f'record {reason}: {identifier or title}; use record list and record read --id ID')
    return matches[0]


def history(records: list[dict[str, Any]], identifier: str) -> list[dict[str, Any]]:
    by_id = {item['metadata']['id']: item for item in records}
    selected = {identifier}
    pending = [identifier]
    # Predecessor links are followed both ways so later rejection/correction/closure
    # cannot disappear. Sources and authority links are followed outward only.
    while pending:
        current = pending.pop()
        adjacent = links(by_id[current]['metadata']) + [item['metadata']['id'] for item in records if current in item['metadata']['predecessors']]
        for target in adjacent:
            if target not in selected:
                selected.add(target)
                pending.append(target)
    return [item for item in records if item['metadata']['id'] in selected]


def inventory_item(item: dict[str, Any]) -> dict[str, Any]:
    metadata = item['metadata']
    return {**{key: metadata[key] for key in ('id', 'title', 'topic', 'candidateRevision', 'kind', 'outcome', 'date', 'summary')},
            'path': item['path'], 'bytes': len(item['raw']), 'sha256': item['sha256'],
            'nextCommand': 'maintain.py record read --id ' + metadata['id']}


def cursor_offset(cursor: str | None, expected: dict[str, Any], boundaries: list[int]) -> int:
    if cursor is None:
        return 0
    binding = read_cursor(cursor)
    if any(binding.get(key) != value for key, value in expected.items()) or type(binding.get('offset')) is not int or binding['offset'] not in boundaries:
        raise ValueError('stale or mismatched cursor; restart the selected read')
    return binding['offset']


def emit_error(command: str, message: str, output_format: str = 'summary') -> int:
    print(message, file=sys.stderr)
    if output_format == 'json':
        emit_json(command=command, response_class='complete-evidence', scope={'kind': 'design-record', 'id': command}, data=None,
                  complete=False, error={'code': 'record.invalid', 'message': message})
    return 2


def read_command(root: Path, identifier: str | None, heading: str | None, include_history: bool, output_format: str, response_class: str, max_bytes: int, cursor: str | None) -> int:
    command = 'record-section' if heading is not None else 'record read'
    try:
        if max_bytes < 4:
            raise ValueError('--max-bytes must be at least 4')
        records = load_store(root)
        selected = find_record(records, identifier=identifier, heading=heading)
        entries = history(records, selected['metadata']['id']) if include_history else [selected]
        source = b'\n'.join(item['raw'] for item in entries)
        binding = {'command': command, 'scope': selected['metadata']['id'], 'history': include_history,
                   'sourceSha256': digest(source), 'storeSha256': store_digest(records), 'maxBytes': max_bytes, 'responseClass': response_class}
        boundaries = [0]
        while boundaries[-1] < len(source):
            _, end = bounded_chunk(source, boundaries[-1], max_bytes)
            boundaries.append(end)
        start = cursor_offset(cursor, binding, boundaries[:-1])
        chunk, end = bounded_chunk(source, start, max_bytes)
        exhausted = end == len(source)
        continuation = None if exhausted else make_cursor({**binding, 'offset': end})
        spans = []
        position = 0
        for item in entries:
            stop = position + len(item['raw'])
            if position < end and stop > start:
                spans.append({'id': item['metadata']['id'], 'path': item['path'], 'sha256': item['sha256'],
                              'startByte': position, 'endByte': stop})
            position = stop + 1  # History members are separated by one LF.
        data = {'id': selected['metadata']['id'], 'heading': '## ' + selected['metadata']['title'], 'startByte': start, 'endByte': end,
                'text': chunk.decode('utf-8'), 'chunkIndex': boundaries.index(start), 'chunkCount': len(boundaries) - 1,
                'reconstructionRequired': len(boundaries) > 2, 'sequenceExhausted': exhausted,
                'storeSha256': binding['storeSha256'], 'recordCount': len(entries), 'records': spans}
        if output_format == 'json':
            emit_json(command=command, response_class=response_class, scope={'kind': 'design-record-history' if include_history else 'design-record', 'id': selected['metadata']['id']},
                      data=data, complete=exhausted and response_class == 'complete-evidence', truncated=not exhausted,
                      returned_items=len(entries), total_items=len(entries), returned_bytes=len(chunk), source_bytes=len(source),
                      source_sha256=binding['sourceSha256'], next_cursor=continuation,
                      error=None if exhausted or response_class == 'discovery-preview' else {'code': 'output.incomplete', 'message': 'continue with --cursor'})
        else:
            print(f"response-class={response_class} complete={str(exhausted and response_class == 'complete-evidence').lower()} bytes={start}:{end}/{len(source)} sha256={binding['sourceSha256']}")
            sys.stdout.write(chunk.decode('utf-8'))
        if continuation:
            selector = '--heading ' + shlex.quote(heading) if heading is not None else '--id ' + selected['metadata']['id']
            extra = ' --history' if include_history else ''
            print(f'next-command: maintain.py {command} {selector}{extra} --format {output_format} --response-class {response_class} --max-bytes {max_bytes} --cursor {continuation}', file=sys.stderr)
        return 0 if exhausted or response_class == 'discovery-preview' else 2
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return emit_error(command, str(exc), output_format)


def list_command(root: Path, topic: str | None, output_format: str, response_class: str, max_bytes: int, cursor: str | None) -> int:
    try:
        records = load_store(root)
        items = [inventory_item(item) for item in records if topic is None or item['metadata']['topic'] == topic]
        source = canonical_json(items).encode('utf-8')
        binding = {'command': 'record list', 'topic': topic, 'sourceSha256': digest(source), 'storeSha256': store_digest(records),
                   'maxBytes': max_bytes, 'responseClass': response_class}
        if not items and cursor is not None:
            raise ValueError('stale cursor: the selected listing is now empty')
        start = cursor_offset(cursor, binding, list(range(len(items)))) if items else 0
        page = []
        end = start
        while end < len(items):
            proposed = page + [items[end]]
            if len(canonical_json(proposed).encode('utf-8')) > max_bytes:
                break
            page = proposed
            end += 1
        if items and not page:
            raise ValueError('byte budget cannot contain one inventory item; increase --max-bytes or use record read --id ID')
        if len(canonical_json(page).encode('utf-8')) > max_bytes:
            raise ValueError('byte budget cannot contain the empty listing')
        exhausted = end == len(items)
        continuation = None if exhausted else make_cursor({**binding, 'offset': end})
        data = {'items': page, 'startItem': start, 'endItem': end, 'sequenceExhausted': exhausted, 'storeSha256': binding['storeSha256']}
        if output_format == 'json':
            emit_json(command='record list', response_class=response_class, scope={'kind': 'design-record-inventory', 'id': topic or 'all'}, data=data,
                      complete=exhausted and response_class == 'complete-evidence', truncated=not exhausted, returned_items=len(page), total_items=len(items),
                      returned_bytes=len(canonical_json(page).encode('utf-8')), source_bytes=len(source), source_sha256=binding['sourceSha256'], next_cursor=continuation,
                      error=None if exhausted or response_class == 'discovery-preview' else {'code': 'output.incomplete', 'message': 'continue with --cursor'})
        else:
            print(f'response-class={response_class} complete={str(exhausted and response_class == "complete-evidence").lower()} items={start}:{end}/{len(items)} sha256={binding["sourceSha256"]}')
            for item in page:
                if output_format == 'full':
                    print(canonical_json(item))
                else:
                    print(f"{item['id']} {item['topic']} {item['kind']}/{item['outcome']} {item['bytes']} bytes: {item['title']}\n  {item['nextCommand']}")
        if continuation:
            selector = '' if topic is None else ' --topic ' + topic
            print(f'next-command: maintain.py record list{selector} --format {output_format} --response-class {response_class} --max-bytes {max_bytes} --cursor {continuation}', file=sys.stderr)
        return 0 if exhausted or response_class == 'discovery-preview' else 2
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return emit_error('record list', str(exc), output_format)


def prepare_add(root: Path, supplied: Any) -> tuple[Path, bytes, dict[str, Any]]:
    if not isinstance(supplied, dict) or set(supplied) != FIELDS:
        raise ValueError('record input fields differ; see references/design-record/README.md')
    validate_fields(supplied)
    issues = integrity_issues(root, allow_writer_artifacts=True)
    if issues:
        raise ValueError('existing history integrity failed: ' + '; '.join(issues))
    records = load_store(root)
    identifier = f'wr-{len(records) + 1:04d}'
    existing = {item['metadata']['id'] for item in records}
    if any(target not in existing for target in links(supplied)):
        raise ValueError('new record references a missing predecessor, source, or authority record')
    metadata = {key: value for key, value in supplied.items() if key != 'body'}
    metadata.update(format='wayfinder-design-record', schemaVersion=1, id=identifier, legacy=None)
    slug = re.sub(r'[^a-z0-9]+', '-', supplied['title'].lower()).strip('-')[:80].rstrip('-') or 'record'
    relative = f'{folder(metadata)}/{identifier}-{slug}.md'
    target = safe_path(root, relative, absent=True)
    body = ('## ' + supplied['title'] + '\n\n' + supplied['body'].rstrip('\n') + '\n').encode('utf-8')
    raw = render(metadata, body)
    parse(raw)
    return target, raw, metadata


def add_command(root: Path, input_path: Path, dry_run: bool, output_format: str, max_bytes: int) -> int:
    lock = None
    pending = None
    lock_identity = None
    try:
        supplied = strict_json(read_regular(input_path))
        if not dry_run:
            lock = safe_path(root, '.record-add.lock', absent=True)
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
                lock_identity = os.fstat(stream.fileno())
                stream.write(canonical_json({'pid': os.getpid(), 'host': platform.node()}) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
        if list(root.glob('.pending-*')):
            raise ValueError('unfinished record creation; inspect pending files and lock before manual cleanup')
        target, raw, metadata = prepare_add(root, supplied)
        data = {'id': metadata['id'], 'path': target.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': digest(raw), 'dryRun': dry_run,
                'written': not dry_run, 'currentStateUpdated': False}
        if dry_run:
            data['text'] = raw.decode('utf-8')
        rendered = canonical_json(data).encode('utf-8')
        if len(rendered) > max_bytes:
            raise ValueError('output budget cannot describe the complete addition before writing; increase --max-bytes')
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            safe_path(root, target.relative_to(root).as_posix(), absent=True)
            descriptor, name = tempfile.mkstemp(prefix='.pending-', dir=root)
            pending = Path(name)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            if read_regular(pending) != raw:
                raise ValueError('staged record bytes differ')
            # Publish an already complete inode exclusively; readers never see a
            # partially written *.md. No fallback to overwrite or partial copy.
            os.link(pending, target)
            if read_regular(target) != raw:
                raise ValueError('published record bytes differ; inspect the created record')
        if output_format == 'json':
            emit_json(command='record add', response_class='complete-evidence', scope={'kind': 'design-record', 'id': metadata['id']}, data=data,
                      returned_bytes=len(rendered), source_bytes=len(raw), source_sha256=digest(raw), returned_items=1, total_items=1)
        elif dry_run:
            print(f"dry-run id={metadata['id']} path={data['path']} sha256={data['sha256']}")
            sys.stdout.write(raw.decode('utf-8'))
        else:
            print(f"created {metadata['id']} {data['path']} sha256={data['sha256']}; current state unchanged")
        return 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return emit_error('record add', str(exc), output_format)
    finally:
        if pending is not None:
            with contextlib.suppress(OSError):
                pending.unlink()
        if lock is not None and lock_identity is not None:
            with contextlib.suppress(OSError):
                actual = lock.lstat()
                if (actual.st_dev, actual.st_ino) == (lock_identity.st_dev, lock_identity.st_ino):
                    lock.unlink()


def integrity_issues(root: Path, *, expected_migration_digest: str | None = MIGRATION_SHA256, allow_writer_artifacts: bool = False) -> list[str]:
    try:
        records = load_store(root)
        artifacts = list(root.glob('.pending-*')) + ([root / '.record-add.lock'] if (root / '.record-add.lock').exists() else [])
        if artifacts and not allow_writer_artifacts:
            raise ValueError('unfinished record writer artifacts; inspect and clean up explicitly')
        manifest_raw = read_regular(safe_path(root, 'migration.json'))
        if expected_migration_digest is not None and digest(manifest_raw) != expected_migration_digest:
            raise ValueError('design-record migration manifest digest differs')
        manifest = strict_json(manifest_raw)
        if manifest['format'] != 'wayfinder-design-record-migration' or manifest['schemaVersion'] != 1:
            raise ValueError('migration format/version differs')
        by_id = {item['metadata']['id']: item for item in records}
        original_parts = [manifest['preamble'].encode('utf-8')]
        offset = len(original_parts[0])
        for index, entry in enumerate(manifest['sections'], 1):
            item = by_id[entry['id']]
            if entry['id'] != f'wr-{index:04d}' or entry['startByte'] != offset or item['path'] != entry['path'] or item['sha256'] != entry['recordSha256']:
                raise ValueError(f'migrated record binding differs: {entry["id"]}')
            migrated = item['body']
            original = bytearray()
            position = 0
            for adjustment in entry['linkAdjustments']:
                start, end = adjustment['startByte'], adjustment['endByte']
                if start < position or migrated[start:end] != adjustment['after'].encode('utf-8'):
                    raise ValueError('link-adjustment range/content differs')
                original.extend(migrated[position:start])
                original.extend(adjustment['before'].encode('utf-8'))
                position = end
            original.extend(migrated[position:])
            raw = bytes(original)
            if digest(raw) != entry['sourceSectionSha256'] or item['metadata']['legacy'] != {'sourceSectionSha256': digest(raw)}:
                raise ValueError(f'historical section content differs: {entry["id"]}')
            offset += len(raw)
            if offset != entry['endByte']:
                raise ValueError('historical byte range differs')
            original_parts.append(raw)
        original = b''.join(original_parts)
        if len(original) != manifest['sourceBytes'] or digest(original) != manifest['sourceSha256']:
            raise ValueError('original design chronology reconstruction differs')
        migrated_ids = {entry['id'] for entry in manifest['sections']}
        if {item['metadata']['id'] for item in records if item['metadata']['legacy'] is not None} != migrated_ids:
            raise ValueError('legacy record membership differs')
        return []
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return [str(exc)]
