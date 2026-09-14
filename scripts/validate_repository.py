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
VERSION = "1.0.0-rc.9"
EXPECTED_DIGESTS = {
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/contract.json": "3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/release.json": "1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder.py": "f8fe1a0987a37e8a9a43003ede1bcb9eda590c88511daebaafcdd5d13932337a",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-node.mjs": "df0f3c2a000454b2f7aaa8fcf6762b670aab34b9cb721da571fe334ae29f10ac",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-powershell.ps1": "b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-8-local.json": "28bc61ede21e0b8041c1951b1327c948642d0712170048f17ce2bab9653562ef",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-8-local.md": "840641fd2b2814104a78f7fe0d4106ac70c4688056237003770d7ec7874e97c0",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json": "6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md": "8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/candidate-revision-9-local.json": "b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/candidate-revision-9-local.md": "99a5ef242b1e96e966d1fe9cff3549565008520451921bc1e9d7abfc3237d264",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-9-local.json": "3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/parity-revision-9-local.md": "11f3f7436b96c2be98e5efeb8fb2fb29bb373ba8826ea38b0594aeba806c00f5",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/proposed-freeze-revision-9.json": "9baf19c1f17848b7f0b1b12ff0e821472358f2aadde3dafa4f423194cb5e916c",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/proposed-freeze-revision-9.md": "b75d8862b47a16b13c4862643e7551d44777c98348cd9608f5c5aebd1ff8855f",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/freeze-acceptance-revision-9.json": "a934affb933fac7ad994257453afda952b6e81d7852e791f60389ebce4767088",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/freeze-acceptance-revision-9.md": "2f0c4bb8859bb3f7f0356038922678673544ddf45907bcdb680670813a581691",
}
TEXT_SUFFIXES = {".abnf", ".json", ".md", ".mjs", ".ps1", ".py", ".sh", ".yaml", ".yml"}
MUTABLE_POST_MIGRATION_PATHS = {
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/SKILL.md",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/design-record.md",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/workflow.md",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/run.py",
    "plugins/wayfinder/skills/wayfinder/SKILL.md",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/conformance/v1/expected/initialize-minimal-golden.json",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/conformance/v1/expected/probe-deterministic.json",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/contract.json",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/release.json",
    "plugins/wayfinder/skills/wayfinder/references/contracts/v1.md",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-node.mjs",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-powershell.ps1",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder.py",
}


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

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if "references/current-state.md" not in agents_text:
        failures.append("AGENTS.md must route mutable Wayfinder status to current-state.md")
    if "v1-candidate-revision-" in agents_text or "five passing entries" in agents_text:
        failures.append("AGENTS.md must not duplicate mutable candidate or hosted status")
    runtime_skill = (ROOT / "plugins/wayfinder/skills/wayfinder/SKILL.md").read_text(encoding="utf-8")
    if "candidate revision 8" in runtime_skill.lower() or "candidate revision 9" in runtime_skill.lower():
        failures.append("runtime skill must not duplicate mutable candidate status")

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
            if (
                item["destinationPath"] not in MUTABLE_POST_MIGRATION_PATHS
                and actual != item["destinationSha256"]
            ):
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
