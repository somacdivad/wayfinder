"""Bounded, machine-discernible output helpers for Wayfinder maintenance."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any


PREVIEW_MAX_BYTES = 16 * 1024
COMPLETE_MAX_BYTES = 64 * 1024
RESPONSE_FORMAT = "wayfinder-maintainer-response"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def make_cursor(binding: dict[str, Any]) -> str:
    raw = canonical_json(binding).encode("utf-8")
    checksum = hashlib.sha256(raw).hexdigest()[:16]
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=") + "." + checksum


def read_cursor(value: str) -> dict[str, Any]:
    try:
        encoded, checksum = value.rsplit(".", 1)
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if hashlib.sha256(raw).hexdigest()[:16] != checksum:
            raise ValueError("checksum")
        decoded = json.loads(raw.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("shape")
        return decoded
    except Exception as exc:
        raise ValueError("invalid cursor") from exc


def bounded_chunk(source: bytes, start: int, max_bytes: int) -> tuple[bytes, int]:
    if max_bytes <= 0 or start < 0 or start > len(source):
        raise ValueError("invalid byte range")
    end = min(len(source), start + max_bytes)
    if end < len(source):
        newline = source.rfind(b"\n", start, end)
        if newline >= start:
            end = newline + 1
        while end > start:
            try:
                source[start:end].decode("utf-8", "strict")
                break
            except UnicodeDecodeError:
                end -= 1
    if end == start and start < len(source):
        raise ValueError("byte budget cannot contain one UTF-8 codepoint")
    return source[start:end], end


def envelope(
    *, command: str, response_class: str, scope: dict[str, Any], data: Any,
    complete: bool = True, truncated: bool = False, returned_items: int | None = None,
    total_items: int | None = None, returned_bytes: int | None = None,
    source_bytes: int | None = None, source_sha256: str | None = None,
    next_cursor: str | None = None, error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "format": RESPONSE_FORMAT,
        "schemaVersion": 1,
        "command": command,
        "responseClass": response_class,
        "scope": scope,
        "complete": complete,
        "truncated": truncated,
        "returnedItems": returned_items,
        "totalItems": total_items,
        "returnedBytes": returned_bytes,
        "sourceBytes": source_bytes,
        "sourceSha256": source_sha256,
        "nextCursor": next_cursor,
        "error": error,
        "data": data,
    }


def emit_json(**values: Any) -> None:
    print(canonical_json(envelope(**values)))
