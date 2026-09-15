#!/usr/bin/env python3
"""Wayfinder version-1 frozen-candidate Python adapter under test."""

from __future__ import annotations

import hashlib
import fnmatch
import ctypes
import json
import os
import platform
import posixpath
import re
import secrets
import shutil
import socket
import stat
import sys
import tempfile
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


CONTRACT_VERSION = 1
SCHEMA_VERSION = 1
CANDIDATE_REVISION = 11
RELEASE_ID = f"v1-candidate-revision-{CANDIDATE_REVISION}"
CONTRACT_STATUS = "frozen"
RELEASE_STATUS = "unactivated-frozen"
ADAPTER_ID = "python-reference-v1"
RELEASE_PATH = "assets/contract-v1/release.json"
CONTRACT_PATH = "assets/contract-v1/contract.json"
ADAPTER_PATH = "scripts/adapters/wayfinder.py"
MAX_EXACT_INTEGER = 9_007_199_254_740_991
RESULT_FIELDS = ("format", "schemaVersion", "ok", "command", "code", "data", "diagnostics")
STANDARD_MODULES = {"decisions", "research", "product", "architecture", "development"}
REGISTERED_GENERATORS = {"document-catalog-v1"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_MODULE_RE = re.compile(r"^local-[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
DOCUMENT_ID_RE = re.compile(r"^wf-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
QUESTION_ID_RE = re.compile(r"^wfq-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
EVIDENCE_KEY_RE = re.compile(r"^src-([0-9]{2,})$")
KINDS = ("map", "brief", "register", "evidence", "decision", "guide", "index")
LIVING_STATUSES = ("Draft", "Active", "Superseded", "Retired")
DECISION_STATUSES = ("Proposed", "Accepted", "Rejected", "Superseded")
QUESTION_STATES = ("Open", "Investigating", "Deferred", "Resolved", "Retired")
RELATION_ORDER = {"Governed-By": 0, "Supported-By": 1}
METADATA_ORDER = ("ID", "Kind", "Status", "Updated", "Summary", "Decision-Date", "Supersedes", "Superseded-By")
GENERATED_START_RE = re.compile(
    r'^<!-- wayfinder:generated name="([a-z0-9]+(?:-[a-z0-9]+)*)" generator="document-index-v1" input-sha256="([0-9a-f]{64})" -->$'
)
GENERATED_END = "<!-- /wayfinder:generated -->"
LINK_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)$")
FIELD_RE = re.compile(r"^- \*\*([A-Za-z][A-Za-z-]*):\*\* (.+)$")
HISTORY_RE = re.compile(r"^- ([0-9]{4}-[0-9]{2}-[0-9]{2}): (None|Open|Investigating|Deferred|Resolved|Retired) -> (Open|Investigating|Deferred|Resolved|Retired) - (.+)$")
MATERIAL_CLAIM_RE = re.compile(r"^- \*\*Material claim:\*\* (.+)$")
TEMPLATE_SLOT_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
PORTABLE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
WINDOWS_DEVICES = {
    "con", "prn", "aux", "nul", "clock$",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
VCS_ADMIN_NAMES = {".git", ".hg", ".svn"}
DEPENDENCY_DIRECTORY_NAMES = {"node_modules", "vendor", ".venv", "venv"}
BUILD_DIRECTORY_NAMES = {"build", "dist", "out", "target", "coverage", ".cache"}
ARCHIVE_SUFFIXES = (
    ".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz",
    ".7z", ".rar", ".gz", ".bz2", ".xz",
)
SECRET_PATTERNS = (
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa", "id_ed25519",
    "credentials", "credentials.*", "secrets", "secrets.*",
)
INITIALIZE_COMMANDS = {"initialize-plan", "initialize-apply", "initialize-recover"}
CONFIRMATION_PREFIX = "wayfinder-confirm-sha256:"
EVENT_FORMAT = "wayfinder-initialization-event"
RECEIPT_FORMAT = "wayfinder-initialization-receipt"
LOCK_FORMAT = "wayfinder-initialization-lock"
JOURNAL_NAME = "events.jsonl"


class WFError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        exit_class: int,
        path: str | None = None,
        field: str | None = None,
        expected: Any = None,
        actual: Any = None,
        remediation: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_class = exit_class
        self.path = path
        self.field = field
        self.expected = expected
        self.actual = actual
        self.remediation = remediation

    def diagnostic(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.path is not None:
            result["path"] = self.path
        if self.field is not None:
            result["field"] = self.field
        if self.expected is not None:
            result["expected"] = self.expected
        if self.actual is not None:
            result["actual"] = self.actual
        if self.remediation is not None:
            result["remediation"] = self.remediation
        return result


def _reject_float(value: str) -> None:
    raise ValueError(f"floating-point number is outside the version-1 subset: {value}")


def _parse_integer(value: str) -> int:
    if value == "-0":
        raise ValueError("negative zero is outside the version-1 subset")
    parsed = int(value)
    if abs(parsed) > MAX_EXACT_INTEGER:
        raise ValueError(f"integer is outside the exact version-1 range: {value}")
    return parsed


def _unicode_scalar_string(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        point = ord(value[index])
        if 0xD800 <= point <= 0xDBFF:
            if index + 1 >= len(value):
                raise ValueError("malformed Unicode surrogate")
            low = ord(value[index + 1])
            if not 0xDC00 <= low <= 0xDFFF:
                raise ValueError("malformed Unicode surrogate")
            result.append(chr(0x10000 + ((point - 0xD800) << 10) + (low - 0xDC00)))
            index += 2
            continue
        if 0xDC00 <= point <= 0xDFFF:
            raise ValueError("malformed Unicode surrogate")
        result.append(value[index])
        index += 1
    return "".join(result)


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        key = _unicode_scalar_string(key)
        if key in result:
            raise ValueError(f"duplicate object name: {key}")
        result[key] = value
    return result


def _normalize_json_strings(value: Any) -> Any:
    if isinstance(value, str):
        return _unicode_scalar_string(value)
    if isinstance(value, list):
        return [_normalize_json_strings(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_json_strings(item) for key, item in value.items()}
    return value


def _check_nfc(value: Any, pointer: str = "") -> None:
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise WFError(
                "text.non-nfc",
                "JSON string is not Unicode NFC",
                exit_class=4,
                field=pointer or "/",
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check_nfc(item, f"{pointer}/{index}")
    elif isinstance(value, dict):
        for key, item in value.items():
            _check_nfc(key, f"{pointer}/<key>")
            escaped = key.replace("~", "~0").replace("/", "~1")
            _check_nfc(item, f"{pointer}/{escaped}")


def strict_json_bytes(raw: bytes, *, path: str, governed: bool = False, exit_class: int = 4) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise WFError("text.bom", "UTF-8 BOM is forbidden", exit_class=exit_class, path=path)
    if b"\r" in raw:
        raise WFError("text.newline", "only LF newlines are accepted", exit_class=exit_class, path=path)
    if governed and (not raw.endswith(b"\n") or raw.endswith(b"\n\n")):
        raise WFError(
            "text.terminal-newline",
            "governed resources require exactly one terminal LF",
            exit_class=exit_class,
            path=path,
        )
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise WFError(
            "text.invalid-utf8",
            "input is not well-formed UTF-8",
            exit_class=exit_class,
            path=path,
            actual=exc.start,
        ) from None
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_int=_parse_integer,
            parse_float=_reject_float,
            parse_constant=_reject_float,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        detail = str(exc)
        code = "json.duplicate-key" if detail.startswith("duplicate object name:") else "json.invalid"
        if "floating-point" in detail or "integer is outside" in detail or "version-1 subset" in detail:
            code = "json.number"
        if "malformed Unicode surrogate" in detail:
            code = "text.invalid-unicode"
        raise WFError(code, f"strict JSON parsing failed: {detail}", exit_class=exit_class, path=path) from None
    try:
        value = _normalize_json_strings(value)
    except ValueError as exc:
        raise WFError("text.invalid-unicode", f"strict JSON parsing failed: {exc}", exit_class=exit_class, path=path) from None
    try:
        _check_nfc(value)
    except WFError as exc:
        exc.exit_class = exit_class
        raise
    return value


def _utf16_sort_key(value: str) -> bytes:
    return value.encode("utf-16-be")


def canonical_json(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if abs(value) > MAX_EXACT_INTEGER:
            raise ValueError("integer outside exact range")
        return str(value)
    if isinstance(value, float):
        raise ValueError("floating point is forbidden")
    if isinstance(value, str):
        value = _unicode_scalar_string(value)
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("object names must be strings")
        keys = sorted(value, key=_utf16_sort_key)
        return "{" + ",".join(canonical_json(key) + ":" + canonical_json(value[key]) for key in keys) + "}"
    raise ValueError(f"unsupported canonical JSON value: {type(value).__name__}")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _expect_object(value: Any, field: str, *, exit_class: int = 4) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WFError("json.type", "expected an object", exit_class=exit_class, field=field, expected="object")
    return value


def _expect_array(value: Any, field: str, *, exit_class: int = 4) -> list[Any]:
    if not isinstance(value, list):
        raise WFError("json.type", "expected an array", exit_class=exit_class, field=field, expected="array")
    return value


def _closed(obj: dict[str, Any], required: Iterable[str], field: str, *, exit_class: int = 4) -> None:
    required_set = set(required)
    unknown = sorted(set(obj) - required_set)
    missing = sorted(required_set - set(obj))
    if unknown:
        raise WFError("json.unknown-field", "closed object has unknown fields", exit_class=exit_class, field=field, actual=unknown)
    if missing:
        raise WFError("json.missing-field", "closed object is missing required fields", exit_class=exit_class, field=field, actual=missing)


def _expect_literal(value: Any, literal: Any, field: str, code: str, *, exit_class: int = 4) -> None:
    if type(value) is not type(literal) or value != literal:
        raise WFError(code, "value does not match the version-1 contract", exit_class=exit_class, field=field, expected=literal, actual=value)


def portable_path(value: Any, field: str, *, allow_dot: bool = False, exit_class: int = 4) -> str:
    if not isinstance(value, str):
        raise WFError("json.type", "path must be a string", exit_class=exit_class, field=field, expected="string")
    if unicodedata.normalize("NFC", value) != value:
        raise WFError("text.non-nfc", "path is not Unicode NFC", exit_class=exit_class, field=field)
    if allow_dot and value == ".":
        return value
    if not value or value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value):
        raise WFError("path.absolute", "path must be relative", exit_class=exit_class, field=field, actual=value)
    if "\\" in value:
        raise WFError("path.backslash", "backslashes are forbidden in manifest paths", exit_class=exit_class, field=field, actual=value)
    if "\x00" in value:
        raise WFError("path.nul", "NUL is forbidden in paths", exit_class=exit_class, field=field)
    segments = value.split("/")
    if any(segment == "" for segment in segments):
        raise WFError("path.empty-segment", "empty path segments are forbidden", exit_class=exit_class, field=field, actual=value)
    if any(segment == "." for segment in segments):
        raise WFError("path.dot-segment", "dot path segments are forbidden", exit_class=exit_class, field=field, actual=value)
    if any(segment == ".." for segment in segments):
        raise WFError("path.traversal", "parent traversal is forbidden", exit_class=exit_class, field=field, actual=value)
    for segment in segments:
        if not PORTABLE_SEGMENT_RE.fullmatch(segment) or segment.endswith((".", " ")) or ":" in segment:
            raise WFError("path.nonportable", "path is outside the portable ASCII profile", exit_class=exit_class, field=field, actual=value)
        device_stem = segment.split(".", 1)[0].lower()
        if device_stem in WINDOWS_DEVICES:
            raise WFError("path.reserved-name", "path contains a reserved portable device name", exit_class=exit_class, field=field, actual=segment)
    return value


def path_key(value: str) -> tuple[str, ...]:
    if value == ".":
        return ()
    return tuple(part.lower() for part in PurePosixPath(value).parts)


def is_within(child: str, parent: str, *, allow_equal: bool = True) -> bool:
    child_parts = path_key(child)
    parent_parts = path_key(parent)
    return len(child_parts) >= len(parent_parts) + (0 if allow_equal else 1) and child_parts[: len(parent_parts)] == parent_parts


def overlaps(first: str, second: str) -> bool:
    return is_within(first, second) or is_within(second, first)


def _physical_check(
    base: Path,
    relative: str,
    field: str,
    expected_kind: str | None = None,
    *,
    required: bool = False,
    exit_class: int = 4,
) -> Path:
    base = base.resolve(strict=True)
    current = base
    parts = () if relative == "." else PurePosixPath(relative).parts
    for part in parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise WFError("path.symlink", "existing managed path component is a symbolic link", exit_class=exit_class, path=str(current), field=field)
    resolved = current.resolve(strict=False)
    try:
        common = os.path.commonpath((str(base), str(resolved)))
    except ValueError:
        common = ""
    if common != str(base):
        raise WFError("path.containment", "physical path escapes its declared owner", exit_class=exit_class, path=str(current), field=field)
    if required and not current.exists():
        raise WFError("manifest.path-missing", "declared live-record path does not exist", exit_class=exit_class, path=str(current), field=field)
    if current.exists():
        if expected_kind == "file" and not current.is_file():
            raise WFError("path.expected-file", "existing entrypoint or artifact is not a regular file", exit_class=exit_class, path=str(current), field=field)
        if expected_kind == "directory" and not current.is_dir():
            raise WFError("path.expected-directory", "existing root is not a directory", exit_class=exit_class, path=str(current), field=field)
    return resolved


def validate_manifest(value: Any, workspace: Path) -> dict[str, Any]:
    manifest = _expect_object(value, "/")
    fields = ("format", "schemaVersion", "recordRoot", "entrypoint", "canonicalBaseline", "modules", "generatedArtifacts")
    _closed(manifest, fields, "/")
    _expect_literal(manifest["format"], "wayfinder-project-record", "/format", "manifest.format")
    _expect_literal(manifest["schemaVersion"], 1, "/schemaVersion", "manifest.unsupported-version")

    record_root_text = portable_path(manifest["recordRoot"], "/recordRoot", allow_dot=True)
    entrypoint = portable_path(manifest["entrypoint"], "/entrypoint")
    if not entrypoint.endswith(".md"):
        raise WFError("manifest.entrypoint-extension", "entrypoint must end in .md", exit_class=4, field="/entrypoint")

    workspace = workspace.resolve(strict=True)
    record_root = _physical_check(workspace, record_root_text, "/recordRoot", "directory", required=True)
    _physical_check(record_root, entrypoint, "/entrypoint", "file", required=True)

    baseline = _expect_object(manifest["canonicalBaseline"], "/canonicalBaseline")
    kind = baseline.get("kind")
    if kind == "git-ref":
        _closed(baseline, ("kind", "ref"), "/canonicalBaseline")
        ref = baseline["ref"]
        if not isinstance(ref, str) or not ref.startswith("refs/") or not re.fullmatch(r"refs/[A-Za-z0-9._/-]+", ref) or "//" in ref or ".." in ref or ref.endswith(("/", ".")) or "@{" in ref:
            raise WFError("manifest.git-ref", "Git baseline ref must be a conservative fully qualified refs/... name", exit_class=4, field="/canonicalBaseline/ref", actual=ref)
    elif kind == "snapshot":
        _closed(baseline, ("kind", "path", "sha256"), "/canonicalBaseline")
        snapshot_path = portable_path(baseline["path"], "/canonicalBaseline/path")
        if not is_within(snapshot_path, ".wayfinder/baselines", allow_equal=False):
            raise WFError("manifest.snapshot-path", "snapshot must be beneath .wayfinder/baselines/", exit_class=4, field="/canonicalBaseline/path")
        if not isinstance(baseline["sha256"], str) or not HEX_RE.fullmatch(baseline["sha256"]):
            raise WFError("manifest.sha256", "snapshot sha256 must be lowercase 64-hex", exit_class=4, field="/canonicalBaseline/sha256")
        _physical_check(workspace, snapshot_path, "/canonicalBaseline/path", "file", required=True)
    else:
        raise WFError("manifest.baseline-kind", "unsupported canonical baseline kind", exit_class=4, field="/canonicalBaseline/kind", actual=kind)

    modules = _expect_array(manifest["modules"], "/modules")
    module_ids: set[str] = set()
    module_roots: list[str] = []
    entrypoint_keys = {path_key(entrypoint)}
    for module_index, raw_module in enumerate(modules):
        pointer = f"/modules/{module_index}"
        module = _expect_object(raw_module, pointer)
        _closed(module, ("id", "root", "entrypoint", "subjects"), pointer)
        module_id = module["id"]
        if not isinstance(module_id, str) or (module_id not in STANDARD_MODULES and not LOCAL_MODULE_RE.fullmatch(module_id)):
            raise WFError("manifest.module-id", "module id is not registered or a local-* slug", exit_class=4, field=f"{pointer}/id", actual=module_id)
        if module_id in module_ids:
            raise WFError("manifest.duplicate-module-id", "module id is duplicated", exit_class=4, field=f"{pointer}/id", actual=module_id)
        module_ids.add(module_id)
        root = portable_path(module["root"], f"{pointer}/root")
        module_entrypoint = portable_path(module["entrypoint"], f"{pointer}/entrypoint")
        if not module_entrypoint.endswith(".md"):
            raise WFError("manifest.entrypoint-extension", "module entrypoint must end in .md", exit_class=4, field=f"{pointer}/entrypoint")
        if not is_within(module_entrypoint, root, allow_equal=False):
            raise WFError("manifest.entrypoint-outside-owner", "module entrypoint is outside its module root", exit_class=4, field=f"{pointer}/entrypoint")
        if any(overlaps(root, prior) for prior in module_roots):
            raise WFError("manifest.module-root-overlap", "module roots overlap or nest", exit_class=4, field=f"{pointer}/root", actual=root)
        if path_key(module_entrypoint) in entrypoint_keys:
            raise WFError("manifest.duplicate-entrypoint", "entrypoint is duplicated", exit_class=4, field=f"{pointer}/entrypoint", actual=module_entrypoint)
        module_roots.append(root)
        entrypoint_keys.add(path_key(module_entrypoint))
        _physical_check(record_root, root, f"{pointer}/root", "directory", required=True)
        _physical_check(record_root, module_entrypoint, f"{pointer}/entrypoint", "file", required=True)

        subjects = _expect_array(module["subjects"], f"{pointer}/subjects")
        subject_ids: set[str] = set()
        collection_roots: list[str] = []
        document_entries: list[tuple[str, str]] = []
        for subject_index, raw_subject in enumerate(subjects):
            subject_pointer = f"{pointer}/subjects/{subject_index}"
            subject = _expect_object(raw_subject, subject_pointer)
            subject_kind = subject.get("kind")
            subject_fields = ("id", "kind", "entrypoint") if subject_kind == "document" else ("id", "kind", "root", "entrypoint")
            if subject_kind not in {"document", "collection"}:
                raise WFError("manifest.subject-kind", "subject kind must be document or collection", exit_class=4, field=f"{subject_pointer}/kind", actual=subject_kind)
            _closed(subject, subject_fields, subject_pointer)
            subject_id = subject["id"]
            if not isinstance(subject_id, str) or not SLUG_RE.fullmatch(subject_id):
                raise WFError("manifest.subject-id", "subject id must be a lowercase ASCII slug", exit_class=4, field=f"{subject_pointer}/id", actual=subject_id)
            if subject_id in subject_ids:
                raise WFError("manifest.duplicate-subject-id", "subject id is duplicated within its module", exit_class=4, field=f"{subject_pointer}/id", actual=subject_id)
            subject_ids.add(subject_id)
            subject_entrypoint = portable_path(subject["entrypoint"], f"{subject_pointer}/entrypoint")
            if not subject_entrypoint.endswith(".md"):
                raise WFError("manifest.entrypoint-extension", "subject entrypoint must end in .md", exit_class=4, field=f"{subject_pointer}/entrypoint")
            if path_key(subject_entrypoint) in entrypoint_keys:
                raise WFError("manifest.duplicate-entrypoint", "entrypoint is duplicated", exit_class=4, field=f"{subject_pointer}/entrypoint", actual=subject_entrypoint)
            entrypoint_keys.add(path_key(subject_entrypoint))
            if subject_kind == "document":
                if not is_within(subject_entrypoint, root):
                    raise WFError("manifest.entrypoint-outside-owner", "document subject is outside its module root", exit_class=4, field=f"{subject_pointer}/entrypoint")
                document_entries.append((subject_entrypoint, f"{subject_pointer}/entrypoint"))
            else:
                subject_root = portable_path(subject["root"], f"{subject_pointer}/root")
                if not is_within(subject_root, root, allow_equal=False):
                    raise WFError("manifest.subject-root-outside-module", "collection root must be strictly beneath its module root", exit_class=4, field=f"{subject_pointer}/root")
                if any(overlaps(subject_root, prior) for prior in collection_roots):
                    raise WFError("manifest.subject-root-overlap", "collection roots overlap or nest", exit_class=4, field=f"{subject_pointer}/root", actual=subject_root)
                if not is_within(subject_entrypoint, subject_root):
                    raise WFError("manifest.entrypoint-outside-owner", "collection entrypoint is outside its root", exit_class=4, field=f"{subject_pointer}/entrypoint")
                collection_roots.append(subject_root)
                _physical_check(record_root, subject_root, f"{subject_pointer}/root", "directory", required=True)
            _physical_check(record_root, subject_entrypoint, f"{subject_pointer}/entrypoint", "file", required=True)
        for document_entrypoint, document_pointer in document_entries:
            if any(is_within(document_entrypoint, collection_root) for collection_root in collection_roots):
                raise WFError("manifest.document-in-collection", "document subject entrypoint falls inside a collection subject", exit_class=4, field=document_pointer)

    if "decisions" not in module_ids:
        raise WFError("manifest.decisions-required", "version 1 requires the decisions module", exit_class=4, field="/modules")

    artifacts = _expect_array(manifest["generatedArtifacts"], "/generatedArtifacts")
    artifact_keys: set[tuple[str, ...]] = set()
    for index, raw_artifact in enumerate(artifacts):
        pointer = f"/generatedArtifacts/{index}"
        artifact = _expect_object(raw_artifact, pointer)
        _closed(artifact, ("path", "generator"), pointer)
        artifact_path = portable_path(artifact["path"], f"{pointer}/path")
        key = path_key(artifact_path)
        if key in artifact_keys:
            raise WFError("manifest.duplicate-artifact", "generated artifact path is duplicated", exit_class=4, field=f"{pointer}/path", actual=artifact_path)
        artifact_keys.add(key)
        if artifact["generator"] not in REGISTERED_GENERATORS:
            raise WFError("manifest.unknown-generator", "generated artifact uses an unregistered generator", exit_class=4, field=f"{pointer}/generator", actual=artifact["generator"])
        if key in entrypoint_keys:
            raise WFError("manifest.artifact-entrypoint-conflict", "generated artifact path conflicts with an authored entrypoint", exit_class=4, field=f"{pointer}/path", actual=artifact_path)
        _physical_check(record_root, artifact_path, f"{pointer}/path", "file", required=True)

    return {
        "manifest": manifest,
        "paths": {
            "workspaceRoot": str(workspace),
            "recordRoot": str(record_root),
            "entrypoint": str(record_root / PurePosixPath(entrypoint)),
        },
    }


def _validate_release(value: Any) -> dict[str, Any]:
    release = _expect_object(value, "/", exit_class=2)
    _closed(release, ("format", "schemaVersion", "releaseId", "status", "contractVersion", "contractManifest", "adapters", "certifications"), "/", exit_class=2)
    _expect_literal(release["format"], "wayfinder-contract-release", "/format", "package.release-format", exit_class=2)
    _expect_literal(release["schemaVersion"], 1, "/schemaVersion", "package.release-version", exit_class=2)
    _expect_literal(release["releaseId"], RELEASE_ID, "/releaseId", "package.release-id", exit_class=2)
    _expect_literal(release["status"], RELEASE_STATUS, "/status", "package.activation-state", exit_class=2)
    _expect_literal(release["contractVersion"], CONTRACT_VERSION, "/contractVersion", "package.contract-version", exit_class=2)
    contract = _expect_object(release["contractManifest"], "/contractManifest", exit_class=2)
    _closed(contract, ("path", "sha256"), "/contractManifest", exit_class=2)
    _expect_literal(contract["path"], CONTRACT_PATH, "/contractManifest/path", "package.contract-path", exit_class=2)
    adapters = _expect_array(release["adapters"], "/adapters", exit_class=2)
    if not adapters:
        raise WFError("package.adapter-entry", "release must list at least one adapter", exit_class=2, field="/adapters")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    current = None
    for index, raw_adapter in enumerate(adapters):
        pointer = f"/adapters/{index}"
        adapter = _expect_object(raw_adapter, pointer, exit_class=2)
        _closed(adapter, ("id", "path", "sha256"), pointer, exit_class=2)
        if not isinstance(adapter["id"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*-v1", adapter["id"]):
            raise WFError("package.adapter-entry", "adapter ID is invalid", exit_class=2, field=f"{pointer}/id")
        path = portable_path(adapter["path"], f"{pointer}/path", exit_class=2)
        if not re.fullmatch(r"scripts/adapters/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:py|mjs|ps1)", path):
            raise WFError("package.adapter-entry", "adapter path is invalid", exit_class=2, field=f"{pointer}/path")
        if adapter["id"] in seen_ids or path_key(path) in seen_paths:
            raise WFError("package.adapter-entry", "adapter IDs and paths must be unique", exit_class=2, field=pointer)
        seen_ids.add(adapter["id"])
        seen_paths.add(path_key(path))
        if adapter["id"] == ADAPTER_ID:
            current = adapter
    if current is None or current["path"] != ADAPTER_PATH:
        raise WFError("package.adapter-entry", "release does not identify the executing adapter", exit_class=2, field="/adapters")
    certifications = _expect_array(release["certifications"], "/certifications", exit_class=2)
    if certifications:
        raise WFError("package.certification-state", "unactivated proposed freeze must not claim certified environments", exit_class=2, field="/certifications")
    for pointer, digest in (("/contractManifest/sha256", contract["sha256"]), ("/adapters", current["sha256"])):
        if not isinstance(digest, str) or not HEX_RE.fullmatch(digest):
            raise WFError("package.digest-format", "package digest must be lowercase 64-hex", exit_class=2, field=pointer)
    return release


def _validate_contract(value: Any) -> dict[str, Any]:
    contract = _expect_object(value, "/", exit_class=2)
    fields = ("format", "schemaVersion", "contractVersion", "candidateRevision", "status", "governedScopes", "governedResources", "registries")
    _closed(contract, fields, "/", exit_class=2)
    _expect_literal(contract["format"], "wayfinder-executable-contract", "/format", "package.contract-format", exit_class=2)
    _expect_literal(contract["schemaVersion"], 1, "/schemaVersion", "package.contract-schema-version", exit_class=2)
    _expect_literal(contract["contractVersion"], 1, "/contractVersion", "package.contract-version", exit_class=2)
    _expect_literal(contract["candidateRevision"], CANDIDATE_REVISION, "/candidateRevision", "package.candidate-revision", exit_class=2)
    _expect_literal(contract["status"], CONTRACT_STATUS, "/status", "package.activation-state", exit_class=2)
    scopes = _expect_array(contract["governedScopes"], "/governedScopes", exit_class=2)
    resources = _expect_array(contract["governedResources"], "/governedResources", exit_class=2)
    seen_paths: set[str] = set()
    for index, scope_value in enumerate(scopes):
        scope = _expect_object(scope_value, f"/governedScopes/{index}", exit_class=2)
        _closed(scope, ("path", "recursive"), f"/governedScopes/{index}", exit_class=2)
        portable_path(scope["path"], f"/governedScopes/{index}/path", exit_class=2)
        if type(scope["recursive"]) is not bool:
            raise WFError("json.type", "recursive must be boolean", exit_class=2, field=f"/governedScopes/{index}/recursive")
    for index, resource_value in enumerate(resources):
        resource = _expect_object(resource_value, f"/governedResources/{index}", exit_class=2)
        _closed(resource, ("path", "role", "sha256"), f"/governedResources/{index}", exit_class=2)
        path = portable_path(resource["path"], f"/governedResources/{index}/path", exit_class=2)
        if path in seen_paths:
            raise WFError("package.duplicate-resource", "governed resource is listed more than once", exit_class=2, field=f"/governedResources/{index}/path", actual=path)
        seen_paths.add(path)
        if not isinstance(resource["role"], str) or not SLUG_RE.fullmatch(resource["role"]):
            raise WFError("package.resource-role", "governed resource role must be a lowercase slug", exit_class=2, field=f"/governedResources/{index}/role")
        if not isinstance(resource["sha256"], str) or not HEX_RE.fullmatch(resource["sha256"]):
            raise WFError("package.digest-format", "resource digest must be lowercase 64-hex", exit_class=2, field=f"/governedResources/{index}/sha256")
    registries = _expect_object(contract["registries"], "/registries", exit_class=2)
    _closed(registries, ("commands", "exitClasses", "generators", "standardModules"), "/registries", exit_class=2)
    if registries["commands"] != ["probe", "discover", "inventory", "initialize-plan", "initialize-apply", "initialize-recover", "validate", "generate"] or registries["generators"] != ["document-catalog-v1", "document-index-v1"] or registries["standardModules"] != ["decisions", "research", "product", "architecture", "development"]:
        raise WFError("package.registry", "contract registry does not match Slice 5", exit_class=2)
    if registries["exitClasses"] != [0, 2, 3, 4, 5, 70]:
        raise WFError("package.registry", "exit class registry does not match version 1", exit_class=2)
    return contract


def verify_package() -> dict[str, Any]:
    skill_root = Path(__file__).resolve().parents[2]
    release_file = skill_root / RELEASE_PATH
    try:
        release_raw = release_file.read_bytes()
        try:
            release_value = strict_json_bytes(release_raw, path=RELEASE_PATH, governed=True)
        except WFError as exc:
            raise WFError("package.release-invalid", f"release descriptor is invalid: {exc.code}", exit_class=2, path=RELEASE_PATH, actual=exc.code) from None
        release = _validate_release(release_value)
    except OSError as exc:
        raise WFError("package.release-missing", "release descriptor cannot be read", exit_class=2, path=str(release_file), actual=str(exc)) from None

    adapter_digest = ""
    for adapter in release["adapters"]:
        adapter_file = skill_root / PurePosixPath(adapter["path"])
        try:
            adapter_raw = adapter_file.read_bytes()
        except OSError as exc:
            raise WFError("package.adapter-missing", "adapter cannot be read", exit_class=2, path=str(adapter_file), actual=str(exc)) from None
        observed_adapter_digest = sha256_bytes(adapter_raw)
        if observed_adapter_digest != adapter["sha256"]:
            raise WFError("package.adapter-digest", "adapter digest does not match release descriptor", exit_class=2, path=adapter["path"], expected=adapter["sha256"], actual=observed_adapter_digest)
        if adapter["id"] == ADAPTER_ID:
            adapter_digest = observed_adapter_digest

    contract_file = skill_root / CONTRACT_PATH
    try:
        contract_raw = contract_file.read_bytes()
    except OSError as exc:
        raise WFError("package.contract-missing", "contract manifest cannot be read", exit_class=2, path=str(contract_file), actual=str(exc)) from None
    contract_digest = sha256_bytes(contract_raw)
    if contract_digest != release["contractManifest"]["sha256"]:
        raise WFError("package.contract-digest", "contract manifest digest does not match release descriptor", exit_class=2, path=CONTRACT_PATH, expected=release["contractManifest"]["sha256"], actual=contract_digest)
    try:
        contract_value = strict_json_bytes(contract_raw, path=CONTRACT_PATH, governed=True)
    except WFError as exc:
        raise WFError("package.contract-invalid", f"contract manifest is invalid: {exc.code}", exit_class=2, path=CONTRACT_PATH, actual=exc.code) from None
    contract = _validate_contract(contract_value)

    listed = {resource["path"]: resource for resource in contract["governedResources"]}
    observed: set[str] = set()
    for scope in contract["governedScopes"]:
        target = skill_root / PurePosixPath(scope["path"])
        if not target.exists():
            if scope["recursive"]:
                raise WFError("package.missing-scope", "governed scope is missing", exit_class=2, path=scope["path"])
            continue
        paths = sorted(target.rglob("*") if scope["recursive"] and target.is_dir() else [target])
        for path in paths:
            if path.is_symlink():
                raise WFError("package.resource-symlink", "governed resources may not be symbolic links", exit_class=2, path=str(path.relative_to(skill_root)))
            if path.is_file():
                observed.add(path.relative_to(skill_root).as_posix())
    unexpected = sorted(observed - set(listed))
    missing = sorted(set(listed) - observed)
    if unexpected:
        raise WFError("package.unlisted-resource", "governed scope contains an unlisted resource", exit_class=2, actual=unexpected)
    if missing:
        raise WFError("package.missing-resource", "listed governed resource is missing", exit_class=2, actual=missing)
    for path in sorted(listed):
        resource_file = skill_root / PurePosixPath(path)
        raw = resource_file.read_bytes()
        digest = sha256_bytes(raw)
        if digest != listed[path]["sha256"]:
            raise WFError("package.resource-digest", "governed resource digest mismatch", exit_class=2, path=path, expected=listed[path]["sha256"], actual=digest)
        if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
            raise WFError("package.resource-text-profile", "governed resource violates UTF-8/LF byte profile", exit_class=2, path=path)
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise WFError("package.resource-text-profile", "governed resource is not well-formed UTF-8", exit_class=2, path=path) from None
        if unicodedata.normalize("NFC", text) != text:
            raise WFError("package.resource-text-profile", "governed resource is not NFC", exit_class=2, path=path)

    release_schema_path = "assets/contract-v1/schemas/release.schema.json"
    release_schema = strict_json_bytes(
        (skill_root / release_schema_path).read_bytes(),
        path=release_schema_path,
        governed=True,
    )
    try:
        release_id_schema = release_schema["properties"]["releaseId"]
        release_status_schema = release_schema["properties"]["status"]
        release_adapters_schema = release_schema["properties"]["adapters"]
    except (KeyError, TypeError):
        raise WFError(
            "package.release-schema",
            "release schema does not define the release identifier constraint",
            exit_class=2,
            path=release_schema_path,
        ) from None
    expected_release_schema = {
        "type": "string",
        "pattern": r"^v1-candidate-revision-[1-9][0-9]*$",
    }
    expected_status_schema = {"enum": ["unactivated-candidate", "unactivated-frozen", "activated-frozen"]}
    adapter_item_properties = release_adapters_schema.get("items", {}).get("properties", {}) if isinstance(release_adapters_schema, dict) else {}
    schema_agrees = (
        release_id_schema == expected_release_schema
        and release_status_schema == expected_status_schema
        and release_adapters_schema.get("type") == "array"
        and release_adapters_schema.get("minItems") == 1
        and adapter_item_properties.get("id", {}).get("pattern") == r"^[a-z0-9]+(?:-[a-z0-9]+)*-v1$"
        and adapter_item_properties.get("path", {}).get("pattern") == r"^scripts/adapters/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:py|mjs|ps1)$"
    )
    if not schema_agrees or not re.fullmatch(expected_release_schema["pattern"], release["releaseId"]):
        raise WFError(
            "package.release-schema",
            "release schema and release descriptor identities disagree",
            exit_class=2,
            path=release_schema_path,
            expected=expected_release_schema,
            actual=release_id_schema,
        )
    return {
        "skillRoot": skill_root,
        "release": release,
        "releaseDigest": sha256_bytes(release_raw),
        "contract": contract,
        "contractDigest": contract_digest,
        "adapterDigest": adapter_digest,
    }


def run_known_answers(package: dict[str, Any]) -> dict[str, Any]:
    skill_root: Path = package["skillRoot"]
    kat_path = skill_root / "assets/contract-v1/known-answer.json"
    kat = strict_json_bytes(kat_path.read_bytes(), path="assets/contract-v1/known-answer.json", governed=True)
    obj = _expect_object(kat, "/", exit_class=2)
    _closed(obj, ("format", "schemaVersion", "canonicalJson", "sha256", "nfc", "portablePaths"), "/", exit_class=2)
    _expect_literal(obj["format"], "wayfinder-known-answer", "/format", "probe.known-answer-format", exit_class=2)
    _expect_literal(obj["schemaVersion"], 1, "/schemaVersion", "probe.known-answer-version", exit_class=2)
    count = 0
    for vector in obj["canonicalJson"]:
        if canonical_json(vector["input"]) != vector["expected"]:
            raise WFError("probe.known-answer", "canonical JSON known-answer failed", exit_class=2, field="/canonicalJson")
        count += 1
    for vector in obj["sha256"]:
        raw = bytes(vector["utf8"])
        if sha256_bytes(raw) != vector["expected"]:
            raise WFError("probe.known-answer", "SHA-256 known-answer failed", exit_class=2, field="/sha256")
        count += 1
    for vector in obj["nfc"]:
        raw = "".join(chr(point) for point in vector["codePoints"])
        if unicodedata.normalize("NFC", raw) != vector["expected"]:
            raise WFError("probe.known-answer", "NFC known-answer failed", exit_class=2, field="/nfc")
        count += 1
    for vector in obj["portablePaths"]:
        accepted = True
        try:
            portable_path(vector["value"], "/portablePaths", allow_dot=vector.get("allowDot", False), exit_class=2)
        except WFError:
            accepted = False
        if accepted != vector["accepted"]:
            raise WFError("probe.known-answer", "portable path known-answer failed", exit_class=2, field="/portablePaths", actual=vector["value"])
        count += 1
    return {"passed": True, "count": count, "vectorsDigest": sha256_bytes(kat_path.read_bytes())}


def command_probe() -> dict[str, Any]:
    if sys.version_info < (3, 11):
        raise WFError(
            "probe.runtime-version",
            "Python 3.11 or newer is required by the candidate adapter contract",
            exit_class=2,
            expected=">=3.11",
            actual=platform.python_version(),
        )
    package = verify_package()
    known_answers = run_known_answers(package)
    resources = [
        {"path": item["path"], "role": item["role"], "sha256": item["sha256"]}
        for item in package["contract"]["governedResources"]
    ]
    return {
        "adapter": {"id": ADAPTER_ID, "path": ADAPTER_PATH, "sha256": package["adapterDigest"]},
        "contract": {
            "version": CONTRACT_VERSION,
            "releaseId": package["release"]["releaseId"],
            "status": package["release"]["status"],
            "releaseDescriptor": RELEASE_PATH,
            "releaseSha256": package["releaseDigest"],
            "manifest": CONTRACT_PATH,
            "manifestSha256": package["contractDigest"],
            "resources": resources,
        },
        "deterministic": {
            "knownAnswers": known_answers,
            "capabilities": [
                "canonical-json-integer-subset",
                "document-catalog-v1",
                "document-index-v1",
                "document-render-v1",
                "initialize-apply-v1",
                "initialize-plan-v1",
                "initialize-recover-v1",
                "nfc",
                "record-validation-v1",
                "sha256",
                "source-inventory-v1",
                "strict-json",
                "symlink-inspection",
                "utf8-strict",
            ],
        },
        "environment": {
            "pythonImplementation": platform.python_implementation(),
            "pythonVersion": platform.python_version(),
            "platform": platform.platform(),
            "filesystemEncoding": sys.getfilesystemencoding(),
            "executable": str(Path(sys.executable).resolve()),
        },
    }


def _manifest_at(directory: Path) -> Path | None:
    control = directory / ".wayfinder"
    try:
        control_mode = control.lstat().st_mode
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(control_mode):
        raise WFError("discover.control-symlink", ".wayfinder may not be a symbolic link", exit_class=4, path=str(control))
    if not stat.S_ISDIR(control_mode):
        return None
    manifest = control / "manifest.json"
    try:
        manifest_mode = manifest.lstat().st_mode
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(manifest_mode):
        raise WFError("discover.manifest-symlink", "manifest.json may not be a symbolic link", exit_class=4, path=str(manifest))
    if not stat.S_ISREG(manifest_mode):
        raise WFError("discover.manifest-type", "manifest.json must be a regular file", exit_class=4, path=str(manifest))
    return manifest


def _git_boundary(start: Path) -> Path | None:
    current = start
    while True:
        marker = current / ".git"
        try:
            mode = marker.lstat().st_mode
        except FileNotFoundError:
            mode = 0
        if mode and (stat.S_ISDIR(mode) or stat.S_ISREG(mode) or stat.S_ISLNK(mode)):
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def command_discover(workspace_root_arg: str | None, start_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is not None and start_arg is not None:
        raise WFError("command.conflicting-arguments", "--workspace-root and --start are mutually exclusive", exit_class=2)
    if workspace_root_arg is not None:
        supplied = Path(workspace_root_arg)
        if not supplied.exists() or not supplied.is_dir():
            raise WFError("discover.workspace-root", "explicit workspace root must be an existing directory", exit_class=3, path=str(supplied))
        workspace = supplied.resolve(strict=True)
        manifest_file = _manifest_at(workspace)
        if manifest_file is None:
            raise WFError("discover.manifest-not-found", "explicit workspace root has no .wayfinder/manifest.json", exit_class=3, path=str(workspace))
        mode = "explicit"
        start = workspace
        boundary = _git_boundary(workspace)
    else:
        supplied = Path(start_arg) if start_arg is not None else Path.cwd()
        if not supplied.exists():
            raise WFError("discover.start-not-found", "discovery start path does not exist", exit_class=3, path=str(supplied))
        physical = supplied.resolve(strict=True)
        if physical.is_file():
            supplied = physical.parent
        elif physical.is_dir():
            supplied = physical
        else:
            raise WFError("discover.start-type", "discovery start must be a directory or regular file", exit_class=3, path=str(supplied))
        start = supplied.resolve(strict=True)
        boundary = _git_boundary(start)
        current = start
        manifest_file = None
        while True:
            manifest_file = _manifest_at(current)
            if manifest_file is not None:
                break
            if boundary is not None and current == boundary:
                break
            if current.parent == current:
                break
            current = current.parent
        if manifest_file is None:
            raise WFError("discover.manifest-not-found", "no Wayfinder manifest exists within the discovery boundary", exit_class=3, path=str(start))
        workspace = manifest_file.parent.parent
        mode = "upward"

    try:
        manifest_raw = manifest_file.read_bytes()
    except OSError as exc:
        raise WFError("discover.manifest-read", "manifest cannot be read", exit_class=4, path=str(manifest_file), actual=str(exc)) from None
    parsed = strict_json_bytes(manifest_raw, path=str(manifest_file))
    validated = validate_manifest(parsed, workspace)
    return {
        "discovery": {
            "mode": mode,
            "start": str(start),
            "gitBoundary": str(boundary) if boundary is not None else None,
        },
        "workspace": validated["paths"],
        "manifestPath": str(manifest_file),
        "manifest": validated["manifest"],
    }


def source_path(value: Any, field: str, *, exit_class: int = 2) -> str:
    """Validate an NFC workspace-relative source path without imposing managed-path ASCII."""
    if not isinstance(value, str):
        raise WFError("json.type", "source path must be a string", exit_class=exit_class, field=field, expected="string")
    if unicodedata.normalize("NFC", value) != value:
        raise WFError("text.non-nfc", "source path is not Unicode NFC", exit_class=exit_class, field=field)
    if not value or value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value):
        raise WFError("path.absolute", "source path must be workspace-relative", exit_class=exit_class, field=field, actual=value)
    if "\\" in value:
        raise WFError("path.backslash", "source paths use forward slashes", exit_class=exit_class, field=field, actual=value)
    if "\x00" in value:
        raise WFError("path.nul", "NUL is forbidden in source paths", exit_class=exit_class, field=field)
    parts = value.split("/")
    if any(part == "" for part in parts):
        raise WFError("path.empty-segment", "empty source path segments are forbidden", exit_class=exit_class, field=field, actual=value)
    if any(part == "." for part in parts):
        raise WFError("path.dot-segment", "dot source path segments are forbidden", exit_class=exit_class, field=field, actual=value)
    if any(part == ".." for part in parts):
        raise WFError("path.traversal", "parent traversal is forbidden", exit_class=exit_class, field=field, actual=value)
    return value


def _read_control_file(path_text: str, label: str) -> tuple[Path, bytes]:
    path = Path(path_text)
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise WFError(f"inventory.{label}-read", f"{label} file cannot be inspected", exit_class=2, path=str(path), actual=str(exc)) from None
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise WFError(f"inventory.{label}-type", f"{label} must be a non-symbolic regular file", exit_class=2, path=str(path))
    try:
        return path, path.read_bytes()
    except OSError as exc:
        raise WFError(f"inventory.{label}-read", f"{label} file cannot be read", exit_class=2, path=str(path), actual=str(exc)) from None


def _positive_limit(value: Any, field: str, maximum: int) -> int:
    if type(value) is not int:
        raise WFError("json.type", "inventory limit must be an integer", exit_class=2, field=field, expected="integer")
    if value < 1 or value > maximum:
        raise WFError("inventory.limit-value", "inventory limit is outside the supported range", exit_class=2, field=field, expected=f"1..{maximum}", actual=value)
    return value


def _validate_inventory_request(value: Any) -> dict[str, Any]:
    request = _expect_object(value, "/", exit_class=2)
    _closed(request, ("format", "schemaVersion", "selections", "targetRoots", "limits"), "/", exit_class=2)
    _expect_literal(request["format"], "wayfinder-source-inventory-request", "/format", "inventory.request-format", exit_class=2)
    _expect_literal(request["schemaVersion"], 1, "/schemaVersion", "inventory.unsupported-version", exit_class=2)
    raw_selections = _expect_array(request["selections"], "/selections", exit_class=2)
    if not raw_selections:
        raise WFError("inventory.empty-selection", "at least one source selection is required", exit_class=2, field="/selections")
    selections: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_selections):
        selected = source_path(raw, f"/selections/{index}")
        key = selected
        if key in seen:
            raise WFError("inventory.duplicate-selection", "source selection is duplicated", exit_class=2, field=f"/selections/{index}", actual=selected)
        seen.add(key)
        selections.append(selected)
    target_roots: list[str] = []
    target_seen: set[str] = set()
    for index, raw in enumerate(_expect_array(request["targetRoots"], "/targetRoots", exit_class=2)):
        target = source_path(raw, f"/targetRoots/{index}")
        key = target
        if key in target_seen:
            raise WFError("inventory.duplicate-target-root", "target root is duplicated", exit_class=2, field=f"/targetRoots/{index}", actual=target)
        target_seen.add(key)
        target_roots.append(target)
    limits = _expect_object(request["limits"], "/limits", exit_class=2)
    _closed(limits, ("maxEntries", "maxFileBytes", "maxTotalBytes", "maxDepth"), "/limits", exit_class=2)
    validated_limits = {
        "maxEntries": _positive_limit(limits["maxEntries"], "/limits/maxEntries", 1_000_000),
        "maxFileBytes": _positive_limit(limits["maxFileBytes"], "/limits/maxFileBytes", MAX_EXACT_INTEGER),
        "maxTotalBytes": _positive_limit(limits["maxTotalBytes"], "/limits/maxTotalBytes", MAX_EXACT_INTEGER),
        "maxDepth": _positive_limit(limits["maxDepth"], "/limits/maxDepth", 1_024),
    }
    return {
        "format": request["format"],
        "schemaVersion": 1,
        "selections": sorted(selections, key=lambda item: item.encode("utf-8")),
        "targetRoots": sorted(target_roots, key=lambda item: item.encode("utf-8")),
        "limits": validated_limits,
    }


def _relative_kind(path: Path) -> str:
    info = path.lstat()
    mode = info.st_mode
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISSOCK(mode):
        return "unsupported-file"
    if os.name == "nt" and getattr(info, "st_reparse_tag", 0):
        return "unsupported-file"
    if stat.S_ISREG(mode):
        return "regular-file"
    if stat.S_ISDIR(mode):
        return "directory"
    return "unsupported-file"


def _bounded_selection_path(workspace: Path, relative: str) -> Path:
    current = workspace
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            raise WFError("inventory.selection-missing", "source selection does not exist", exit_class=3, path=relative) from None
        except OSError as exc:
            raise WFError("inventory.selection-read", "source selection cannot be inspected", exit_class=3, path=relative, actual=str(exc)) from None
        if index < len(parts) - 1 and stat.S_ISLNK(mode):
            raise WFError("inventory.selection-symlink-component", "source selection crosses a symbolic-link directory", exit_class=3, path=relative)
    return current


def _is_within_source(child: str, parent: str) -> bool:
    child_parts = tuple(part.casefold() for part in PurePosixPath(child).parts)
    parent_parts = tuple(part.casefold() for part in PurePosixPath(parent).parts)
    return len(child_parts) >= len(parent_parts) and child_parts[:len(parent_parts)] == parent_parts


def _exclusion(path: str, kind: str, target_roots: list[str], *, explicit_regular: bool) -> str | None:
    parts = PurePosixPath(path).parts
    lower_parts = tuple(part.casefold() for part in parts)
    name = parts[-1]
    lower_name = name.casefold()
    if any(part in VCS_ADMIN_NAMES for part in lower_parts):
        return "vcs-administration"
    if ".wayfinder" in lower_parts:
        return "wayfinder-state"
    if any(_is_within_source(path, root) for root in target_roots):
        return "declared-target-root"
    if any(fnmatch.fnmatchcase(lower_name, pattern) for pattern in SECRET_PATTERNS):
        return "secret-safety"
    if kind == "symlink":
        return "symbolic-link"
    if kind == "unsupported-file":
        return "unsupported-special-file"
    if not explicit_regular:
        if kind == "directory" and lower_name in DEPENDENCY_DIRECTORY_NAMES:
            return "dependency-directory"
        if kind == "directory" and lower_name in BUILD_DIRECTORY_NAMES:
            return "build-output-directory"
        if kind == "regular-file" and lower_name.endswith(ARCHIVE_SUFFIXES):
            return "archive-file"
    return None


def _read_regular_file(path: Path, expected: os.stat_result) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise WFError("inventory.source-read", "source regular file cannot be opened safely", exit_class=3, path=str(path), actual=str(exc)) from None
    try:
        observed = os.fstat(descriptor)
        if not stat.S_ISREG(observed.st_mode):
            raise WFError("inventory.source-changed", "source type changed during inventory", exit_class=3, path=str(path))
        if (observed.st_dev, observed.st_ino, observed.st_size) != (expected.st_dev, expected.st_ino, expected.st_size):
            raise WFError("inventory.source-changed", "source changed during inventory", exit_class=3, path=str(path))
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
        final = os.fstat(descriptor)
        if final.st_size != len(raw) or final.st_mtime_ns != observed.st_mtime_ns:
            raise WFError("inventory.source-changed", "source changed while it was read", exit_class=3, path=str(path))
        return raw
    finally:
        os.close(descriptor)


def _markdown_outline(text: str) -> dict[str, Any]:
    headings: list[dict[str, Any]] = []
    fence: tuple[str, int] | None = None
    for line_number, line in enumerate(text.splitlines(), 1):
        fence_match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not fence_match.group(2).strip():
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(.*)$", line)
        if not match:
            continue
        content = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip(" \t")
        if not content:
            continue
        headings.append({"level": len(match.group(1)), "text": content, "line": line_number})
    h1 = next((item["text"] for item in headings if item["level"] == 1), None)
    return {"h1": h1, "outline": headings}


def build_inventory(workspace: Path, request: dict[str, Any]) -> dict[str, Any]:
    workspace = workspace.resolve(strict=True)
    target_roots = request["targetRoots"]
    limits = request["limits"]
    entries: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    explicit_regulars: set[str] = set()

    selected: list[tuple[str, Path, str]] = []
    for selection in request["selections"]:
        path = _bounded_selection_path(workspace, selection)
        kind = _relative_kind(path)
        if kind == "regular-file":
            explicit_regulars.add(selection)
        selected.append((selection, path, kind))

    def add(relative: str, path: Path, depth: int) -> None:
        nonlocal total_bytes
        source_path(relative, "/filesystem/path", exit_class=3)
        path = _bounded_selection_path(workspace, relative)
        try:
            relative.encode("utf-8", "strict")
        except UnicodeEncodeError:
            raise WFError("inventory.path-encoding", "source path is not representable as strict UTF-8", exit_class=3, path=relative) from None
        if unicodedata.normalize("NFC", relative) != relative:
            raise WFError("text.non-nfc", "filesystem source path is not Unicode NFC", exit_class=3, path=relative)
        key = relative
        if key in entries:
            return
        if depth > limits["maxDepth"]:
            raise WFError("inventory.limit-depth", "source traversal exceeded maxDepth", exit_class=3, path=relative, expected=limits["maxDepth"], actual=depth)
        if len(entries) >= limits["maxEntries"]:
            raise WFError("inventory.limit-entries", "source traversal exceeded maxEntries", exit_class=3, expected=limits["maxEntries"])
        try:
            info = path.lstat()
        except OSError as exc:
            raise WFError("inventory.source-read", "source entry cannot be inspected", exit_class=3, path=relative, actual=str(exc)) from None
        kind = _relative_kind(path)
        explicit_regular = kind == "regular-file" and key in explicit_regulars
        exclusion = _exclusion(relative, kind, target_roots, explicit_regular=explicit_regular)
        entry: dict[str, Any] = {
            "path": relative,
            "type": kind,
            "included": exclusion is None,
            "exclusion": exclusion,
            "byteLength": None,
            "sha256": None,
            "content": None,
            "markdown": None,
        }
        if kind == "regular-file":
            if info.st_size > MAX_EXACT_INTEGER:
                raise WFError("inventory.limit-file-bytes", "source file size exceeds the version-1 numeric range", exit_class=3, path=relative, expected=MAX_EXACT_INTEGER, actual=info.st_size)
            entry["byteLength"] = info.st_size
            if exclusion is None:
                if info.st_size > limits["maxFileBytes"]:
                    raise WFError("inventory.limit-file-bytes", "source file exceeds maxFileBytes", exit_class=3, path=relative, expected=limits["maxFileBytes"], actual=info.st_size)
                if total_bytes + info.st_size > limits["maxTotalBytes"]:
                    raise WFError("inventory.limit-total-bytes", "included sources exceed maxTotalBytes", exit_class=3, path=relative, expected=limits["maxTotalBytes"], actual=total_bytes + info.st_size)
                raw = _read_regular_file(path, info)
                after = _bounded_selection_path(workspace, relative).lstat()
                if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns):
                    raise WFError("inventory.source-changed", "source path changed around its inventory read", exit_class=3, path=relative)
                total_bytes += len(raw)
                entry["sha256"] = sha256_bytes(raw)
                try:
                    text = raw.decode("utf-8", "strict")
                    entry["content"] = "strict-utf8"
                except UnicodeDecodeError:
                    text = None
                    entry["content"] = "opaque-bytes"
                if relative.casefold().endswith(".md") and text is not None:
                    if unicodedata.normalize("NFC", text) == text:
                        entry["markdown"] = {"accepted": True, **_markdown_outline(text)}
                    else:
                        entry["markdown"] = {"accepted": False, "reason": "non-nfc-text", "h1": None, "outline": []}
        entries[key] = entry
        if kind == "directory" and exclusion is None:
            try:
                children = sorted(os.scandir(path), key=lambda child: child.name.encode("utf-8", "strict"))
            except (OSError, UnicodeEncodeError) as exc:
                raise WFError("inventory.directory-read", "source directory cannot be enumerated deterministically", exit_class=3, path=relative, actual=str(exc)) from None
            for child in children:
                child_relative = f"{relative}/{child.name}"
                add(child_relative, Path(child.path), depth + 1)

    for relative, path, kind in selected:
        add(relative, path, 0)

    ordered_entries = sorted(entries.values(), key=lambda item: item["path"].encode("utf-8"))
    digests: dict[str, list[str]] = {}
    for entry in ordered_entries:
        if entry["included"] and entry["type"] == "regular-file":
            digests.setdefault(entry["sha256"], []).append(entry["path"])
    duplicate_groups = [
        {"sha256": digest, "paths": sorted(paths, key=lambda item: item.encode("utf-8"))}
        for digest, paths in digests.items() if len(paths) > 1
    ]
    duplicate_groups.sort(key=lambda item: (item["sha256"], [path.encode("utf-8") for path in item["paths"]]))
    counts: dict[str, int] = {name: 0 for name in ("regular-file", "directory", "symlink", "unsupported-file")}
    for entry in ordered_entries:
        counts[entry["type"]] += 1
    inventory = {
        "format": "wayfinder-source-inventory",
        "schemaVersion": 1,
        "selections": [
            {"path": relative, "type": kind} for relative, _path, kind in sorted(selected, key=lambda item: item[0].encode("utf-8"))
        ],
        "targetRoots": target_roots,
        "limits": limits,
        "entries": ordered_entries,
        "duplicateGroups": duplicate_groups,
        "summary": {
            "entries": len(ordered_entries),
            "includedRegularFiles": sum(entry["included"] and entry["type"] == "regular-file" for entry in ordered_entries),
            "excluded": sum(not entry["included"] for entry in ordered_entries),
            "totalIncludedBytes": total_bytes,
            "byType": counts,
            "duplicateGroups": len(duplicate_groups),
        },
    }
    return inventory


def _string_list(value: Any, field: str, pattern: re.Pattern[str] | None = None) -> list[str]:
    values = _expect_array(value, field, exit_class=2)
    observed: set[str] = set()
    result: list[str] = []
    for index, item in enumerate(values):
        if not isinstance(item, str) or not item or (pattern is not None and not pattern.fullmatch(item)):
            raise WFError("intake.identifier", "intake identifier is invalid", exit_class=2, field=f"{field}/{index}", actual=item)
        if item in observed:
            raise WFError("intake.duplicate-identifier", "intake identifier is duplicated", exit_class=2, field=f"{field}/{index}", actual=item)
        observed.add(item)
        result.append(item)
    return result


def validate_intake_ledger(value: Any, inventory: dict[str, Any], inventory_digest: str, workspace: Path) -> dict[str, Any]:
    ledger = _expect_object(value, "/", exit_class=2)
    _closed(ledger, ("format", "schemaVersion", "inventorySha256", "sources"), "/", exit_class=2)
    _expect_literal(ledger["format"], "wayfinder-intake-ledger", "/format", "intake.format", exit_class=2)
    _expect_literal(ledger["schemaVersion"], 1, "/schemaVersion", "intake.unsupported-version", exit_class=2)
    if not isinstance(ledger["inventorySha256"], str) or not HEX_RE.fullmatch(ledger["inventorySha256"]):
        raise WFError("intake.inventory-digest", "inventorySha256 must be lowercase 64-hex", exit_class=2, field="/inventorySha256")
    by_path = {entry["path"]: entry for entry in inventory["entries"]}
    sources: list[dict[str, Any]] = []
    seen: set[str] = set()
    dispositions = {"incorporate", "reference", "preserve-out-of-scope", "unresolved"}
    for index, raw in enumerate(_expect_array(ledger["sources"], "/sources", exit_class=2)):
        pointer = f"/sources/{index}"
        item = _expect_object(raw, pointer, exit_class=2)
        fields = ("path", "sha256", "byteLength", "disposition", "reason", "targetIds", "transformationNote", "evidenceKeys", "questionIds")
        _closed(item, fields, pointer, exit_class=2)
        path = source_path(item["path"], f"{pointer}/path")
        if path in seen:
            raise WFError("intake.duplicate-source", "intake source path is duplicated", exit_class=2, field=f"{pointer}/path", actual=path)
        seen.add(path)
        inventory_entry = by_path.get(path)
        if inventory_entry is None or inventory_entry["type"] != "regular-file" or not inventory_entry["included"]:
            if ledger["inventorySha256"] != inventory_digest:
                raise WFError("intake.source-stale", "ledger source is missing or changed in the current inventory", exit_class=3, path=path)
            raise WFError("intake.unknown-source", "intake source is not an included regular inventory file", exit_class=2, field=f"{pointer}/path", actual=path)
        if not isinstance(item["sha256"], str) or not HEX_RE.fullmatch(item["sha256"]):
            raise WFError("intake.sha256", "source sha256 must be lowercase 64-hex", exit_class=2, field=f"{pointer}/sha256")
        if type(item["byteLength"]) is not int or item["byteLength"] < 0:
            raise WFError("json.type", "source byteLength must be a non-negative integer", exit_class=2, field=f"{pointer}/byteLength")
        if item["sha256"] != inventory_entry["sha256"] or item["byteLength"] != inventory_entry["byteLength"]:
            raise WFError("intake.source-stale", "ledger source identity differs from current source bytes", exit_class=3, path=path)
        disposition = item["disposition"]
        if disposition not in dispositions:
            raise WFError("intake.disposition", "source disposition is not registered", exit_class=2, field=f"{pointer}/disposition", actual=disposition)
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise WFError("intake.reason", "source disposition requires a non-empty review reason", exit_class=2, field=f"{pointer}/reason")
        targets = _string_list(item["targetIds"], f"{pointer}/targetIds", DOCUMENT_ID_RE)
        evidence = _string_list(item["evidenceKeys"], f"{pointer}/evidenceKeys", EVIDENCE_KEY_RE)
        questions = _string_list(item["questionIds"], f"{pointer}/questionIds", QUESTION_ID_RE)
        note = item["transformationNote"]
        if note is not None and (not isinstance(note, str) or not note.strip()):
            raise WFError("intake.transformation-note", "transformationNote must be null or non-empty text", exit_class=2, field=f"{pointer}/transformationNote")
        if disposition == "incorporate" and (not targets or note is None):
            raise WFError("intake.incorporate-fields", "incorporate requires targetIds and a transformationNote", exit_class=2, field=pointer)
        if disposition == "reference" and (targets or note is not None or not evidence):
            raise WFError("intake.reference-fields", "reference requires evidenceKeys and forbids targets or transformation", exit_class=2, field=pointer)
        if disposition == "preserve-out-of-scope" and (targets or evidence or questions or note is not None):
            raise WFError("intake.preserve-fields", "preserve-out-of-scope forbids mappings, questions, and transformation", exit_class=2, field=pointer)
        if disposition == "unresolved" and (targets or evidence or note is not None or not questions):
            raise WFError("intake.unresolved-fields", "unresolved requires questionIds and forbids targets, evidence, and transformation", exit_class=2, field=pointer)
        current_path = workspace / PurePosixPath(path)
        try:
            info = current_path.lstat()
        except OSError:
            raise WFError("intake.source-stale", "ledger source is missing or unreadable", exit_class=3, path=path) from None
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise WFError("intake.source-stale", "ledger source is no longer a regular file", exit_class=3, path=path)
        raw_bytes = _read_regular_file(current_path, info)
        if len(raw_bytes) != item["byteLength"] or sha256_bytes(raw_bytes) != item["sha256"]:
            raise WFError("intake.source-stale", "ledger source bytes changed after inventory", exit_class=3, path=path)
        sources.append({field: item[field] for field in fields})
    if ledger["inventorySha256"] != inventory_digest:
        raise WFError("intake.inventory-digest", "ledger is bound to a different inventory", exit_class=3, field="/inventorySha256", expected=inventory_digest, actual=ledger["inventorySha256"])
    sources.sort(key=lambda item: item["path"].encode("utf-8"))
    normalized = {
        "format": "wayfinder-intake-ledger",
        "schemaVersion": 1,
        "inventorySha256": inventory_digest,
        "sources": sources,
    }
    return normalized


def command_inventory(workspace_root_arg: str | None, request_arg: str | None, ledger_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is None or request_arg is None:
        raise WFError("command.arguments", "inventory requires --workspace-root PATH and --request FILE", exit_class=2)
    supplied = Path(workspace_root_arg)
    if not supplied.exists() or not supplied.is_dir():
        raise WFError("inventory.workspace-root", "workspace root must be an existing directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    request_path, request_raw = _read_control_file(request_arg, "request")
    request_value = strict_json_bytes(request_raw, path=str(request_path), exit_class=2)
    request = _validate_inventory_request(request_value)
    inventory = build_inventory(workspace, request)
    inventory_digest = sha256_bytes(canonical_json(inventory).encode("utf-8"))
    data: dict[str, Any] = {
        "inventory": inventory,
        "inventorySha256": inventory_digest,
        "environment": {"workspaceRoot": str(workspace)},
    }
    if ledger_arg is not None:
        ledger_path, ledger_raw = _read_control_file(ledger_arg, "ledger")
        ledger_value = strict_json_bytes(ledger_raw, path=str(ledger_path), exit_class=2)
        normalized = validate_intake_ledger(ledger_value, inventory, inventory_digest, workspace)
        counts = {name: 0 for name in ("incorporate", "reference", "preserve-out-of-scope", "unresolved")}
        for item in normalized["sources"]:
            counts[item["disposition"]] += 1
        data["intake"] = {
            "ledger": normalized,
            "ledgerSha256": sha256_bytes(canonical_json(normalized).encode("utf-8")),
            "dispositionCounts": counts,
            "sourceDigestsRechecked": len(normalized["sources"]),
        }
    return data


def _calendar_date(value: str, field: str, *, exit_class: int = 4) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise WFError("record.date", "date must use exact YYYY-MM-DD", exit_class=exit_class, field=field, actual=value)
    try:
        date.fromisoformat(value)
    except ValueError:
        raise WFError("record.date", "date is not a calendar date", exit_class=exit_class, field=field, actual=value) from None
    return value


def _identifier(value: Any, kind: str, field: str, *, exit_class: int = 4) -> tuple[int, str]:
    pattern = DOCUMENT_ID_RE if kind == "document" else QUESTION_ID_RE
    if not isinstance(value, str) or (match := pattern.fullmatch(value)) is None:
        raise WFError(f"record.{kind}-id", f"{kind} ID is outside the version-1 grammar", exit_class=exit_class, field=field, actual=value)
    ordinal_text, mnemonic = match.groups()
    ordinal = int(ordinal_text)
    if ordinal < 1 or (ordinal < 1000 and len(ordinal_text) != 4) or len(mnemonic) > 48:
        raise WFError(f"record.{kind}-id", f"{kind} ID ordinal or mnemonic is outside the version-1 boundary", exit_class=exit_class, field=field, actual=value)
    return ordinal, mnemonic


def _markdown_text(raw: bytes, path: str) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise WFError("text.bom", "UTF-8 BOM is forbidden", exit_class=4, path=path)
    if b"\r" in raw or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise WFError("text.newline", "authored Markdown requires LF and exactly one terminal LF", exit_class=4, path=path)
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise WFError("text.invalid-utf8", "authored Markdown is not strict UTF-8", exit_class=4, path=path, actual=exc.start) from None
    if unicodedata.normalize("NFC", text) != text:
        raise WFError("text.non-nfc", "authored Markdown is not Unicode NFC", exit_class=4, path=path)
    if any(line.endswith((" ", "\t")) for line in text.splitlines()):
        raise WFError("text.trailing-whitespace", "trailing whitespace is forbidden", exit_class=4, path=path)
    return text


def _parse_field_lines(lines: list[str], allowed: tuple[str, ...], path: str, context: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines, 1):
        match = FIELD_RE.fullmatch(line)
        if match is None:
            raise WFError(f"{context}.field-syntax", "field line does not match the exact grammar", exit_class=4, path=path, actual=line)
        name, value = match.groups()
        if name not in allowed:
            raise WFError(f"{context}.unknown-field", "field is not registered", exit_class=4, path=path, field=name)
        if name in seen and context not in {"relationship", "question"}:
            raise WFError(f"{context}.duplicate-field", "field may not be repeated", exit_class=4, path=path, field=name)
        seen.add(name)
        result.append((name, value))
    return result


def _extract_blocks(lines: list[str], start: str, end: str, path: str, code: str) -> list[tuple[int, int, list[str]]]:
    blocks: list[tuple[int, int, list[str]]] = []
    active: int | None = None
    for index, line in enumerate(lines):
        if line == start:
            if active is not None:
                raise WFError(f"{code}.nested", "nested blocks are forbidden", exit_class=4, path=path, actual=index + 1)
            active = index
        elif line == end:
            if active is None:
                raise WFError(f"{code}.delimiter", "closing delimiter has no opener", exit_class=4, path=path, actual=index + 1)
            blocks.append((active, index, lines[active + 1:index]))
            active = None
    if active is not None:
        raise WFError(f"{code}.delimiter", "block is missing its exact closing delimiter", exit_class=4, path=path, actual=active + 1)
    return blocks


def _parse_link(value: str, field: str, path: str) -> dict[str, str]:
    match = LINK_RE.fullmatch(value)
    if match is None:
        raise WFError("relationship.link", "typed target must be one Markdown link", exit_class=4, path=path, field=field, actual=value)
    label, destination = match.groups()
    _identifier(label, "document", field)
    if not destination or destination.startswith(("/", "\\")) or "\\" in destination or "#" in destination or "?" in destination:
        raise WFError("relationship.destination", "typed target must use a normalized relative Markdown path", exit_class=4, path=path, field=field, actual=destination)
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(path), destination))
    if normalized.startswith("../") or normalized == ".." or not normalized.endswith(".md"):
        raise WFError("relationship.destination", "typed target escapes the record or is not Markdown", exit_class=4, path=path, field=field, actual=destination)
    canonical_destination = posixpath.relpath(normalized, posixpath.dirname(path) or ".")
    if canonical_destination != destination:
        raise WFError("relationship.destination", "typed target path is not normalized", exit_class=4, path=path, field=field, expected=canonical_destination, actual=destination)
    return {"id": label, "destination": destination, "path": normalized}


def _sections(block: list[str], path: str, code: str) -> dict[str, str]:
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in block:
        if line.startswith("#### "):
            current = line[5:]
            if not current or current in found:
                raise WFError(f"{code}.section", "section heading is empty or duplicated", exit_class=4, path=path, actual=current)
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {name: "\n".join(value).strip() for name, value in found.items()}


def _parse_question(block: list[str], path: str) -> dict[str, Any]:
    if len(block) < 8:
        raise WFError("question.shape", "question block is incomplete", exit_class=4, path=path)
    anchor = re.fullmatch(r'<a id="(wfq-[^"]+)"></a>', block[0])
    if anchor is None or not block[1].startswith("### "):
        raise WFError("question.anchor", "question requires an exact ID anchor followed by H3", exit_class=4, path=path)
    title = block[1][4:]
    field_end = next((index for index in range(2, len(block)) if block[index].startswith("#### ")), len(block))
    field_lines = [line for line in block[2:field_end] if line]
    pairs = _parse_field_lines(field_lines, ("ID", "State", "Raised", "Scope", "Applies-To", "Addressed-By", "Resolved-By", "Resolution-Date"), path, "question")
    scalar: dict[str, str] = {}
    links: dict[str, list[dict[str, str]]] = {name: [] for name in ("Applies-To", "Addressed-By", "Resolved-By")}
    ordered_names = [name for name, _ in pairs]
    rank = {name: index for index, name in enumerate(("ID", "State", "Raised", "Scope", "Applies-To", "Addressed-By", "Resolved-By", "Resolution-Date"))}
    if [rank[name] for name in ordered_names] != sorted(rank[name] for name in ordered_names):
        raise WFError("question.field-order", "question fields are outside canonical order", exit_class=4, path=path)
    for name, value in pairs:
        if name in links:
            link = _parse_link(value, name, path)
            if link in links[name]:
                raise WFError("question.duplicate-edge", "question edge is duplicated", exit_class=4, path=path, field=name)
            links[name].append(link)
        elif name in scalar:
            raise WFError("question.duplicate-field", "question scalar field is duplicated", exit_class=4, path=path, field=name)
        else:
            scalar[name] = value
    for required in ("ID", "State", "Raised"):
        if required not in scalar:
            raise WFError("question.missing-field", "question is missing a required field", exit_class=4, path=path, field=required)
    ordinal, _ = _identifier(scalar["ID"], "question", "ID")
    if anchor.group(1) != scalar["ID"]:
        raise WFError("question.anchor", "question anchor must equal its ID", exit_class=4, path=path, expected=scalar["ID"], actual=anchor.group(1))
    state = scalar["State"]
    if state not in QUESTION_STATES:
        raise WFError("question.state", "question state is not registered", exit_class=4, path=path, actual=state)
    raised = _calendar_date(scalar["Raised"], "Raised")
    if scalar.get("Scope") not in {None, "Record-Wide"}:
        raise WFError("question.scope", "Scope, when present, must be Record-Wide", exit_class=4, path=path)
    if not links["Applies-To"] and scalar.get("Scope") != "Record-Wide":
        raise WFError("question.scope", "question requires Applies-To or explicit Record-Wide scope", exit_class=4, path=path)
    if state == "Resolved":
        if not links["Resolved-By"] or "Resolution-Date" not in scalar:
            raise WFError("question.resolution", "resolved question requires Resolution-Date and Resolved-By", exit_class=4, path=path)
        _calendar_date(scalar["Resolution-Date"], "Resolution-Date")
    elif links["Resolved-By"] or "Resolution-Date" in scalar:
        raise WFError("question.resolution", "resolution fields are allowed only for Resolved", exit_class=4, path=path)
    sections = _sections(block[field_end:], path, "question")
    required_sections = {
        "Open": {"Why it matters", "Next step", "History"},
        "Investigating": {"Why it matters", "Current activity", "History"},
        "Deferred": {"Why it matters", "Deferral reason", "Revisit trigger", "History"},
        "Resolved": {"Why it matters", "Resolution", "History"},
        "Retired": {"Why it matters", "Retirement reason", "History"},
    }[state]
    if set(sections) != required_sections or any(not sections[name] for name in required_sections):
        raise WFError("question.conditional-content", "question sections do not match its state", exit_class=4, path=path, expected=sorted(required_sections), actual=sorted(sections))
    history_lines = sections["History"].splitlines()
    history: list[dict[str, str]] = []
    prior = "None"
    allowed = {
        "None": set(QUESTION_STATES),
        "Open": {"Investigating", "Deferred", "Resolved", "Retired"},
        "Investigating": {"Open", "Deferred", "Resolved", "Retired"},
        "Deferred": {"Open", "Investigating", "Resolved", "Retired"},
        "Resolved": {"Open"},
        "Retired": set(),
    }
    for line in history_lines:
        match = HISTORY_RE.fullmatch(line)
        if match is None:
            raise WFError("question.history-syntax", "history line is malformed", exit_class=4, path=path, actual=line)
        event_date, before, after, reason = match.groups()
        _calendar_date(event_date, "History")
        if before != prior or after not in allowed[before] or not reason.strip():
            raise WFError("question.transition", "question history contains an invalid transition", exit_class=4, path=path, actual=line)
        if before == "Resolved" and after == "Open" and "reopen" not in reason.casefold():
            raise WFError("question.reopen-reason", "reopening must state a reopen reason", exit_class=4, path=path, actual=reason)
        prior = after
        history.append({"date": event_date, "from": before, "to": after, "reason": reason})
    if not history or history[0]["date"] != raised or prior != state:
        raise WFError("question.history-state", "history must begin on Raised and end at current State", exit_class=4, path=path)
    return {"id": scalar["ID"], "ordinal": ordinal, "anchor": anchor.group(1), "title": title, "state": state, "raised": raised, "scope": scalar.get("Scope"), "links": links, "sections": sections, "history": history}


def _parse_source(block: list[str], path: str) -> dict[str, Any]:
    if len(block) < 8:
        raise WFError("source.shape", "source block is incomplete", exit_class=4, path=path)
    anchor = re.fullmatch(r'<a id="(src-[^"]+)"></a>', block[0])
    heading = re.fullmatch(r"### (src-[0-9]{2,}) — (.+)", block[1])
    if anchor is None or heading is None or anchor.group(1) != heading.group(1):
        raise WFError("source.anchor", "source anchor and H3 key must agree", exit_class=4, path=path)
    key_match = EVIDENCE_KEY_RE.fullmatch(anchor.group(1))
    if key_match is None or int(key_match.group(1)) < 1:
        raise WFError("source.key", "source key is outside the version-1 grammar", exit_class=4, path=path)
    field_end = next((index for index in range(2, len(block)) if block[index].startswith("#### ")), len(block))
    pairs = _parse_field_lines([line for line in block[2:field_end] if line], ("Citation", "Original", "Published", "Accessed", "Applicability"), path, "source")
    fields = dict(pairs)
    expected_order = [name for name in ("Citation", "Original", "Published", "Accessed", "Applicability") if name in fields]
    if [name for name, _ in pairs] != expected_order:
        raise WFError("source.field-order", "source fields are outside canonical order", exit_class=4, path=path)
    for required in ("Citation", "Original", "Accessed", "Applicability"):
        if required not in fields:
            raise WFError("source.missing-field", "source is missing a required field", exit_class=4, path=path, field=required)
    _calendar_date(fields["Accessed"], "Accessed")
    if fields["Applicability"] not in {"Direct", "Adjacent", "General"}:
        raise WFError("source.applicability", "source applicability is not registered", exit_class=4, path=path)
    if "Published" in fields:
        _calendar_date(fields["Published"], "Published")
    original = fields["Original"]
    if not (re.fullmatch(r"https://[^\s]+", original) or (not original.startswith(("/", "\\")) and "\\" not in original and posixpath.normpath(original) == original)):
        raise WFError("source.original", "Original must be an HTTPS URL or normalized relative path", exit_class=4, path=path, actual=original)
    sections = _sections(block[field_end:], path, "source")
    if set(sections) != {"Used for", "Limitations"} or any(not value for value in sections.values()):
        raise WFError("source.sections", "source requires nonempty Used for and Limitations sections", exit_class=4, path=path)
    return {"key": anchor.group(1), "ordinal": int(key_match.group(1)), "title": heading.group(2), "fields": fields, "sections": sections}


def parse_document(raw: bytes, path: str) -> dict[str, Any]:
    text = _markdown_text(raw, path)
    lines = text[:-1].split("\n")
    h1s = [(index, line[2:]) for index, line in enumerate(lines) if line.startswith("# ")]
    if len(h1s) != 1 or h1s[0][0] != 0 or not h1s[0][1]:
        raise WFError("document.h1", "document requires exactly one nonempty H1 at line 1", exit_class=4, path=path)
    metadata_blocks = _extract_blocks(lines, "<!-- wayfinder:metadata -->", "<!-- /wayfinder:metadata -->", path, "metadata")
    if len(metadata_blocks) != 1 or metadata_blocks[0][0] != 2:
        raise WFError("metadata.location", "one metadata block must follow H1 and one blank line", exit_class=4, path=path)
    start, end, content = metadata_blocks[0]
    pairs = _parse_field_lines(content, METADATA_ORDER, path, "metadata")
    fields = dict(pairs)
    if [name for name, _ in pairs] != [name for name in METADATA_ORDER if name in fields]:
        raise WFError("metadata.field-order", "metadata fields are outside canonical order", exit_class=4, path=path)
    for required in METADATA_ORDER[:5]:
        if required not in fields:
            raise WFError("metadata.missing-field", "metadata is missing a universal field", exit_class=4, path=path, field=required)
    ordinal, _ = _identifier(fields["ID"], "document", "ID")
    kind = fields["Kind"]
    status = fields["Status"]
    if kind not in KINDS:
        raise WFError("document.kind", "document kind is not registered", exit_class=4, path=path, actual=kind)
    statuses = DECISION_STATUSES if kind == "decision" else LIVING_STATUSES
    if status not in statuses:
        raise WFError("document.status", "status is forbidden for this kind", exit_class=4, path=path, actual=status)
    _calendar_date(fields["Updated"], "Updated")
    if not fields["Summary"].strip():
        raise WFError("metadata.summary", "Summary must be nonempty", exit_class=4, path=path)
    decision_date = fields.get("Decision-Date")
    if kind == "decision" and status in {"Accepted", "Rejected", "Superseded"}:
        if decision_date is None:
            raise WFError("decision.date-required", "decision status requires Decision-Date", exit_class=4, path=path)
        _calendar_date(decision_date, "Decision-Date")
    elif decision_date is not None:
        raise WFError("decision.date-forbidden", "Decision-Date is forbidden for this kind/status", exit_class=4, path=path)
    id_lists: dict[str, list[str]] = {}
    for name in ("Supersedes", "Superseded-By"):
        if name not in fields:
            id_lists[name] = []
            continue
        values = fields[name].split(", ")
        if not values or ", ".join(values) != fields[name]:
            raise WFError("supersession.list", "supersession list uses exact comma-space separation", exit_class=4, path=path, field=name)
        ordinals = [_identifier(value, "document", name)[0] for value in values]
        if len(set(values)) != len(values) or ordinals != sorted(ordinals):
            raise WFError("supersession.order", "supersession IDs must be unique and numerically sorted", exit_class=4, path=path, field=name)
        id_lists[name] = values
    if status == "Superseded" and not id_lists["Superseded-By"]:
        raise WFError("supersession.required", "Superseded status requires Superseded-By", exit_class=4, path=path)
    relationship_blocks = _extract_blocks(lines, "<!-- wayfinder:relationships -->", "<!-- /wayfinder:relationships -->", path, "relationship")
    relationships: list[dict[str, str]] = []
    if relationship_blocks:
        if len(relationship_blocks) != 1 or relationship_blocks[0][0] != end + 2:
            raise WFError("relationship.location", "relationship block must immediately follow metadata and one blank line", exit_class=4, path=path)
        rel_pairs = _parse_field_lines(relationship_blocks[0][2], tuple(RELATION_ORDER), path, "relationship")
        for name, value in rel_pairs:
            link = _parse_link(value, name, path)
            edge = {"relation": name, **link}
            if edge in relationships:
                raise WFError("relationship.duplicate-edge", "typed relationship is duplicated", exit_class=4, path=path)
            relationships.append(edge)
        if [(RELATION_ORDER[item["relation"]], _identifier(item["id"], "document", item["relation"])[0]) for item in relationships] != sorted((RELATION_ORDER[item["relation"]], _identifier(item["id"], "document", item["relation"])[0]) for item in relationships):
            raise WFError("relationship.order", "relationships are outside canonical order", exit_class=4, path=path)
    questions = [_parse_question(block, path) for _start, _end, block in _extract_blocks(lines, "<!-- wayfinder:question -->", "<!-- /wayfinder:question -->", path, "question")]
    sources = [_parse_source(block, path) for _start, _end, block in _extract_blocks(lines, "<!-- wayfinder:source -->", "<!-- /wayfinder:source -->", path, "source")]
    if questions and kind != "register":
        raise WFError("question.owner-kind", "question blocks belong only in register documents", exit_class=4, path=path)
    if sources and kind != "evidence":
        raise WFError("source.owner-kind", "source blocks belong only in evidence documents", exit_class=4, path=path)
    if len({item["key"] for item in sources}) != len(sources):
        raise WFError("source.duplicate-key", "source key is duplicated within evidence document", exit_class=4, path=path)
    if [item["ordinal"] for item in sources] != sorted(item["ordinal"] for item in sources):
        raise WFError("source.order", "source entries must be in numeric key order", exit_class=4, path=path)
    citations = re.findall(r"\[(src-[0-9]{2,})\]\(#\1\)", text)
    declared = {item["key"] for item in sources}
    if set(citations) - declared:
        raise WFError("source.citation-missing", "citation targets an undeclared local source", exit_class=4, path=path, actual=sorted(set(citations) - declared))
    for line in lines:
        claim = MATERIAL_CLAIM_RE.fullmatch(line)
        if claim and not re.search(r"\[(src-[0-9]{2,})\]\(#\1\)", claim.group(1)):
            raise WFError("source.material-claim", "declared material claim requires a local source citation", exit_class=4, path=path, actual=line)
    unused = sorted(declared - set(citations))
    required_headings = {
        "evidence": ["## Question and scope", "## Method", "## Findings", "## Applicability and limitations", "## Evidence, inference, and hypothesis", "## Implications", "## Unknowns", "## Next validation", "## Sources"],
        "decision": ["## Context", "## Options considered", "## Decision", "## Rationale", "## Consequences", "## References", "## Supersession"],
    }.get(kind)
    if required_headings is not None:
        positions = [lines.index(heading) if heading in lines else -1 for heading in required_headings]
        if -1 in positions or positions != sorted(positions):
            raise WFError(f"{kind}.sections", f"{kind} requires exact ordered section headings", exit_class=4, path=path, expected=required_headings)
    generated: list[dict[str, Any]] = []
    active_start: tuple[int, re.Match[str]] | None = None
    names: set[str] = set()
    for index, line in enumerate(lines):
        match = GENERATED_START_RE.fullmatch(line)
        if match:
            if active_start is not None:
                raise WFError("generated.nested", "generated regions may not nest", exit_class=4, path=path)
            if match.group(1) in names:
                raise WFError("generated.duplicate-name", "generated region name is duplicated", exit_class=4, path=path, actual=match.group(1))
            names.add(match.group(1))
            active_start = (index, match)
        elif line == GENERATED_END:
            if active_start is None:
                raise WFError("generated.delimiter", "generated end delimiter has no opener", exit_class=4, path=path)
            start_index, start_match = active_start
            generated.append({"name": start_match.group(1), "generator": "document-index-v1", "inputSha256": start_match.group(2), "start": start_index, "end": index})
            active_start = None
        elif line.startswith("<!-- wayfinder:generated"):
            raise WFError("generated.marker", "generated region opener is malformed or uses an unregistered generator", exit_class=4, path=path, actual=line)
    if active_start is not None:
        raise WFError("generated.delimiter", "generated region is missing its exact end delimiter", exit_class=4, path=path)
    if generated and kind not in {"map", "index"}:
        raise WFError("generated.owner-kind", "generated regions are allowed only in map and index documents", exit_class=4, path=path)
    return {"path": path, "title": h1s[0][1], "id": fields["ID"], "ordinal": ordinal, "kind": kind, "status": status, "updated": fields["Updated"], "summary": fields["Summary"], "decisionDate": decision_date, "supersedes": id_lists["Supersedes"], "supersededBy": id_lists["Superseded-By"], "relationships": relationships, "questions": questions, "sources": sources, "unusedSources": unused, "generatedRegions": generated, "raw": raw}


def _membership(path: str, manifest: dict[str, Any]) -> tuple[str | None, str | None]:
    if path == manifest["entrypoint"]:
        return None, None
    matching = [module for module in manifest["modules"] if is_within(path, module["root"])]
    if not matching and "/" not in path:
        return None, None
    if len(matching) != 1:
        raise WFError("record.module-containment", "authored document must be the record entrypoint or belong to exactly one module", exit_class=4, path=path)
    module = matching[0]
    subject_id: str | None = None
    for subject in module["subjects"]:
        if subject["kind"] == "document" and path == subject["entrypoint"]:
            subject_id = subject["id"]
        elif subject["kind"] == "collection" and is_within(path, subject["root"]):
            if subject_id is not None:
                raise WFError("record.subject-containment", "document belongs to multiple subjects", exit_class=4, path=path)
            subject_id = subject["id"]
    return module["id"], subject_id


def load_record(workspace: Path) -> dict[str, Any]:
    manifest_path = workspace / ".wayfinder/manifest.json"
    manifest = validate_manifest(strict_json_bytes(manifest_path.read_bytes(), path=str(manifest_path)), workspace)["manifest"]
    record_root = workspace if manifest["recordRoot"] == "." else workspace / PurePosixPath(manifest["recordRoot"])
    artifact_keys = {path_key(item["path"]) for item in manifest["generatedArtifacts"]}
    documents: list[dict[str, Any]] = []
    for file in sorted(record_root.rglob("*.md"), key=lambda item: item.relative_to(record_root).as_posix().encode("utf-8")):
        relative = file.relative_to(record_root).as_posix()
        if path_key(relative) in artifact_keys or relative.startswith(".wayfinder/"):
            continue
        if file.is_symlink() or not file.is_file():
            raise WFError("record.document-type", "record Markdown path must be a non-symbolic regular file", exit_class=4, path=relative)
        document = parse_document(file.read_bytes(), relative)
        for source in document["sources"]:
            original = source["fields"]["Original"]
            if not original.startswith("https://"):
                local_source = portable_path(original, "Original")
                _physical_check(workspace, local_source, "Original", "file", required=True)
        module, subject = _membership(relative, manifest)
        document["module"] = module
        document["subject"] = f"{module}/{subject}" if subject is not None else None
        documents.append(document)
    by_id: dict[str, dict[str, Any]] = {}
    ordinals: dict[int, str] = {}
    by_path = {item["path"]: item for item in documents}
    for document in documents:
        if document["id"] in by_id:
            raise WFError("record.duplicate-document-id", "document ID is duplicated", exit_class=4, path=document["path"], actual=document["id"])
        if document["ordinal"] in ordinals:
            raise WFError("record.duplicate-document-ordinal", "document ordinal is duplicated", exit_class=4, path=document["path"], actual=document["ordinal"])
        by_id[document["id"]] = document
        ordinals[document["ordinal"]] = document["id"]
    required_paths = {manifest["entrypoint"]}
    for module in manifest["modules"]:
        required_paths.add(module["entrypoint"])
        required_paths.update(subject["entrypoint"] for subject in module["subjects"])
    missing = sorted(required_paths - set(by_path))
    if missing:
        raise WFError("record.entrypoint-not-authored", "declared entrypoint is not an authored Wayfinder document", exit_class=4, actual=missing)
    if by_path[manifest["entrypoint"]]["kind"] != "map":
        raise WFError("record.entrypoint-kind", "record entrypoint must be kind map", exit_class=4, path=manifest["entrypoint"])
    question_ids: dict[str, dict[str, Any]] = {}
    question_ordinals: dict[int, str] = {}
    for document in documents:
        for question in document["questions"]:
            question["path"] = document["path"]
            if question["id"] in question_ids or question["ordinal"] in question_ordinals:
                raise WFError("record.duplicate-question-id", "question ID or ordinal is duplicated", exit_class=4, path=document["path"], actual=question["id"])
            question_ids[question["id"]] = question
            question_ordinals[question["ordinal"]] = question["id"]
    for document in documents:
        for edge in document["relationships"]:
            target = by_id.get(edge["id"])
            if target is None or target["path"] != edge["path"]:
                raise WFError("relationship.target", "typed relationship target ID and path must resolve together", exit_class=4, path=document["path"], actual=edge)
            if edge["relation"] == "Governed-By" and (target["kind"], target["status"]) != ("decision", "Accepted"):
                raise WFError("relationship.target-kind-status", "Governed-By targets an Accepted decision", exit_class=4, path=document["path"], actual=edge["id"])
            if edge["relation"] == "Supported-By" and (target["kind"], target["status"]) != ("evidence", "Active"):
                raise WFError("relationship.target-kind-status", "Supported-By targets Active evidence", exit_class=4, path=document["path"], actual=edge["id"])
        for direction, reverse in (("supersedes", "supersededBy"), ("supersededBy", "supersedes")):
            for target_id in document[direction]:
                if target_id == document["id"]:
                    raise WFError("supersession.self-edge", "document may not supersede itself", exit_class=4, path=document["path"])
                target = by_id.get(target_id)
                if target is None:
                    raise WFError("supersession.target-missing", "supersession target does not exist", exit_class=4, path=document["path"], actual=target_id)
                if (document["kind"] == "decision") != (target["kind"] == "decision"):
                    raise WFError("supersession.kind", "supersession must stay within one lifecycle family", exit_class=4, path=document["path"], actual=target_id)
                if document["id"] not in target[reverse]:
                    raise WFError("supersession.reciprocal", "supersession edge is not reciprocal", exit_class=4, path=document["path"], actual=target_id)
        for question in document["questions"]:
            for relation, links in question["links"].items():
                for link in links:
                    target = by_id.get(link["id"])
                    if target is None or target["path"] != link["path"]:
                        raise WFError("question.target", "question target ID and path must resolve together", exit_class=4, path=document["path"], actual=link)
                    if relation == "Addressed-By" and target["kind"] != "evidence":
                        raise WFError("question.target-kind", "Addressed-By targets evidence", exit_class=4, path=document["path"], actual=link["id"])
                    if relation == "Resolved-By":
                        valid = (target["kind"] == "decision" and target["status"] == "Accepted") or (target["kind"] in {"evidence", "brief"} and target["status"] == "Active")
                        if not valid:
                            raise WFError("question.target-kind-status", "Resolved-By target lacks required kind/status", exit_class=4, path=document["path"], actual=link["id"])
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise WFError("supersession.cycle", "supersession graph contains a cycle", exit_class=4, actual=identifier)
        if identifier in visited:
            return
        visiting.add(identifier)
        for target in by_id[identifier]["supersedes"]:
            visit(target)
        visiting.remove(identifier)
        visited.add(identifier)
    for identifier in by_id:
        visit(identifier)
    return {"workspace": workspace, "recordRoot": record_root, "manifest": manifest, "documents": documents, "byId": by_id, "byPath": by_path, "questions": question_ids}


def _catalog_basis(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest": record["manifest"],
        "documents": [
            {
                "id": item["id"], "path": item["path"], "title": item["title"], "kind": item["kind"], "status": item["status"],
                "updated": item["updated"], "summary": item["summary"], "module": item["module"], "subject": item["subject"],
                "supersedes": item["supersedes"], "supersededBy": item["supersededBy"],
                "governedBy": [edge["id"] for edge in item["relationships"] if edge["relation"] == "Governed-By"],
                "supportedBy": [edge["id"] for edge in item["relationships"] if edge["relation"] == "Supported-By"],
            }
            for item in sorted(record["documents"], key=lambda value: value["ordinal"])
        ],
        "questions": [
            {
                "id": item["id"], "path": item["path"], "anchor": item["anchor"], "title": item["title"], "state": item["state"], "raised": item["raised"],
                "appliesTo": [link["id"] for link in item["links"]["Applies-To"]],
                "addressedBy": [link["id"] for link in item["links"]["Addressed-By"]],
                "resolvedBy": [link["id"] for link in item["links"]["Resolved-By"]],
                "resumption": item["sections"].get("Next step") or item["sections"].get("Current activity") or item["sections"].get("Revisit trigger") or item["sections"].get("Resolution") or item["sections"].get("Retirement reason"),
            }
            for item in sorted(record["questions"].values(), key=lambda value: value["ordinal"])
        ],
    }


def render_catalog(record: dict[str, Any]) -> bytes:
    basis = _catalog_basis(record)
    catalog = {
        "format": "wayfinder-document-catalog",
        "schemaVersion": 1,
        "generator": "document-catalog-v1",
        "inputSha256": sha256_bytes(canonical_json(basis).encode("utf-8")),
        "documents": basis["documents"],
        "questions": basis["questions"],
    }
    return (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _region_members(record: dict[str, Any], owner: dict[str, Any]) -> list[dict[str, Any]]:
    if owner["module"] is None:
        member_paths = {module["entrypoint"] for module in record["manifest"]["modules"]}
        return [item for item in record["documents"] if item["path"] in member_paths]
    if owner["subject"] is not None:
        return [item for item in record["documents"] if item["subject"] == owner["subject"] and item["id"] != owner["id"]]
    return [item for item in record["documents"] if item["module"] == owner["module"] and item["id"] != owner["id"]]


def render_region(record: dict[str, Any], owner: dict[str, Any], name: str = "members") -> list[str]:
    members = sorted(_region_members(record, owner), key=lambda value: value["ordinal"])
    projection = [{"id": item["id"], "path": item["path"], "title": item["title"], "kind": item["kind"], "status": item["status"], "summary": item["summary"]} for item in members]
    digest = sha256_bytes(canonical_json(projection).encode("utf-8"))
    lines = [f'<!-- wayfinder:generated name="{name}" generator="document-index-v1" input-sha256="{digest}" -->', "| ID | Title | Kind | Status | Summary |", "| --- | --- | --- | --- | --- |"]
    for item in members:
        destination = posixpath.relpath(item["path"], posixpath.dirname(owner["path"]) or ".")
        values = (f"[{item['id']}]({destination})", item["title"], item["kind"], item["status"], item["summary"])
        if any("|" in value or "\n" in value for value in values):
            raise WFError("generated.table-value", "catalog projection cannot render an unescaped table delimiter", exit_class=4, path=item["path"])
        lines.append("| " + " | ".join(values) + " |")
    lines.append(GENERATED_END)
    return lines


def _replace_regions(record: dict[str, Any], document: dict[str, Any]) -> bytes:
    text = document["raw"].decode("utf-8")
    lines = text[:-1].split("\n")
    for region in sorted(document["generatedRegions"], key=lambda item: item["start"], reverse=True):
        lines[region["start"]:region["end"] + 1] = render_region(record, document, region["name"])
    return ("\n".join(lines) + "\n").encode("utf-8")


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    warnings: list[dict[str, Any]] = []
    for document in record["documents"]:
        for key in document["unusedSources"]:
            warnings.append({"code": "source.unused", "message": "source entry has no local citation", "path": document["path"], "actual": key})
        if document["generatedRegions"] and _replace_regions(record, document) != document["raw"]:
            raise WFError("generated.stale", "generated region does not match authoritative inputs", exit_class=4, path=document["path"], remediation="Run generate with a regions request naming this path.")
    expected_catalog = render_catalog(record)
    for artifact in record["manifest"]["generatedArtifacts"]:
        target = record["recordRoot"] / PurePosixPath(artifact["path"])
        if artifact["generator"] == "document-catalog-v1" and target.read_bytes() != expected_catalog:
            raise WFError("generated.catalog-stale", "generated catalog does not match authoritative inputs", exit_class=4, path=artifact["path"], remediation="Run generate with action catalog.")
    return {"documents": len(record["documents"]), "questions": len(record["questions"]), "warnings": warnings, "catalogSha256": sha256_bytes(expected_catalog)}


def command_validate(workspace_root_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is None:
        raise WFError("command.arguments", "validate requires --workspace-root PATH", exit_class=2)
    supplied = Path(workspace_root_arg)
    if not supplied.exists() or not supplied.is_dir():
        raise WFError("validate.workspace-root", "workspace root must be an existing directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    record = load_record(workspace)
    validation = validate_record(record)
    return {"validation": validation, "environment": {"workspaceRoot": str(workspace)}}


def _closed_generation(value: Any, fields: tuple[str, ...], pointer: str) -> dict[str, Any]:
    obj = _expect_object(value, pointer, exit_class=2)
    _closed(obj, fields, pointer, exit_class=2)
    return obj


def _render_metadata(spec: dict[str, Any]) -> str:
    fields = [("ID", spec["id"]), ("Kind", spec["kind"]), ("Status", spec["status"]), ("Updated", spec["updated"]), ("Summary", spec["summary"])]
    for key, source in (("Decision-Date", "decisionDate"), ("Supersedes", "supersedes"), ("Superseded-By", "supersededBy")):
        value = spec[source]
        if isinstance(value, list) and value:
            value = ", ".join(value)
        if value not in (None, []):
            fields.append((key, value))
    return "\n".join(["<!-- wayfinder:metadata -->", *(f"- **{name}:** {value}" for name, value in fields), "<!-- /wayfinder:metadata -->"])


def _render_relationships(spec: dict[str, Any]) -> str:
    if not spec["relationships"]:
        return ""
    lines = ["<!-- wayfinder:relationships -->"]
    for item in spec["relationships"]:
        lines.append(f"- **{item['relation']}:** [{item['targetId']}]({item['targetPath']})")
    lines.extend(["<!-- /wayfinder:relationships -->", "", ""])
    return "\n".join(lines)


def _render_sections(spec: dict[str, Any]) -> str:
    lines: list[str] = []
    for section in spec["sections"]:
        lines.extend([f"## {section['heading']}", "", section["content"], ""])
    for question in spec["questions"]:
        lines.extend(["<!-- wayfinder:question -->", f'<a id="{question["id"]}"></a>', f"### {question['title']}"])
        for name in ("ID", "State", "Raised", "Scope"):
            key = {"ID": "id", "State": "state", "Raised": "raised", "Scope": "scope"}[name]
            if question[key] is not None:
                lines.append(f"- **{name}:** {question[key]}")
        for name, key in (("Applies-To", "appliesTo"), ("Addressed-By", "addressedBy"), ("Resolved-By", "resolvedBy")):
            for link in question[key]:
                lines.append(f"- **{name}:** [{link['targetId']}]({link['targetPath']})")
        if question["resolutionDate"] is not None:
            lines.append(f"- **Resolution-Date:** {question['resolutionDate']}")
        lines.append("")
        for section in question["sections"]:
            lines.extend([f"#### {section['heading']}", "", section["content"], ""])
        lines[-1] = "<!-- /wayfinder:question -->"
        lines.append("")
    for source in spec["sources"]:
        lines.extend(["<!-- wayfinder:source -->", f'<a id="{source["key"]}"></a>', f"### {source['key']} — {source['title']}"])
        for name, key in (("Citation", "citation"), ("Original", "original"), ("Published", "published"), ("Accessed", "accessed"), ("Applicability", "applicability")):
            if source[key] is not None:
                lines.append(f"- **{name}:** {source[key]}")
        lines.extend(["", "#### Used for", "", source["usedFor"], "", "#### Limitations", "", source["limitations"], "<!-- /wayfinder:source -->", ""])
    return "\n".join(lines).rstrip()


def _render_template(skill_root: Path, kind: str, slots: dict[str, str]) -> bytes:
    template_path = skill_root / f"assets/contract-v1/templates/{kind}.md"
    raw = template_path.read_bytes()
    template = _markdown_text(raw, template_path.relative_to(skill_root).as_posix())
    observed = TEMPLATE_SLOT_RE.findall(template)
    if set(observed) != set(slots) or len(observed) != len(set(observed)):
        raise WFError("template.slots", "template slots do not match the closed renderer contract", exit_class=2, path=str(template_path), expected=sorted(slots), actual=observed)
    if any(TEMPLATE_SLOT_RE.search(value) for value in slots.values()):
        raise WFError("template.recursive-slot", "slot values may not contain reserved template tokens", exit_class=2)
    rendered = template
    for name in observed:
        rendered = rendered.replace("{{" + name + "}}", slots[name], 1)
    if TEMPLATE_SLOT_RE.search(rendered):
        raise WFError("template.unexpanded-slot", "rendered document retains a template slot", exit_class=2)
    return rendered.encode("utf-8")


def _validate_render_spec(value: Any, pointer: str) -> dict[str, Any]:
    fields = ("output", "title", "id", "kind", "status", "updated", "summary", "decisionDate", "supersedes", "supersededBy", "relationships", "sections", "questions", "sources")
    spec = _closed_generation(value, fields, pointer)
    portable_path(spec["output"], f"{pointer}/output")
    if not spec["output"].endswith(".md") or not isinstance(spec["title"], str) or not spec["title"] or "\n" in spec["title"]:
        raise WFError("render.document", "render output/title is invalid", exit_class=2, field=pointer)
    _identifier(spec["id"], "document", f"{pointer}/id", exit_class=2)
    if spec["kind"] not in KINDS or spec["status"] not in (DECISION_STATUSES if spec["kind"] == "decision" else LIVING_STATUSES):
        raise WFError("render.lifecycle", "render kind/status combination is invalid", exit_class=2, field=pointer)
    _calendar_date(spec["updated"], f"{pointer}/updated", exit_class=2)
    if not isinstance(spec["summary"], str) or not spec["summary"].strip() or "\n" in spec["summary"]:
        raise WFError("render.summary", "render summary must be nonempty single-line text", exit_class=2, field=f"{pointer}/summary")
    if spec["decisionDate"] is not None:
        _calendar_date(spec["decisionDate"], f"{pointer}/decisionDate", exit_class=2)
    for key in ("supersedes", "supersededBy"):
        values = _expect_array(spec[key], f"{pointer}/{key}", exit_class=2)
        for index, identifier in enumerate(values):
            _identifier(identifier, "document", f"{pointer}/{key}/{index}", exit_class=2)
    for index, relation in enumerate(_expect_array(spec["relationships"], f"{pointer}/relationships", exit_class=2)):
        item = _closed_generation(relation, ("relation", "targetId", "targetPath"), f"{pointer}/relationships/{index}")
        if item["relation"] not in RELATION_ORDER:
            raise WFError("render.relationship", "relationship is not registered", exit_class=2, field=f"{pointer}/relationships/{index}/relation")
        _identifier(item["targetId"], "document", f"{pointer}/relationships/{index}/targetId", exit_class=2)
        _render_link_destination(item["targetPath"], spec["output"], f"{pointer}/relationships/{index}/targetPath")
    for key in ("sections",):
        for index, section in enumerate(_expect_array(spec[key], f"{pointer}/{key}", exit_class=2)):
            item = _closed_generation(section, ("heading", "content"), f"{pointer}/{key}/{index}")
            if not all(isinstance(item[name], str) and item[name].strip() for name in item):
                raise WFError("render.section", "section heading/content must be nonempty text", exit_class=2, field=f"{pointer}/{key}/{index}")
    # Question and source records are closed recursively by the renderer-facing schema contract.
    question_fields = ("id", "title", "state", "raised", "scope", "appliesTo", "addressedBy", "resolvedBy", "resolutionDate", "sections")
    for index, question in enumerate(_expect_array(spec["questions"], f"{pointer}/questions", exit_class=2)):
        item = _closed_generation(question, question_fields, f"{pointer}/questions/{index}")
        _identifier(item["id"], "question", f"{pointer}/questions/{index}/id", exit_class=2)
        if not isinstance(item["title"], str) or not item["title"].strip() or "\n" in item["title"]:
            raise WFError("render.question", "question title must be nonempty single-line text", exit_class=2, field=f"{pointer}/questions/{index}/title")
        if item["state"] not in QUESTION_STATES or item["scope"] not in (None, "Record-Wide"):
            raise WFError("render.question", "question state or scope is invalid", exit_class=2, field=f"{pointer}/questions/{index}")
        _calendar_date(item["raised"], f"{pointer}/questions/{index}/raised", exit_class=2)
        if item["resolutionDate"] is not None:
            _calendar_date(item["resolutionDate"], f"{pointer}/questions/{index}/resolutionDate", exit_class=2)
        for link_key in ("appliesTo", "addressedBy", "resolvedBy"):
            for link_index, link in enumerate(_expect_array(item[link_key], f"{pointer}/questions/{index}/{link_key}", exit_class=2)):
                link_item = _closed_generation(link, ("targetId", "targetPath"), f"{pointer}/questions/{index}/{link_key}/{link_index}")
                _identifier(link_item["targetId"], "document", f"{pointer}/questions/{index}/{link_key}/{link_index}/targetId", exit_class=2)
                _render_link_destination(link_item["targetPath"], spec["output"], f"{pointer}/questions/{index}/{link_key}/{link_index}/targetPath")
        for section_index, section in enumerate(_expect_array(item["sections"], f"{pointer}/questions/{index}/sections", exit_class=2)):
            section_item = _closed_generation(section, ("heading", "content"), f"{pointer}/questions/{index}/sections/{section_index}")
            if not all(isinstance(section_item[name], str) and section_item[name].strip() for name in section_item):
                raise WFError("render.question", "question section heading/content must be nonempty text", exit_class=2, field=f"{pointer}/questions/{index}/sections/{section_index}")
    source_fields = ("key", "title", "citation", "original", "published", "accessed", "applicability", "usedFor", "limitations")
    for index, source in enumerate(_expect_array(spec["sources"], f"{pointer}/sources", exit_class=2)):
        item = _closed_generation(source, source_fields, f"{pointer}/sources/{index}")
        if not isinstance(item["key"], str) or EVIDENCE_KEY_RE.fullmatch(item["key"]) is None:
            raise WFError("render.source", "source key is outside the version-1 grammar", exit_class=2, field=f"{pointer}/sources/{index}/key")
        for key in ("title", "citation", "original", "accessed", "usedFor", "limitations"):
            if not isinstance(item[key], str) or not item[key].strip():
                raise WFError("render.source", "source text fields must be nonempty", exit_class=2, field=f"{pointer}/sources/{index}/{key}")
        if item["published"] is not None:
            _calendar_date(item["published"], f"{pointer}/sources/{index}/published", exit_class=2)
        _calendar_date(item["accessed"], f"{pointer}/sources/{index}/accessed", exit_class=2)
        if item["applicability"] not in {"Direct", "Adjacent", "General"}:
            raise WFError("render.source", "source applicability is not registered", exit_class=2, field=f"{pointer}/sources/{index}/applicability")
    return spec


def _render_link_destination(value: Any, owner_output: str, field: str) -> str:
    if not isinstance(value, str) or not value or value.startswith(("/", "\\")) or "\\" in value or "#" in value or "?" in value:
        raise WFError("render.relationship", "rendered typed link destination is invalid", exit_class=2, field=field, actual=value)
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(owner_output), value))
    if normalized.startswith("../") or normalized == ".." or not normalized.endswith(".md"):
        raise WFError("render.relationship", "rendered typed link escapes the record or is not Markdown", exit_class=2, field=field, actual=value)
    canonical = posixpath.relpath(normalized, posixpath.dirname(owner_output) or ".")
    if canonical != value:
        raise WFError("render.relationship", "rendered typed link destination is not normalized", exit_class=2, field=field, expected=canonical, actual=value)
    return value


def _atomic_declared_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".wayfinder-tmp")
    if temporary.exists():
        raise WFError("generate.temporary-exists", "generation temporary path already exists", exit_class=3, path=str(temporary))
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _exclusive_declared_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        raise WFError("generate.output-exists", "render never overwrites an output", exit_class=3, path=str(path)) from None
    except Exception:
        if created and path.exists() and not path.is_symlink():
            path.unlink()
        raise


def _allocation_mnemonic(title: str, explicit: Any, field: str) -> str:
    if explicit is not None:
        if not isinstance(explicit, str) or not SLUG_RE.fullmatch(explicit) or len(explicit) > 48:
            raise WFError("allocation.mnemonic", "explicit mnemonic is outside the grammar", exit_class=2, field=field, actual=explicit)
        return explicit
    words = re.findall(r"[a-z0-9]+", title.lower())
    selected: list[str] = []
    for word in words:
        candidate = "-".join([*selected, word])
        if len(candidate) > 48:
            break
        selected.append(word)
    if not selected:
        raise WFError("allocation.mnemonic-required", "title has no safe ASCII mnemonic; provide mnemonic", exit_class=2, field=field)
    return "-".join(selected)


def command_generate(workspace_root_arg: str | None, request_arg: str | None, output_root_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is None or request_arg is None:
        raise WFError("command.arguments", "generate requires --workspace-root PATH and --request FILE", exit_class=2)
    supplied = Path(workspace_root_arg)
    if not supplied.exists() or not supplied.is_dir():
        raise WFError("generate.workspace-root", "workspace root must be an existing directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    request_path, request_raw = _read_control_file(request_arg, "request")
    request = _expect_object(strict_json_bytes(request_raw, path=str(request_path), exit_class=2), "/", exit_class=2)
    base = ("format", "schemaVersion", "action")
    _expect_literal(request.get("format"), "wayfinder-generation-request", "/format", "generate.format", exit_class=2)
    _expect_literal(request.get("schemaVersion"), 1, "/schemaVersion", "generate.unsupported-version", exit_class=2)
    action = request.get("action")
    if action == "allocate":
        _closed(request, (*base, "documents", "questions"), "/", exit_class=2)
        record = load_record(workspace)
        max_doc = max((item["ordinal"] for item in record["documents"]), default=0)
        max_question = max((item["ordinal"] for item in record["questions"].values()), default=0)
        allocated_documents = []
        for index, raw_item in enumerate(_expect_array(request["documents"], "/documents", exit_class=2)):
            item = _closed_generation(raw_item, ("title", "mnemonic"), f"/documents/{index}")
            if not isinstance(item["title"], str):
                raise WFError("allocation.title", "allocation title must be text", exit_class=2, field=f"/documents/{index}/title")
            max_doc += 1
            mnemonic = _allocation_mnemonic(item["title"], item["mnemonic"], f"/documents/{index}/mnemonic")
            allocated_documents.append({"id": f"wf-{max_doc:04d}-{mnemonic}", "candidate": True})
        allocated_questions = []
        for index, raw_item in enumerate(_expect_array(request["questions"], "/questions", exit_class=2)):
            item = _closed_generation(raw_item, ("title", "mnemonic"), f"/questions/{index}")
            max_question += 1
            mnemonic = _allocation_mnemonic(item["title"], item["mnemonic"], f"/questions/{index}/mnemonic")
            allocated_questions.append({"id": f"wfq-{max_question:04d}-{mnemonic}", "candidate": True})
        return {"action": action, "documents": allocated_documents, "questions": allocated_questions, "writes": []}
    if action == "render":
        _closed(request, (*base, "documents"), "/", exit_class=2)
        if output_root_arg is None:
            raise WFError("command.arguments", "render requires --output-root PATH", exit_class=2)
        output_candidate = Path(output_root_arg)
        if not output_candidate.exists() or not output_candidate.is_dir():
            raise WFError("generate.output-root", "render output root must be an existing directory", exit_class=3, path=str(output_candidate))
        output_root = output_candidate.resolve(strict=True)
        documents = [_validate_render_spec(value, f"/documents/{index}") for index, value in enumerate(_expect_array(request["documents"], "/documents", exit_class=2))]
        if len({path_key(item["output"]) for item in documents}) != len(documents):
            raise WFError("render.duplicate-output", "render output path is duplicated", exit_class=2)
        rendered: list[tuple[Path, bytes, str]] = []
        skill_root = Path(__file__).resolve().parents[2]
        for spec in documents:
            raw = _render_template(skill_root, spec["kind"], {"TITLE": spec["title"], "METADATA_BLOCK": _render_metadata(spec), "RELATIONSHIP_BLOCK": _render_relationships(spec), "CONTENT": _render_sections(spec)})
            parse_document(raw, spec["output"])
            target = _physical_check(output_root, spec["output"], f"/documents/{spec['output']}/output", required=False, exit_class=3)
            if target.exists():
                raise WFError("generate.output-exists", "render never overwrites an output", exit_class=3, path=str(target))
            rendered.append((target, raw, spec["output"]))
        for target, raw, _relative in rendered:
            _exclusive_declared_write(target, raw)
        return {"action": action, "writes": [{"path": relative, "byteLength": len(raw), "sha256": sha256_bytes(raw)} for _target, raw, relative in rendered]}
    record = load_record(workspace)
    if action == "catalog":
        _closed(request, base, "/", exit_class=2)
        if output_root_arg is not None:
            raise WFError("command.arguments", "catalog does not accept --output-root", exit_class=2)
        raw = render_catalog(record)
        writes = []
        for artifact in record["manifest"]["generatedArtifacts"]:
            if artifact["generator"] == "document-catalog-v1":
                target = record["recordRoot"] / PurePosixPath(artifact["path"])
                _atomic_declared_write(target, raw)
                writes.append({"path": artifact["path"], "byteLength": len(raw), "sha256": sha256_bytes(raw)})
        return {"action": action, "writes": writes}
    if action == "regions":
        _closed(request, (*base, "paths"), "/", exit_class=2)
        if output_root_arg is not None:
            raise WFError("command.arguments", "regions does not accept --output-root", exit_class=2)
        requested = [portable_path(value, f"/paths/{index}", exit_class=2) for index, value in enumerate(_expect_array(request["paths"], "/paths", exit_class=2))]
        if len(set(map(path_key, requested))) != len(requested):
            raise WFError("generate.duplicate-path", "region path is duplicated", exit_class=2)
        writes = []
        for relative in requested:
            document = record["byPath"].get(relative)
            if document is None or not document["generatedRegions"]:
                raise WFError("generate.region-path", "requested path is not an authored document with a region", exit_class=2, path=relative)
            raw = _replace_regions(record, document)
            target = record["recordRoot"] / PurePosixPath(relative)
            _atomic_declared_write(target, raw)
            writes.append({"path": relative, "byteLength": len(raw), "sha256": sha256_bytes(raw)})
        return {"action": action, "writes": writes}
    raise WFError("generate.action", "generation action is not registered", exit_class=2, field="/action", actual=action)


def _proposal_text(value: Any, field: str, *, single_line: bool = False) -> str:
    if not isinstance(value, str) or not value.strip() or (single_line and "\n" in value):
        raise WFError("proposal.text", "proposal text must be nonempty" + (" and single-line" if single_line else ""), exit_class=2, field=field)
    return value


def _proposal_string_array(value: Any, field: str) -> list[str]:
    values = _expect_array(value, field, exit_class=2)
    result: list[str] = []
    for index, item in enumerate(values):
        result.append(_proposal_text(item, f"{field}/{index}", single_line=True))
    if len(set(result)) != len(result):
        raise WFError("proposal.duplicate", "proposal array contains duplicate values", exit_class=2, field=field)
    return result


def _validate_initialization_proposal(value: Any) -> dict[str, Any]:
    proposal = _closed_generation(
        value,
        (
            "format", "schemaVersion", "mode", "profile", "effectiveDate", "manifest",
            "documents", "concerns", "epistemicStates", "omittedModules",
            "authorityBoundary", "interviewResume", "materialInferences",
            "sourceInventory", "intakeLedger", "materialSourcePaths", "semanticReadiness",
        ),
        "/",
    )
    _expect_literal(proposal["format"], "wayfinder-initialize-proposal", "/format", "proposal.format", exit_class=2)
    _expect_literal(proposal["schemaVersion"], 1, "/schemaVersion", "proposal.unsupported-version", exit_class=2)
    if proposal["mode"] not in {"fresh", "source-assisted"}:
        raise WFError("proposal.mode", "initialization mode is not registered", exit_class=2, field="/mode", actual=proposal["mode"])
    profile = _closed_generation(proposal["profile"], ("id", "confirmed"), "/profile")
    if profile["id"] not in {"foundation", "evidence-led", "software-product"} or profile["confirmed"] is not True:
        raise WFError("proposal.profile", "profile must be a supported, explicitly confirmed choice", exit_class=2, field="/profile")
    _calendar_date(proposal["effectiveDate"], "/effectiveDate", exit_class=2)

    manifest = _closed_generation(
        proposal["manifest"],
        ("format", "schemaVersion", "recordRoot", "entrypoint", "canonicalBaseline", "modules", "generatedArtifacts"),
        "/manifest",
    )
    _expect_literal(manifest["format"], "wayfinder-project-record", "/manifest/format", "manifest.format", exit_class=2)
    _expect_literal(manifest["schemaVersion"], 1, "/manifest/schemaVersion", "manifest.unsupported-version", exit_class=2)
    portable_path(manifest["recordRoot"], "/manifest/recordRoot", allow_dot=True, exit_class=2)
    portable_path(manifest["entrypoint"], "/manifest/entrypoint", exit_class=2)
    # Full manifest constraints are exercised against a materialized virtual record below.

    documents = [
        _validate_render_spec(item, f"/documents/{index}")
        for index, item in enumerate(_expect_array(proposal["documents"], "/documents", exit_class=2))
    ]
    if not documents:
        raise WFError("proposal.documents", "initialization requires authored documents", exit_class=2, field="/documents")
    bare_placeholder = re.compile(r"^(?:[-*] )?(?:TBD|TODO|lorem ipsum|none)\.?$", re.IGNORECASE)
    for document_index, document in enumerate(documents):
        text_values = [section["content"] for section in document["sections"]]
        text_values.extend(section["content"] for question in document["questions"] for section in question["sections"])
        text_values.extend(value for source in document["sources"] for value in (source["usedFor"], source["limitations"]))
        if any(bare_placeholder.fullmatch(line.strip()) for value in text_values for line in value.splitlines()):
            raise WFError("proposal.placeholder", "bare placeholders and unexplained empty-state words are forbidden", exit_class=2, field=f"/documents/{document_index}")
    paths = [item["output"] for item in documents]
    if len({path_key(item) for item in paths}) != len(paths):
        raise WFError("proposal.duplicate-target", "authored target paths must be unique", exit_class=2, field="/documents")
    document_ids = [item["id"] for item in documents]
    document_ordinals = [_identifier(item, "document", "/documents/id", exit_class=2)[0] for item in document_ids]
    if len(set(document_ids)) != len(document_ids) or len(set(document_ordinals)) != len(document_ordinals):
        raise WFError("proposal.document-id-collision", "document IDs and ordinals must be unique", exit_class=2, field="/documents")
    if document_ordinals != list(range(1, len(document_ordinals) + 1)):
        raise WFError("proposal.document-id-order", "greenfield candidate document IDs must be ordered consecutively from 1", exit_class=2, field="/documents")
    questions = [question for document in documents for question in document["questions"]]
    question_ids = [item["id"] for item in questions]
    question_ordinals = [_identifier(item, "question", "/documents/questions/id", exit_class=2)[0] for item in question_ids]
    if len(set(question_ids)) != len(question_ids) or len(set(question_ordinals)) != len(question_ordinals):
        raise WFError("proposal.question-id-collision", "question IDs and ordinals must be unique", exit_class=2, field="/documents/questions")
    if question_ordinals != list(range(1, len(question_ordinals) + 1)):
        raise WFError("proposal.question-id-order", "greenfield candidate question IDs must be ordered consecutively from 1", exit_class=2, field="/documents/questions")

    concerns: list[dict[str, Any]] = []
    concern_ids: set[str] = set()
    all_targets = set(document_ids) | set(question_ids)
    for index, raw in enumerate(_expect_array(proposal["concerns"], "/concerns", exit_class=2)):
        pointer = f"/concerns/{index}"
        item = _closed_generation(raw, ("id", "statement", "homeId"), pointer)
        if not isinstance(item["id"], str) or not SLUG_RE.fullmatch(item["id"]) or item["id"] in concern_ids:
            raise WFError("proposal.concern-id", "concern IDs must be unique lowercase slugs", exit_class=2, field=f"{pointer}/id")
        concern_ids.add(item["id"])
        _proposal_text(item["statement"], f"{pointer}/statement")
        if item["homeId"] not in all_targets:
            raise WFError("proposal.concern-home", "each concern must have exactly one declared document or question home", exit_class=2, field=f"{pointer}/homeId", actual=item["homeId"])
        concerns.append(item)
    if not concerns:
        raise WFError("proposal.concern-home", "initialization requires a complete nonempty concern-to-home map", exit_class=2, field="/concerns")

    states = {"Hypothesis", "Assumption", "Open question", "Deferred", "Not applicable", "Not yet elicited"}
    epistemic: list[dict[str, Any]] = []
    for index, raw in enumerate(_expect_array(proposal["epistemicStates"], "/epistemicStates", exit_class=2)):
        pointer = f"/epistemicStates/{index}"
        item = _closed_generation(raw, ("state", "statement", "targetId"), pointer)
        if item["state"] not in states or item["targetId"] not in all_targets:
            raise WFError("proposal.epistemic-state", "epistemic state or target is invalid", exit_class=2, field=pointer)
        _proposal_text(item["statement"], f"{pointer}/statement")
        epistemic.append(item)

    enabled_modules: set[str] = set()
    for index, raw_module in enumerate(_expect_array(manifest["modules"], "/manifest/modules", exit_class=2)):
        module = _expect_object(raw_module, f"/manifest/modules/{index}", exit_class=2)
        if isinstance(module.get("id"), str):
            enabled_modules.add(module["id"])
    omitted: list[dict[str, str]] = []
    omitted_ids: set[str] = set()
    for index, raw in enumerate(_expect_array(proposal["omittedModules"], "/omittedModules", exit_class=2)):
        pointer = f"/omittedModules/{index}"
        item = _closed_generation(raw, ("id", "reason"), pointer)
        if item["id"] not in STANDARD_MODULES or item["id"] in omitted_ids or item["id"] in enabled_modules:
            raise WFError("proposal.omitted-module", "omitted standard modules must be unique and disabled", exit_class=2, field=f"{pointer}/id")
        _proposal_text(item["reason"], f"{pointer}/reason")
        omitted_ids.add(item["id"])
        omitted.append(item)
    expected_omitted = STANDARD_MODULES - {item for item in enabled_modules if item in STANDARD_MODULES}
    if omitted_ids != expected_omitted:
        raise WFError("proposal.omitted-module-completeness", "every disabled standard module requires one stated omission reason", exit_class=2, field="/omittedModules", expected=sorted(expected_omitted), actual=sorted(omitted_ids))

    authority = _closed_generation(proposal["authorityBoundary"], ("statement", "coauthoritativePaths", "competingCurrentAuthority"), "/authorityBoundary")
    _proposal_text(authority["statement"], "/authorityBoundary/statement")
    coauthoritative = [source_path(item, f"/authorityBoundary/coauthoritativePaths/{index}") for index, item in enumerate(_expect_array(authority["coauthoritativePaths"], "/authorityBoundary/coauthoritativePaths", exit_class=2))]
    if len(set(coauthoritative)) != len(coauthoritative):
        raise WFError("proposal.duplicate", "co-authoritative paths must be unique", exit_class=2, field="/authorityBoundary/coauthoritativePaths")
    competing = _proposal_string_array(authority["competingCurrentAuthority"], "/authorityBoundary/competingCurrentAuthority")
    if competing:
        raise WFError("proposal.competing-authority", "initialization is blocked while competing current authority remains", exit_class=3, field="/authorityBoundary/competingCurrentAuthority", actual=competing)

    resume = _closed_generation(proposal["interviewResume"], ("summary", "nextWorkflow", "recommendedFocusIds"), "/interviewResume")
    _proposal_text(resume["summary"], "/interviewResume/summary")
    _expect_literal(resume["nextWorkflow"], "interview", "/interviewResume/nextWorkflow", "proposal.next-workflow", exit_class=2)
    focus = _proposal_string_array(resume["recommendedFocusIds"], "/interviewResume/recommendedFocusIds")
    if not focus or any(item not in all_targets for item in focus):
        raise WFError("proposal.resumption", "Interview resumption requires existing document or question focus IDs", exit_class=2, field="/interviewResume/recommendedFocusIds")

    inferences: list[dict[str, Any]] = []
    for index, raw in enumerate(_expect_array(proposal["materialInferences"], "/materialInferences", exit_class=2)):
        pointer = f"/materialInferences/{index}"
        item = _closed_generation(raw, ("statement", "basis", "confirmed"), pointer)
        _proposal_text(item["statement"], f"{pointer}/statement")
        _proposal_text(item["basis"], f"{pointer}/basis")
        if item["confirmed"] is not True:
            raise WFError("proposal.inference-unconfirmed", "material agent inferences must be disclosed and confirmed", exit_class=3, field=f"{pointer}/confirmed")
        inferences.append(item)

    readiness_fields = ("identityAndIntent", "outcomes", "boundaries", "people", "currentKnowledge", "consequentialUnknowns", "structure", "publicationBasis")
    readiness = _closed_generation(proposal["semanticReadiness"], readiness_fields, "/semanticReadiness")
    for field in readiness_fields:
        if readiness[field] not in {"supported", "explicit-unresolved"}:
            raise WFError("proposal.semantic-readiness", "readiness fields must be supported or explicit-unresolved", exit_class=2, field=f"/semanticReadiness/{field}")
    if "explicit-unresolved" in readiness.values() and not question_ids:
        raise WFError("proposal.semantic-readiness", "explicit unresolved readiness requires a durable question", exit_class=3, field="/semanticReadiness")

    for field in ("sourceInventory", "intakeLedger"):
        binding = proposal[field]
        if binding is not None:
            binding = _closed_generation(binding, ("path", "sha256"), f"/{field}")
            source_path(binding["path"], f"/{field}/path")
            if not isinstance(binding["sha256"], str) or not HEX_RE.fullmatch(binding["sha256"]):
                raise WFError("proposal.binding-digest", "binding sha256 must be lowercase 64-hex", exit_class=2, field=f"/{field}/sha256")
    if proposal["mode"] == "fresh" and (proposal["sourceInventory"] is not None or proposal["intakeLedger"] is not None):
        raise WFError("proposal.source-binding", "fresh initialization forbids source inventory and intake bindings", exit_class=2)
    if proposal["mode"] == "source-assisted" and (proposal["sourceInventory"] is None or proposal["intakeLedger"] is None):
        raise WFError("proposal.source-binding", "source-assisted initialization requires inventory and intake bindings", exit_class=2)
    material_paths = [source_path(item, f"/materialSourcePaths/{index}") for index, item in enumerate(_expect_array(proposal["materialSourcePaths"], "/materialSourcePaths", exit_class=2))]
    if len(set(material_paths)) != len(material_paths):
        raise WFError("proposal.material-source", "material source paths must be unique", exit_class=2, field="/materialSourcePaths")
    if proposal["mode"] == "fresh" and material_paths:
        raise WFError("proposal.material-source", "fresh initialization has no material source paths", exit_class=2, field="/materialSourcePaths")
    return proposal


def _target_workspace_path(record_root: str, record_relative: str) -> str:
    return record_relative if record_root == "." else f"{record_root}/{record_relative}"


def _resolve_initialization_baseline(workspace: Path, baseline: Any) -> dict[str, Any]:
    obj = _expect_object(baseline, "/manifest/canonicalBaseline", exit_class=2)
    kind = obj.get("kind")
    if kind == "snapshot":
        _closed(obj, ("kind", "path", "sha256"), "/manifest/canonicalBaseline", exit_class=2)
        path = portable_path(obj["path"], "/manifest/canonicalBaseline/path", exit_class=2)
        if not isinstance(obj["sha256"], str) or not HEX_RE.fullmatch(obj["sha256"]):
            raise WFError("manifest.sha256", "snapshot sha256 must be lowercase 64-hex", exit_class=2, field="/manifest/canonicalBaseline/sha256")
        target = _physical_check(workspace, path, "/manifest/canonicalBaseline/path", "file", required=True, exit_class=3)
        actual = sha256_bytes(target.read_bytes())
        if actual != obj["sha256"]:
            raise WFError("initialize.baseline-stale", "snapshot baseline digest does not match", exit_class=3, path=path, expected=obj["sha256"], actual=actual)
        return {"kind": "snapshot", "path": path, "sha256": actual}
    if kind != "git-ref":
        raise WFError("manifest.baseline-kind", "unsupported canonical baseline kind", exit_class=2, field="/manifest/canonicalBaseline/kind", actual=kind)
    _closed(obj, ("kind", "ref"), "/manifest/canonicalBaseline", exit_class=2)
    ref = obj["ref"]
    if not isinstance(ref, str) or not ref.startswith("refs/") or not re.fullmatch(r"refs/[A-Za-z0-9._/-]+", ref) or "//" in ref or ".." in ref or ref.endswith(("/", ".")) or "@{" in ref:
        raise WFError("manifest.git-ref", "Git baseline ref is invalid", exit_class=2, field="/manifest/canonicalBaseline/ref")
    marker = workspace / ".git"
    if marker.is_symlink() or not marker.exists():
        raise WFError("initialize.baseline-unresolved", "Git baseline requires local non-symbolic Git metadata", exit_class=3, path=str(marker))
    git_dir = marker
    if marker.is_file():
        try:
            marker_text = marker.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            marker_text = ""
        if not marker_text.startswith("gitdir: "):
            raise WFError("initialize.baseline-unresolved", "Git worktree marker is malformed", exit_class=3, path=str(marker))
        git_dir = Path(marker_text[8:])
        if not git_dir.is_absolute():
            git_dir = workspace / git_dir
        git_dir = git_dir.resolve(strict=True)
    direct = git_dir / PurePosixPath(ref)
    commit: str | None = None
    if direct.exists() and direct.is_file() and not direct.is_symlink():
        commit = direct.read_text(encoding="ascii").strip()
    packed = git_dir / "packed-refs"
    if commit is None and packed.exists() and packed.is_file() and not packed.is_symlink():
        for line in packed.read_text(encoding="ascii").splitlines():
            if line and not line.startswith(("#", "^")):
                candidate, separator, name = line.partition(" ")
                if separator and name == ref:
                    commit = candidate
                    break
    if commit is None or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None:
        raise WFError("initialize.baseline-unresolved", "declared Git ref does not resolve locally without fetching", exit_class=3, field="/manifest/canonicalBaseline/ref", actual=ref)
    return {"kind": "git-ref", "ref": ref, "commit": commit}


def _initialization_preflight(workspace: Path, proposal: dict[str, Any], bundle_root: Path) -> dict[str, Any]:
    manifest = proposal["manifest"]
    if bundle_root.exists() or bundle_root.is_symlink():
        raise WFError("initialize.bundle-exists", "initialize-plan never overwrites an existing bundle target", exit_class=3, path=str(bundle_root))
    control = workspace / ".wayfinder"
    manifest_path = control / "manifest.json"
    if manifest_path.exists() or manifest_path.is_symlink():
        raise WFError("initialize.manifest-exists", "a manifest already exists; use Update or repair the invalid manifest", exit_class=3, path=str(manifest_path))
    operations = control / "operations"
    if operations.exists():
        if operations.is_symlink() or not operations.is_dir() or any(operations.iterdir()):
            raise WFError("initialize.recovery-required", "existing initialization operation state requires recovery before planning", exit_class=5, path=str(operations))
    record_root = manifest["recordRoot"]
    targets = [".wayfinder/manifest.json"]
    targets.extend(_target_workspace_path(record_root, item["output"]) for item in proposal["documents"])
    for artifact in manifest["generatedArtifacts"]:
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str):
            targets.append(_target_workspace_path(record_root, artifact["path"]))
    if len({path_key(item) for item in targets}) != len(targets):
        raise WFError("initialize.target-collision", "planned targets collide by portable path identity", exit_class=2, actual=targets)
    absent: list[str] = []
    for target in targets:
        portable_path(target, "/preconditions/targets", exit_class=2)
        resolved = _physical_check(workspace, target, "/preconditions/targets", required=False, exit_class=3)
        if resolved.exists():
            raise WFError("initialize.target-exists", "every initialization target must be absent", exit_class=3, path=target)
        absent.append(target)
    module_roots: list[str] = []
    for index, module in enumerate(_expect_array(manifest["modules"], "/manifest/modules", exit_class=2)):
        if not isinstance(module, dict) or not isinstance(module.get("root"), str):
            continue
        target = _target_workspace_path(record_root, module["root"])
        portable_path(target, f"/manifest/modules/{index}/root", exit_class=2)
        resolved = _physical_check(workspace, target, f"/manifest/modules/{index}/root", required=False, exit_class=3)
        if resolved.exists():
            raise WFError("initialize.module-root-exists", "proposed module roots must be absent", exit_class=3, path=target)
        module_roots.append(target)
    return {"manifestAbsent": True, "targetsAbsent": absent, "moduleRootsAbsent": module_roots, "bundleAbsent": True, "canonicalBaseline": _resolve_initialization_baseline(workspace, manifest["canonicalBaseline"])}


def _source_bindings(workspace: Path, proposal: dict[str, Any]) -> dict[str, Any]:
    if proposal["mode"] == "fresh":
        return {"inventory": None, "intake": None}
    inventory_binding = proposal["sourceInventory"]
    intake_binding = proposal["intakeLedger"]
    inventory_path = _physical_check(workspace, inventory_binding["path"], "/sourceInventory/path", "file", required=True, exit_class=3)
    inventory_raw = inventory_path.read_bytes()
    inventory = strict_json_bytes(inventory_raw, path=str(inventory_path), exit_class=2)
    inventory_digest = sha256_bytes(canonical_json(inventory).encode("utf-8"))
    if inventory_digest != inventory_binding["sha256"]:
        raise WFError("initialize.inventory-digest", "source inventory binding is stale", exit_class=3, path=inventory_binding["path"], expected=inventory_binding["sha256"], actual=inventory_digest)
    inventory_obj = _expect_object(inventory, "/sourceInventory", exit_class=2)
    request = {
        "format": "wayfinder-source-inventory-request", "schemaVersion": 1,
        "selections": [item["path"] for item in _expect_array(inventory_obj.get("selections"), "/sourceInventory/selections", exit_class=2)],
        "targetRoots": inventory_obj.get("targetRoots"), "limits": inventory_obj.get("limits"),
    }
    normalized_request = _validate_inventory_request(request)
    current_inventory = build_inventory(workspace, normalized_request)
    if canonical_json(current_inventory) != canonical_json(inventory_obj):
        raise WFError("initialize.inventory-stale", "source inventory no longer matches the workspace", exit_class=3, path=inventory_binding["path"])
    ledger_path = _physical_check(workspace, intake_binding["path"], "/intakeLedger/path", "file", required=True, exit_class=3)
    ledger_value = strict_json_bytes(ledger_path.read_bytes(), path=str(ledger_path), exit_class=2)
    ledger = validate_intake_ledger(ledger_value, current_inventory, inventory_digest, workspace)
    ledger_digest = sha256_bytes(canonical_json(ledger).encode("utf-8"))
    if ledger_digest != intake_binding["sha256"]:
        raise WFError("initialize.intake-digest", "intake ledger binding is stale", exit_class=3, path=intake_binding["path"], expected=intake_binding["sha256"], actual=ledger_digest)
    ledger_paths = {item["path"] for item in ledger["sources"]}
    if any(path not in ledger_paths for path in proposal["materialSourcePaths"]):
        raise WFError("initialize.material-source-disposition", "every declared material source requires exactly one reviewed intake disposition", exit_class=3, field="/materialSourcePaths")
    return {"inventory": {"path": inventory_binding["path"], "sha256": inventory_digest, "value": current_inventory}, "intake": {"path": intake_binding["path"], "sha256": ledger_digest, "ledger": ledger}}


def _render_initial_record(workspace: Path, proposal: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    skill_root = Path(__file__).resolve().parents[2]
    rendered_documents: list[tuple[dict[str, Any], bytes]] = []
    for spec in proposal["documents"]:
        raw = _render_template(skill_root, spec["kind"], {"TITLE": spec["title"], "METADATA_BLOCK": _render_metadata(spec), "RELATIONSHIP_BLOCK": _render_relationships(spec), "CONTENT": _render_sections(spec)})
        parse_document(raw, spec["output"])
        rendered_documents.append((spec, raw))
    manifest_raw = (json.dumps(proposal["manifest"], ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="wayfinder-plan-") as temporary_raw:
        virtual = Path(temporary_raw)
        (virtual / ".wayfinder").mkdir()
        (virtual / ".wayfinder/manifest.json").write_bytes(manifest_raw)
        record_root = virtual if proposal["manifest"]["recordRoot"] == "." else virtual / PurePosixPath(proposal["manifest"]["recordRoot"])
        record_root.mkdir(parents=True, exist_ok=True)
        for module in proposal["manifest"]["modules"]:
            (record_root / PurePosixPath(module["root"])).mkdir(parents=True, exist_ok=True)
        baseline = proposal["manifest"]["canonicalBaseline"]
        if isinstance(baseline, dict) and baseline.get("kind") == "snapshot" and isinstance(baseline.get("path"), str):
            source = _physical_check(workspace, baseline["path"], "/manifest/canonicalBaseline/path", "file", required=True, exit_class=3)
            raw = source.read_bytes()
            if sha256_bytes(raw) != baseline.get("sha256"):
                raise WFError("initialize.baseline-stale", "snapshot baseline digest does not match", exit_class=3, path=baseline["path"])
            destination = virtual / PurePosixPath(baseline["path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        for spec, raw in rendered_documents:
            target = record_root / PurePosixPath(spec["output"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            parsed = parse_document(raw, spec["output"])
            for source in parsed["sources"]:
                original = source["fields"]["Original"]
                if not original.startswith("https://"):
                    source_path_real = _physical_check(workspace, original, "Original", "file", required=True, exit_class=3)
                    destination = virtual / PurePosixPath(original)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source_path_real.read_bytes())
        for artifact in proposal["manifest"]["generatedArtifacts"]:
            target = record_root / PurePosixPath(artifact["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"{}\n")
        record = load_record(virtual)
        for document in record["documents"]:
            if document["generatedRegions"]:
                (record_root / PurePosixPath(document["path"])).write_bytes(_replace_regions(record, document))
        record = load_record(virtual)
        catalog_raw = render_catalog(record)
        for artifact in proposal["manifest"]["generatedArtifacts"]:
            if artifact["generator"] == "document-catalog-v1":
                (record_root / PurePosixPath(artifact["path"])).write_bytes(catalog_raw)
        record = load_record(virtual)
        validation = validate_record(record)
        final_documents = [(item, (record_root / PurePosixPath(item["output"])).read_bytes()) for item in proposal["documents"]]
        artifacts = [(item, (record_root / PurePosixPath(item["path"])).read_bytes()) for item in proposal["manifest"]["generatedArtifacts"]]
        entry_raw = (record_root / PurePosixPath(proposal["manifest"]["entrypoint"])).read_text(encoding="utf-8")
        for heading in ("## Authority boundary", "## Next planning step"):
            if heading not in entry_raw.splitlines():
                raise WFError("proposal.knowledge-map", "knowledge map lacks a required durable boundary or resumption section", exit_class=3, path=proposal["manifest"]["entrypoint"], expected=heading)
        for module in proposal["manifest"]["modules"]:
            if module["id"].startswith("local-"):
                local_raw = (record_root / PurePosixPath(module["entrypoint"])).read_text(encoding="utf-8")
                required = {"## Purpose", "## Authority boundary", "## Audience", "## Relationship to standard modules"}
                if not required.issubset(set(local_raw.splitlines())):
                    raise WFError("proposal.local-module-boundary", "local module entrypoint lacks its required independent boundary declaration", exit_class=3, path=module["entrypoint"], expected=sorted(required))
    payloads: list[dict[str, Any]] = []
    for spec, raw in final_documents:
        template_raw = (skill_root / f"assets/contract-v1/templates/{spec['kind']}.md").read_bytes()
        payloads.append({"targetPath": _target_workspace_path(proposal["manifest"]["recordRoot"], spec["output"]), "role": "authored-document", "documentId": spec["id"], "producer": {"id": f"template-{spec['kind']}-v1", "sha256": sha256_bytes(template_raw)}, "raw": raw})
    for artifact, raw in artifacts:
        payloads.append({"targetPath": _target_workspace_path(proposal["manifest"]["recordRoot"], artifact["path"]), "role": "generated-artifact", "documentId": None, "producer": {"id": artifact["generator"], "sha256": sha256_bytes((skill_root / "references/contracts/v1.md").read_bytes())}, "raw": raw})
    manifest_schema = (skill_root / "assets/contract-v1/schemas/manifest.schema.json").read_bytes()
    payloads.append({"targetPath": ".wayfinder/manifest.json", "role": "manifest", "documentId": None, "producer": {"id": "manifest-schema-v1", "sha256": sha256_bytes(manifest_schema)}, "raw": manifest_raw})
    return payloads, validation


def _initialization_review(proposal: dict[str, Any], target_paths: list[str]) -> dict[str, Any]:
    return {
        "profile": proposal["profile"],
        "concernHomes": proposal["concerns"],
        "epistemicStates": proposal["epistemicStates"],
        "omittedModules": proposal["omittedModules"],
        "authorityBoundary": proposal["authorityBoundary"],
        "materialInferences": proposal["materialInferences"],
        "interviewResume": proposal["interviewResume"],
        "semanticReadiness": proposal["semanticReadiness"],
        "targetTree": sorted(target_paths, key=lambda item: item.encode("utf-8")),
    }


def _render_initialization_preview(plan: dict[str, Any], plan_digest: str, operation_id: str, payloads: list[dict[str, Any]]) -> bytes:
    review = plan["review"]
    lines = [
        "# Wayfinder initialization review", "",
        f"- **Plan digest:** `sha256:{plan_digest}`",
        f"- **Operation ID:** `{operation_id}`",
        f"- **Mode:** `{plan['mode']}`",
        f"- **Profile:** `{review['profile']['id']}` (confirmed)",
        f"- **Workspace:** `{plan['workspace']['workspaceRoot']}`",
        f"- **Record root:** `{plan['manifest']['recordRoot']}`", "",
        "## Exact target tree", "",
    ]
    lines.extend(f"- `{path}`" for path in review["targetTree"])
    lines.extend(["", "## Concern-to-home map", ""])
    lines.extend(f"- `{item['id']}` → `{item['homeId']}` — {item['statement']}" for item in review["concernHomes"])
    lines.extend(["", "## Explicit unresolved and epistemic states", ""])
    lines.extend(f"- **{item['state']}:** {item['statement']} (`{item['targetId']}`)" for item in review["epistemicStates"])
    if not review["epistemicStates"]:
        lines.append("- No special epistemic state was declared in this proposal.")
    lines.extend(["", "## Omitted standard modules", ""])
    lines.extend(f"- `{item['id']}` — {item['reason']}" for item in review["omittedModules"])
    lines.extend(["", "## Authority boundary", "", review["authorityBoundary"]["statement"], "", "## Material agent inferences", ""])
    lines.extend(f"- {item['statement']} — Basis: {item['basis']} (confirmed)" for item in review["materialInferences"])
    if not review["materialInferences"]:
        lines.append("- None declared.")
    lines.extend(["", "## Preconditions", ""])
    lines.extend(f"- `{path}` is absent." for path in plan["preconditions"]["targetsAbsent"])
    lines.extend(["", "## Ordered future operation", ""])
    lines.extend(f"{index}. `{item['action']}` `{item['path']}`" for index, item in enumerate(plan["operations"], 1))
    lines.extend(["", "## Exact authored document payloads", ""])
    by_bundle = {item["bundlePath"]: raw_item["raw"] for item, raw_item in zip(plan["payloads"], payloads)}
    for item in plan["payloads"]:
        if item["role"] != "authored-document":
            continue
        raw = by_bundle[item["bundlePath"]]
        lines.extend([f"### `{item['targetPath']}` — `{item['documentId']}`", "", "```markdown", raw.decode("utf-8").rstrip("\n"), "```", ""])
    lines.extend(["## Interview resumption", "", review["interviewResume"]["summary"], "", "Recommended focus: " + ", ".join(f"`{item}`" for item in review["interviewResume"]["recommendedFocusIds"]), ""])
    return "\n".join(lines).encode("utf-8")


def command_initialize_plan(workspace_root_arg: str | None, proposal_arg: str | None, bundle_root_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is None or proposal_arg is None or bundle_root_arg is None:
        raise WFError("command.arguments", "initialize-plan requires --workspace-root PATH --proposal FILE --bundle-root PATH", exit_class=2)
    supplied = Path(workspace_root_arg)
    if not supplied.exists() or not supplied.is_dir():
        raise WFError("initialize.workspace-root", "workspace root must be an existing directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    proposal_path, proposal_raw = _read_control_file(proposal_arg, "proposal")
    proposal = _validate_initialization_proposal(strict_json_bytes(proposal_raw, path=str(proposal_path), exit_class=2))
    bundle_candidate = Path(bundle_root_arg)
    if not bundle_candidate.is_absolute():
        bundle_candidate = Path.cwd() / bundle_candidate
    nearest_existing = bundle_candidate
    while not nearest_existing.exists() and not nearest_existing.is_symlink() and nearest_existing != nearest_existing.parent:
        nearest_existing = nearest_existing.parent
    if nearest_existing.is_symlink():
        raise WFError("initialize.bundle-symlink", "bundle path components may not be symbolic links", exit_class=3, path=str(nearest_existing))
    bundle_root = bundle_candidate.resolve(strict=False)
    try:
        within_workspace = os.path.commonpath((str(workspace), str(bundle_root))) == str(workspace)
    except ValueError:
        within_workspace = False
    if within_workspace:
        raise WFError("initialize.bundle-location", "bundle root must be outside the workspace and all final record paths", exit_class=2, path=str(bundle_root))
    preconditions = _initialization_preflight(workspace, proposal, bundle_root)
    bindings = _source_bindings(workspace, proposal)
    payload_raw, validation = _render_initial_record(workspace, proposal)
    document_ids = {item["id"] for item in proposal["documents"]}
    question_ids = {question["id"] for item in proposal["documents"] for question in item["questions"]}
    evidence_keys: dict[str, int] = {}
    for document in proposal["documents"]:
        for source in document["sources"]:
            evidence_keys[source["key"]] = evidence_keys.get(source["key"], 0) + 1
    if bindings["intake"] is not None:
        for source in bindings["intake"]["ledger"]["sources"]:
            if any(item not in document_ids for item in source["targetIds"]) or any(item not in question_ids for item in source["questionIds"]):
                raise WFError("initialize.intake-binding", "intake target or question ID is absent from the proposal", exit_class=3, path=source["path"])
            if any(evidence_keys.get(item) != 1 for item in source["evidenceKeys"]):
                raise WFError("initialize.intake-binding", "intake evidence key must resolve uniquely in the proposal", exit_class=3, path=source["path"])
    payloads: list[dict[str, Any]] = []
    for index, item in enumerate(payload_raw, 1):
        raw = item.pop("raw")
        bundle_path = f"payload/{index:04d}"
        payloads.append({
            "bundlePath": bundle_path, "targetPath": item["targetPath"], "role": item["role"],
            "documentId": item["documentId"], "byteLength": len(raw), "sha256": sha256_bytes(raw), "producer": item["producer"],
        })
        item["raw"] = raw
    if len({path_key(item["targetPath"]) for item in payloads}) != len(payloads):
        raise WFError("initialize.payload-duplicate", "payload targets must be unique", exit_class=2)
    non_manifest = [item for item in payloads if item["role"] != "manifest"]
    manifest_payload = [item for item in payloads if item["role"] == "manifest"]
    if len(manifest_payload) != 1:
        raise WFError("initialize.payload-manifest", "plan requires exactly one manifest payload", exit_class=70)
    directories = sorted({posixpath.dirname(item["targetPath"]) for item in payloads if posixpath.dirname(item["targetPath"])}, key=lambda item: (len(PurePosixPath(item).parts), item.encode("utf-8")))
    operations = [{"action": "create-directory", "path": item} for item in directories]
    operations.extend({"action": "create-file", "path": item["targetPath"], "payload": item["bundlePath"], "sha256": item["sha256"]} for item in non_manifest)
    operations.append({"action": "publish-manifest", "path": manifest_payload[0]["targetPath"], "payload": manifest_payload[0]["bundlePath"], "sha256": manifest_payload[0]["sha256"]})
    skill_root = Path(__file__).resolve().parents[2]
    contract_digest = sha256_bytes((skill_root / CONTRACT_PATH).read_bytes())
    plan = {
        "format": "wayfinder-initialize-plan", "schemaVersion": 1, "contractVersion": CONTRACT_VERSION,
        "contractSha256": contract_digest, "proposalSha256": sha256_bytes(canonical_json(proposal).encode("utf-8")),
        "mode": proposal["mode"], "effectiveDate": proposal["effectiveDate"],
        "workspace": {"workspaceRoot": str(workspace), "recordRoot": str((workspace if proposal["manifest"]["recordRoot"] == "." else workspace / PurePosixPath(proposal["manifest"]["recordRoot"])).resolve(strict=False))},
        "manifest": proposal["manifest"], "sourceBindings": {
            "inventory": None if bindings["inventory"] is None else {"path": bindings["inventory"]["path"], "sha256": bindings["inventory"]["sha256"], "bundlePath": "inventory.json"},
            "intake": None if bindings["intake"] is None else {"path": bindings["intake"]["path"], "sha256": bindings["intake"]["sha256"], "bundlePath": "intake.json"},
            "materialSourcePaths": proposal["materialSourcePaths"],
        },
        "preconditions": preconditions, "review": _initialization_review(proposal, [item["targetPath"] for item in payloads]),
        "validation": {"documents": validation["documents"], "questions": validation["questions"], "warnings": validation["warnings"], "catalogSha256": validation["catalogSha256"]},
        "payloads": payloads, "operations": operations,
    }
    plan_raw = canonical_json(plan).encode("utf-8")
    plan_digest = sha256_bytes(plan_raw)
    injected_operation = os.environ.get("WAYFINDER_TEST_OPERATION_ID") if os.environ.get("WAYFINDER_TEST_MODE") == "1" else None
    operation_id = injected_operation or f"wfinit-{plan_digest[:24]}"
    if injected_operation is not None and re.fullmatch(r"wfinit-test-[a-z0-9]+(?:-[a-z0-9]+)*", injected_operation) is None:
        raise WFError("initialize.operation-id", "maintainer-injected operation ID is invalid", exit_class=2)
    preview_raw = _render_initialization_preview(plan, plan_digest, operation_id, payload_raw)
    attachment_files: list[tuple[str, bytes]] = []
    if bindings["inventory"] is not None:
        attachment_files.append(("inventory.json", canonical_json(bindings["inventory"]["value"]).encode("utf-8")))
        attachment_files.append(("intake.json", canonical_json(bindings["intake"]["ledger"]).encode("utf-8")))
    bundle_files = [("plan.json", plan_raw), ("preview.md", preview_raw), *attachment_files] + [(item["bundlePath"], raw_item["raw"]) for item, raw_item in zip(payloads, payload_raw)]
    try:
        bundle_root.mkdir(parents=False, exist_ok=False)
    except FileExistsError:
        raise WFError("initialize.bundle-exists", "initialize-plan never overwrites an existing bundle target", exit_class=3, path=str(bundle_root)) from None
    except FileNotFoundError:
        raise WFError("initialize.bundle-parent", "bundle parent directory must already exist", exit_class=3, path=str(bundle_root.parent)) from None
    (bundle_root / "payload").mkdir(exist_ok=False)
    for relative, raw in bundle_files:
        target = bundle_root / PurePosixPath(relative)
        if relative.startswith("payload/"):
            _exclusive_declared_write(target, raw)
        else:
            with target.open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
    return {
        "planSha256": plan_digest, "operationId": operation_id, "bundleRoot": str(bundle_root),
        "plan": "plan.json", "preview": {"path": "preview.md", "byteLength": len(preview_raw), "sha256": sha256_bytes(preview_raw)},
        "payloadCount": len(payloads), "targetTree": plan["review"]["targetTree"], "writes": [{"path": relative, "byteLength": len(raw), "sha256": sha256_bytes(raw)} for relative, raw in bundle_files],
    }


def _utc_now() -> str:
    injected = os.environ.get("WAYFINDER_TEST_CLOCK")
    if injected is not None:
        if os.environ.get("WAYFINDER_TEST_MODE") != "1":
            raise WFError("initialize.test-control", "maintainer clock control requires test mode", exit_class=2)
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", injected) is None:
            raise WFError("initialize.test-control", "maintainer clock must use UTC RFC 3339 whole seconds", exit_class=2)
        return injected
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _failure_boundary(name: str) -> None:
    boundary = os.environ.get("WAYFINDER_TEST_FAILURE_BOUNDARY")
    if boundary is None:
        return
    if os.environ.get("WAYFINDER_TEST_MODE") != "1":
        raise WFError("initialize.test-control", "maintainer failure control requires test mode", exit_class=2)
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", boundary) is None:
        raise WFError("initialize.test-control", "maintainer failure boundary is invalid", exit_class=2)
    if boundary == name:
        raise WFError(
            "initialize.interrupted",
            "maintainer-injected interruption left explicit recovery state",
            exit_class=5,
            actual=name,
            remediation="Run initialize-recover with inspect, then explicitly choose resume or rollback.",
        )


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _mkdir_private(path: Path) -> None:
    path.mkdir(mode=0o700, exist_ok=False)
    try:
        path.chmod(0o700)
    except OSError:
        pass
    _fsync_directory(path.parent)


def _read_exact_regular(path: Path, label: str) -> bytes:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        raise WFError("initialize.bundle-missing", "required bundle file is missing", exit_class=3, path=str(path), actual=label) from None
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise WFError("initialize.bundle-type", "bundle entries must be non-symbolic regular files", exit_class=3, path=str(path), actual=label)
    return path.read_bytes()


def _validate_apply_plan(value: Any, raw: bytes, workspace: Path, supplied_digest: str) -> dict[str, Any]:
    plan = _expect_object(value, "/", exit_class=2)
    fields = (
        "format", "schemaVersion", "contractVersion", "contractSha256", "proposalSha256", "mode", "effectiveDate",
        "workspace", "manifest", "sourceBindings", "preconditions", "review", "validation", "payloads", "operations",
    )
    _closed(plan, fields, "/", exit_class=2)
    _expect_literal(plan["format"], "wayfinder-initialize-plan", "/format", "apply.plan-format", exit_class=2)
    _expect_literal(plan["schemaVersion"], 1, "/schemaVersion", "apply.plan-version", exit_class=2)
    _expect_literal(plan["contractVersion"], CONTRACT_VERSION, "/contractVersion", "apply.contract-version", exit_class=2)
    if canonical_json(plan).encode("utf-8") != raw:
        raise WFError("apply.plan-canonical", "plan.json must be exact canonical JSON without a terminal newline", exit_class=2)
    actual_digest = sha256_bytes(raw)
    if not isinstance(supplied_digest, str) or not HEX_RE.fullmatch(supplied_digest) or supplied_digest != actual_digest:
        raise WFError("apply.plan-digest", "supplied plan digest does not match exact plan bytes", exit_class=3, expected=supplied_digest, actual=actual_digest)
    skill_root = Path(__file__).resolve().parents[2]
    current_contract = sha256_bytes((skill_root / CONTRACT_PATH).read_bytes())
    if not isinstance(plan["contractSha256"], str) or plan["contractSha256"] != current_contract:
        raise WFError("apply.contract-digest", "plan contract digest does not match the executing package", exit_class=3, expected=current_contract, actual=plan["contractSha256"])
    if plan["mode"] not in {"fresh", "source-assisted"}:
        raise WFError("apply.plan-mode", "plan mode is unsupported", exit_class=2, actual=plan["mode"])
    _calendar_date(plan["effectiveDate"], "/effectiveDate", exit_class=2)
    workspace_obj = _expect_object(plan["workspace"], "/workspace", exit_class=2)
    _closed(workspace_obj, ("workspaceRoot", "recordRoot"), "/workspace", exit_class=2)
    if workspace_obj["workspaceRoot"] != str(workspace):
        raise WFError("apply.workspace-binding", "plan is bound to a different physical workspace", exit_class=3, expected=workspace_obj["workspaceRoot"], actual=str(workspace))
    expected_record = workspace if plan["manifest"].get("recordRoot") == "." else workspace / PurePosixPath(str(plan["manifest"].get("recordRoot", "")))
    if workspace_obj["recordRoot"] != str(expected_record.resolve(strict=False)):
        raise WFError("apply.record-root-binding", "plan record-root identity is inconsistent", exit_class=3)

    payloads = _expect_array(plan["payloads"], "/payloads", exit_class=2)
    if not payloads:
        raise WFError("apply.payloads", "plan requires at least one payload", exit_class=2)
    payload_paths: set[tuple[str, ...]] = set()
    target_paths: set[tuple[str, ...]] = set()
    normalized_payloads: list[dict[str, Any]] = []
    for index, value_item in enumerate(payloads):
        pointer = f"/payloads/{index}"
        item = _expect_object(value_item, pointer, exit_class=2)
        _closed(item, ("bundlePath", "targetPath", "role", "documentId", "byteLength", "sha256", "producer"), pointer, exit_class=2)
        bundle_path = portable_path(item["bundlePath"], f"{pointer}/bundlePath", exit_class=2)
        target_path = portable_path(item["targetPath"], f"{pointer}/targetPath", exit_class=2)
        if not is_within(bundle_path, "payload", allow_equal=False):
            raise WFError("apply.payload-path", "payload must be beneath bundle payload/", exit_class=2, field=f"{pointer}/bundlePath")
        if path_key(bundle_path) in payload_paths or path_key(target_path) in target_paths:
            raise WFError("apply.payload-duplicate", "payload or target path is duplicated", exit_class=2, field=pointer)
        payload_paths.add(path_key(bundle_path))
        target_paths.add(path_key(target_path))
        if item["role"] not in {"authored-document", "generated-artifact", "manifest"}:
            raise WFError("apply.payload-role", "payload role is unsupported", exit_class=2, field=f"{pointer}/role")
        if item["role"] == "manifest" and (target_path != ".wayfinder/manifest.json" or item["documentId"] is not None):
            raise WFError("apply.manifest-payload", "manifest payload has an invalid target or document identity", exit_class=2, field=pointer)
        if item["role"] == "authored-document":
            _identifier(item["documentId"], "document", f"{pointer}/documentId", exit_class=2)
        elif item["documentId"] is not None:
            raise WFError("apply.payload-document-id", "only authored payloads have document IDs", exit_class=2, field=f"{pointer}/documentId")
        if type(item["byteLength"]) is not int or item["byteLength"] < 0:
            raise WFError("json.type", "payload byteLength must be a nonnegative integer", exit_class=2, field=f"{pointer}/byteLength")
        if not isinstance(item["sha256"], str) or not HEX_RE.fullmatch(item["sha256"]):
            raise WFError("apply.payload-digest", "payload digest must be lowercase 64-hex", exit_class=2, field=f"{pointer}/sha256")
        producer = _expect_object(item["producer"], f"{pointer}/producer", exit_class=2)
        _closed(producer, ("id", "sha256"), f"{pointer}/producer", exit_class=2)
        if not isinstance(producer["id"], str) or not producer["id"] or not isinstance(producer["sha256"], str) or not HEX_RE.fullmatch(producer["sha256"]):
            raise WFError("apply.producer", "payload producer identity is invalid", exit_class=2, field=f"{pointer}/producer")
        normalized_payloads.append(item)
    if sum(1 for item in normalized_payloads if item["role"] == "manifest") != 1:
        raise WFError("apply.manifest-payload", "plan requires exactly one manifest payload", exit_class=2)

    expected_directories = sorted(
        {posixpath.dirname(item["targetPath"]) for item in normalized_payloads if posixpath.dirname(item["targetPath"])},
        key=lambda item: (len(PurePosixPath(item).parts), item.encode("utf-8")),
    )
    non_manifest = [item for item in normalized_payloads if item["role"] != "manifest"]
    manifest_item = next(item for item in normalized_payloads if item["role"] == "manifest")
    expected_operations = [{"action": "create-directory", "path": item} for item in expected_directories]
    expected_operations.extend({"action": "create-file", "path": item["targetPath"], "payload": item["bundlePath"], "sha256": item["sha256"]} for item in non_manifest)
    expected_operations.append({"action": "publish-manifest", "path": manifest_item["targetPath"], "payload": manifest_item["bundlePath"], "sha256": manifest_item["sha256"]})
    if plan["operations"] != expected_operations:
        raise WFError("apply.operation-order", "operation list is not the exact declarative manifest-last order", exit_class=2)
    preconditions = _expect_object(plan["preconditions"], "/preconditions", exit_class=2)
    _closed(preconditions, ("manifestAbsent", "targetsAbsent", "moduleRootsAbsent", "bundleAbsent", "canonicalBaseline"), "/preconditions", exit_class=2)
    if preconditions["manifestAbsent"] is not True or preconditions["bundleAbsent"] is not True:
        raise WFError("apply.preconditions", "plan precondition constants are invalid", exit_class=2)
    target_absent = _expect_array(preconditions["targetsAbsent"], "/preconditions/targetsAbsent", exit_class=2)
    expected_absent = [manifest_item["targetPath"], *(item["targetPath"] for item in non_manifest)]
    if target_absent != expected_absent:
        raise WFError("apply.preconditions", "recorded target-absence set differs from payload targets", exit_class=2)
    manifest_obj = _expect_object(plan["manifest"], "/manifest", exit_class=2)
    module_roots = []
    modules_value = manifest_obj.get("modules")
    if not isinstance(modules_value, list):
        raise WFError("json.type", "manifest modules must be an array", exit_class=2, field="/manifest/modules")
    record_root_value = manifest_obj.get("recordRoot")
    portable_path(record_root_value, "/manifest/recordRoot", allow_dot=True, exit_class=2)
    for index, module in enumerate(modules_value):
        if not isinstance(module, dict) or not isinstance(module.get("root"), str):
            raise WFError("json.type", "manifest module root is invalid", exit_class=2, field=f"/manifest/modules/{index}/root")
        module_root = module["root"] if record_root_value == "." else f"{record_root_value}/{module['root']}"
        module_roots.append(module_root)
    if preconditions["moduleRootsAbsent"] != module_roots:
        raise WFError("apply.preconditions", "recorded module-root absence set differs from the manifest", exit_class=2)
    baseline_obj = _expect_object(preconditions["canonicalBaseline"], "/preconditions/canonicalBaseline", exit_class=2)
    if baseline_obj.get("kind") not in {"git-ref", "snapshot"}:
        raise WFError("apply.preconditions", "recorded canonical baseline is invalid", exit_class=2)
    source_bindings = _expect_object(plan["sourceBindings"], "/sourceBindings", exit_class=2)
    _closed(source_bindings, ("inventory", "intake", "materialSourcePaths"), "/sourceBindings", exit_class=2)
    review = _expect_object(plan["review"], "/review", exit_class=2)
    _closed(review, ("profile", "concernHomes", "epistemicStates", "omittedModules", "authorityBoundary", "materialInferences", "interviewResume", "semanticReadiness", "targetTree"), "/review", exit_class=2)
    readiness = _expect_object(review["semanticReadiness"], "/review/semanticReadiness", exit_class=2)
    readiness_fields = ("identityAndIntent", "outcomes", "boundaries", "people", "currentKnowledge", "consequentialUnknowns", "structure", "publicationBasis")
    _closed(readiness, readiness_fields, "/review/semanticReadiness", exit_class=2)
    if any(value not in {"supported", "explicit-unresolved"} for value in readiness.values()):
        raise WFError("apply.semantic-readiness", "plan readiness predicates are invalid", exit_class=2)
    authority = _expect_object(review["authorityBoundary"], "/review/authorityBoundary", exit_class=2)
    if authority.get("competingCurrentAuthority") != []:
        raise WFError("apply.semantic-readiness", "plan retains competing current authority", exit_class=3)
    resume = _expect_object(review["interviewResume"], "/review/interviewResume", exit_class=2)
    if resume.get("nextWorkflow") != "interview" or not isinstance(resume.get("recommendedFocusIds"), list) or not resume["recommendedFocusIds"]:
        raise WFError("apply.interview-handoff", "plan lacks durable Interview resumption data", exit_class=2)
    if review["targetTree"] != sorted((item["targetPath"] for item in normalized_payloads), key=lambda item: item.encode("utf-8")):
        raise WFError("apply.target-tree", "review target tree differs from payload targets", exit_class=2)
    validation_obj = _expect_object(plan["validation"], "/validation", exit_class=2)
    _closed(validation_obj, ("documents", "questions", "warnings", "catalogSha256"), "/validation", exit_class=2)
    if type(validation_obj["documents"]) is not int or validation_obj["documents"] < 1 or type(validation_obj["questions"]) is not int or validation_obj["questions"] < 0 or not isinstance(validation_obj["warnings"], list) or not isinstance(validation_obj["catalogSha256"], str) or not HEX_RE.fullmatch(validation_obj["catalogSha256"]):
        raise WFError("apply.validation-projection", "plan validation projection is invalid", exit_class=2)
    return plan


def _external_bundle(bundle_root_arg: str, workspace: Path, supplied_digest: str) -> tuple[Path, bytes, dict[str, Any], dict[str, bytes]]:
    bundle = Path(bundle_root_arg)
    if not bundle.is_absolute():
        bundle = Path.cwd() / bundle
    if bundle.is_symlink() or not bundle.exists() or not bundle.is_dir():
        raise WFError("initialize.bundle-root", "bundle root must be an existing non-symbolic directory", exit_class=3, path=str(bundle))
    bundle = bundle.resolve(strict=True)
    try:
        if os.path.commonpath((str(workspace), str(bundle))) == str(workspace):
            raise WFError("initialize.bundle-location", "apply bundle must remain outside the target workspace", exit_class=2, path=str(bundle))
    except ValueError:
        pass
    plan_raw = _read_exact_regular(bundle / "plan.json", "plan.json")
    plan_value = strict_json_bytes(plan_raw, path=str(bundle / "plan.json"), exit_class=2)
    plan = _validate_apply_plan(plan_value, plan_raw, workspace, supplied_digest)
    expected = {"plan.json", "preview.md", *(item["bundlePath"] for item in plan["payloads"])}
    for field in ("inventory", "intake"):
        binding = plan["sourceBindings"].get(field) if isinstance(plan["sourceBindings"], dict) else None
        if binding is not None:
            expected.add(binding["bundlePath"])
    observed: set[str] = set()
    for entry in bundle.rglob("*"):
        relative = entry.relative_to(bundle).as_posix()
        if entry.is_symlink():
            raise WFError("initialize.bundle-symlink", "bundle may not contain symbolic links", exit_class=3, path=relative)
        if entry.is_file():
            observed.add(relative)
        elif entry.is_dir() and relative != "payload":
            raise WFError("initialize.bundle-extra", "bundle contains an undeclared directory", exit_class=3, path=relative)
    if observed != expected:
        raise WFError("initialize.bundle-members", "bundle members differ from the exact plan-declared bundle", exit_class=3, expected=sorted(expected), actual=sorted(observed))
    raw_files = {relative: _read_exact_regular(bundle / PurePosixPath(relative), relative) for relative in sorted(expected)}
    for item in plan["payloads"]:
        raw = raw_files[item["bundlePath"]]
        if len(raw) != item["byteLength"] or sha256_bytes(raw) != item["sha256"]:
            raise WFError("apply.payload-digest", "bundle payload bytes differ from the confirmed plan", exit_class=3, path=item["bundlePath"], expected=item["sha256"], actual=sha256_bytes(raw))
    return bundle, plan_raw, plan, raw_files


def _baseline_recheck(workspace: Path, plan: dict[str, Any]) -> None:
    current = _resolve_initialization_baseline(workspace, plan["manifest"]["canonicalBaseline"])
    if current != plan["preconditions"]["canonicalBaseline"]:
        raise WFError("apply.baseline-stale", "canonical baseline changed after planning", exit_class=3, expected=plan["preconditions"]["canonicalBaseline"], actual=current)


def _source_recheck(workspace: Path, plan: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any] | None:
    bindings = _expect_object(plan["sourceBindings"], "/sourceBindings", exit_class=2)
    _closed(bindings, ("inventory", "intake", "materialSourcePaths"), "/sourceBindings", exit_class=2)
    if plan["mode"] == "fresh":
        if bindings != {"inventory": None, "intake": None, "materialSourcePaths": []}:
            raise WFError("apply.source-binding", "fresh plan contains source bindings", exit_class=2)
        return None
    inventory_binding = _expect_object(bindings["inventory"], "/sourceBindings/inventory", exit_class=2)
    intake_binding = _expect_object(bindings["intake"], "/sourceBindings/intake", exit_class=2)
    for pointer, binding in (("inventory", inventory_binding), ("intake", intake_binding)):
        _closed(binding, ("path", "sha256", "bundlePath"), f"/sourceBindings/{pointer}", exit_class=2)
        source_path(binding["path"], f"/sourceBindings/{pointer}/path")
        portable_path(binding["bundlePath"], f"/sourceBindings/{pointer}/bundlePath", exit_class=2)
        if not isinstance(binding["sha256"], str) or not HEX_RE.fullmatch(binding["sha256"]):
            raise WFError("apply.source-binding", "source binding digest is invalid", exit_class=2, field=f"/sourceBindings/{pointer}/sha256")
    inventory = strict_json_bytes(files[inventory_binding["bundlePath"]], path=inventory_binding["bundlePath"], exit_class=3)
    inventory_digest = sha256_bytes(canonical_json(inventory).encode("utf-8"))
    if inventory_digest != inventory_binding["sha256"]:
        raise WFError("apply.inventory-digest", "imported inventory differs from the confirmed plan", exit_class=3)
    request = {
        "format": "wayfinder-source-inventory-request", "schemaVersion": 1,
        "selections": [item["path"] for item in inventory["selections"]],
        "targetRoots": inventory["targetRoots"], "limits": inventory["limits"],
    }
    current = build_inventory(workspace, _validate_inventory_request(request))
    if canonical_json(current) != canonical_json(inventory):
        raise WFError("apply.inventory-stale", "source inventory changed after planning", exit_class=3)
    ledger = strict_json_bytes(files[intake_binding["bundlePath"]], path=intake_binding["bundlePath"], exit_class=3)
    ledger_digest = sha256_bytes(canonical_json(ledger).encode("utf-8"))
    if ledger_digest != intake_binding["sha256"]:
        raise WFError("apply.intake-digest", "imported intake ledger differs from the confirmed plan", exit_class=3)
    normalized = validate_intake_ledger(ledger, inventory, inventory_digest, workspace)
    material = bindings["materialSourcePaths"]
    if not isinstance(material, list) or sorted(material) != sorted(item["path"] for item in normalized["sources"]):
        raise WFError("apply.material-source-disposition", "material source dispositions differ from the plan", exit_class=3)
    return {"inventory": inventory, "ledger": normalized}


def _target_recheck(workspace: Path, plan: dict[str, Any], *, allow_control: bool = False) -> None:
    manifest = workspace / ".wayfinder/manifest.json"
    if manifest.exists() or manifest.is_symlink():
        raise WFError("apply.manifest-exists", "manifest must remain absent until publication", exit_class=3, path=str(manifest))
    for item in plan["payloads"]:
        relative = item["targetPath"]
        if allow_control and relative == ".wayfinder/manifest.json":
            continue
        target = _physical_check(workspace, relative, "/preconditions/targetsAbsent", exit_class=3)
        if target.exists() or target.is_symlink():
            raise WFError("apply.target-exists", "planned target is no longer absent", exit_class=3, path=relative)
    for relative in plan["preconditions"]["moduleRootsAbsent"]:
        target = _physical_check(workspace, relative, "/preconditions/moduleRootsAbsent", exit_class=3)
        if target.exists() or target.is_symlink():
            raise WFError("apply.module-root-exists", "planned module root is no longer absent", exit_class=3, path=relative)


def _lock_path(workspace: Path) -> Path:
    return workspace / ".wayfinder/initialize.lock"


def _windows_process_alive(
    pid: int,
    *,
    kernel32: Any | None = None,
    get_last_error: Any | None = None,
) -> bool:
    if pid <= 0 or pid > 0xFFFFFFFF:
        return False
    if kernel32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if get_last_error is None:
        get_last_error = ctypes.get_last_error
    handle_type = ctypes.c_void_p
    dword_type = ctypes.c_uint32
    bool_type = ctypes.c_int32
    kernel32.OpenProcess.argtypes = (dword_type, bool_type, dword_type)
    kernel32.OpenProcess.restype = handle_type
    kernel32.WaitForSingleObject.argtypes = (handle_type, dword_type)
    kernel32.WaitForSingleObject.restype = dword_type
    kernel32.CloseHandle.argtypes = (handle_type,)
    kernel32.CloseHandle.restype = bool_type
    handle = kernel32.OpenProcess(0x00100000, False, pid)
    if not handle:
        error = get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER
            return False
        return True  # access denied and every other indeterminate failure
    try:
        result = kernel32.WaitForSingleObject(handle, 0)
        if result == 0x00000102:  # WAIT_TIMEOUT
            return True
        if result == 0x00000000:  # WAIT_OBJECT_0
            return False
        return True  # WAIT_FAILED and every unexpected result are indeterminate
    finally:
        kernel32.CloseHandle(handle)


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return _windows_process_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_lock(path: Path) -> dict[str, Any]:
    value = strict_json_bytes(_read_exact_regular(path, "initialize.lock"), path=str(path), exit_class=5)
    obj = _expect_object(value, "/", exit_class=5)
    _closed(obj, ("format", "schemaVersion", "operationId", "planSha256", "owner"), "/", exit_class=5)
    _expect_literal(obj["format"], LOCK_FORMAT, "/format", "lock.format", exit_class=5)
    _expect_literal(obj["schemaVersion"], 1, "/schemaVersion", "lock.version", exit_class=5)
    owner = _expect_object(obj["owner"], "/owner", exit_class=5)
    _closed(owner, ("host", "pid", "token"), "/owner", exit_class=5)
    if not isinstance(owner["host"], str) or type(owner["pid"]) is not int or not isinstance(owner["token"], str):
        raise WFError("lock.owner", "operation lock owner is invalid", exit_class=5)
    return obj


def _acquire_initialize_lock(workspace: Path, operation_id: str, plan_digest: str, *, recovery: bool = False) -> tuple[Path, str, bool]:
    control = workspace / ".wayfinder"
    control_created = False
    if control.exists() or control.is_symlink():
        if control.is_symlink() or not control.is_dir():
            raise WFError("path.symlink", ".wayfinder must be a non-symbolic directory", exit_class=3, path=str(control))
    else:
        _mkdir_private(control)
        control_created = True
    lock_path = _lock_path(workspace)
    if lock_path.exists() or lock_path.is_symlink():
        try:
            current = _read_lock(lock_path)
        except WFError:
            raise WFError("lock.manual-recovery", "operation lock is malformed and cannot be reclaimed automatically", exit_class=5, path=str(lock_path)) from None
        owner = current["owner"]
        if not recovery or current["operationId"] != operation_id or current["planSha256"] != plan_digest or owner["host"] != socket.gethostname():
            raise WFError("lock.contention", "another initialization owner holds the operation lock", exit_class=5, path=str(lock_path), actual=current["operationId"])
        if _process_alive(owner["pid"]):
            raise WFError("lock.contention", "another initialization owner holds the operation lock", exit_class=5, path=str(lock_path), actual=current["operationId"])
        lock_path.unlink()
        _fsync_directory(lock_path.parent)
    token = secrets.token_hex(16)
    lock = {
        "format": LOCK_FORMAT, "schemaVersion": 1, "operationId": operation_id, "planSha256": plan_digest,
        "owner": {"host": socket.gethostname(), "pid": os.getpid(), "token": token},
    }
    try:
        _exclusive_declared_write(lock_path, canonical_json(lock).encode("utf-8"))
    except WFError as exc:
        raise WFError("lock.contention", "operation lock acquisition lost a race", exit_class=5, path=str(lock_path)) from exc
    return lock_path, token, control_created


def _release_initialize_lock(lock_path: Path, token: str) -> None:
    if not lock_path.exists():
        return
    lock = _read_lock(lock_path)
    if lock["owner"]["token"] != token or lock["owner"]["pid"] != os.getpid():
        raise WFError("lock.ownership", "operation lock ownership changed", exit_class=5, path=str(lock_path))
    lock_path.unlink()
    _fsync_directory(lock_path.parent)


def _event_basis(event: dict[str, Any]) -> dict[str, Any]:
    return {key: event[key] for key in ("format", "schemaVersion", "operationId", "sequence", "timestamp", "type", "previousEventSha256", "data")}


def _read_journal(operation_root: Path, operation_id: str, *, required: bool = True) -> list[dict[str, Any]]:
    journal = operation_root / JOURNAL_NAME
    if not journal.exists():
        if required:
            raise WFError("journal.missing", "operation journal is missing", exit_class=5, path=str(journal))
        return []
    if journal.is_symlink() or not journal.is_file():
        raise WFError("journal.type", "operation journal must be a non-symbolic regular file", exit_class=5, path=str(journal))
    raw = journal.read_bytes()
    if not raw or not raw.endswith(b"\n") or b"\r" in raw:
        raise WFError("journal.truncated", "operation journal is empty, truncated, or has invalid newlines", exit_class=5, path=str(journal))
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for index, line in enumerate(raw.splitlines()):
        value = strict_json_bytes(line, path=f"{journal}:{index + 1}", exit_class=5)
        event = _expect_object(value, f"/{index}", exit_class=5)
        _closed(event, ("format", "schemaVersion", "operationId", "sequence", "timestamp", "type", "previousEventSha256", "data", "eventSha256"), f"/{index}", exit_class=5)
        _expect_literal(event["format"], EVENT_FORMAT, f"/{index}/format", "journal.format", exit_class=5)
        _expect_literal(event["schemaVersion"], 1, f"/{index}/schemaVersion", "journal.version", exit_class=5)
        if event["operationId"] != operation_id or event["sequence"] != index + 1 or event["previousEventSha256"] != previous:
            raise WFError("journal.chain", "journal sequence or predecessor link is invalid", exit_class=5, field=f"/{index}")
        expected = sha256_bytes(canonical_json(_event_basis(event)).encode("utf-8"))
        if event["eventSha256"] != expected:
            raise WFError("journal.hash", "journal event digest is invalid", exit_class=5, field=f"/{index}", expected=expected, actual=event["eventSha256"])
        if canonical_json(event).encode("utf-8") != line:
            raise WFError("journal.canonical", "journal event is not canonical JSON", exit_class=5, field=f"/{index}")
        if not isinstance(event["type"], str) or not isinstance(event["data"], dict):
            raise WFError("journal.event", "journal event type or data is invalid", exit_class=5, field=f"/{index}")
        previous = event["eventSha256"]
        events.append(event)
    if events and events[0]["type"] != "operation-recorded":
        raise WFError("journal.state", "journal must begin with operation-recorded", exit_class=5)
    recognized = {
        "operation-recorded", "staging-started", "payload-staged", "staging-complete", "preconditions-rechecked",
        "publication-started", "directory-created", "file-create-started", "file-created", "manifest-publish-started",
        "manifest-published", "live-validation-started", "live-validation-complete", "receipt-written", "complete",
        "rollback-started", "path-removed", "rollback-complete", "rollback-blocked",
    }
    if any(event["type"] not in recognized for event in events):
        raise WFError("journal.event-type", "journal contains an unrecognized event type", exit_class=5)
    if events:
        targets = events[0]["data"].get("targets")
        if not isinstance(targets, list) or not all(isinstance(item, dict) and isinstance(item.get("path"), str) and item.get("role") in {"authored-document", "generated-artifact", "manifest"} for item in targets):
            raise WFError("journal.intent", "first event does not contain the complete intended target set", exit_class=5)
        target_paths = [item["path"] for item in targets]
        if len(target_paths) != len(set(target_paths)) or sum(item["role"] == "manifest" for item in targets) != 1:
            raise WFError("journal.intent", "first event target set is duplicated or lacks one manifest", exit_class=5)
        rank = {
            "operation-recorded": 0, "staging-started": 1, "payload-staged": 2, "staging-complete": 3,
            "preconditions-rechecked": 4, "publication-started": 5, "directory-created": 6,
            "file-create-started": 7, "file-created": 7, "manifest-publish-started": 8,
            "manifest-published": 9, "live-validation-started": 10, "live-validation-complete": 11,
            "receipt-written": 12, "complete": 13,
        }
        prior_rank = -1
        rollback = False
        staged: list[str] = []
        started_files: list[str] = []
        created_files: list[str] = []
        non_manifest_targets = [item["path"] for item in targets if item["role"] != "manifest"]
        for event in events:
            kind = event["type"]
            if rollback:
                if kind not in {"path-removed", "rollback-complete", "rollback-blocked"}:
                    raise WFError("journal.state", "normal event follows rollback start", exit_class=5, actual=kind)
                continue
            if kind == "rollback-started":
                rollback = True
                continue
            current_rank = rank[kind]
            if current_rank < prior_rank:
                raise WFError("journal.state", "journal event order moves backward", exit_class=5, actual=kind)
            prior_rank = current_rank
            if kind == "payload-staged":
                path = event["data"].get("path")
                if path not in target_paths or path in staged or target_paths.index(path) != len(staged):
                    raise WFError("journal.state", "staged payload events are missing, duplicated, or reordered", exit_class=5, actual=path)
                staged.append(path)
            elif kind == "staging-complete" and staged != target_paths:
                raise WFError("journal.state", "staging completed before every intended payload", exit_class=5)
            elif kind == "file-create-started":
                path = event["data"].get("path")
                if path not in non_manifest_targets or path in started_files or non_manifest_targets.index(path) != len(started_files):
                    raise WFError("journal.state", "file-start events are missing, duplicated, or reordered", exit_class=5, actual=path)
                started_files.append(path)
            elif kind == "file-created":
                path = event["data"].get("path")
                if path not in started_files or path in created_files or started_files.index(path) != len(created_files):
                    raise WFError("journal.state", "file-created event lacks its ordered start", exit_class=5, actual=path)
                created_files.append(path)
            elif kind == "manifest-publish-started" and created_files != non_manifest_targets:
                raise WFError("journal.state", "manifest publication began before all non-manifest files", exit_class=5)
            elif kind == "manifest-published" and not any(item["type"] == "manifest-publish-started" for item in events[:event["sequence"] - 1]):
                raise WFError("journal.state", "manifest publication lacks its pre-event", exit_class=5)
            elif kind == "receipt-written" and not any(item["type"] == "live-validation-complete" for item in events[:event["sequence"] - 1]):
                raise WFError("journal.state", "receipt precedes successful live validation", exit_class=5)
            elif kind == "complete" and not any(item["type"] == "receipt-written" for item in events[:event["sequence"] - 1]):
                raise WFError("journal.state", "completion precedes the receipt", exit_class=5)
    terminal = [event for event in events if event["type"] in {"complete", "rollback-complete", "rollback-blocked"}]
    if terminal and events[-1] is not terminal[-1]:
        raise WFError("journal.state", "journal contains events after a terminal state", exit_class=5)
    return events


def _append_event(operation_root: Path, operation_id: str, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    events = _read_journal(operation_root, operation_id, required=False)
    basis = {
        "format": EVENT_FORMAT, "schemaVersion": 1, "operationId": operation_id,
        "sequence": len(events) + 1, "timestamp": _utc_now(), "type": event_type,
        "previousEventSha256": None if not events else events[-1]["eventSha256"], "data": data,
    }
    event = {**basis, "eventSha256": sha256_bytes(canonical_json(basis).encode("utf-8"))}
    raw = canonical_json(event).encode("utf-8") + b"\n"
    journal = operation_root / JOURNAL_NAME
    with journal.open("ab") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_directory(operation_root)
    return event


def _copy_bundle(operation_root: Path, raw_files: dict[str, bytes]) -> None:
    imported = operation_root / "bundle"
    _mkdir_private(imported)
    (imported / "payload").mkdir(mode=0o700)
    for relative, raw in sorted(raw_files.items()):
        target = imported / PurePosixPath(relative)
        _exclusive_declared_write(target, raw)
    _fsync_directory(imported / "payload")
    _fsync_directory(imported)


def _operation_bundle_files(operation_root: Path, plan: dict[str, Any]) -> dict[str, bytes]:
    imported = operation_root / "bundle"
    expected = {"plan.json", "preview.md", *(item["bundlePath"] for item in plan["payloads"])}
    for field in ("inventory", "intake"):
        binding = plan["sourceBindings"][field]
        if binding is not None:
            expected.add(binding["bundlePath"])
    observed = {path.relative_to(imported).as_posix() for path in imported.rglob("*") if path.is_file() and not path.is_symlink()}
    if observed != expected or any(path.is_symlink() for path in imported.rglob("*")):
        raise WFError("recovery.bundle-members", "imported bundle is missing, altered, or has extra members", exit_class=5)
    result = {relative: _read_exact_regular(imported / PurePosixPath(relative), relative) for relative in sorted(expected)}
    plan_raw = result["plan.json"]
    if sha256_bytes(plan_raw) != sha256_bytes((imported / "plan.json").read_bytes()):
        raise WFError("recovery.plan", "imported plan could not be verified", exit_class=5)
    for item in plan["payloads"]:
        raw = result[item["bundlePath"]]
        if len(raw) != item["byteLength"] or sha256_bytes(raw) != item["sha256"]:
            raise WFError("recovery.payload", "imported payload differs from the recorded plan", exit_class=5, path=item["bundlePath"])
    return result


def _target_set_digest(plan: dict[str, Any]) -> str:
    basis = [{"path": item["targetPath"], "byteLength": item["byteLength"], "sha256": item["sha256"]} for item in plan["payloads"]]
    return sha256_bytes(canonical_json(basis).encode("utf-8"))


def _stage_and_validate(workspace: Path, operation_root: Path, operation_id: str, plan: dict[str, Any], files: dict[str, bytes], source_state: dict[str, Any] | None) -> dict[str, Any]:
    staging = operation_root / "staging"
    events = _read_journal(operation_root, operation_id)
    types = [event["type"] for event in events]
    if "staging-complete" in types:
        return next(event["data"]["validation"] for event in events if event["type"] == "staging-complete")
    if staging.exists():
        shutil.rmtree(staging)
    _mkdir_private(staging)
    if "staging-started" not in types:
        _append_event(operation_root, operation_id, "staging-started", {"sameFilesystem": staging.stat().st_dev == workspace.stat().st_dev})
        _failure_boundary("after-staging-started")
    staged_paths = {event["data"].get("path") for event in _read_journal(operation_root, operation_id) if event["type"] == "payload-staged"}
    for index, item in enumerate(plan["payloads"], 1):
        target = staging / PurePosixPath(item["targetPath"])
        target.parent.mkdir(parents=True, exist_ok=True)
        _exclusive_live_write(target, files[item["bundlePath"]])
        if len(target.read_bytes()) != item["byteLength"] or sha256_bytes(target.read_bytes()) != item["sha256"]:
            raise WFError("apply.staging-digest", "staged payload failed byte verification", exit_class=5, path=item["targetPath"])
        if item["targetPath"] not in staged_paths:
            _append_event(operation_root, operation_id, "payload-staged", {"path": item["targetPath"], "sha256": item["sha256"]})
        _failure_boundary(f"after-stage-{index:04d}")
    if source_state is not None:
        for entry in source_state["inventory"]["entries"]:
            if entry.get("included") and entry.get("type") == "regular-file":
                source = workspace / PurePosixPath(entry["path"])
                destination = staging / PurePosixPath(entry["path"])
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
    baseline = plan["manifest"]["canonicalBaseline"]
    if baseline["kind"] == "snapshot":
        destination = staging / PurePosixPath(baseline["path"])
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((workspace / PurePosixPath(baseline["path"])).read_bytes())
    validation = validate_record(load_record(staging))
    if validation != plan["validation"]:
        raise WFError("apply.staging-validation", "staged exact bytes do not reproduce planned validation", exit_class=5, expected=plan["validation"], actual=validation)
    _append_event(operation_root, operation_id, "staging-complete", {"validation": validation})
    _failure_boundary("after-staging-complete")
    return validation


def _exclusive_live_write(path: Path, raw: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)


def _intake_counts(source_state: dict[str, Any] | None) -> dict[str, Any]:
    result = {"ledgerDigest": None, "incorporate": 0, "reference": 0, "preserveOutOfScope": 0, "unresolved": 0}
    if source_state is None:
        return result
    result["ledgerDigest"] = sha256_bytes(canonical_json(source_state["ledger"]).encode("utf-8"))
    mapping = {"incorporate": "incorporate", "reference": "reference", "preserve-out-of-scope": "preserveOutOfScope", "unresolved": "unresolved"}
    for item in source_state["ledger"]["sources"]:
        result[mapping[item["disposition"]]] += 1
    return result


def _validate_receipt(value: Any, operation_id: str, plan_digest: str) -> dict[str, Any]:
    receipt = _expect_object(value, "/", exit_class=5)
    fields = ("format", "schemaVersion", "operationId", "completedAt", "mode", "planSha256", "contractVersion", "contractSha256", "adapter", "canonicalBaseline", "manifestSha256", "targetSetSha256", "intake", "validation", "operationalIntegrity", "semanticReadiness", "entrypoint", "openQuestionIds", "nextWorkflow", "recommendedFocusIds", "journalHeadSha256")
    _closed(receipt, fields, "/", exit_class=5)
    _expect_literal(receipt["format"], RECEIPT_FORMAT, "/format", "receipt.format", exit_class=5)
    _expect_literal(receipt["schemaVersion"], 1, "/schemaVersion", "receipt.version", exit_class=5)
    if receipt["operationId"] != operation_id or receipt["planSha256"] != plan_digest:
        raise WFError("receipt.binding", "receipt does not bind the operation and plan", exit_class=5)
    if not isinstance(receipt["completedAt"], str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", receipt["completedAt"]) is None:
        raise WFError("receipt.timestamp", "receipt completion time is invalid", exit_class=5)
    for field in ("contractSha256", "manifestSha256", "targetSetSha256", "journalHeadSha256"):
        if not isinstance(receipt[field], str) or not HEX_RE.fullmatch(receipt[field]):
            raise WFError("receipt.digest", "receipt digest field is invalid", exit_class=5, field=f"/{field}")
    if receipt["nextWorkflow"] != "interview" or receipt["operationalIntegrity"].get("status") != "passed" or receipt["semanticReadiness"].get("status") != "passed":
        raise WFError("receipt.gates", "receipt does not record both completion gates and Interview handoff", exit_class=5)
    return receipt


def _build_receipt(operation_root: Path, operation_id: str, plan_digest: str, plan: dict[str, Any], source_state: dict[str, Any] | None, validation: dict[str, Any]) -> dict[str, Any]:
    package = verify_package()
    events = _read_journal(operation_root, operation_id)
    manifest_item = next(item for item in plan["payloads"] if item["role"] == "manifest")
    question_ids = sorted({item["targetId"] for item in plan["review"]["epistemicStates"] if isinstance(item.get("targetId"), str) and item["targetId"].startswith("wfq-")}, key=lambda item: _identifier(item, "question", "/review/epistemicStates", exit_class=5)[0])
    validation_basis = {"validatorVersion": 1, "errors": 0, "warnings": len(validation["warnings"]), "result": validation}
    return {
        "format": RECEIPT_FORMAT, "schemaVersion": 1, "operationId": operation_id, "completedAt": _utc_now(),
        "mode": plan["mode"], "planSha256": plan_digest, "contractVersion": CONTRACT_VERSION,
        "contractSha256": package["contractDigest"], "adapter": {"id": ADAPTER_ID, "sha256": package["adapterDigest"]},
        "canonicalBaseline": plan["preconditions"]["canonicalBaseline"], "manifestSha256": manifest_item["sha256"],
        "targetSetSha256": _target_set_digest(plan), "intake": _intake_counts(source_state),
        "validation": {"validatorVersion": 1, "errors": 0, "warnings": len(validation["warnings"]), "resultSha256": sha256_bytes(canonical_json(validation_basis).encode("utf-8"))},
        "operationalIntegrity": {"status": "passed", "targetCount": len(plan["payloads"]), "manifestPublishedLast": True},
        "semanticReadiness": {"status": "passed", "predicates": plan["review"]["semanticReadiness"], "authorityConfirmed": True},
        "entrypoint": plan["manifest"]["entrypoint"], "openQuestionIds": question_ids, "nextWorkflow": "interview",
        "recommendedFocusIds": plan["review"]["interviewResume"]["recommendedFocusIds"],
        "journalHeadSha256": events[-1]["eventSha256"],
    }


def _event_paths(events: list[dict[str, Any]], event_type: str) -> set[str]:
    return {event["data"]["path"] for event in events if event["type"] == event_type and isinstance(event["data"].get("path"), str)}


def _continue_initialize(workspace: Path, operation_root: Path, operation_id: str, plan_digest: str, plan: dict[str, Any], files: dict[str, bytes], source_state: dict[str, Any] | None) -> dict[str, Any]:
    events = _read_journal(operation_root, operation_id)
    types = [event["type"] for event in events]
    validation = _stage_and_validate(workspace, operation_root, operation_id, plan, files, source_state)
    events = _read_journal(operation_root, operation_id)
    types = [event["type"] for event in events]
    if "preconditions-rechecked" not in types:
        _baseline_recheck(workspace, plan)
        _source_recheck(workspace, plan, files)
        created_files = _event_paths(events, "file-created") | _event_paths(events, "manifest-published")
        for item in plan["payloads"]:
            target = workspace / PurePosixPath(item["targetPath"])
            if item["targetPath"] not in created_files and (target.exists() or target.is_symlink()):
                raise WFError("apply.target-race", "a planned target appeared before exclusive publication", exit_class=5, path=item["targetPath"])
        _append_event(operation_root, operation_id, "preconditions-rechecked", {"baseline": plan["preconditions"]["canonicalBaseline"], "sourcesRechecked": 0 if source_state is None else len(source_state["ledger"]["sources"])})
        _failure_boundary("after-preconditions-rechecked")
    if "publication-started" not in [event["type"] for event in _read_journal(operation_root, operation_id)]:
        _append_event(operation_root, operation_id, "publication-started", {"manifestLast": True})
        _failure_boundary("after-publication-started")
    events = _read_journal(operation_root, operation_id)
    created_dirs = _event_paths(events, "directory-created")
    for index, operation in enumerate((item for item in plan["operations"] if item["action"] == "create-directory"), 1):
        relative = operation["path"]
        target = workspace / PurePosixPath(relative)
        if relative == ".wayfinder":
            continue
        if relative in created_dirs:
            if not target.is_dir() or target.is_symlink():
                raise WFError("recovery.directory-changed", "an operation-created directory is missing or changed", exit_class=5, path=relative)
            continue
        if target.exists() or target.is_symlink():
            raise WFError("apply.directory-race", "a planned directory appeared before exclusive creation", exit_class=5, path=relative)
        target.mkdir()
        _fsync_directory(target.parent)
        _append_event(operation_root, operation_id, "directory-created", {"path": relative})
        _failure_boundary(f"after-directory-{index:04d}")
    events = _read_journal(operation_root, operation_id)
    created_files = _event_paths(events, "file-created")
    non_manifest_ops = [item for item in plan["operations"] if item["action"] == "create-file"]
    for index, operation in enumerate(non_manifest_ops, 1):
        relative = operation["path"]
        target = workspace / PurePosixPath(relative)
        if relative in created_files:
            if not target.is_file() or target.is_symlink() or sha256_bytes(target.read_bytes()) != operation["sha256"]:
                raise WFError("recovery.created-path-changed", "an operation-created file is missing or externally modified", exit_class=5, path=relative)
            continue
        if not any(event["type"] == "file-create-started" and event["data"].get("path") == relative for event in _read_journal(operation_root, operation_id)):
            _append_event(operation_root, operation_id, "file-create-started", {"path": relative, "sha256": operation["sha256"]})
            _failure_boundary(f"before-file-{index:04d}")
        if target.exists() or target.is_symlink():
            raise WFError("apply.target-race", "a planned file appeared before exclusive creation", exit_class=5, path=relative)
        try:
            _exclusive_live_write(target, files[operation["payload"]])
        except FileExistsError:
            raise WFError("apply.target-race", "exclusive file creation lost a target race", exit_class=5, path=relative) from None
        if sha256_bytes(target.read_bytes()) != operation["sha256"]:
            raise WFError("apply.placement-digest", "placed file failed byte verification", exit_class=5, path=relative)
        _append_event(operation_root, operation_id, "file-created", {"path": relative, "sha256": operation["sha256"]})
        _failure_boundary(f"after-file-{index:04d}")
    manifest_op = plan["operations"][-1]
    manifest = workspace / ".wayfinder/manifest.json"
    events = _read_journal(operation_root, operation_id)
    if "manifest-published" not in [event["type"] for event in events]:
        if not any(event["type"] == "manifest-publish-started" for event in events):
            _append_event(operation_root, operation_id, "manifest-publish-started", {"path": manifest_op["path"], "sha256": manifest_op["sha256"]})
            _failure_boundary("before-manifest-publication")
        if manifest.exists() or manifest.is_symlink():
            raise WFError("apply.manifest-race", "manifest appeared before exclusive manifest-last publication", exit_class=5, path=str(manifest))
        try:
            _exclusive_live_write(manifest, files[manifest_op["payload"]])
        except FileExistsError:
            raise WFError("apply.manifest-race", "exclusive manifest publication lost a race", exit_class=5, path=str(manifest)) from None
        if sha256_bytes(manifest.read_bytes()) != manifest_op["sha256"]:
            raise WFError("apply.manifest-digest", "published manifest failed byte verification", exit_class=5, path=str(manifest))
        _append_event(operation_root, operation_id, "manifest-published", {"path": manifest_op["path"], "sha256": manifest_op["sha256"]})
        _failure_boundary("after-manifest-publication")
    elif not manifest.is_file() or manifest.is_symlink() or sha256_bytes(manifest.read_bytes()) != manifest_op["sha256"]:
        raise WFError("recovery.manifest-changed", "published manifest is missing or externally modified", exit_class=5, path=str(manifest))
    events = _read_journal(operation_root, operation_id)
    if "live-validation-started" not in [event["type"] for event in events]:
        _append_event(operation_root, operation_id, "live-validation-started", {})
        _failure_boundary("after-live-validation-started")
    live_validation = validate_record(load_record(workspace))
    if live_validation != plan["validation"]:
        raise WFError("apply.live-validation", "published record does not reproduce planned validation", exit_class=5, expected=plan["validation"], actual=live_validation)
    for item in plan["payloads"]:
        target = workspace / PurePosixPath(item["targetPath"])
        if not target.is_file() or target.is_symlink() or len(target.read_bytes()) != item["byteLength"] or sha256_bytes(target.read_bytes()) != item["sha256"]:
            raise WFError("apply.operational-integrity", "live target set differs from the confirmed plan", exit_class=5, path=item["targetPath"])
    events = _read_journal(operation_root, operation_id)
    if "live-validation-complete" not in [event["type"] for event in events]:
        _append_event(operation_root, operation_id, "live-validation-complete", {"validation": live_validation, "targetSetSha256": _target_set_digest(plan), "operationalGate": "passed", "semanticGate": "passed"})
        _failure_boundary("after-live-validation-complete")
    staging = operation_root / "staging"
    if staging.exists():
        shutil.rmtree(staging)
        _fsync_directory(operation_root)
    receipt_path = operation_root / "receipt.json"
    events = _read_journal(operation_root, operation_id)
    if not receipt_path.exists():
        receipt = _build_receipt(operation_root, operation_id, plan_digest, plan, source_state, live_validation)
        _exclusive_declared_write(receipt_path, canonical_json(receipt).encode("utf-8"))
    else:
        receipt = _validate_receipt(strict_json_bytes(_read_exact_regular(receipt_path, "receipt.json"), path=str(receipt_path), exit_class=5), operation_id, plan_digest)
    events = _read_journal(operation_root, operation_id)
    if "receipt-written" not in [event["type"] for event in events]:
        _append_event(operation_root, operation_id, "receipt-written", {"path": ".wayfinder/operations/" + operation_id + "/receipt.json", "sha256": sha256_bytes(receipt_path.read_bytes())})
        _failure_boundary("after-receipt-written")
    events = _read_journal(operation_root, operation_id)
    if "complete" not in [event["type"] for event in events]:
        _append_event(operation_root, operation_id, "complete", {"receiptSha256": sha256_bytes(receipt_path.read_bytes())})
        _failure_boundary("after-complete")
    final_event = _read_journal(operation_root, operation_id)[-1]
    return {
        "status": "completed", "operationId": operation_id, "planSha256": plan_digest,
        "manifest": ".wayfinder/manifest.json", "receipt": f".wayfinder/operations/{operation_id}/receipt.json",
        "journalHeadSha256": final_event["eventSha256"], "validation": live_validation,
        "handoff": {"entrypoint": plan["manifest"]["entrypoint"], "nextWorkflow": "interview", "recommendedFocusIds": plan["review"]["interviewResume"]["recommendedFocusIds"], "summary": plan["review"]["interviewResume"]["summary"]},
    }


def command_initialize_apply(workspace_root_arg: str | None, bundle_root_arg: str | None, plan_digest_arg: str | None, confirmation_arg: str | None) -> dict[str, Any]:
    if None in {workspace_root_arg, bundle_root_arg, plan_digest_arg, confirmation_arg}:
        raise WFError("command.arguments", "initialize-apply requires --workspace-root PATH --bundle-root PATH --plan-sha256 HEX --confirmation-token TOKEN", exit_class=2)
    supplied = Path(str(workspace_root_arg))
    if not supplied.exists() or not supplied.is_dir() or supplied.is_symlink():
        raise WFError("initialize.workspace-root", "workspace root must be an existing non-symbolic directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    bundle, plan_raw, plan, raw_files = _external_bundle(str(bundle_root_arg), workspace, str(plan_digest_arg))
    expected_confirmation = CONFIRMATION_PREFIX + str(plan_digest_arg)
    if confirmation_arg != expected_confirmation:
        raise WFError("apply.confirmation-token", "confirmation token does not bind the exact plan digest", exit_class=2, expected=expected_confirmation)
    operation_id = f"wfinit-{str(plan_digest_arg)[:24]}"
    _baseline_recheck(workspace, plan)
    source_state = _source_recheck(workspace, plan, raw_files)
    _target_recheck(workspace, plan)
    operation_root = workspace / ".wayfinder/operations" / operation_id
    if operation_root.exists() or operation_root.is_symlink():
        raise WFError("apply.recovery-required", "operation state already exists; inspect it before continuing", exit_class=5, path=str(operation_root))
    lock_path, lock_token, control_created = _acquire_initialize_lock(workspace, operation_id, str(plan_digest_arg))
    _failure_boundary("after-lock-acquired")
    try:
        operations_root = operation_root.parent
        if operations_root.exists() or operations_root.is_symlink():
            if operations_root.is_symlink() or not operations_root.is_dir():
                raise WFError("apply.operations-root", "operations root must be a non-symbolic directory", exit_class=5, path=str(operations_root))
            if any(operations_root.iterdir()):
                raise WFError("apply.recovery-required", "another operation requires recovery", exit_class=5, path=str(operations_root))
        else:
            _mkdir_private(operations_root)
        _mkdir_private(operation_root)
        _copy_bundle(operation_root, raw_files)
        _append_event(operation_root, operation_id, "operation-recorded", {
            "planSha256": plan_digest_arg, "contractSha256": plan["contractSha256"], "targetSetSha256": _target_set_digest(plan),
            "targets": [{"path": item["targetPath"], "byteLength": item["byteLength"], "sha256": item["sha256"], "role": item["role"]} for item in plan["payloads"]],
            "controlRootCreated": control_created, "bundleImportedFrom": str(bundle),
        })
        _failure_boundary("after-bundle-imported")
        result = _continue_initialize(workspace, operation_root, operation_id, str(plan_digest_arg), plan, raw_files, source_state)
        _release_initialize_lock(lock_path, lock_token)
        return result
    except Exception:
        raise


def _load_operation(workspace: Path, operation_id: str) -> tuple[Path, bytes, dict[str, Any], dict[str, bytes]]:
    if re.fullmatch(r"wfinit-(?:[0-9a-f]{24}|test-[a-z0-9]+(?:-[a-z0-9]+)*)", operation_id) is None:
        raise WFError("recovery.operation-id", "operation ID is invalid", exit_class=2, actual=operation_id)
    operation_root = workspace / ".wayfinder/operations" / operation_id
    if operation_root.is_symlink() or not operation_root.exists() or not operation_root.is_dir():
        raise WFError("recovery.operation-missing", "operation state does not exist", exit_class=3, path=str(operation_root))
    plan_path = operation_root / "bundle/plan.json"
    plan_raw = _read_exact_regular(plan_path, "plan.json")
    digest = sha256_bytes(plan_raw)
    plan = _validate_apply_plan(strict_json_bytes(plan_raw, path=str(plan_path), exit_class=5), plan_raw, workspace, digest)
    if operation_id.startswith("wfinit-") and not operation_id.startswith("wfinit-test-") and operation_id != f"wfinit-{digest[:24]}":
        raise WFError("recovery.operation-binding", "operation ID does not derive from its imported plan", exit_class=5)
    files = _operation_bundle_files(operation_root, plan)
    return operation_root, plan_raw, plan, files


def _inspect_operation(workspace: Path, operation_id: str, operation_root: Path, plan_digest: str, plan: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
    try:
        events = _read_journal(operation_root, operation_id)
    except WFError as exc:
        return {"status": "manual-recovery", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect"], "issues": [exc.diagnostic()]}
    types = [event["type"] for event in events]
    if types and types[-1] == "rollback-complete":
        return {"status": "rolled-back", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect"], "issues": []}
    if types and types[-1] == "rollback-blocked":
        return {"status": "manual-recovery", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect"], "issues": events[-1]["data"].get("issues", [])}
    issues: list[dict[str, Any]] = []
    created_files = _event_paths(events, "file-created")
    if "manifest-published" in types:
        created_files.add(".wayfinder/manifest.json")
    removed_files = {event["data"].get("path") for event in events if event["type"] == "path-removed" and event["data"].get("kind") == "file"}
    created_files -= removed_files
    for item in plan["payloads"]:
        target = workspace / PurePosixPath(item["targetPath"])
        exists = target.exists() or target.is_symlink()
        if item["targetPath"] in created_files:
            if not target.is_file() or target.is_symlink():
                issues.append({"code": "recovery.created-path-missing", "message": "an event-recorded created path is missing or not a regular file", "path": item["targetPath"]})
            elif len(target.read_bytes()) != item["byteLength"] or sha256_bytes(target.read_bytes()) != item["sha256"]:
                issues.append({"code": "recovery.created-path-modified", "message": "an event-recorded created path was externally modified", "path": item["targetPath"]})
        elif exists:
            issues.append({"code": "recovery.unowned-target", "message": "a target exists without a completed creation event", "path": item["targetPath"]})
    if issues:
        return {"status": "manual-recovery", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect", "rollback"], "issues": issues}
    if "rollback-started" in types:
        return {"status": "resumable", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect", "rollback"], "recoveryAction": "rollback", "issues": []}
    if types and types[-1] == "complete":
        receipt_path = operation_root / "receipt.json"
        try:
            receipt = _validate_receipt(strict_json_bytes(_read_exact_regular(receipt_path, "receipt.json"), path=str(receipt_path), exit_class=5), operation_id, plan_digest)
            validation = validate_record(load_record(workspace))
            if validation != plan["validation"]:
                raise WFError("recovery.validation", "completed record no longer validates against the plan", exit_class=5)
            package = verify_package()
            manifest_item = next(item for item in plan["payloads"] if item["role"] == "manifest")
            receipt_event = next((event for event in events if event["type"] == "receipt-written"), None)
            receipt_index = events.index(receipt_event) if receipt_event is not None else -1
            expected = {
                "mode": plan["mode"], "contractVersion": CONTRACT_VERSION, "contractSha256": package["contractDigest"],
                "adapter": {"id": ADAPTER_ID, "sha256": package["adapterDigest"]}, "canonicalBaseline": plan["preconditions"]["canonicalBaseline"],
                "manifestSha256": manifest_item["sha256"], "targetSetSha256": _target_set_digest(plan),
                "entrypoint": plan["manifest"]["entrypoint"], "nextWorkflow": "interview",
                "recommendedFocusIds": plan["review"]["interviewResume"]["recommendedFocusIds"],
            }
            if any(receipt[key] != expected_value for key, expected_value in expected.items()):
                raise WFError("receipt.agreement", "receipt disagrees with the confirmed plan or executing package", exit_class=5)
            if receipt_event is None or receipt_event["data"].get("sha256") != sha256_bytes(receipt_path.read_bytes()) or events[-1]["data"].get("receiptSha256") != sha256_bytes(receipt_path.read_bytes()):
                raise WFError("receipt.journal-binding", "receipt digest does not agree with terminal journal events", exit_class=5)
            if receipt_index <= 0 or receipt["journalHeadSha256"] != events[receipt_index - 1]["eventSha256"]:
                raise WFError("receipt.journal-head", "receipt does not bind the pre-receipt journal head", exit_class=5)
        except WFError as exc:
            return {"status": "manual-recovery", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect"], "issues": [exc.diagnostic()]}
        return {"status": "completed", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect"], "receipt": receipt}
    try:
        _baseline_recheck(workspace, plan)
        source_state = _source_recheck(workspace, plan, files)
    except WFError as exc:
        return {"status": "blocked", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect", "rollback"], "issues": [exc.diagnostic()]}
    return {"status": "resumable", "operationId": operation_id, "planSha256": plan_digest, "allowedActions": ["inspect", "resume", "rollback"], "issues": [], "sourcesRechecked": 0 if source_state is None else len(source_state["ledger"]["sources"])}


def _rollback_operation(workspace: Path, operation_id: str, operation_root: Path, plan_digest: str, plan: dict[str, Any]) -> dict[str, Any]:
    events = _read_journal(operation_root, operation_id)
    if events and events[-1]["type"] == "complete":
        raise WFError("recovery.completed", "a completed initialization is not rolled back by version 1 recovery", exit_class=5)
    if not any(event["type"] == "rollback-started" for event in events):
        _append_event(operation_root, operation_id, "rollback-started", {})
        _failure_boundary("after-rollback-started")
        events = _read_journal(operation_root, operation_id)
    issues: list[dict[str, Any]] = []
    created_files = _event_paths(events, "file-created")
    if any(event["type"] == "manifest-published" for event in events):
        created_files.add(".wayfinder/manifest.json")
    already_removed_files = {event["data"].get("path") for event in events if event["type"] == "path-removed" and event["data"].get("kind") == "file"}
    created_files -= already_removed_files
    ordered = [".wayfinder/manifest.json"] + [item["targetPath"] for item in reversed(plan["payloads"]) if item["targetPath"] != ".wayfinder/manifest.json"]
    by_target = {item["targetPath"]: item for item in plan["payloads"]}
    for index, relative in enumerate(ordered, 1):
        if relative not in created_files:
            continue
        target = workspace / PurePosixPath(relative)
        item = by_target[relative]
        if not target.exists() and not target.is_symlink():
            issues.append({"code": "recovery.missing-unexpected", "message": "operation-created path is unexpectedly missing and was preserved as a manual-recovery issue", "path": relative})
            continue
        if target.is_symlink() or not target.is_file() or sha256_bytes(target.read_bytes()) != item["sha256"]:
            issues.append({"code": "recovery.modified-preserved", "message": "externally modified operation path was preserved", "path": relative})
            continue
        target.unlink()
        _fsync_directory(target.parent)
        _append_event(operation_root, operation_id, "path-removed", {"path": relative, "kind": "file"})
        _failure_boundary(f"after-rollback-file-{index:04d}")
    already_removed_dirs = {event["data"].get("path") for event in events if event["type"] == "path-removed" and event["data"].get("kind") == "directory"}
    created_dirs = list(reversed([event["data"]["path"] for event in events if event["type"] == "directory-created" and event["data"]["path"] not in already_removed_dirs]))
    for index, relative in enumerate(created_dirs, 1):
        target = workspace / PurePosixPath(relative)
        if not target.exists():
            issues.append({"code": "recovery.directory-missing", "message": "operation-created directory is unexpectedly missing", "path": relative})
        elif target.is_symlink() or not target.is_dir() or any(target.iterdir()):
            issues.append({"code": "recovery.directory-preserved", "message": "nonempty or modified operation-created directory was preserved", "path": relative})
        else:
            target.rmdir()
            _fsync_directory(target.parent)
            _append_event(operation_root, operation_id, "path-removed", {"path": relative, "kind": "directory"})
        _failure_boundary(f"after-rollback-directory-{index:04d}")
    staging = operation_root / "staging"
    if staging.exists() and staging.is_dir() and not staging.is_symlink():
        shutil.rmtree(staging)
    terminal = "rollback-blocked" if issues else "rollback-complete"
    _append_event(operation_root, operation_id, terminal, {"issues": issues})
    return {"status": "manual-recovery" if issues else "rolled-back", "operationId": operation_id, "planSha256": plan_digest, "issues": issues, "preserved": [item["path"] for item in issues]}


def command_initialize_recover(workspace_root_arg: str | None, operation_id_arg: str | None, action_arg: str | None) -> dict[str, Any]:
    if workspace_root_arg is None or operation_id_arg is None or action_arg is None:
        raise WFError("command.arguments", "initialize-recover requires --workspace-root PATH --operation-id ID --action inspect|resume|rollback", exit_class=2)
    if action_arg not in {"inspect", "resume", "rollback"}:
        raise WFError("recovery.action", "recovery action must be inspect, resume, or rollback", exit_class=2, actual=action_arg)
    supplied = Path(workspace_root_arg)
    if not supplied.exists() or not supplied.is_dir() or supplied.is_symlink():
        raise WFError("initialize.workspace-root", "workspace root must be an existing non-symbolic directory", exit_class=3, path=str(supplied))
    workspace = supplied.resolve(strict=True)
    operation_candidate = workspace / ".wayfinder/operations" / operation_id_arg
    if not operation_candidate.exists() and not operation_candidate.is_symlink():
        lock_candidate = _lock_path(workspace)
        if not lock_candidate.exists() and not lock_candidate.is_symlink():
            raise WFError("recovery.operation-missing", "operation state does not exist", exit_class=3, path=str(operation_candidate))
        lock = _read_lock(lock_candidate)
        if lock["operationId"] != operation_id_arg:
            raise WFError("lock.contention", "operation lock belongs to another operation", exit_class=5, actual=lock["operationId"])
        same_host = lock["owner"]["host"] == socket.gethostname()
        reclaimable = same_host and not _process_alive(lock["owner"]["pid"])
        state = {"status": "blocked", "operationId": operation_id_arg, "planSha256": lock["planSha256"], "allowedActions": ["inspect", "rollback"] if reclaimable else ["inspect"], "issues": [{"code": "recovery.lock-only", "message": "interruption occurred after lock acquisition and before durable operation import"}]}
        if action_arg == "inspect":
            return state
        if action_arg != "rollback" or not reclaimable:
            raise WFError("recovery.action-blocked", "lock-only state cannot perform the requested action", exit_class=5, actual=state["status"])
        lock_candidate.unlink()
        _fsync_directory(lock_candidate.parent)
        operations_root = workspace / ".wayfinder/operations"
        if operations_root.exists() and operations_root.is_dir() and not any(operations_root.iterdir()):
            operations_root.rmdir()
        return {"status": "rolled-back", "operationId": operation_id_arg, "planSha256": lock["planSha256"], "issues": [], "preserved": [".wayfinder"]}
    try:
        operation_root, plan_raw, plan, files = _load_operation(workspace, operation_id_arg)
    except WFError as exc:
        if action_arg == "inspect":
            return {"status": "manual-recovery", "operationId": operation_id_arg, "planSha256": None, "allowedActions": ["inspect"], "issues": [exc.diagnostic()]}
        raise WFError("recovery.action-blocked", "operation metadata or imported bundle is not trustworthy enough to mutate", exit_class=5, actual=exc.code) from None
    plan_digest = sha256_bytes(plan_raw)
    inspection = _inspect_operation(workspace, operation_id_arg, operation_root, plan_digest, plan, files)
    if action_arg == "inspect":
        return inspection
    if action_arg not in inspection["allowedActions"]:
        raise WFError("recovery.action-blocked", "requested recovery action is unsafe in the inspected state", exit_class=5, actual=inspection["status"])
    lock_path, token, _ = _acquire_initialize_lock(workspace, operation_id_arg, plan_digest, recovery=True)
    try:
        if action_arg == "resume":
            source_state = _source_recheck(workspace, plan, files)
            result = _continue_initialize(workspace, operation_root, operation_id_arg, plan_digest, plan, files, source_state)
        else:
            result = _rollback_operation(workspace, operation_id_arg, operation_root, plan_digest, plan)
        _release_initialize_lock(lock_path, token)
        return result
    except Exception:
        raise


def result_envelope(ok: bool, command: str, code: str, data: dict[str, Any], diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "format": "wayfinder-command-result",
        "schemaVersion": SCHEMA_VERSION,
        "ok": ok,
        "command": command,
        "code": code,
        "data": data,
        "diagnostics": diagnostics,
    }


def emit(result: dict[str, Any]) -> None:
    ordered = {field: result[field] for field in RESULT_FIELDS}
    sys.stdout.write(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + "\n")


def parse_command(argv: list[str]) -> tuple[str, dict[str, str | None]]:
    if not argv:
        raise WFError("command.missing", "a command is required", exit_class=2)
    command = argv[0]
    if command == "probe":
        if len(argv) != 1:
            raise WFError("command.arguments", "probe accepts no arguments", exit_class=2)
        return command, {}
    if command not in {"discover", "inventory", "initialize-plan", "initialize-apply", "initialize-recover", "validate", "generate"}:
        raise WFError("command.unknown", "command must be probe, discover, inventory, initialize-plan, initialize-apply, initialize-recover, validate, or generate", exit_class=2, actual=command)
    if command == "discover":
        allowed = {"--workspace-root", "--start"}
    elif command == "inventory":
        allowed = {"--workspace-root", "--request", "--ledger"}
    elif command == "validate":
        allowed = {"--workspace-root"}
    elif command == "initialize-plan":
        allowed = {"--workspace-root", "--proposal", "--bundle-root"}
    elif command == "initialize-apply":
        allowed = {"--workspace-root", "--bundle-root", "--plan-sha256", "--confirmation-token"}
    elif command == "initialize-recover":
        allowed = {"--workspace-root", "--operation-id", "--action"}
    else:
        allowed = {"--workspace-root", "--request", "--output-root"}
    options: dict[str, str | None] = {"workspace_root": None, "start": None, "request": None, "ledger": None, "output_root": None, "proposal": None, "bundle_root": None, "plan_sha256": None, "confirmation_token": None, "operation_id": None, "action": None}
    index = 1
    while index < len(argv):
        flag = argv[index]
        if flag not in allowed or index + 1 >= len(argv):
            usage = {
                "discover": "discover accepts --workspace-root PATH or --start PATH",
                "inventory": "inventory accepts --workspace-root PATH --request FILE [--ledger FILE]",
                "initialize-plan": "initialize-plan accepts --workspace-root PATH --proposal FILE --bundle-root PATH",
                "initialize-apply": "initialize-apply accepts --workspace-root PATH --bundle-root PATH --plan-sha256 HEX --confirmation-token TOKEN",
                "initialize-recover": "initialize-recover accepts --workspace-root PATH --operation-id ID --action inspect|resume|rollback",
                "validate": "validate accepts --workspace-root PATH",
                "generate": "generate accepts --workspace-root PATH --request FILE [--output-root PATH]",
            }[command]
            raise WFError("command.arguments", usage, exit_class=2, actual=flag)
        key = {"--workspace-root": "workspace_root", "--start": "start", "--request": "request", "--ledger": "ledger", "--output-root": "output_root", "--proposal": "proposal", "--bundle-root": "bundle_root", "--plan-sha256": "plan_sha256", "--confirmation-token": "confirmation_token", "--operation-id": "operation_id", "--action": "action"}[flag]
        if options[key] is not None:
            raise WFError("command.arguments", "command option is duplicated", exit_class=2, actual=flag)
        options[key] = argv[index + 1]
        index += 2
    return command, options


def main(argv: list[str]) -> int:
    command = argv[0] if argv and argv[0] in {"probe", "discover", "inventory", "initialize-plan", "initialize-apply", "initialize-recover", "validate", "generate"} else "unknown"
    try:
        command, options = parse_command(argv)
        if os.environ.get("WAYFINDER_TEST_MODE") == "1" and os.environ.get("WAYFINDER_TEST_RAISE") == "1":
            raise RuntimeError("injected maintainer-only unexpected failure")
        if command == "probe":
            data = command_probe()
        elif command == "discover":
            data = command_discover(options["workspace_root"], options["start"])
        elif command == "inventory":
            data = command_inventory(options["workspace_root"], options["request"], options["ledger"])
        elif command == "initialize-plan":
            data = command_initialize_plan(options["workspace_root"], options["proposal"], options["bundle_root"])
        elif command == "initialize-apply":
            data = command_initialize_apply(options["workspace_root"], options["bundle_root"], options["plan_sha256"], options["confirmation_token"])
        elif command == "initialize-recover":
            data = command_initialize_recover(options["workspace_root"], options["operation_id"], options["action"])
        elif command == "validate":
            data = command_validate(options["workspace_root"])
        else:
            data = command_generate(options["workspace_root"], options["request"], options["output_root"])
        emit(result_envelope(True, command, "ok", data, []))
        return 0
    except WFError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        emit(result_envelope(False, command, exc.code, {}, [exc.diagnostic()]))
        return exc.exit_class
    except Exception:
        code = "internal.unexpected"
        message = "unexpected internal failure"
        print(f"{code}: {message}", file=sys.stderr)
        emit(result_envelope(False, command, code, {}, [{"code": code, "message": message}]))
        return 70


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
