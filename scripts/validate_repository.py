#!/usr/bin/env python3
"""Validate Wayfinder repository packaging and migration invariants."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAMES = ("wayfinder", "wayfinder-maintainer")
VERSION = "1.0.0-rc.8"
EXPECTED_DIGESTS = {
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/contract.json": "75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/release.json": "677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder.py": "d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-node.mjs": "fcd01cfd47c98488eb2e85055924630642ee4093c02272bb67ba961d4e084125",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-powershell.ps1": "9b64624f0c837db6082ce241a3f17f3d05614490e4e721d757588c8fefbe0bce",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-8-local.json": "28bc61ede21e0b8041c1951b1327c948642d0712170048f17ce2bab9653562ef",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-8-local.md": "840641fd2b2814104a78f7fe0d4106ac70c4688056237003770d7ec7874e97c0",
}
TEXT_SUFFIXES = {".abnf", ".json", ".md", ".mjs", ".ps1", ".py", ".sh", ".yaml", ".yml"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate member {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_bytes().decode("utf-8", "strict"), object_pairs_hook=pairs)


def main() -> int:
    failures: list[str] = []

    for name in PLUGIN_NAMES:
        plugin_root = ROOT / "plugins" / name
        portable = load_json(plugin_root / "plugin.json")
        claude = load_json(plugin_root / ".claude-plugin" / "plugin.json")
        codex = load_json(plugin_root / ".codex-plugin" / "plugin.json")
        for field in ("name", "version", "description", "author", "homepage", "repository", "license"):
            if portable.get(field) != claude.get(field) or portable.get(field) != codex.get(field):
                failures.append(f"{name}: compatibility manifest differs at {field}")
        if portable.get("name") != name or portable.get("version") != VERSION:
            failures.append(f"{name}: portable identity differs")
        if codex.get("skills") != "./skills/":
            failures.append(f"{name}: Codex skills path differs")
        skill_root = plugin_root / "skills" / name
        if not (skill_root / "SKILL.md").is_file():
            failures.append(f"{name}: skill entrypoint missing")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if [entry.get("name") for entry in codex_market.get("plugins", [])] != ["wayfinder"]:
        failures.append("Codex marketplace must list only the runtime plugin")
    if [entry.get("name") for entry in claude_market.get("plugins", [])] != ["wayfinder"]:
        failures.append("Claude marketplace must list only the runtime plugin")

    for relative, expected in EXPECTED_DIGESTS.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            failures.append(f"frozen or accepted digest differs: {relative}")

    manifest_path = ROOT / "docs" / "migration-manifest.json"
    if manifest_path.is_file():
        manifest = load_json(manifest_path)
        for item in manifest.get("files", []):
            destination = ROOT / item["destinationPath"]
            actual = sha256(destination) if destination.is_file() else "missing"
            if actual != item["destinationSha256"]:
                failures.append(f"migration destination differs: {item['destinationPath']}")
            if item["status"] == "byte-identical" and item["sourceSha256"] != item["destinationSha256"]:
                failures.append(f"byte-identical migration entry disagrees: {item['destinationPath']}")
    else:
        failures.append("migration manifest missing")

    for path in ROOT.rglob("*"):
        if path.is_symlink():
            failures.append(f"symbolic link is not allowed: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                failures.append(f"UTF-8 BOM is not allowed: {path.relative_to(ROOT)}")
            if b"\r\n" in raw or b"\r" in raw:
                failures.append(f"non-LF newline is not allowed: {path.relative_to(ROOT)}")
    if list(ROOT.rglob("__pycache__")) or list(ROOT.rglob("*.pyc")):
        failures.append("Python bytecode cache is present")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS repository packaging, frozen digests, migration manifest, and text profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
