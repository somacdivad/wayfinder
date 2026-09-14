#!/usr/bin/env python3
"""Rebuild or check the digest-bound cumulative Slice 5 contract package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any


CONTRACT_REL = "assets/contract-v1/contract.json"
RELEASE_REL = "assets/contract-v1/release.json"


def encode_pretty(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def role_for(path: str) -> str:
    if path == "references/contracts/v1.md":
        return "semantic-contract"
    if "/schemas/" in path:
        return "machine-schema"
    if "/templates/" in path:
        return "literal-template"
    if path.endswith("grammar.abnf"):
        return "machine-grammar"
    if path.endswith("known-answer.json"):
        return "known-answer"
    if path.endswith("cases.json"):
        return "fixture-index"
    if "/inputs/" in path:
        return "fixture-input"
    if "/expected/" in path:
        return "fixture-expected"
    raise ValueError(f"no governed role for {path}")


def validate_text(path: Path, raw: bytes) -> None:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ValueError(f"invalid UTF-8/LF profile: {path}")
    text = raw.decode("utf-8", "strict")
    if unicodedata.normalize("NFC", text) != text:
        raise ValueError(f"non-NFC governed resource: {path}")


def build(skill_root: Path) -> tuple[bytes, bytes]:
    contract_path = skill_root / CONTRACT_REL
    release_path = skill_root / RELEASE_REL
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    resources: list[dict[str, str]] = []
    observed: set[str] = set()
    for scope in contract["governedScopes"]:
        target = skill_root / PurePosixPath(scope["path"])
        candidates = sorted(target.rglob("*") if scope["recursive"] and target.is_dir() else [target])
        for path in candidates:
            if path.is_symlink():
                raise ValueError(f"symlink in governed scope: {path}")
            if path.is_file():
                relative = path.relative_to(skill_root).as_posix()
                if relative in observed:
                    raise ValueError(f"resource appears in multiple scopes: {relative}")
                observed.add(relative)
                raw = path.read_bytes()
                validate_text(path, raw)
                resources.append({"path": relative, "role": role_for(relative), "sha256": digest(raw)})
    resources.sort(key=lambda item: item["path"])
    contract["governedResources"] = resources
    contract_raw = encode_pretty(contract)

    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["contractManifest"]["sha256"] = digest(contract_raw)
    for adapter in release["adapters"]:
        adapter_path = skill_root / PurePosixPath(adapter["path"])
        adapter_raw = adapter_path.read_bytes()
        validate_text(adapter_path, adapter_raw)
        adapter["sha256"] = digest(adapter_raw)
    release_raw = encode_pretty(release)
    return contract_raw, release_raw


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--skill-root", type=Path)
    args = parser.parse_args(argv)
    maintainer_root = Path(__file__).resolve().parents[3]
    packaged_root = maintainer_root.parents[2] / "wayfinder" / "skills" / "wayfinder"
    legacy_root = maintainer_root.parent / "wayfinder"
    configured_root = os.environ.get("WAYFINDER_SKILL_ROOT")
    skill_root = (
        args.skill_root
        or (Path(configured_root).expanduser() if configured_root else None)
        or (packaged_root if packaged_root.is_dir() else legacy_root)
    ).resolve()
    contract_raw, release_raw = build(skill_root)
    current_contract = (skill_root / CONTRACT_REL).read_bytes()
    current_release = (skill_root / RELEASE_REL).read_bytes()
    if args.check:
        if current_contract != contract_raw or current_release != release_raw:
            print("contract package digests are stale", file=sys.stderr)
            return 1
        print(f"contract={digest(contract_raw)} release={digest(release_raw)}")
        return 0
    (skill_root / CONTRACT_REL).write_bytes(contract_raw)
    (skill_root / RELEASE_REL).write_bytes(release_raw)
    print(f"contract={digest(contract_raw)} release={digest(release_raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
