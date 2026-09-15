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
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts"))
import maintain as maintainer
EXPECTED_DIGESTS = {
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/contract.json": "0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341",
    "plugins/wayfinder/skills/wayfinder/assets/contract-v1/release.json": "581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder.py": "e0b89ba35f223567efe2545d323d816dbaeeedfa8de8fb784fcc7b1c347cb596",
    "plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-node.mjs": "f6d695e60e5964448947ed9f835526efa0f84e3764fb8acdd7f765e3bbe4fa3e",
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
    try:
        status = maintainer.parse_status(maintainer.CURRENT_STATE_PATH)
        failures.extend("status authority: " + issue for issue in maintainer.status_issues(status))
        failures.extend("public status projection differs: " + path for path in maintainer.projection_drift(ROOT, status))
    except Exception as exc:
        failures.append(f"public status validation failed: {exc}")
        status = None

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if "references/current-state.md" not in agents_text:
        failures.append("AGENTS.md must route mutable Wayfinder status to current-state.md")
    if "v1-candidate-revision-" in agents_text or "five passing entries" in agents_text:
        failures.append("AGENTS.md must not duplicate mutable candidate or hosted status")
    if not all(
        marker in agents_text
        for marker in ("approval-response.md", "affirmative", "rejection", "Never begin the next task automatically")
    ):
        failures.append("AGENTS.md must route approval turns to the maintainer approval-response protocol")

    maintainer_root = ROOT / "plugins/wayfinder-maintainer/skills/wayfinder-maintainer"
    failures.extend("design history: " + issue for issue in maintainer.records.integrity_issues(maintainer_root / "references/design-record"))
    maintainer_skill = (maintainer_root / "SKILL.md").read_text(encoding="utf-8")
    if not all(
        marker in maintainer_skill
        for marker in ("Before asking the owner", "when processing the owner's response", "references/approval-response.md")
    ):
        failures.append("maintainer skill must route approval questions and responses to approval-response.md")
    approval_path = maintainer_root / "references/approval-response.md"
    approval_text = approval_path.read_text(encoding="utf-8") if approval_path.is_file() else ""
    if not all(
        marker in approval_text
        for marker in (
            "## Explicit affirmative response",
            "## Explicit rejection or revision request",
            "## Conditional response",
            "## Ambiguous response",
            "one material question per turn",
            "copy-ready prompt",
        )
    ):
        failures.append("canonical approval-response reference is missing required response behavior")
    workflow_text = (maintainer_root / "references/workflow.md").read_text(encoding="utf-8")
    if "[approval-response protocol](approval-response.md) is mandatory" not in workflow_text:
        failures.append("maintainer workflow must route approval handling to approval-response.md")
    for label, text in (("repository instructions", agents_text), ("maintainer skill", maintainer_skill), ("workflow", workflow_text), ("approval protocol", approval_text)):
        if not all(marker in text for marker in ("record list", "record read --id ID --history", "record add")):
            failures.append(f"{label} must advertise record discovery, affected-history reading, and exclusive additions")
    legacy_path = maintainer_root / "references/design-record.md"
    legacy_text = legacy_path.read_text(encoding="utf-8")
    try:
        manifest = load_json(maintainer_root / "references/design-record/migration.json")
        for section in manifest["sections"]:
            if f"## {section['title']}\n" not in legacy_text or f"(design-record/{section['path']})" not in legacy_text:
                failures.append(f"legacy design-record anchor/route missing: {section['id']}")
    except Exception as exc:
        failures.append(f"legacy design-record routing failed: {exc}")
    handoff_source = (maintainer_root / "scripts/maintain.py").read_text(encoding="utf-8")
    if not all(
        marker in handoff_source
        for marker in ("Approval response", "references/approval-response.md", "stop without beginning that task")
    ):
        failures.append("maintainer handoff generator must carry the approval-response reminder")

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
        expected_version = status["candidate"]["packageVersion"] if name == "wayfinder" and status else portable.get("version")
        if portable.get("name") != name or portable.get("version") != expected_version or not portable.get("version"):
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
