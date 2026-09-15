"""Ephemeral, non-authoritative Wayfinder maintenance checkpoints."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


def _run(root: Path, *args: str) -> bytes:
    completed = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise ValueError(completed.stderr.decode("utf-8", "replace").strip())
    return completed.stdout


def fingerprint(root: Path) -> dict[str, Any]:
    root = root.resolve()
    head = _run(root, "rev-parse", "HEAD").decode().strip()
    staged = _run(root, "diff", "--cached", "--binary", "--no-ext-diff")
    unstaged = _run(root, "diff", "--binary", "--no-ext-diff")
    names = _run(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    untracked: list[tuple[bytes, str]] = []
    for raw in names:
        if not raw:
            continue
        relative = raw.decode("utf-8", "surrogateescape")
        path = root / relative
        if path.is_symlink():
            identity = b"symlink\0" + os.fsencode(os.readlink(path))
        elif path.is_file():
            identity = b"file\0" + path.read_bytes()
        else:
            identity = f"unsupported\0{path.lstat().st_mode}".encode()
        untracked.append((raw, hashlib.sha256(identity).hexdigest()))
    digest = hashlib.sha256()
    for label, data in ((b"HEAD\0", head.encode()), (b"STAGED\0", staged), (b"UNSTAGED\0", unstaged)):
        digest.update(label); digest.update(data); digest.update(b"\0")
    for raw, file_digest in sorted(untracked):
        digest.update(b"UNTRACKED\0"); digest.update(raw); digest.update(b"\0"); digest.update(file_digest.encode()); digest.update(b"\0")
    return {"head": head, "sha256": digest.hexdigest(), "stagedBytes": len(staged), "unstagedBytes": len(unstaged), "untrackedFiles": len(untracked)}


def create_checkpoint(root: Path, supplied: dict[str, Any], current_state: Path) -> dict[str, Any]:
    root = root.resolve()
    current_state = current_state.resolve()
    required = {"objective", "tranche", "exclusions", "sources", "validations", "mutations", "failures", "unresolved", "nextSafeAction", "cursor"}
    if not isinstance(supplied, dict) or set(supplied) != required:
        raise ValueError("checkpoint input fields differ")
    if any(not isinstance(supplied[key], str) or not supplied[key] for key in ("objective", "tranche", "nextSafeAction")):
        raise ValueError("checkpoint objective, tranche, and next safe action must be nonempty strings")
    if any(not isinstance(supplied[key], list) for key in ("exclusions", "sources", "validations", "mutations", "failures", "unresolved")):
        raise ValueError("checkpoint record fields must be arrays")
    if not all(isinstance(item, str) for item in supplied["exclusions"]):
        raise ValueError("checkpoint exclusions must be strings")
    if supplied["cursor"] is not None and not isinstance(supplied["cursor"], str):
        raise ValueError("checkpoint cursor must be a string or null")
    sources = []
    for item in supplied["sources"]:
        if isinstance(item, dict) and set(item) == {"locator", "scope", "sha256"}:
            if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
                raise ValueError("external source digest must be SHA-256")
            sources.append(dict(item))
            continue
        if not isinstance(item, dict) or set(item) != {"path", "scope"}:
            raise ValueError("checkpoint source must name path/scope or locator/scope/sha256")
        relative = Path(item["path"])
        original = root / relative
        path = original.resolve()
        symbolic = any((root / Path(*relative.parts[:index])).is_symlink() for index in range(1, len(relative.parts) + 1))
        if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root) or symbolic or not path.is_file():
            raise ValueError(f"unsafe checkpoint source: {relative}")
        sources.append({"path": relative.as_posix(), "scope": item["scope"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {
        "format": "wayfinder-maintainer-checkpoint", "schemaVersion": 1,
        "authority": "derived-non-authoritative", **{key: supplied[key] for key in required if key != "sources"},
        "sources": sources,
        "currentState": {"path": str(current_state.relative_to(root)), "sha256": hashlib.sha256(current_state.read_bytes()).hexdigest()},
        "worktree": fingerprint(root),
    }


def verify_checkpoint(root: Path, checkpoint: dict[str, Any], current_state: Path) -> list[str]:
    root = root.resolve()
    current_state = current_state.resolve()
    issues: list[str] = []
    required = {"format", "schemaVersion", "authority", "objective", "tranche", "exclusions", "sources", "validations", "mutations", "failures", "unresolved", "nextSafeAction", "cursor", "currentState", "worktree"}
    if not isinstance(checkpoint, dict) or set(checkpoint) != required or checkpoint.get("format") != "wayfinder-maintainer-checkpoint" or checkpoint.get("schemaVersion") != 1 or checkpoint.get("authority") != "derived-non-authoritative":
        return ["checkpoint identity differs"]
    if checkpoint.get("currentState", {}).get("sha256") != hashlib.sha256(current_state.read_bytes()).hexdigest():
        issues.append("current state changed")
    if checkpoint.get("currentState", {}).get("path") != str(current_state.relative_to(root)):
        issues.append("current state path differs")
    if checkpoint.get("worktree") != fingerprint(root):
        issues.append("worktree changed")
    for item in checkpoint.get("sources", []):
        if not isinstance(item, dict) or set(item) not in ({"path", "scope", "sha256"}, {"locator", "scope", "sha256"}):
            issues.append("source provenance fields differ")
            continue
        if "locator" in item:
            continue
        original = root / item.get("path", "")
        path = (root / item.get("path", "")).resolve()
        relative = Path(item.get("path", ""))
        symbolic = any((root / Path(*relative.parts[:index])).is_symlink() for index in range(1, len(relative.parts) + 1))
        if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root) or not path.is_file() or symbolic:
            issues.append(f"source unavailable: {item.get('path')}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            issues.append(f"source changed: {item.get('path')}")
    return issues
