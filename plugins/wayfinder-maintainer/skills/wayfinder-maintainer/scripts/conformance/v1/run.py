#!/usr/bin/env python3
"""Black-box conformance runner for Wayfinder Stage 0 through Slice 5."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from test_controls import TestControls


RESULT_FIELDS = ["format", "schemaVersion", "ok", "command", "code", "data", "diagnostics"]
CONFORMANCE_REL = "assets/contract-v1/conformance/v1"
OBSERVATIONS: list[dict[str, Any]] | None = None
OBSERVATION_ROOT: Path | None = None
OBSERVATION_CASE: str | None = None
DIFFERENTIAL_MODE = False


class CaseFailure(Exception):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pretty(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def snapshot(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            items.append({"path": relative, "kind": "symlink", "target": os.readlink(path)})
        elif path.is_dir():
            items.append({"path": relative, "kind": "directory"})
        elif path.is_file():
            raw = path.read_bytes()
            items.append({"path": relative, "kind": "file", "size": len(raw), "sha256": sha256(raw)})
    return items


def adapter_command(adapter: Path) -> list[str]:
    suffix = adapter.suffix.lower()
    if suffix == ".py":
        return [sys.executable, str(adapter)]
    if suffix == ".mjs":
        return [os.environ.get("WAYFINDER_NODE_RUNTIME", "node"), str(adapter)]
    if suffix == ".ps1":
        return [
            os.environ.get("WAYFINDER_POWERSHELL_RUNTIME", "pwsh"),
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(adapter),
        ]
    raise CaseFailure(f"unsupported adapter suffix: {adapter}")


def invoke(adapter: Path, args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    if (
        DIFFERENTIAL_MODE
        and args
        and args[0] in {"initialize-apply", "initialize-recover"}
        and not any(key.startswith("WAYFINDER_TEST_") for key in (env or {}))
    ):
        process_env["WAYFINDER_TEST_MODE"] = "1"
        process_env["WAYFINDER_TEST_CLOCK"] = "2026-09-13T12:34:56Z"
    completed = subprocess.run(
        [*adapter_command(adapter), *args],
        cwd=str(cwd) if cwd else None,
        env=process_env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=15,
        check=False,
    )
    if not completed.stdout.endswith(b"\n") or len(completed.stdout.splitlines()) != 1:
        raise CaseFailure(f"stdout is not exactly one LF-terminated line: {completed.stdout!r}")
    try:
        result = json.loads(completed.stdout.decode("utf-8"))
    except Exception as exc:
        raise CaseFailure(f"stdout is not one UTF-8 JSON object: {exc}") from exc
    if not isinstance(result, dict) or list(result) != RESULT_FIELDS:
        raise CaseFailure(f"result envelope fields/order differ: {list(result) if isinstance(result, dict) else type(result)}")
    if result["format"] != "wayfinder-command-result" or result["schemaVersion"] != 1:
        raise CaseFailure("result envelope identity differs")
    if completed.returncode == 0 and completed.stderr:
        raise CaseFailure(f"successful command wrote stderr: {completed.stderr!r}")
    if completed.returncode != 0 and not completed.stderr:
        raise CaseFailure("failed command did not write a human diagnostic to stderr")
    if b"Traceback" in completed.stdout or b"Traceback" in completed.stderr:
        raise CaseFailure("traceback contaminated command output")
    if OBSERVATIONS is not None:
        root = str(OBSERVATION_ROOT) if OBSERVATION_ROOT is not None else ""

        def normalized(value: Any) -> Any:
            if isinstance(value, str):
                return value.replace(root, "<TEMP>") if root else value
            if isinstance(value, list):
                return [normalized(item) for item in value]
            if isinstance(value, dict):
                return {key: normalized(item) for key, item in value.items()}
            return value

        OBSERVATIONS.append({
            "case": OBSERVATION_CASE,
            "invocation": sum(1 for item in OBSERVATIONS if item["case"] == OBSERVATION_CASE) + 1,
            "arguments": normalized(args),
            "exit": completed.returncode,
            "result": normalized(result),
            "stderr": normalized(completed.stderr.decode("utf-8", "replace")),
        })
    return completed, result


def assert_expected(case: dict[str, Any], completed: subprocess.CompletedProcess[bytes], result: dict[str, Any]) -> None:
    if completed.returncode != case["exit"]:
        raise CaseFailure(f"exit {completed.returncode}, expected {case['exit']}; stderr={completed.stderr.decode(errors='replace')}")
    if result["code"] != case["code"]:
        raise CaseFailure(f"code {result['code']!r}, expected {case['code']!r}")
    if result["ok"] != (case["exit"] == 0):
        raise CaseFailure("ok flag disagrees with exit class")
    if result["ok"] and result["diagnostics"] != []:
        raise CaseFailure("successful result has diagnostics")
    if not result["ok"]:
        if len(result["diagnostics"]) != 1 or result["diagnostics"][0].get("code") != result["code"]:
            raise CaseFailure("failure diagnostics do not contain exactly the primary stable code")


def load_manifest(skill_root: Path, name: str = "manifest-minimal.json") -> dict[str, Any]:
    return json.loads((skill_root / CONFORMANCE_REL / "inputs" / name).read_text(encoding="utf-8"))


def materialize(workspace: Path, manifest: dict[str, Any], *, raw: bytes | None = None) -> None:
    control = workspace / ".wayfinder"
    control.mkdir(parents=True, exist_ok=True)
    record_root = workspace if manifest.get("recordRoot") == "." else workspace / manifest.get("recordRoot", "record")
    record_root.mkdir(parents=True, exist_ok=True)
    entrypoint = manifest.get("entrypoint")
    if isinstance(entrypoint, str) and ".." not in entrypoint and "\\" not in entrypoint and not entrypoint.startswith("/"):
        target = record_root / entrypoint
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Record\n", encoding="utf-8", newline="\n")
    for module in manifest.get("modules", []):
        if not isinstance(module, dict):
            continue
        for key, is_dir in (("root", True), ("entrypoint", False)):
            value = module.get(key)
            if isinstance(value, str) and value and ".." not in value and "\\" not in value and not value.startswith("/"):
                target = record_root / value
                if is_dir:
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("# Module\n", encoding="utf-8", newline="\n")
        for subject in module.get("subjects", []):
            if not isinstance(subject, dict):
                continue
            if subject.get("kind") == "collection" and isinstance(subject.get("root"), str):
                (record_root / subject["root"]).mkdir(parents=True, exist_ok=True)
            value = subject.get("entrypoint")
            if isinstance(value, str) and value and ".." not in value and "\\" not in value and not value.startswith("/"):
                target = record_root / value
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# Subject\n", encoding="utf-8", newline="\n")
    baseline = manifest.get("canonicalBaseline", {})
    if isinstance(baseline, dict) and baseline.get("kind") == "snapshot" and isinstance(baseline.get("path"), str):
        target = workspace / baseline["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n", encoding="utf-8", newline="\n")
    for artifact in manifest.get("generatedArtifacts", []):
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str):
            target = record_root / artifact["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8", newline="\n")
    (control / "manifest.json").write_bytes(raw if raw is not None else pretty(manifest))


def source_request(selections: list[str] | None = None, *, limits: dict[str, int] | None = None) -> dict[str, Any]:
    return {
        "format": "wayfinder-source-inventory-request",
        "schemaVersion": 1,
        "selections": selections or ["sources"],
        "targetRoots": ["sources/target"],
        "limits": limits or {"maxEntries": 200, "maxFileBytes": 10000, "maxTotalBytes": 100000, "maxDepth": 12},
    }


def make_source_tree(workspace: Path) -> None:
    sources = workspace / "sources"
    (sources / "nested").mkdir(parents=True)
    (sources / "node_modules").mkdir()
    (sources / "build").mkdir()
    (sources / ".git").mkdir()
    (sources / ".wayfinder").mkdir()
    (sources / "target").mkdir()
    (sources / "a.md").write_bytes(b"# Alpha\n\n## Details ##\n\n```\n# Not a heading\n```\n")
    (sources / "z.txt").write_bytes(b"same\n")
    (sources / "nested/b.txt").write_bytes(b"same\n")
    (sources / "bad.bin").write_bytes(b"\xff\xfe\x00")
    (sources / "node_modules/pkg.txt").write_bytes(b"dependency\n")
    (sources / "build/out.txt").write_bytes(b"build\n")
    (sources / "archive.zip").write_bytes(b"archive\n")
    (sources / ".env").write_bytes(b"SECRET=value\n")
    (sources / ".git/config").write_bytes(b"[core]\n")
    (sources / ".wayfinder/state.json").write_bytes(b"{}\n")
    (sources / "target/generated.md").write_bytes(b"# Target\n")
    outside = workspace / "outside"
    outside.mkdir()
    (outside / "outside.txt").write_bytes(b"outside\n")
    (sources / "link-file").symlink_to("a.md")
    (sources / "link-dir").symlink_to(outside, target_is_directory=True)
    if hasattr(os, "mkfifo"):
        os.mkfifo(sources / "named-pipe")


def invoke_inventory(
    adapter: Path,
    workspace: Path,
    request: dict[str, Any] | bytes,
    *,
    ledger: dict[str, Any] | bytes | None = None,
) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    request_path = workspace.parent / "request.json"
    request_path.write_bytes(request if isinstance(request, bytes) else pretty(request))
    args = ["inventory", "--workspace-root", str(workspace), "--request", str(request_path)]
    if ledger is not None:
        ledger_path = workspace.parent / "ledger.json"
        ledger_path.write_bytes(ledger if isinstance(ledger, bytes) else pretty(ledger))
        args.extend(["--ledger", str(ledger_path)])
    return invoke(adapter, args)


def invoke_generate(
    adapter: Path,
    workspace: Path,
    request: dict[str, Any] | bytes,
    *,
    output_root: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    request_path = workspace.parent / "generation-request.json"
    request_path.write_bytes(request if isinstance(request, bytes) else pretty(request))
    args = ["generate", "--workspace-root", str(workspace), "--request", str(request_path)]
    if output_root is not None:
        args.extend(["--output-root", str(output_root)])
    return invoke(adapter, args, env=env)


def initialize_proposal(skill_root: Path) -> dict[str, Any]:
    return json.loads((skill_root / CONFORMANCE_REL / "inputs/initialize-minimal.json").read_text(encoding="utf-8"))


def make_git_baseline(workspace: Path) -> None:
    target = workspace / ".git/refs/heads/main"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("1111111111111111111111111111111111111111\n", encoding="ascii", newline="\n")


def invoke_initialize(adapter: Path, workspace: Path, proposal: dict[str, Any], bundle: Path, *, env: dict[str, str] | None = None, raw: bytes | None = None) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    request_path = workspace.parent / (bundle.name + "-proposal.json")
    request_path.write_bytes(raw if raw is not None else pretty(proposal))
    return invoke(adapter, ["initialize-plan", "--workspace-root", str(workspace), "--proposal", str(request_path), "--bundle-root", str(bundle)], env=env)


def prepare_apply(skill_root: Path, adapter: Path, temporary: Path, *, source_assisted: bool = False) -> tuple[Path, Path, str, str, dict[str, Any]]:
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_git_baseline(workspace)
    (workspace / "unrelated.txt").write_bytes(b"preserve me\n")
    proposal = initialize_proposal(skill_root)
    if source_assisted:
        source_root = workspace / "sources"
        source_root.mkdir()
        source_file = source_root / "legacy.md"
        source_file.write_bytes(b"# Legacy planning note\n\nPreserved outside the initial governed scope.\n")
        request = source_request(["sources"])
        request["targetRoots"] = ["record"]
        completed, inventory_result = invoke_inventory(adapter, workspace, request)
        if completed.returncode != 0:
            raise CaseFailure("source-assisted apply setup inventory failed")
        inventory = inventory_result["data"]["inventory"]
        inventory_digest = inventory_result["data"]["inventorySha256"]
        inventory_path = workspace / "source-inventory.json"
        inventory_path.write_bytes(pretty(inventory))
        entry = next(item for item in inventory["entries"] if item["path"] == "sources/legacy.md")
        ledger = {
            "format": "wayfinder-intake-ledger", "schemaVersion": 1, "inventorySha256": inventory_digest,
            "sources": [{
                "path": "sources/legacy.md", "sha256": entry["sha256"], "byteLength": entry["byteLength"],
                "disposition": "preserve-out-of-scope", "reason": "The owner confirmed this source remains outside the bootstrap.",
                "targetIds": [], "transformationNote": None, "evidenceKeys": [], "questionIds": [],
            }],
        }
        ledger_path = workspace / "intake-ledger.json"
        ledger_path.write_bytes(pretty(ledger))
        ledger_digest = sha256(json.dumps(ledger, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        proposal["mode"] = "source-assisted"
        proposal["sourceInventory"] = {"path": "source-inventory.json", "sha256": inventory_digest}
        proposal["intakeLedger"] = {"path": "intake-ledger.json", "sha256": ledger_digest}
        proposal["materialSourcePaths"] = ["sources/legacy.md"]
    bundle = temporary / "bundle"
    completed, result = invoke_initialize(adapter, workspace, proposal, bundle)
    if completed.returncode != 0:
        raise CaseFailure(f"apply setup planning failed: {completed.stderr!r}")
    digest = result["data"]["planSha256"]
    operation_id = f"wfinit-{digest[:24]}"
    return workspace, bundle, digest, operation_id, proposal


def invoke_apply(adapter: Path, workspace: Path, bundle: Path, digest: str, *, token: str | None = None, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    return invoke(adapter, [
        "initialize-apply", "--workspace-root", str(workspace), "--bundle-root", str(bundle),
        "--plan-sha256", digest, "--confirmation-token", token if token is not None else f"wayfinder-confirm-sha256:{digest}",
    ], env=env)


def invoke_recover(adapter: Path, workspace: Path, operation_id: str, action: str, *, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    return invoke(adapter, ["initialize-recover", "--workspace-root", str(workspace), "--operation-id", operation_id, "--action", action], env=env)


def wf_metadata(identifier: str, kind: str, status: str, summary: str, *, decision_date: str | None = None, supersedes: list[str] | None = None, superseded_by: list[str] | None = None) -> str:
    lines = [
        "<!-- wayfinder:metadata -->",
        f"- **ID:** {identifier}",
        f"- **Kind:** {kind}",
        f"- **Status:** {status}",
        "- **Updated:** 2026-09-13",
        f"- **Summary:** {summary}",
    ]
    if decision_date is not None:
        lines.append(f"- **Decision-Date:** {decision_date}")
    if supersedes:
        lines.append(f"- **Supersedes:** {', '.join(supersedes)}")
    if superseded_by:
        lines.append(f"- **Superseded-By:** {', '.join(superseded_by)}")
    lines.append("<!-- /wayfinder:metadata -->")
    return "\n".join(lines)


def wf_doc(title: str, identifier: str, kind: str, status: str, summary: str, body: str, *, decision_date: str | None = None, supersedes: list[str] | None = None, superseded_by: list[str] | None = None, relationships: list[tuple[str, str, str]] | None = None) -> bytes:
    parts = [f"# {title}", "", wf_metadata(identifier, kind, status, summary, decision_date=decision_date, supersedes=supersedes, superseded_by=superseded_by)]
    if relationships:
        parts.extend(["", "<!-- wayfinder:relationships -->"])
        parts.extend(f"- **{relation}:** [{target_id}]({target_path})" for relation, target_id, target_path in relationships)
        parts.append("<!-- /wayfinder:relationships -->")
    parts.extend(["", body.rstrip(), ""])
    return "\n".join(parts).encode("utf-8")


def base_generation_request(action: str) -> dict[str, Any]:
    return {"format": "wayfinder-generation-request", "schemaVersion": 1, "action": action}


def make_slice3_record(adapter: Path, workspace: Path, *, with_regions: bool = True) -> dict[str, Any]:
    manifest = {
        "format": "wayfinder-project-record",
        "schemaVersion": 1,
        "recordRoot": "record",
        "entrypoint": "README.md",
        "canonicalBaseline": {"kind": "git-ref", "ref": "refs/heads/main"},
        "modules": [
            {"id": "decisions", "root": "decisions", "entrypoint": "decisions/README.md", "subjects": []},
            {"id": "research", "root": "research", "entrypoint": "research/README.md", "subjects": [{"id": "sources", "kind": "collection", "root": "research/sources", "entrypoint": "research/sources/README.md"}]},
            {"id": "product", "root": "product", "entrypoint": "product/product.md", "subjects": [{"id": "questions", "kind": "document", "entrypoint": "product/questions.md"}]},
        ],
        "generatedArtifacts": [{"path": ".wayfinder/catalog.json", "generator": "document-catalog-v1"}],
    }
    control = workspace / ".wayfinder"
    record = workspace / "record"
    control.mkdir(parents=True)
    (record / ".wayfinder").mkdir(parents=True)
    for directory in ("decisions", "research", "research/sources", "product"):
        (record / directory).mkdir(parents=True, exist_ok=True)
    (control / "manifest.json").write_bytes(pretty(manifest))
    (record / ".wayfinder/catalog.json").write_bytes(b"{}\n")
    placeholder = '<!-- wayfinder:generated name="members" generator="document-index-v1" input-sha256="' + "0" * 64 + '" -->\nold\n<!-- /wayfinder:generated -->'
    map_body = "## Authority boundary\n\nSynthetic record authority."
    if with_regions:
        map_body += "\n\n## Modules\n\n" + placeholder
    (record / "README.md").write_bytes(wf_doc("Synthetic record", "wf-0001-record-map", "map", "Active", "Routes the synthetic record.", map_body))
    index_body = "## Collection scope\n\nSynthetic collection."
    if with_regions:
        index_body += "\n\n## Members\n\n" + placeholder
    (record / "decisions/README.md").write_bytes(wf_doc("Decision index", "wf-0002-decision-index", "index", "Active", "Indexes synthetic decisions.", index_body))
    decision_body = "## Context\n\nA choice was required.\n\n## Options considered\n\nOne option.\n\n## Decision\n\nUse the synthetic rule.\n\n## Rationale\n\nIt is testable.\n\n## Consequences\n\nFixtures rely on it.\n\n## References\n\nNo external references.\n\n## Supersession\n\nThis decision supersedes nothing."
    (record / "decisions/decision.md").write_bytes(wf_doc("Synthetic decision", "wf-0003-synthetic-decision", "decision", "Accepted", "Governs the synthetic record.", decision_body, decision_date="2026-09-13"))
    (record / "research/README.md").write_bytes(wf_doc("Research index", "wf-0004-research-index", "index", "Active", "Indexes synthetic evidence.", index_body))
    (record / "research/sources/README.md").write_bytes(wf_doc("Source collection", "wf-0005-source-index", "index", "Active", "Indexes source evidence.", index_body))
    evidence_body = """## Question and scope

What evidence supports the synthetic rule?

## Method

Inspect one authoritative source.

## Findings

- **Material claim:** The source exists. [src-01](#src-01)

## Applicability and limitations

The source is synthetic and direct.

## Evidence, inference, and hypothesis

The claim is evidence.

## Implications

The fixture may cite it.

## Unknowns

None for this fixture.

## Next validation

Re-run conformance.

## Sources

<!-- wayfinder:source -->
<a id="src-01"></a>
### src-01 — Synthetic source
- **Citation:** Synthetic source record, 2026.
- **Original:** https://example.test/source
- **Accessed:** 2026-09-13
- **Applicability:** Direct

#### Used for

The existence claim.

#### Limitations

Synthetic fixture only.
<!-- /wayfinder:source -->"""
    (record / "research/sources/evidence.md").write_bytes(wf_doc("Synthetic evidence", "wf-0006-synthetic-evidence", "evidence", "Active", "Supports the synthetic rule.", evidence_body))
    relationships = [("Governed-By", "wf-0003-synthetic-decision", "../decisions/decision.md"), ("Supported-By", "wf-0006-synthetic-evidence", "../research/sources/evidence.md")]
    (record / "product/product.md").write_bytes(wf_doc("Product brief", "wf-0007-product-brief", "brief", "Active", "States the synthetic product direction.", "## Current synthesis\n\nFollow the synthetic rule.", relationships=relationships))
    question_body = """## Open questions

<!-- wayfinder:question -->
<a id="wfq-0001-retention"></a>
### How long should records be retained?
- **ID:** wfq-0001-retention
- **State:** Open
- **Raised:** 2026-09-13
- **Applies-To:** [wf-0007-product-brief](product.md)

#### Why it matters

It affects the synthetic boundary.

#### Next step

Ask the record owner.

#### History

- 2026-09-13: None -> Open - Raised during initialization.
<!-- /wayfinder:question -->"""
    (record / "product/questions.md").write_bytes(wf_doc("Open questions", "wf-0008-open-questions", "register", "Active", "Tracks synthetic open questions.", question_body))
    if with_regions:
        region_paths = ["README.md", "decisions/README.md", "research/README.md", "research/sources/README.md"]
        completed, result = invoke_generate(adapter, workspace, {**base_generation_request("regions"), "paths": region_paths})
        if completed.returncode != 0:
            raise CaseFailure(f"could not seed generated regions: {completed.stderr!r} {result}")
    completed, result = invoke_generate(adapter, workspace, base_generation_request("catalog"))
    if completed.returncode != 0:
        raise CaseFailure(f"could not seed catalog: {completed.stderr!r} {result}")
    return manifest


def ledger_source(entry: dict[str, Any], disposition: str) -> dict[str, Any]:
    result = {
        "path": entry["path"],
        "sha256": entry["sha256"],
        "byteLength": entry["byteLength"],
        "disposition": disposition,
        "reason": f"Reviewed as {disposition}.",
        "targetIds": [],
        "transformationNote": None,
        "evidenceKeys": [],
        "questionIds": [],
    }
    if disposition == "incorporate":
        result["targetIds"] = ["wf-0001-product-brief"]
        result["transformationNote"] = "Selected and synthesized relevant content."
    elif disposition == "reference":
        result["evidenceKeys"] = ["src-01"]
    elif disposition == "unresolved":
        result["questionIds"] = ["wfq-0001-source-authority"]
    return result


def run_discover(adapter: Path, workspace: Path, case: dict[str, Any], *, start: Path | None = None, explicit: bool = True) -> dict[str, Any]:
    args = ["discover", "--workspace-root", str(workspace)] if explicit else ["discover", "--start", str(start or workspace)]
    completed, result = invoke(adapter, args)
    assert_expected(case, completed, result)
    return result


def rewrite_package_json(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    path.write_bytes(pretty(value))


def package_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    copied = temporary / "wayfinder"
    shutil.copytree(skill_root, copied, symlinks=True)
    release = copied / "assets/contract-v1/release.json"
    contract = copied / "assets/contract-v1/contract.json"
    try:
        adapter_relative = adapter.relative_to(skill_root)
    except ValueError as exc:
        raise CaseFailure(f"adapter is outside staged skill root: {adapter}") from exc
    copied_adapter = copied / adapter_relative
    case_id = case["id"]
    if case_id == "package-resource-changed":
        path = copied / "references/contracts/v1.md"
        path.write_bytes(path.read_bytes() + b"<!-- mutation -->\n")
    elif case_id == "package-resource-missing":
        (copied / "assets/contract-v1/known-answer.json").unlink()
    elif case_id == "package-resource-unlisted":
        (copied / CONFORMANCE_REL / "expected/unlisted.json").write_text("{}\n", encoding="utf-8", newline="\n")
    elif case_id == "package-contract-version":
        rewrite_package_json(release, lambda value: value.__setitem__("contractVersion", 2))
    elif case_id == "package-adapter-changed":
        marker = b"// mutation\n" if copied_adapter.suffix == ".mjs" else b"# mutation\n"
        copied_adapter.write_bytes(copied_adapter.read_bytes() + marker)
    elif case_id == "package-release-malformed":
        release.write_bytes(b"{\n")
    elif case_id == "package-resource-duplicate":
        def duplicate(value: dict[str, Any]) -> None:
            value["governedResources"].append(copy.deepcopy(value["governedResources"][0]))
        rewrite_package_json(contract, duplicate)
        rewrite_package_json(release, lambda value: value["contractManifest"].__setitem__("sha256", sha256(contract.read_bytes())))
    elif case_id == "package-release-schema-mismatch":
        schema = copied / "assets/contract-v1/schemas/release.schema.json"
        rewrite_package_json(
            schema,
            lambda value: value["properties"].__setitem__(
                "releaseId",
                {"const": "v1-candidate-revision-999"},
            ),
        )
        rebuilt = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve().parent / "build_package.py"),
                "--skill-root",
                str(copied),
            ],
            cwd=copied,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if rebuilt.returncode != 0:
            raise CaseFailure(f"could not rebuild mutated package: {rebuilt.stderr}")
    elif case_id == "package-status-schema-mismatch":
        schema = copied / "assets/contract-v1/schemas/release.schema.json"
        rewrite_package_json(
            schema,
            lambda value: value["properties"].__setitem__("status", {"const": "unactivated-candidate"}),
        )
        rebuilt = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent / "build_package.py"), "--skill-root", str(copied)],
            cwd=copied,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if rebuilt.returncode != 0:
            raise CaseFailure(f"could not rebuild status-mutated package: {rebuilt.stderr}")
    elif case_id == "package-adapter-registry-mismatch":
        rewrite_package_json(
            release,
            lambda value: next(
                item for item in value["adapters"] if item["path"] == adapter_relative.as_posix()
            ).__setitem__("id", "other-reference-v1"),
        )
        rebuilt = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent / "build_package.py"), "--skill-root", str(copied)],
            cwd=copied,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if rebuilt.returncode != 0:
            raise CaseFailure(f"could not rebuild adapter-mutated package: {rebuilt.stderr}")
    completed, result = invoke(copied_adapter, ["probe"])
    assert_expected(case, completed, result)


def json_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    name = "manifest-realistic.json" if case["id"] == "json-valid-realistic" else "manifest-minimal.json"
    manifest = load_manifest(skill_root, name)
    workspace = temporary / "workspace"
    workspace.mkdir()
    raw: bytes | None = None
    case_id = case["id"]
    if case_id == "json-bom":
        raw = b"\xef\xbb\xbf" + pretty(manifest)
    elif case_id == "json-malformed-utf8":
        raw = pretty(manifest).replace(b"record", b"rec\xfford", 1)
    elif case_id == "json-malformed-unicode":
        raw = pretty(manifest).replace(b'"recordRoot": "record"', b'"recordRoot": "\\ud800"', 1)
    elif case_id == "json-duplicate-key":
        raw = pretty(manifest).replace(b'  "format":', b'  "format": "wayfinder-project-record",\n  "format":', 1)
    elif case_id == "json-unknown-key":
        manifest["extension"] = True
    elif case_id == "json-missing-field":
        del manifest["entrypoint"]
    elif case_id == "json-wrong-type":
        manifest["schemaVersion"] = True
    elif case_id == "json-unsupported-version":
        manifest["schemaVersion"] = 2
    elif case_id == "json-float":
        raw = pretty(manifest).replace(b'"schemaVersion": 1', b'"schemaVersion": 1.0', 1)
    elif case_id == "json-exponent":
        raw = pretty(manifest).replace(b'"schemaVersion": 1', b'"schemaVersion": 1e0', 1)
    elif case_id == "json-out-of-range-integer":
        raw = pretty(manifest).replace(b'"schemaVersion": 1', b'"schemaVersion": 9007199254740992', 1)
    elif case_id == "json-negative-zero":
        raw = pretty(manifest).replace(b'"schemaVersion": 1', b'"schemaVersion": -0', 1)
    elif case_id == "json-non-nfc":
        manifest["recordRoot"] = "re\u0301cord"
    elif case_id == "json-crlf":
        raw = pretty(manifest).replace(b"\n", b"\r\n")
    materialize(workspace, manifest, raw=raw)
    run_discover(adapter, workspace, case)


def discovery_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    manifest = load_manifest(skill_root)
    case_id = case["id"]
    if case_id in {"discover-explicit", "discover-upward", "discover-repository-root", "discover-file-start"}:
        workspace = temporary / "workspace"
        workspace.mkdir()
        if case_id == "discover-repository-root":
            (workspace / ".git").mkdir()
        materialize(workspace, manifest)
        nested = workspace / "nested/deep"
        nested.mkdir(parents=True)
        start: Path = nested
        explicit = case_id == "discover-explicit"
        if case_id == "discover-file-start":
            start = nested / "source.txt"
            start.write_text("source\n", encoding="utf-8")
        result = run_discover(adapter, workspace, case, start=start, explicit=explicit)
        if result["data"]["workspace"]["workspaceRoot"] != str(workspace.resolve()):
            raise CaseFailure("discovery selected the wrong workspace")
        return
    if case_id in {"discover-nearest-wins", "discover-invalid-nearest"}:
        parent = temporary / "parent"
        parent.mkdir()
        materialize(parent, manifest)
        nested = parent / "nested"
        nested.mkdir()
        nested_manifest = copy.deepcopy(manifest)
        nested_manifest["recordRoot"] = "inner-record"
        if case_id == "discover-invalid-nearest":
            nested_manifest["format"] = "not-wayfinder"
        materialize(nested, nested_manifest)
        start = nested / "deep"
        start.mkdir()
        result = run_discover(adapter, nested, case, start=start, explicit=False)
        if case["exit"] == 0 and result["data"]["workspace"]["workspaceRoot"] != str(nested.resolve()):
            raise CaseFailure("nearest workspace did not win")
        return
    if case_id == "discover-vcs-boundary":
        parent = temporary / "parent"
        parent.mkdir()
        materialize(parent, manifest)
        nested = parent / "repo"
        (nested / ".git").mkdir(parents=True)
        start = nested / "deep"
        start.mkdir()
        run_discover(adapter, nested, case, start=start, explicit=False)
        return
    if case_id == "discover-no-manifest":
        workspace = temporary / "workspace"
        (workspace / "docs").mkdir(parents=True)
        (workspace / "README.md").write_text("# Not inferred\n", encoding="utf-8")
        run_discover(adapter, workspace, case, start=workspace / "docs", explicit=False)
        return
    if case_id == "discover-control-symlink":
        workspace = temporary / "workspace"
        target = temporary / "control"
        workspace.mkdir()
        target.mkdir()
        (target / "manifest.json").write_bytes(pretty(manifest))
        (workspace / ".wayfinder").symlink_to(target, target_is_directory=True)
        run_discover(adapter, workspace, case)
        return
    if case_id == "discover-manifest-symlink":
        workspace = temporary / "workspace"
        control = workspace / ".wayfinder"
        control.mkdir(parents=True)
        target = temporary / "manifest.json"
        target.write_bytes(pretty(manifest))
        (control / "manifest.json").symlink_to(target)
        run_discover(adapter, workspace, case)
        return
    raise CaseFailure(f"unimplemented discovery case {case_id}")


def manifest_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    case_id = case["id"]
    if case_id == "manifest-document-collection":
        manifest = load_manifest(skill_root, "manifest-realistic.json")
    else:
        manifest = load_manifest(skill_root)
    original = copy.deepcopy(manifest)
    decision = manifest["modules"][0]
    if case_id == "manifest-absolute-path":
        manifest["recordRoot"] = "/record"
    elif case_id == "manifest-backslash":
        manifest["recordRoot"] = "record\\child"
    elif case_id == "manifest-empty-segment":
        manifest["recordRoot"] = "record//child"
    elif case_id == "manifest-dot-segment":
        manifest["recordRoot"] = "record/./child"
    elif case_id == "manifest-traversal":
        manifest["recordRoot"] = "record/../escape"
    elif case_id == "manifest-case-alias":
        manifest["modules"].append({"id": "product", "root": "Decisions", "entrypoint": "Decisions/product.md", "subjects": []})
    elif case_id == "manifest-duplicate-module-id":
        manifest["modules"].append({"id": "decisions", "root": "product", "entrypoint": "product/README.md", "subjects": []})
    elif case_id == "manifest-duplicate-module-root":
        manifest["modules"].append({"id": "product", "root": "decisions", "entrypoint": "decisions/product.md", "subjects": []})
    elif case_id == "manifest-nested-module-root":
        manifest["modules"].append({"id": "product", "root": "decisions/nested", "entrypoint": "decisions/nested/README.md", "subjects": []})
    elif case_id == "manifest-duplicate-subject-id":
        manifest = load_manifest(skill_root, "manifest-realistic.json")
        original = copy.deepcopy(manifest)
        product = manifest["modules"][0]
        product["subjects"].append({"id": "audiences", "kind": "document", "entrypoint": "product/market.md"})
    elif case_id == "manifest-overlapping-subjects":
        manifest = load_manifest(skill_root, "manifest-realistic.json")
        original = copy.deepcopy(manifest)
        product = manifest["modules"][0]
        product["subjects"].append({"id": "sharing", "kind": "collection", "root": "product/collaboration/sharing", "entrypoint": "product/collaboration/sharing/README.md"})
    elif case_id == "manifest-document-in-collection":
        manifest = load_manifest(skill_root, "manifest-realistic.json")
        manifest["modules"][0]["subjects"][0]["entrypoint"] = "product/collaboration/audiences.md"
        original = copy.deepcopy(manifest)
    elif case_id == "manifest-module-entrypoint-outside":
        decision["entrypoint"] = "outside.md"
    elif case_id == "manifest-subject-entrypoint-outside":
        decision["subjects"] = [{"id": "scope", "kind": "document", "entrypoint": "outside/scope.md"}]
    elif case_id == "manifest-unknown-generator":
        manifest["generatedArtifacts"] = [{"path": "generated/catalog.json", "generator": "unknown-v1"}]
    elif case_id == "manifest-unsafe-snapshot":
        manifest["canonicalBaseline"] = {"kind": "snapshot", "path": "baselines/canonical.json", "sha256": "a" * 64}
    elif case_id == "manifest-artifact-entrypoint-conflict":
        manifest["generatedArtifacts"] = [{"path": "README.md", "generator": "document-catalog-v1"}]
    workspace = temporary / "workspace"
    workspace.mkdir()
    materialize(workspace, original)
    if case_id == "manifest-managed-symlink":
        target = workspace / "record/decisions"
        shutil.rmtree(target)
        outside = temporary / "outside"
        outside.mkdir()
        target.symlink_to(outside, target_is_directory=True)
    elif case_id == "manifest-missing-entrypoint":
        (workspace / "record/README.md").unlink()
    (workspace / ".wayfinder/manifest.json").write_bytes(pretty(manifest))
    run_discover(adapter, workspace, case)


def inventory_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_source_tree(workspace)
    case_id = case["id"]
    request = source_request()
    if case_id == "inventory-files-roots":
        request["selections"] = ["sources/a.md", "sources/nested"]
    elif case_id == "inventory-overlapping-selection":
        request["selections"] = ["sources", "sources/a.md"]
    elif case_id == "inventory-duplicate-selection":
        request["selections"] = ["sources/a.md", "sources/a.md"]
    elif case_id == "inventory-traversal":
        request["selections"] = ["../outside"]
    elif case_id == "inventory-missing-selection":
        request["selections"] = ["missing"]
    elif case_id == "inventory-symlink-selected":
        request["selections"] = ["sources/link-file"]
    elif case_id == "inventory-symlink-component":
        request["selections"] = ["sources/link-dir/outside.txt"]
    elif case_id == "inventory-special-file":
        request["selections"] = ["sources/named-pipe"]
    elif case_id == "inventory-explicit-soft-include":
        request["selections"] = ["sources/archive.zip", "sources/build/out.txt", "sources/node_modules/pkg.txt"]
    elif case_id == "inventory-explicit-secret-excluded":
        request["selections"] = ["sources/.env"]
    elif case_id == "inventory-malformed-utf8":
        request["selections"] = ["sources/bad.bin"]
    elif case_id == "inventory-markdown-headings":
        request["selections"] = ["sources/a.md"]
    elif case_id == "inventory-exact-duplicates":
        request["selections"] = ["sources/z.txt", "sources/nested/b.txt"]
    elif case_id == "inventory-limit-entries":
        request["limits"]["maxEntries"] = 1
    elif case_id == "inventory-limit-file-bytes":
        request["selections"] = ["sources/a.md"]
        request["limits"]["maxFileBytes"] = 2
    elif case_id == "inventory-limit-total-bytes":
        request["selections"] = ["sources/z.txt", "sources/nested/b.txt"]
        request["limits"]["maxTotalBytes"] = 6
    elif case_id == "inventory-limit-depth":
        request["limits"]["maxDepth"] = 1
    elif case_id == "inventory-golden-result":
        request["selections"] = ["sources/a.md", "sources/bad.bin", "sources/z.txt", "sources/nested/b.txt"]

    completed, result = invoke_inventory(adapter, workspace, request)
    assert_expected(case, completed, result)
    if not result["ok"]:
        return
    inventory = result["data"]["inventory"]
    paths = [entry["path"] for entry in inventory["entries"]]
    if paths != sorted(paths, key=lambda value: value.encode("utf-8")):
        raise CaseFailure("inventory entries are not in stable UTF-8 path order")
    if case_id == "inventory-files-roots":
        if set(paths) != {"sources/a.md", "sources/nested", "sources/nested/b.txt"}:
            raise CaseFailure(f"explicit file/root inventory differs: {paths}")
    elif case_id == "inventory-overlapping-selection":
        if paths.count("sources/a.md") != 1:
            raise CaseFailure("overlapping selections duplicated a source path")
    elif case_id in {"inventory-symlink-selected", "inventory-symlink-nested"}:
        symlinks = [entry for entry in inventory["entries"] if entry["type"] == "symlink"]
        if not symlinks or any(entry["included"] or entry["exclusion"] != "symbolic-link" for entry in symlinks):
            raise CaseFailure("symlinks were not listed as excluded without following")
        if "outside/outside.txt" in paths:
            raise CaseFailure("symlink traversal escaped the source tree")
    elif case_id == "inventory-special-file":
        entry = inventory["entries"][0]
        if entry["type"] != "unsupported-file" or entry["exclusion"] != "unsupported-special-file":
            raise CaseFailure("special file classification differs")
    elif case_id == "inventory-exclusions":
        reasons = {entry["exclusion"] for entry in inventory["entries"] if entry["exclusion"]}
        required = {"vcs-administration", "wayfinder-state", "declared-target-root", "secret-safety", "dependency-directory", "build-output-directory", "archive-file", "symbolic-link", "unsupported-special-file"}
        if not required.issubset(reasons):
            raise CaseFailure(f"missing exclusion classes: {sorted(required - reasons)}")
    elif case_id == "inventory-explicit-soft-include":
        if not all(entry["included"] for entry in inventory["entries"]):
            raise CaseFailure("explicit ordinary file did not override a soft exclusion")
    elif case_id == "inventory-explicit-secret-excluded":
        if inventory["entries"][0]["included"] or inventory["entries"][0]["sha256"] is not None:
            raise CaseFailure("explicit secret file was opened or included")
    elif case_id == "inventory-malformed-utf8":
        if inventory["entries"][0]["content"] != "opaque-bytes":
            raise CaseFailure("malformed UTF-8 was not classified as opaque bytes")
    elif case_id == "inventory-markdown-headings":
        markdown = inventory["entries"][0]["markdown"]
        if markdown["h1"] != "Alpha" or [item["text"] for item in markdown["outline"]] != ["Alpha", "Details"]:
            raise CaseFailure(f"Markdown heading extraction differs: {markdown}")
    elif case_id == "inventory-exact-duplicates":
        groups = inventory["duplicateGroups"]
        if len(groups) != 1 or groups[0]["paths"] != ["sources/nested/b.txt", "sources/z.txt"]:
            raise CaseFailure(f"exact duplicate grouping differs: {groups}")
    elif case_id == "inventory-golden-result":
        expected = json.loads((skill_root / CONFORMANCE_REL / "expected/inventory-golden.json").read_text(encoding="utf-8"))
        if inventory != expected:
            raise CaseFailure("canonical inventory differs from reviewed golden result")


def intake_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_source_tree(workspace)
    request = source_request(["sources/a.md", "sources/z.txt", "sources/nested/b.txt", "sources/bad.bin"])
    initial, initial_result = invoke_inventory(adapter, workspace, request)
    if initial.returncode != 0:
        raise CaseFailure(f"could not build intake basis: {initial.stderr!r}")
    inventory = initial_result["data"]["inventory"]
    digest = initial_result["data"]["inventorySha256"]
    entries = {entry["path"]: entry for entry in inventory["entries"]}
    sources = [
        ledger_source(entries["sources/a.md"], "incorporate"),
        ledger_source(entries["sources/z.txt"], "reference"),
        ledger_source(entries["sources/nested/b.txt"], "preserve-out-of-scope"),
        ledger_source(entries["sources/bad.bin"], "unresolved"),
    ]
    ledger: dict[str, Any] = {"format": "wayfinder-intake-ledger", "schemaVersion": 1, "inventorySha256": digest, "sources": sources}
    raw_ledger: bytes | None = None
    case_id = case["id"]
    if case_id == "intake-duplicate-field":
        raw_ledger = pretty(ledger).replace(b'  "format":', b'  "format": "wayfinder-intake-ledger",\n  "format":', 1)
    elif case_id == "intake-unknown-field":
        ledger["unknown"] = True
    elif case_id == "intake-missing-field":
        del ledger["sources"]
    elif case_id == "intake-wrong-type":
        ledger["sources"] = {}
    elif case_id == "intake-unsupported-version":
        ledger["schemaVersion"] = 2
    elif case_id == "intake-invalid-disposition":
        sources[0]["disposition"] = "ignore"
    elif case_id == "intake-invalid-incorporate":
        sources[0]["targetIds"] = []
    elif case_id == "intake-invalid-reference":
        sources[1]["evidenceKeys"] = []
    elif case_id == "intake-invalid-preserve":
        sources[2]["targetIds"] = ["wf-0002-open-questions"]
    elif case_id == "intake-invalid-unresolved":
        sources[3]["questionIds"] = []
    elif case_id == "intake-invalid-target-id":
        sources[0]["targetIds"] = ["bad-target"]
    elif case_id == "intake-invalid-evidence-key":
        sources[1]["evidenceKeys"] = ["source-1"]
    elif case_id == "intake-invalid-question-id":
        sources[3]["questionIds"] = ["question-1"]
    elif case_id == "intake-inventory-digest":
        ledger["inventorySha256"] = "0" * 64
    elif case_id == "intake-source-stale-size":
        (workspace / "sources/a.md").write_bytes(b"changed length\n")
    elif case_id == "intake-source-stale-digest":
        original = (workspace / "sources/z.txt").read_bytes()
        (workspace / "sources/z.txt").write_bytes(b"diff\n")
        if len(original) != len((workspace / "sources/z.txt").read_bytes()):
            raise CaseFailure("same-size stale fixture was not same size")
    completed, result = invoke_inventory(adapter, workspace, request, ledger=raw_ledger or ledger)
    assert_expected(case, completed, result)
    if case_id == "intake-all-dispositions":
        intake = result["data"]["intake"]
        if intake["dispositionCounts"] != {"incorporate": 1, "reference": 1, "preserve-out-of-scope": 1, "unresolved": 1}:
            raise CaseFailure("disposition counts differ")
        if intake["sourceDigestsRechecked"] != 4:
            raise CaseFailure("source digest recheck count differs")
        if intake.get("semanticDecisions") is not None:
            raise CaseFailure("adapter invented a semantic decision while validating intake")


def _replace_file(path: Path, old: bytes, new: bytes, *, count: int = 1) -> None:
    raw = path.read_bytes()
    if raw.count(old) < count:
        raise CaseFailure(f"mutation basis missing in {path}: {old!r}")
    path.write_bytes(raw.replace(old, new, count))


def record_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_slice3_record(adapter, workspace)
    record = workspace / "record"
    product = record / "product/product.md"
    questions = record / "product/questions.md"
    decision = record / "decisions/decision.md"
    evidence = record / "research/sources/evidence.md"
    research_index = record / "research/README.md"
    case_id = case["id"]
    if case_id == "record-valid":
        pass
    elif case_id == "record-document-id-zero":
        _replace_file(product, b"wf-0007-product-brief", b"wf-0000-product-brief")
    elif case_id == "record-document-id-short":
        _replace_file(product, b"wf-0007-product-brief", b"wf-007-product-brief")
    elif case_id == "record-document-id-uppercase":
        _replace_file(product, b"wf-0007-product-brief", b"WF-0007-product-brief")
    elif case_id == "record-document-id-mnemonic-boundary":
        _replace_file(product, b"wf-0007-product-brief", ("wf-0007-" + "a" * 49).encode())
    elif case_id == "record-duplicate-document-id":
        _replace_file(product, b"wf-0007-product-brief", b"wf-0006-synthetic-evidence")
    elif case_id == "record-duplicate-document-ordinal":
        _replace_file(product, b"wf-0007-product-brief", b"wf-0006-other-brief")
    elif case_id == "record-question-id-zero":
        _replace_file(questions, b"wfq-0001-retention", b"wfq-0000-retention", count=2)
    elif case_id == "record-duplicate-question-id":
        block = questions.read_bytes().split(b"<!-- wayfinder:question -->", 1)[1]
        questions.write_bytes(questions.read_bytes().rstrip(b"\n") + b"\n\n<!-- wayfinder:question -->" + block)
    elif case_id == "metadata-delimiter":
        _replace_file(product, b"<!-- /wayfinder:metadata -->", b"<!-- /wayfinder:metadata-invalid -->")
    elif case_id == "metadata-location":
        _replace_file(product, b"# Product brief\n\n", b"# Product brief\n")
    elif case_id == "metadata-order":
        _replace_file(product, b"- **Kind:** brief\n- **Status:** Active", b"- **Status:** Active\n- **Kind:** brief")
    elif case_id == "metadata-missing":
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", b"")
    elif case_id == "metadata-duplicate":
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", b"- **Summary:** States the synthetic product direction.\n- **Summary:** Duplicate.\n")
    elif case_id == "metadata-unknown":
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", b"- **Summary:** States the synthetic product direction.\n- **Owner:** Nobody\n")
    elif case_id == "metadata-malformed":
        _replace_file(product, b"- **Kind:** brief", b"- **Kind**: brief")
    elif case_id == "document-h1":
        _replace_file(product, b"## Current synthesis", b"# Second title")
    elif case_id == "document-invalid-kind":
        _replace_file(product, b"- **Kind:** brief", b"- **Kind:** requirement")
    elif case_id == "document-invalid-status":
        _replace_file(product, b"- **Status:** Active", b"- **Status:** Accepted")
    elif case_id == "decision-invalid-status":
        _replace_file(decision, b"- **Status:** Accepted", b"- **Status:** Active")
    elif case_id == "decision-date-required":
        _replace_file(decision, b"- **Decision-Date:** 2026-09-13\n", b"")
    elif case_id == "decision-date-forbidden":
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", b"- **Summary:** States the synthetic product direction.\n- **Decision-Date:** 2026-09-13\n")
    elif case_id == "decision-sections":
        _replace_file(decision, b"## Rationale", b"## Reason")
    elif case_id == "evidence-sections":
        _replace_file(evidence, b"## Findings", b"## Results")
    elif case_id == "relationship-malformed":
        _replace_file(product, b"[wf-0003-synthetic-decision](../decisions/decision.md)", b"wf-0003-synthetic-decision")
    elif case_id == "relationship-label-mismatch":
        _replace_file(product, b"[wf-0003-synthetic-decision](../decisions/decision.md)", b"[wf-0006-synthetic-evidence](../decisions/decision.md)")
    elif case_id == "relationship-target-missing":
        _replace_file(product, b"[wf-0003-synthetic-decision](../decisions/decision.md)", b"[wf-0999-missing](../decisions/decision.md)")
    elif case_id == "relationship-target-kind-status":
        _replace_file(product, b"[wf-0003-synthetic-decision](../decisions/decision.md)", b"[wf-0004-research-index](../research/README.md)")
    elif case_id == "relationship-target-status":
        _replace_file(evidence, b"- **Status:** Active", b"- **Status:** Draft")
    elif case_id == "relationship-duplicate":
        line = b"- **Governed-By:** [wf-0003-synthetic-decision](../decisions/decision.md)\n"
        _replace_file(product, line, line + line)
    elif case_id == "relationship-order":
        first = b"- **Governed-By:** [wf-0003-synthetic-decision](../decisions/decision.md)\n- **Supported-By:** [wf-0006-synthetic-evidence](../research/sources/evidence.md)"
        second = b"- **Supported-By:** [wf-0006-synthetic-evidence](../research/sources/evidence.md)\n- **Governed-By:** [wf-0003-synthetic-decision](../decisions/decision.md)"
        _replace_file(product, first, second)
    elif case_id in {"supersession-reciprocal", "supersession-missing-target", "supersession-self-edge", "supersession-kind", "supersession-order"}:
        target = {
            "supersession-reciprocal": "wf-0004-research-index",
            "supersession-missing-target": "wf-0999-missing",
            "supersession-self-edge": "wf-0007-product-brief",
            "supersession-kind": "wf-0003-synthetic-decision",
            "supersession-order": "wf-0004-research-index, wf-0002-decision-index",
        }[case_id]
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", f"- **Summary:** States the synthetic product direction.\n- **Supersedes:** {target}\n".encode())
    elif case_id == "supersession-cycle":
        _replace_file(product, b"- **Summary:** States the synthetic product direction.\n", b"- **Summary:** States the synthetic product direction.\n- **Supersedes:** wf-0004-research-index\n- **Superseded-By:** wf-0004-research-index\n")
        _replace_file(research_index, b"- **Summary:** Indexes synthetic evidence.\n", b"- **Summary:** Indexes synthetic evidence.\n- **Supersedes:** wf-0007-product-brief\n- **Superseded-By:** wf-0007-product-brief\n")
    elif case_id == "question-anchor":
        _replace_file(questions, b'<a id="wfq-0001-retention"></a>', b'<a id="wfq-0002-other"></a>')
    elif case_id == "question-scope":
        _replace_file(questions, b"- **Applies-To:** [wf-0007-product-brief](product.md)\n", b"")
    elif case_id == "question-invalid-state":
        _replace_file(questions, b"- **State:** Open", b"- **State:** Answered")
    elif case_id == "question-conditional":
        _replace_file(questions, b"#### Next step", b"#### Revisit trigger")
    elif case_id == "question-history":
        _replace_file(questions, b"- **State:** Open", b"- **State:** Investigating")
        _replace_file(questions, b"#### Next step", b"#### Current activity")
    elif case_id == "question-transition":
        _replace_file(questions, b"- 2026-09-13: None -> Open - Raised during initialization.", b"- 2026-09-13: None -> Open - Raised during initialization.\n- 2026-09-13: Open -> Open - Invalid self transition.")
    elif case_id == "question-reopen-reason":
        _replace_file(questions, b"- 2026-09-13: None -> Open - Raised during initialization.", b"- 2026-09-13: None -> Open - Raised during initialization.\n- 2026-09-13: Open -> Resolved - Answered.\n- 2026-09-13: Resolved -> Open - More work.")
    elif case_id == "question-retired-terminal":
        _replace_file(questions, b"- 2026-09-13: None -> Open - Raised during initialization.", b"- 2026-09-13: None -> Retired - Scope removed.\n- 2026-09-13: Retired -> Open - Reopened incorrectly.")
    elif case_id == "question-resolved-target":
        _replace_file(questions, b"- **State:** Open", b"- **State:** Resolved")
        _replace_file(questions, b"- **Applies-To:** [wf-0007-product-brief](product.md)\n", b"- **Applies-To:** [wf-0007-product-brief](product.md)\n- **Resolved-By:** [wf-0004-research-index](../research/README.md)\n- **Resolution-Date:** 2026-09-13\n")
        _replace_file(questions, b"#### Next step\n\nAsk the record owner.", b"#### Resolution\n\nAnswered elsewhere.")
        _replace_file(questions, b"- 2026-09-13: None -> Open - Raised during initialization.", b"- 2026-09-13: None -> Resolved - Answered directly.")
    elif case_id == "question-addressed-target":
        _replace_file(questions, b"- **Applies-To:** [wf-0007-product-brief](product.md)\n", b"- **Applies-To:** [wf-0007-product-brief](product.md)\n- **Addressed-By:** [wf-0007-product-brief](product.md)\n")
    elif case_id == "question-all-states":
        def question_block(identifier: str, title: str, state: str, fields: list[str], sections: list[tuple[str, str]], history: list[str]) -> str:
            lines = ["<!-- wayfinder:question -->", f'<a id="{identifier}"></a>', f"### {title}", f"- **ID:** {identifier}", f"- **State:** {state}", "- **Raised:** 2026-09-13", "- **Applies-To:** [wf-0007-product-brief](product.md)", *fields, ""]
            for heading, content in sections:
                lines.extend([f"#### {heading}", "", content, ""])
            lines.extend(["#### History", "", *history, "<!-- /wayfinder:question -->"])
            return "\n".join(lines)
        blocks = [
            question_block("wfq-0001-open", "Open question", "Open", [], [("Why it matters", "Open impact."), ("Next step", "Ask someone.")], ["- 2026-09-13: None -> Open - Raised."]),
            question_block("wfq-0002-investigating", "Investigating question", "Investigating", ["- **Addressed-By:** [wf-0006-synthetic-evidence](../research/sources/evidence.md)"], [("Why it matters", "Investigation impact."), ("Current activity", "Read the evidence.")], ["- 2026-09-13: None -> Investigating - Investigation began."]),
            question_block("wfq-0003-deferred", "Deferred question", "Deferred", [], [("Why it matters", "Deferred impact."), ("Deferral reason", "Capacity is limited."), ("Revisit trigger", "Capacity becomes available.")], ["- 2026-09-13: None -> Deferred - Deliberately deferred."]),
            question_block("wfq-0004-resolved", "Resolved question", "Resolved", ["- **Resolved-By:** [wf-0003-synthetic-decision](../decisions/decision.md)", "- **Resolution-Date:** 2026-09-13"], [("Why it matters", "Resolved impact."), ("Resolution", "The decision answers it.")], ["- 2026-09-13: None -> Resolved - Answered directly."]),
            question_block("wfq-0005-retired", "Retired question", "Retired", [], [("Why it matters", "Historical impact."), ("Retirement reason", "The scope was removed.")], ["- 2026-09-13: None -> Retired - Scope removed."]),
            question_block("wfq-0006-reopened", "Reopened question", "Open", [], [("Why it matters", "The answer changed."), ("Next step", "Investigate again.")], ["- 2026-09-13: None -> Resolved - Initially answered.", "- 2026-09-13: Resolved -> Open - Reopened after new evidence."]),
        ]
        questions.write_bytes(wf_doc("Open questions", "wf-0008-open-questions", "register", "Active", "Tracks every question state.", "## Open questions\n\n" + "\n\n".join(blocks)))
        seeded, seeded_result = invoke_generate(adapter, workspace, base_generation_request("catalog"))
        if seeded.returncode != 0:
            raise CaseFailure(f"could not refresh all-state catalog: {seeded.stderr!r} {seeded_result}")
    elif case_id == "source-anchor":
        _replace_file(evidence, b'<a id="src-01"></a>', b'<a id="src-02"></a>')
    elif case_id == "source-required-field":
        _replace_file(evidence, b"- **Citation:** Synthetic source record, 2026.\n", b"")
    elif case_id == "source-applicability":
        _replace_file(evidence, b"- **Applicability:** Direct", b"- **Applicability:** Certain")
    elif case_id == "source-published-date":
        _replace_file(evidence, b"- **Accessed:** 2026-09-13", b"- **Published:** 2026-02-30\n- **Accessed:** 2026-09-13")
    elif case_id == "source-local-contained":
        local = workspace / "local-sources/source.txt"
        local.parent.mkdir()
        local.write_bytes(b"local evidence\n")
        _replace_file(evidence, b"https://example.test/source", b"local-sources/source.txt")
    elif case_id == "source-local-traversal":
        _replace_file(evidence, b"https://example.test/source", b"../outside.txt")
    elif case_id == "source-local-missing":
        _replace_file(evidence, b"https://example.test/source", b"local-sources/missing.txt")
    elif case_id == "source-local-symlink":
        outside = temporary / "outside.txt"
        outside.write_bytes(b"outside\n")
        (workspace / "local-source.txt").symlink_to(outside)
        _replace_file(evidence, b"https://example.test/source", b"local-source.txt")
    elif case_id == "source-duplicate-key":
        source = evidence.read_bytes().split(b"<!-- wayfinder:source -->", 1)[1]
        evidence.write_bytes(evidence.read_bytes().rstrip(b"\n") + b"\n\n<!-- wayfinder:source -->" + source)
    elif case_id == "source-citation-missing":
        _replace_file(evidence, b"[src-01](#src-01)", b"[src-02](#src-02)")
    elif case_id == "source-material-claim":
        _replace_file(evidence, b"The source exists. [src-01](#src-01)", b"The source exists.")
    elif case_id == "record-module-containment":
        (record / "misc").mkdir()
        (record / "misc/outside.md").write_bytes(wf_doc("Outside", "wf-0009-outside", "brief", "Active", "Outside all modules.", "## Scope\n\nOutside."))
    elif case_id == "record-entrypoint-kind":
        target = record / "README.md"
        raw = target.read_bytes()
        start = raw.index(b"<!-- wayfinder:generated")
        end = raw.index(b"<!-- /wayfinder:generated -->", start) + len(b"<!-- /wayfinder:generated -->")
        target.write_bytes((raw[:start] + raw[end:]).rstrip(b"\n") + b"\n")
        _replace_file(target, b"- **Kind:** map", b"- **Kind:** brief")
    elif case_id == "record-catalog-subject-membership":
        catalog = json.loads((record / ".wayfinder/catalog.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in catalog["documents"]}
        if by_id["wf-0006-synthetic-evidence"]["subject"] != "research/sources" or by_id["wf-0007-product-brief"]["subject"] is not None or by_id["wf-0008-open-questions"]["subject"] != "product/questions":
            raise CaseFailure("manifest-derived module/subject projection differs")
    elif case_id == "generated-stale-region":
        _replace_file(record / "README.md", b"| ID | Title | Kind | Status | Summary |", b"| ID | Edited | Kind | Status | Summary |")
    elif case_id == "generated-nested":
        marker = b'<!-- wayfinder:generated name="nested" generator="document-index-v1" input-sha256="' + b"0" * 64 + b'" -->\n'
        _replace_file(record / "README.md", b"| ID | Title | Kind | Status | Summary |", marker + b"| ID | Title | Kind | Status | Summary |")
    elif case_id == "generated-duplicate":
        source = record / "README.md"
        start = source.read_bytes().index(b"<!-- wayfinder:generated")
        block = source.read_bytes()[start:source.read_bytes().index(b"<!-- /wayfinder:generated -->", start) + len(b"<!-- /wayfinder:generated -->")]
        source.write_bytes(source.read_bytes().rstrip(b"\n") + b"\n\n" + block + b"\n")
    elif case_id == "generated-owner-kind":
        marker = b'\n\n<!-- wayfinder:generated name="members" generator="document-index-v1" input-sha256="' + b"0" * 64 + b'" -->\nold\n<!-- /wayfinder:generated -->'
        product.write_bytes(product.read_bytes().rstrip(b"\n") + marker + b"\n")
    elif case_id == "generated-unknown-marker":
        _replace_file(record / "README.md", b'generator="document-index-v1"', b'generator="unknown-v1"')
    elif case_id == "generated-catalog-stale":
        (record / ".wayfinder/catalog.json").write_bytes(b"{}\n")
    elif case_id == "record-crlf":
        product.write_bytes(product.read_bytes().replace(b"\n", b"\r\n"))
    elif case_id == "record-non-nfc":
        _replace_file(product, b"Product brief", ("Produ" + "\u0301" + "ct brief").encode("utf-8"))
    elif case_id == "record-trailing-whitespace":
        _replace_file(product, b"# Product brief\n", b"# Product brief \n")
    else:
        raise CaseFailure(f"unimplemented record case {case_id}")
    before = snapshot(workspace)
    completed, result = invoke(adapter, ["validate", "--workspace-root", str(workspace)])
    assert_expected(case, completed, result)
    if snapshot(workspace) != before:
        raise CaseFailure("validate changed the workspace")


def render_spec(kind: str, ordinal: int) -> dict[str, Any]:
    headings = {
        "evidence": ["Question and scope", "Method", "Findings", "Applicability and limitations", "Evidence, inference, and hypothesis", "Implications", "Unknowns", "Next validation", "Sources"],
        "decision": ["Context", "Options considered", "Decision", "Rationale", "Consequences", "References", "Supersession"],
    }.get(kind, ["Scope"])
    status = "Accepted" if kind == "decision" else "Active"
    return {
        "output": f"{kind}.md", "title": f"{kind.title()} title", "id": f"wf-{ordinal:04d}-{kind}-document", "kind": kind,
        "status": status, "updated": "2026-09-13", "summary": f"Synthetic {kind} summary.",
        "decisionDate": "2026-09-13" if kind == "decision" else None, "supersedes": [], "supersededBy": [], "relationships": [],
        "sections": [{"heading": heading, "content": f"Exact {heading} prose."} for heading in headings], "questions": [], "sources": [],
    }


def render_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    workspace = temporary / "workspace"
    output = temporary / "output"
    workspace.mkdir()
    output.mkdir()
    documents = [render_spec(kind, index + 1) for index, kind in enumerate(("map", "brief", "register", "evidence", "decision", "guide", "index"))]
    local_adapter = adapter
    case_id = case["id"]
    if case_id == "render-all-kinds":
        ordinal = 8
        for kind in ("map", "brief", "register", "evidence", "guide", "index"):
            for status in ("Draft", "Retired", "Superseded"):
                spec = render_spec(kind, ordinal)
                spec["output"] = f"{kind}-{status.lower()}.md"
                spec["status"] = status
                spec["supersededBy"] = ["wf-0099-successor"] if status == "Superseded" else []
                documents.append(spec)
                ordinal += 1
        for status in ("Proposed", "Rejected", "Superseded"):
            spec = render_spec("decision", ordinal)
            spec["output"] = f"decision-{status.lower()}.md"
            spec["status"] = status
            spec["decisionDate"] = None if status == "Proposed" else "2026-09-13"
            spec["supersededBy"] = ["wf-0099-successor"] if status == "Superseded" else []
            documents.append(spec)
            ordinal += 1
    if case_id == "render-no-prose-rewrite":
        documents = [render_spec("brief", 1)]
        documents[0]["sections"][0]["content"] = "Line  one.\n\nLine two—with punctuation."
    elif case_id == "render-output-exists":
        documents = [render_spec("brief", 1)]
        (output / "brief.md").write_text("existing\n", encoding="utf-8")
    elif case_id == "render-duplicate-output":
        documents = [render_spec("brief", 1), render_spec("brief", 2)]
    elif case_id == "render-unknown-field":
        documents = [render_spec("brief", 1)]
        documents[0]["unknown"] = True
    elif case_id == "render-recursive-slot":
        documents = [render_spec("brief", 1)]
        documents[0]["title"] = "{{TITLE}}"
    elif case_id in {"render-template-missing-slot", "render-template-unknown-slot", "render-template-duplicate-slot"}:
        copied = temporary / "wayfinder"
        shutil.copytree(skill_root, copied)
        local_adapter = copied / adapter.relative_to(skill_root)
        template = copied / "assets/contract-v1/templates/brief.md"
        if case_id == "render-template-missing-slot":
            _replace_file(template, b"{{CONTENT}}", b"content")
        elif case_id == "render-template-unknown-slot":
            _replace_file(template, b"{{CONTENT}}", b"{{UNKNOWN}}")
        else:
            _replace_file(template, b"{{CONTENT}}", b"{{CONTENT}}{{TITLE}}")
        documents = [render_spec("brief", 1)]
    elif case_id == "render-golden":
        documents = [render_spec("brief", 1)]
    elif case_id == "render-source-type":
        documents = [render_spec("evidence", 1)]
        documents[0]["sources"] = [{
            "key": "src-01", "title": "Source", "citation": "Citation.", "original": "https://example.test/source",
            "published": None, "accessed": "2026-09-13", "applicability": "Direct", "usedFor": 7, "limitations": "Synthetic.",
        }]
    elif case_id == "render-output-symlink-component":
        documents = [render_spec("brief", 1)]
        documents[0]["output"] = "linked/brief.md"
        outside = temporary / "outside"
        outside.mkdir()
        (output / "linked").symlink_to(outside, target_is_directory=True)
    request = {**base_generation_request("render"), "documents": documents}
    before_workspace = snapshot(workspace)
    completed, result = invoke_generate(local_adapter, workspace, request, output_root=output)
    assert_expected(case, completed, result)
    if snapshot(workspace) != before_workspace:
        raise CaseFailure("render changed its workspace")
    if case["exit"] != 0:
        allowed_output = {"render-output-symlink-component": [{"path": "linked", "kind": "symlink", "target": str(temporary / "outside")}]}.get(case_id, [])
        if case_id != "render-output-exists" and snapshot(output) != allowed_output:
            raise CaseFailure("rejected render wrote output")
        return
    if case_id == "render-all-kinds":
        expected = {f"{kind}.md" for kind in ("map", "brief", "register", "evidence", "decision", "guide", "index")}
        expected.update(f"{kind}-{status}.md" for kind in ("map", "brief", "register", "evidence", "guide", "index") for status in ("draft", "retired", "superseded"))
        expected.update(f"decision-{status}.md" for status in ("proposed", "rejected", "superseded"))
        if {path.name for path in output.glob("*.md")} != expected:
            raise CaseFailure("not every literal kind/lifecycle representative rendered")
    if case_id == "render-no-prose-rewrite" and b"Line  one.\n\nLine two\xe2\x80\x94with punctuation." not in (output / "brief.md").read_bytes():
        raise CaseFailure("renderer rewrote supplied prose bytes")
    if case_id == "render-golden" and (output / "brief.md").read_bytes() != (skill_root / CONFORMANCE_REL / "expected/render-brief.md").read_bytes():
        raise CaseFailure("rendered brief differs from reviewed golden bytes")


def generation_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_slice3_record(adapter, workspace)
    record = workspace / "record"
    case_id = case["id"]
    if case_id.startswith("allocation-"):
        documents = [{"title": "New Product Area", "mnemonic": None}, {"title": "Second Area", "mnemonic": None}]
        questions = [{"title": "What Comes Next?", "mnemonic": None}]
        if case_id == "allocation-explicit-mnemonic":
            documents = [{"title": "日本語", "mnemonic": "explicit-name"}]
            questions = []
        elif case_id == "allocation-mnemonic-required":
            documents = [{"title": "日本語", "mnemonic": None}]
            questions = []
        elif case_id == "allocation-scan-max-with-gap":
            for path in record.rglob("*.md"):
                _replace_file(path, b"wf-0007-product-brief", b"wf-0011-product-brief") if b"wf-0007-product-brief" in path.read_bytes() else None
            refreshed, refreshed_result = invoke_generate(adapter, workspace, base_generation_request("catalog"))
            if refreshed.returncode != 0:
                raise CaseFailure(f"could not refresh gapped catalog: {refreshed.stderr!r} {refreshed_result}")
            documents = [{"title": "After Gap", "mnemonic": None}]
            questions = []
        before = snapshot(workspace)
        completed, result = invoke_generate(adapter, workspace, {**base_generation_request("allocate"), "documents": documents, "questions": questions})
        assert_expected(case, completed, result)
        if snapshot(workspace) != before:
            raise CaseFailure("allocation wrote to workspace")
        if case_id == "allocation-order" and ([item["id"] for item in result["data"]["documents"]] != ["wf-0009-new-product-area", "wf-0010-second-area"] or [item["id"] for item in result["data"]["questions"]] != ["wfq-0002-what-comes-next"] or not all(item["candidate"] for item in result["data"]["documents"] + result["data"]["questions"])):
            raise CaseFailure("allocation ordering or candidate boundary differs")
        if case_id == "allocation-scan-max-with-gap" and result["data"]["documents"] != [{"id": "wf-0012-after-gap", "candidate": True}]:
            raise CaseFailure("allocation filled a gap instead of using record-wide max + 1")
        return
    if case_id == "generation-catalog-repeat":
        request = base_generation_request("catalog")
        first, result = invoke_generate(adapter, workspace, request)
        assert_expected(case, first, result)
        first_bytes = (record / ".wayfinder/catalog.json").read_bytes()
        second, second_result = invoke_generate(adapter, workspace, request)
        assert_expected(case, second, second_result)
        if first.stdout != second.stdout or first_bytes != (record / ".wayfinder/catalog.json").read_bytes():
            raise CaseFailure("catalog generation is not byte deterministic")
        return
    if case_id == "generation-catalog-golden":
        if (record / ".wayfinder/catalog.json").read_bytes() != (skill_root / CONFORMANCE_REL / "expected/catalog-golden.json").read_bytes():
            raise CaseFailure("catalog differs from reviewed golden bytes")
        completed, result = invoke_generate(adapter, workspace, base_generation_request("catalog"))
        assert_expected(case, completed, result)
        return
    if case_id in {"generation-region-preservation", "generation-region-idempotent"}:
        target = record / "README.md"
        before = target.read_bytes()
        start = before.index(b"<!-- wayfinder:generated")
        end = before.index(b"<!-- /wayfinder:generated -->") + len(b"<!-- /wayfinder:generated -->")
        target.write_bytes(before[:start] + b'<!-- wayfinder:generated name="members" generator="document-index-v1" input-sha256="' + b"0" * 64 + b'" -->\nchanged\n<!-- /wayfinder:generated -->' + before[end:])
        outside_before = (before[:start], before[end:])
        request = {**base_generation_request("regions"), "paths": ["README.md"]}
        first, result = invoke_generate(adapter, workspace, request)
        assert_expected(case, first, result)
        after = target.read_bytes()
        if not after.startswith(outside_before[0]) or not after.endswith(outside_before[1]):
            raise CaseFailure("region generation changed authored bytes outside the region")
        if case_id == "generation-region-idempotent":
            second, second_result = invoke_generate(adapter, workspace, request)
            assert_expected(case, second, second_result)
            if after != target.read_bytes() or first.stdout != second.stdout:
                raise CaseFailure("region generation is not idempotent")
        return
    if case_id == "generation-undeclared-region-path":
        request = {**base_generation_request("regions"), "paths": ["product/product.md"]}
    elif case_id == "generation-unknown-action":
        request = {**base_generation_request("unknown")}
    else:
        raise CaseFailure(f"unimplemented generation case {case_id}")
    completed, result = invoke_generate(adapter, workspace, request)
    assert_expected(case, completed, result)


def property_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    if case["id"] in {"property-record-seeded-id", "property-catalog-repeat-bytes"}:
        rng = random.Random(20260913)
        for iteration in range(8):
            workspace = temporary / f"workspace-{iteration}"
            workspace.mkdir()
            make_slice3_record(adapter, workspace, with_regions=False)
            request = {**base_generation_request("allocate"), "documents": [], "questions": []}
            for index in range(rng.randrange(1, 6)):
                request["documents"].append({"title": f"Generated {rng.randrange(100000)} Item {index}", "mnemonic": None})
            for index in range(rng.randrange(1, 5)):
                request["questions"].append({"title": f"Generated {rng.randrange(100000)} Question {index}", "mnemonic": None})
            first, result = invoke_generate(adapter, workspace, request)
            assert_expected(case, first, result)
            second, second_result = invoke_generate(adapter, workspace, request)
            assert_expected(case, second, second_result)
            if first.stdout != second.stdout:
                raise CaseFailure("seeded allocation output differs")
            doc_ids = [item["id"] for item in result["data"]["documents"]]
            question_ids = [item["id"] for item in result["data"]["questions"]]
            if len(doc_ids) != len(set(doc_ids)) or len(question_ids) != len(set(question_ids)):
                raise CaseFailure("seeded allocation collided")
            if case["id"] == "property-catalog-repeat-bytes":
                catalog = workspace / "record/.wayfinder/catalog.json"
                before = catalog.read_bytes()
                done, generated = invoke_generate(adapter, workspace, base_generation_request("catalog"))
                assert_expected(case, done, generated)
                if before != catalog.read_bytes():
                    raise CaseFailure("catalog bytes changed without authority changes")
        return
    if case["id"] in {"property-inventory-repeat-output", "property-inventory-seeded-order"}:
        workspace = temporary / "workspace"
        workspace.mkdir()
        source = workspace / "generated"
        source.mkdir()
        rng = random.Random(20260913)
        names = [f"{rng.randrange(100000):05d}-{index:02d}.txt" for index in range(24)]
        creation_order = list(names)
        rng.shuffle(creation_order)
        for name in creation_order:
            (source / name).write_bytes((name + "\n").encode("utf-8"))
        request = source_request(["generated"])
        first, result = invoke_inventory(adapter, workspace, request)
        assert_expected(case, first, result)
        second, second_result = invoke_inventory(adapter, workspace, request)
        assert_expected(case, second, second_result)
        if first.stdout != second.stdout or first.stderr != second.stderr:
            raise CaseFailure("repeated inventory output differs byte-for-byte")
        paths = [entry["path"] for entry in result["data"]["inventory"]["entries"]]
        if paths != sorted(paths, key=lambda value: value.encode("utf-8")):
            raise CaseFailure("seeded filesystem creation order affected inventory ordering")
        return
    if case["id"] == "property-repeat-output":
        first, result = invoke(adapter, ["probe"])
        assert_expected(case, first, result)
        second, second_result = invoke(adapter, ["probe"])
        assert_expected(case, second, second_result)
        if first.stdout != second.stdout or first.stderr != second.stderr:
            raise CaseFailure("repeated probe output differs byte-for-byte")
        return
    rng = random.Random(20260913)
    for index in range(16):
        manifest = load_manifest(skill_root)
        token = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(8))
        manifest["recordRoot"] = f"record-{index}-{token}"
        workspace = temporary / f"valid-{index}"
        workspace.mkdir()
        materialize(workspace, manifest)
        completed, result = invoke(adapter, ["discover", "--workspace-root", str(workspace)])
        if completed.returncode != 0 or result["code"] != "ok":
            raise CaseFailure(f"generated portable path was rejected: {manifest['recordRoot']}")
    invalid = ["../escape", "a//b", "a/./b", "C:/drive", "a\\b", "NUL", "trail."]
    for index, value in enumerate(invalid):
        manifest = load_manifest(skill_root)
        manifest["recordRoot"] = value
        workspace = temporary / f"invalid-{index}"
        workspace.mkdir()
        materialize(workspace, load_manifest(skill_root))
        (workspace / ".wayfinder/manifest.json").write_bytes(pretty(manifest))
        completed, result = invoke(adapter, ["discover", "--workspace-root", str(workspace)])
        if completed.returncode != 4 or result["ok"]:
            raise CaseFailure(f"generated unsafe path was accepted: {value}")


def command_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    case_id = case["id"]
    if case_id == "command-unknown":
        completed, result = invoke(adapter, ["initialize-activate"])
        assert_expected(case, completed, result)
        return
    if case_id == "command-unexpected":
        completed, result = invoke(adapter, ["probe"], env={"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_RAISE": "1"})
        assert_expected(case, completed, result)
        return
    if case_id == "command-envelope":
        completed, result = invoke(adapter, ["probe"])
        assert_expected(case, completed, result)
        expected = json.loads((skill_root / CONFORMANCE_REL / "expected/result-envelope-fields.json").read_text(encoding="utf-8"))
        if list(result) != expected:
            raise CaseFailure("envelope does not match fixed expected field list")
        return
    if case_id == "command-deterministic":
        first, result = invoke(adapter, ["probe"])
        assert_expected(case, first, result)
        second, second_result = invoke(adapter, ["probe"])
        assert_expected(case, second, second_result)
        if first.stdout != second.stdout:
            raise CaseFailure("deterministic probe bytes differ")
        expected = json.loads((skill_root / CONFORMANCE_REL / "expected/probe-deterministic.json").read_text(encoding="utf-8"))
        observed = {
            "knownAnswerCount": result["data"]["deterministic"]["knownAnswers"]["count"],
            "capabilities": result["data"]["deterministic"]["capabilities"],
            "contractVersion": result["data"]["contract"]["version"],
            "releaseId": result["data"]["contract"]["releaseId"],
            "status": result["data"]["contract"]["status"],
        }
        if observed != expected:
            raise CaseFailure(f"deterministic probe projection differs: {observed!r}")
        if set(result["data"]) != {"adapter", "contract", "deterministic", "environment"}:
            raise CaseFailure("probe does not separate deterministic and environment evidence")
        if result["data"]["deterministic"]["knownAnswers"]["count"] != expected["knownAnswerCount"]:
            raise CaseFailure("probe did not recompute the governed known-answer set")
        return
    if case_id == "command-no-writes":
        workspace = temporary / "workspace"
        workspace.mkdir()
        manifest = load_manifest(skill_root)
        materialize(workspace, manifest)
        before_workspace = snapshot(workspace)
        before_skill = snapshot(skill_root)
        completed, result = invoke(adapter, ["discover", "--workspace-root", str(workspace)])
        assert_expected(case, completed, result)
        invoke(adapter, ["probe"])
        if before_workspace != snapshot(workspace) or before_skill != snapshot(skill_root):
            raise CaseFailure("read-only commands changed project or package files")
        return
    if case_id == "command-inventory-no-writes":
        workspace = temporary / "workspace"
        workspace.mkdir()
        make_source_tree(workspace)
        request = source_request()
        before_workspace = snapshot(workspace)
        before_skill = snapshot(skill_root)
        completed, result = invoke_inventory(adapter, workspace, request)
        assert_expected(case, completed, result)
        if before_workspace != snapshot(workspace) or before_skill != snapshot(skill_root):
            raise CaseFailure("inventory changed source, project, or package files")
        return
    if case_id == "command-validate-no-writes":
        workspace = temporary / "workspace"
        workspace.mkdir()
        make_slice3_record(adapter, workspace)
        before_workspace = snapshot(workspace)
        before_skill = snapshot(skill_root)
        completed, result = invoke(adapter, ["validate", "--workspace-root", str(workspace)])
        assert_expected(case, completed, result)
        if before_workspace != snapshot(workspace) or before_skill != snapshot(skill_root):
            raise CaseFailure("validate changed project or package files")
        return
    if case_id == "command-generate-declared-writes":
        workspace = temporary / "workspace"
        workspace.mkdir()
        make_slice3_record(adapter, workspace)
        before = snapshot(workspace)
        completed, result = invoke_generate(adapter, workspace, base_generation_request("catalog"))
        assert_expected(case, completed, result)
        changed = []
        after_by_path = {item["path"]: item for item in snapshot(workspace)}
        for item in before:
            if after_by_path.get(item["path"]) != item:
                changed.append(item["path"])
        if changed not in ([], ["record/.wayfinder/catalog.json"]):
            raise CaseFailure(f"generation wrote outside declared catalog: {changed}")
        return
    if case_id == "command-generate-unexpected":
        workspace = temporary / "workspace"
        workspace.mkdir()
        request_path = temporary / "request.json"
        request_path.write_bytes(pretty(base_generation_request("catalog")))
        completed, result = invoke(adapter, ["generate", "--workspace-root", str(workspace), "--request", str(request_path)], env={"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_RAISE": "1"})
        assert_expected(case, completed, result)
        return
    raise CaseFailure(f"unimplemented command case {case_id}")


def initialize_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    case_id = case["id"]
    workspace = temporary / "workspace"
    workspace.mkdir()
    make_git_baseline(workspace)
    proposal = initialize_proposal(skill_root)
    bundle = temporary / "bundle"
    before_workspace = snapshot(workspace)
    before_skill = snapshot(skill_root)

    if case_id == "initialize-seeded-candidate-boundaries":
        rng = random.Random(20260913)
        for index in range(24):
            candidate = initialize_proposal(skill_root)
            ordinal = rng.randint(5, 999)
            candidate["documents"][-1]["id"] = f"wf-{ordinal:04d}-seeded-gap"
            candidate_bundle = temporary / f"seeded-{index:02d}"
            completed, result = invoke_initialize(adapter, workspace, candidate, candidate_bundle)
            if completed.returncode != 2 or result["code"] != "proposal.document-id-order" or candidate_bundle.exists():
                raise CaseFailure(f"seeded invalid candidate ordinal was not rejected: {ordinal}")
        if snapshot(workspace) != before_workspace or snapshot(skill_root) != before_skill:
            raise CaseFailure("seeded proposal checks mutated workspace or skill")
        return

    source_cases = {"initialize-source-assisted", "initialize-inventory-digest", "initialize-inventory-stale", "initialize-intake-digest", "initialize-material-source-disposition"}
    if case_id in source_cases:
        source_root = workspace / "sources"
        source_root.mkdir()
        (source_root / "intent.md").write_bytes(b"# Legacy intent\n\nPreserved source material.\n")
        (source_root / "reference.txt").write_bytes(b"Reference evidence.\n")
        (source_root / "preserve.txt").write_bytes(b"Material retained outside scope.\n")
        (source_root / "unresolved.txt").write_bytes(b"Meaning remains unresolved.\n")
        request = source_request(["sources"])
        request["targetRoots"] = ["record"]
        completed_inventory, inventory_result = invoke_inventory(adapter, workspace, request)
        if completed_inventory.returncode != 0:
            raise CaseFailure("source-assisted setup inventory failed")
        inventory = inventory_result["data"]["inventory"]
        inventory_digest = inventory_result["data"]["inventorySha256"]
        inventory_path = workspace / "source-inventory.json"
        inventory_path.write_bytes(pretty(inventory))
        entries = {item["path"]: item for item in inventory["entries"]}
        evidence = copy.deepcopy(proposal["documents"][1])
        evidence.update({
            "output": "research/evidence.md", "title": "Initialization evidence", "id": "wf-0005-initialization-evidence",
            "kind": "evidence", "status": "Active", "summary": "Preserves one reviewed source used by the bootstrap.",
            "sections": [
                {"heading": "Question and scope", "content": "What source supports the initial record design?"},
                {"heading": "Method", "content": "The owner reviewed the bounded local source inventory."},
                {"heading": "Findings", "content": "- **Material claim:** A reviewed reference exists. [src-01](#src-01)"},
                {"heading": "Applicability and limitations", "content": "The source is direct only to this synthetic initialization example."},
                {"heading": "Evidence, inference, and hypothesis", "content": "The cited line is evidence; no broader conclusion is inferred."},
                {"heading": "Implications", "content": "The record can preserve a traceable local-source binding."},
                {"heading": "Unknowns", "content": "Broader evidence needs remain open."},
                {"heading": "Next validation", "content": "Interview should review whether more sources are material."},
                {"heading": "Sources", "content": "The governed source entry follows."},
            ],
            "questions": [],
            "sources": [{
                "key": "src-01", "title": "Synthetic reference", "citation": "Owner-provided local reference", "original": "sources/reference.txt",
                "published": None, "accessed": "2026-09-13", "applicability": "Direct", "usedFor": "Supports the explicit synthetic material claim.",
                "limitations": "This fixture does not establish any external fact."
            }],
        })
        proposal["documents"].append(evidence)
        proposal["manifest"]["modules"].append({"id": "research", "root": "research", "entrypoint": "research/evidence.md", "subjects": []})
        proposal["omittedModules"] = [item for item in proposal["omittedModules"] if item["id"] != "research"]
        def ledger_item(path: str, disposition: str, *, targets: list[str] | None = None, evidence_keys: list[str] | None = None, questions: list[str] | None = None, note: str | None = None) -> dict[str, Any]:
            entry = entries[path]
            return {"path": path, "sha256": entry["sha256"], "byteLength": entry["byteLength"], "disposition": disposition, "reason": f"The owner confirmed the {disposition} disposition.", "targetIds": targets or [], "transformationNote": note, "evidenceKeys": evidence_keys or [], "questionIds": questions or []}
        ledger = {
            "format": "wayfinder-intake-ledger", "schemaVersion": 1, "inventorySha256": inventory_digest,
            "sources": [
                ledger_item("sources/intent.md", "incorporate", targets=["wf-0002-plan-brief"], note="Selected intent was synthesized into the confirmed brief."),
                ledger_item("sources/preserve.txt", "preserve-out-of-scope"),
                ledger_item("sources/reference.txt", "reference", evidence_keys=["src-01"]),
                ledger_item("sources/unresolved.txt", "unresolved", questions=["wfq-0001-success-evidence"]),
            ],
        }
        ledger["sources"].sort(key=lambda item: item["path"].encode("utf-8"))
        ledger_path = workspace / "intake-ledger.json"
        ledger_path.write_bytes(pretty(ledger))
        ledger_digest = sha256(json.dumps(ledger, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        proposal["mode"] = "source-assisted"
        proposal["sourceInventory"] = {"path": "source-inventory.json", "sha256": inventory_digest}
        proposal["intakeLedger"] = {"path": "intake-ledger.json", "sha256": ledger_digest}
        proposal["materialSourcePaths"] = sorted(item["path"] for item in ledger["sources"])
        if case_id == "initialize-inventory-digest":
            proposal["sourceInventory"]["sha256"] = "0" * 64
        elif case_id == "initialize-inventory-stale":
            (source_root / "intent.md").write_bytes(b"# Changed\n")
        elif case_id == "initialize-intake-digest":
            proposal["intakeLedger"]["sha256"] = "0" * 64
        elif case_id == "initialize-material-source-disposition":
            proposal["materialSourcePaths"].append("sources/missing.md")
        before_workspace = snapshot(workspace)
    elif case_id == "proposal-duplicate-field":
        raw = pretty(proposal).replace(b'{\n  "format":', b'{\n  "format": "wayfinder-initialize-proposal",\n  "format":', 1)
        completed, result = invoke_initialize(adapter, workspace, proposal, bundle, raw=raw)
        assert_expected(case, completed, result)
        if bundle.exists():
            raise CaseFailure("rejected duplicate field created a bundle")
        return
    elif case_id == "proposal-unknown-field":
        proposal["unknown"] = True
    elif case_id == "proposal-missing-field":
        del proposal["concerns"]
    elif case_id == "proposal-wrong-type":
        proposal["profile"] = "foundation"
    elif case_id == "proposal-unsupported-version":
        proposal["schemaVersion"] = 2
    elif case_id == "proposal-non-nfc":
        proposal["authorityBoundary"]["statement"] = "Cafe\u0301"
    elif case_id == "proposal-malformed-unicode":
        raw = pretty(proposal).replace(b"Project North", b"\\ud800", 1)
        completed, result = invoke_initialize(adapter, workspace, proposal, bundle, raw=raw)
        assert_expected(case, completed, result)
        if bundle.exists():
            raise CaseFailure("rejected malformed Unicode created a bundle")
        return
    elif case_id == "proposal-mode":
        proposal["mode"] = "automatic"
    elif case_id == "proposal-profile-unconfirmed":
        proposal["profile"]["confirmed"] = False
    elif case_id == "initialize-taxonomy-subjects":
        proposal["documents"][1]["output"] = "product/plan.md"
        proposal["documents"][2]["output"] = "product/questions/README.md"
        proposal["documents"][2]["questions"][0]["appliesTo"][0]["targetPath"] = "../plan.md"
        product_index = copy.deepcopy(proposal["documents"][3])
        product_index.update({"output": "product/README.md", "title": "Product index", "id": "wf-0005-product-index", "summary": "Routes the confirmed product taxonomy.", "sections": [{"heading": "Scope", "content": "This module owns the confirmed product-planning concerns."}]})
        proposal["documents"].append(product_index)
        proposal["manifest"]["modules"].append({"id": "product", "root": "product", "entrypoint": "product/README.md", "subjects": [{"id": "current-plan", "kind": "document", "entrypoint": "product/plan.md"}, {"id": "questions", "kind": "collection", "root": "product/questions", "entrypoint": "product/questions/README.md"}]})
        proposal["omittedModules"] = [item for item in proposal["omittedModules"] if item["id"] != "product"]
    elif case_id in {"initialize-local-module", "proposal-local-module-boundary"}:
        local = copy.deepcopy(proposal["documents"][1])
        local.update({"output": "safety/README.md", "title": "Safety planning", "id": "wf-0005-safety-planning", "kind": "guide", "summary": "Defines the distinct safety-planning boundary.", "sections": [{"heading": "Purpose", "content": "Preserve safety planning that has a distinct review lifecycle."}, {"heading": "Authority boundary", "content": "This module governs safety-planning guidance, not product or technical choices."}, {"heading": "Audience", "content": "The accountable safety reviewer is the primary reader."}, {"heading": "Relationship to standard modules", "content": "Product, research, decision, architecture, and development records link here without duplicating its guidance."}]})
        if case_id == "proposal-local-module-boundary":
            local["sections"] = [item for item in local["sections"] if item["heading"] != "Audience"]
        proposal["documents"].append(local)
        proposal["manifest"]["modules"].append({"id": "local-safety", "root": "safety", "entrypoint": "safety/README.md", "subjects": []})
        proposal["concerns"].append({"id": "safety-guidance", "statement": "Safety guidance needs a distinct authority and review audience.", "homeId": "wf-0005-safety-planning"})
    elif case_id == "proposal-document-id-collision":
        proposal["documents"][1]["id"] = proposal["documents"][0]["id"]
    elif case_id == "proposal-document-id-gap":
        proposal["documents"][-1]["id"] = "wf-0005-decision-index"
    elif case_id == "proposal-question-id-gap":
        proposal["documents"][2]["questions"][0]["id"] = "wfq-0002-success-evidence"
    elif case_id == "proposal-concern-home":
        proposal["concerns"][0]["homeId"] = "wf-9999-missing"
    elif case_id == "proposal-concern-duplicate":
        proposal["concerns"][1]["id"] = proposal["concerns"][0]["id"]
    elif case_id == "proposal-omission-incomplete":
        proposal["omittedModules"].pop()
    elif case_id == "proposal-competing-authority":
        proposal["authorityBoundary"]["competingCurrentAuthority"] = ["legacy-plan.md also claims current project-plan authority"]
    elif case_id == "proposal-inference-unconfirmed":
        proposal["materialInferences"] = [{"statement": "The owner may value speed.", "basis": "Agent interpretation.", "confirmed": False}]
    elif case_id == "proposal-unresolved-without-question":
        proposal["documents"][2]["questions"] = []
        proposal["epistemicStates"] = []
        proposal["interviewResume"]["recommendedFocusIds"] = ["wf-0002-plan-brief"]
        proposal["concerns"][1]["homeId"] = "wf-0002-plan-brief"
    elif case_id == "proposal-fresh-source-binding":
        proposal["sourceInventory"] = {"path": "inventory.json", "sha256": "0" * 64}
    elif case_id == "proposal-source-assisted-binding":
        proposal["mode"] = "source-assisted"
    elif case_id == "proposal-placeholder":
        proposal["documents"][1]["sections"][0]["content"] = "TBD"
    elif case_id == "proposal-knowledge-map":
        proposal["documents"][0]["sections"] = [item for item in proposal["documents"][0]["sections"] if item["heading"] != "Authority boundary"]
    elif case_id == "proposal-module-containment":
        extra = copy.deepcopy(proposal["documents"][1])
        extra["output"] = "misc/extra.md"
        extra["id"] = "wf-0005-extra"
        proposal["documents"].append(extra)
    elif case_id == "proposal-generated-containment":
        proposal["manifest"]["generatedArtifacts"][0]["path"] = "../catalog.json"
    elif case_id == "proposal-target-collision":
        proposal["manifest"]["generatedArtifacts"][0]["path"] = "README.md"
    elif case_id == "initialize-target-exists":
        target = workspace / "record/plan-brief.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"existing\n")
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-late-target-exists":
        target = workspace / "record/decisions/README.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"existing late target\n")
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-module-root-exists":
        (workspace / "record/decisions").mkdir(parents=True)
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-manifest-exists":
        target = workspace / ".wayfinder/manifest.json"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"{}\n")
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-baseline-unresolved":
        proposal["manifest"]["canonicalBaseline"]["ref"] = "refs/heads/missing"
    elif case_id == "initialize-snapshot-baseline":
        snapshot_path = workspace / ".wayfinder/baselines/initial.json"
        snapshot_path.parent.mkdir(parents=True)
        snapshot_path.write_bytes(b"{}\n")
        proposal["manifest"]["canonicalBaseline"] = {"kind": "snapshot", "path": ".wayfinder/baselines/initial.json", "sha256": sha256(snapshot_path.read_bytes())}
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-bundle-exists":
        bundle.mkdir()
    elif case_id == "initialize-bundle-location":
        bundle = workspace / "bundle"
    elif case_id == "initialize-bundle-symlink":
        real_parent = temporary / "real-parent"
        real_parent.mkdir()
        linked_parent = temporary / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        bundle = linked_parent / "bundle"
    elif case_id == "initialize-target-symlink":
        outside = temporary / "outside"
        outside.mkdir()
        (workspace / "record").symlink_to(outside, target_is_directory=True)
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-recovery-required":
        state = workspace / ".wayfinder/operations/old"
        state.mkdir(parents=True)
        (state / "event.json").write_bytes(b"{}\n")
        before_workspace = snapshot(workspace)
    elif case_id == "initialize-unexpected":
        completed, result = invoke_initialize(adapter, workspace, proposal, bundle, env={"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_RAISE": "1"})
        assert_expected(case, completed, result)
        if bundle.exists():
            raise CaseFailure("unexpected pre-dispatch failure created a bundle")
        return

    plan_env = None
    if case_id == "initialize-repeat-bytes":
        plan_env = {"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_OPERATION_ID": "wfinit-test-repeatable"}
    completed, result = invoke_initialize(adapter, workspace, proposal, bundle, env=plan_env)
    assert_expected(case, completed, result)
    if case["exit"] != 0:
        if bundle.exists() and case_id != "initialize-bundle-exists":
            raise CaseFailure("rejected initialize preflight created a bundle")
        if snapshot(workspace) != before_workspace or snapshot(skill_root) != before_skill:
            raise CaseFailure("rejected initialize planning mutated workspace or skill")
        return
    if snapshot(workspace) != before_workspace or snapshot(skill_root) != before_skill:
        raise CaseFailure("successful initialize planning mutated workspace or skill")
    if (workspace / ".wayfinder/manifest.json").exists() or (workspace / "record").exists():
        raise CaseFailure("initialize-plan published target record content")
    plan_raw = (bundle / "plan.json").read_bytes()
    plan = json.loads(plan_raw)
    expected_canonical = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if plan_raw != expected_canonical or plan_raw.endswith(b"\n"):
        raise CaseFailure("plan is not exact canonical JSON")
    if sha256(plan_raw) != result["data"]["planSha256"]:
        raise CaseFailure("result plan digest differs from exact plan bytes")
    if plan["operations"][-1]["action"] != "publish-manifest" or plan["operations"][-1]["path"] != ".wayfinder/manifest.json":
        raise CaseFailure("manifest is not the final declarative operation")
    seen_targets: set[str] = set()
    for item in plan["payloads"]:
        raw = (bundle / item["bundlePath"]).read_bytes()
        if len(raw) != item["byteLength"] or sha256(raw) != item["sha256"]:
            raise CaseFailure("payload manifest differs from exact payload bytes")
        if item["targetPath"] in seen_targets:
            raise CaseFailure("payload target is duplicated")
        seen_targets.add(item["targetPath"])
    if case_id == "initialize-source-assisted":
        if not (bundle / "inventory.json").is_file() or not (bundle / "intake.json").is_file():
            raise CaseFailure("source-assisted bundle lacks canonical inventory or intake attachment")
        attached = json.loads((bundle / "intake.json").read_bytes())
        if {item["disposition"] for item in attached["sources"]} != {"incorporate", "reference", "preserve-out-of-scope", "unresolved"}:
            raise CaseFailure("source-assisted plan does not demonstrate all dispositions")
    if case_id == "initialize-minimal":
        golden = json.loads((skill_root / CONFORMANCE_REL / "expected/initialize-minimal-golden.json").read_text(encoding="utf-8"))
        normalized_plan = plan_raw.replace(str(workspace).encode("utf-8"), b"<WORKSPACE>")
        normalized_plan = normalized_plan.replace(plan["contractSha256"].encode("ascii"), b"<CONTRACT_SHA256>")
        preview_raw = (bundle / "preview.md").read_bytes()
        normalized_preview = preview_raw.replace(str(workspace).encode("utf-8"), b"<WORKSPACE>")
        normalized_preview = normalized_preview.replace(result["data"]["planSha256"].encode("ascii"), b"<PLAN_SHA256>")
        normalized_preview = normalized_preview.replace(result["data"]["operationId"].encode("ascii"), b"<OPERATION_ID>")
        observed = {
            "bundleFiles": sorted(path.relative_to(bundle).as_posix() for path in bundle.rglob("*") if path.is_file()),
            "normalizedPlanSha256": sha256(normalized_plan),
            "normalizedPreviewSha256": sha256(normalized_preview),
            "payloadSha256": [sha256(path.read_bytes()) for path in sorted((bundle / "payload").glob("*"))],
        }
        if observed != golden:
            raise CaseFailure(f"minimal golden bundle projection differs: {observed!r}")
    if case_id == "initialize-repeat-bytes":
        second_bundle = temporary / "bundle-second"
        second, second_result = invoke_initialize(adapter, workspace, proposal, second_bundle, env=plan_env)
        assert_expected(case, second, second_result)
        for path in sorted(item.relative_to(bundle) for item in bundle.rglob("*") if item.is_file()):
            if (bundle / path).read_bytes() != (second_bundle / path).read_bytes():
                raise CaseFailure(f"repeated bundle bytes differ: {path}")
        if result["data"]["planSha256"] != second_result["data"]["planSha256"]:
            raise CaseFailure("repeated plan digests differ")
        if plan["effectiveDate"] != proposal["effectiveDate"] or result["data"]["operationId"] != "wfinit-test-repeatable":
            raise CaseFailure("explicit effective date or maintainer operation-ID control was not preserved")
    if case_id == "initialize-digest-mutation":
        changed = copy.deepcopy(proposal)
        changed["authorityBoundary"]["statement"] += " Confirmed wording changed."
        second_bundle = temporary / "bundle-mutated"
        second, second_result = invoke_initialize(adapter, workspace, changed, second_bundle)
        assert_expected(case, second, second_result)
        if result["data"]["planSha256"] == second_result["data"]["planSha256"]:
            raise CaseFailure("material proposal mutation did not change plan digest")


def apply_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    case_id = case["id"]
    source_assisted = case_id in {"apply-source-assisted", "apply-source-stale"}
    workspace, bundle, digest, operation_id, _ = prepare_apply(skill_root, adapter, temporary, source_assisted=source_assisted)
    before_skill = snapshot(skill_root)
    before_unrelated = (workspace / "unrelated.txt").read_bytes()
    before_git = snapshot(workspace / ".git")
    test_env = {"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_CLOCK": "2026-09-13T12:34:56Z"}

    def rewrite_plan(mutate: Callable[[dict[str, Any]], None]) -> None:
        nonlocal digest, operation_id
        path = bundle / "plan.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        mutate(value)
        path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        digest = sha256(path.read_bytes())
        operation_id = f"wfinit-{digest[:24]}"

    if case_id == "apply-wrong-confirmation":
        completed, result = invoke_apply(adapter, workspace, bundle, digest, token="wayfinder-confirm-sha256:" + "0" * 64)
        assert_expected(case, completed, result)
    elif case_id == "apply-wrong-plan-digest":
        completed, result = invoke_apply(adapter, workspace, bundle, "0" * 64)
        assert_expected(case, completed, result)
    elif case_id == "apply-contract-digest":
        rewrite_plan(lambda value: value.__setitem__("contractSha256", "0" * 64))
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-workspace-binding":
        rewrite_plan(lambda value: value["workspace"].__setitem__("workspaceRoot", "/tmp/not-this-workspace"))
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-plan-unknown-field":
        rewrite_plan(lambda value: value.__setitem__("unknown", True))
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-plan-duplicate-field":
        path = bundle / "plan.json"
        path.write_bytes(path.read_bytes().replace(b'{"contractSha256":', b'{"format":"wayfinder-initialize-plan","contractSha256":', 1))
        digest = sha256(path.read_bytes())
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-plan-truncated":
        path = bundle / "plan.json"
        path.write_bytes(path.read_bytes()[:-1])
        digest = sha256(path.read_bytes())
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-payload-altered":
        target = next((bundle / "payload").iterdir())
        target.write_bytes(target.read_bytes() + b"altered")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-payload-missing":
        next((bundle / "payload").iterdir()).unlink()
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-bundle-extra":
        (bundle / "extra.txt").write_bytes(b"extra\n")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-baseline-stale":
        (workspace / ".git/refs/heads/main").write_bytes(b"2222222222222222222222222222222222222222\n")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-source-stale":
        (workspace / "sources/legacy.md").write_bytes(b"# Changed\n")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-target-appeared":
        target = workspace / "record/plan-brief.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"race\n")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
        if target.read_bytes() != b"race\n":
            raise CaseFailure("pre-existing target was overwritten")
    elif case_id == "apply-manifest-appeared":
        target = workspace / ".wayfinder/manifest.json"
        target.parent.mkdir()
        target.write_bytes(b"{}\n")
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id == "apply-lock-contention":
        import socket
        control = workspace / ".wayfinder"
        control.mkdir()
        lock = {"format": "wayfinder-initialization-lock", "schemaVersion": 1, "operationId": operation_id, "planSha256": digest, "owner": {"host": socket.gethostname(), "pid": os.getpid(), "token": "fixture-owner"}}
        (control / "initialize.lock").write_bytes(json.dumps(lock, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        completed, result = invoke_apply(adapter, workspace, bundle, digest)
        assert_expected(case, completed, result)
    elif case_id in {"apply-lock-foreign-owner", "apply-lock-malformed"}:
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-file-0001"})
        if interrupted.returncode != 5:
            raise CaseFailure("lock recovery setup did not interrupt")
        lock_path = workspace / ".wayfinder/initialize.lock"
        if case_id == "apply-lock-foreign-owner":
            lock = json.loads(lock_path.read_text())
            lock["owner"]["host"] = "foreign-host.example"
            lock_path.write_bytes(json.dumps(lock, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        else:
            lock_path.write_bytes(b"{broken")
        completed, result = invoke_recover(adapter, workspace, operation_id, "resume")
        assert_expected(case, completed, result)
    elif case_id == "apply-unexpected":
        completed, result = invoke_apply(adapter, workspace, bundle, digest, env={"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_RAISE": "1"})
        assert_expected(case, completed, result)
    elif case_id in {"apply-journal-altered", "apply-journal-reordered", "apply-journal-rehashed-reorder", "apply-journal-truncated", "apply-journal-duplicated", "apply-journal-forked"}:
        env = {**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-file-0002"}
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env=env)
        if interrupted.returncode != 5:
            raise CaseFailure("journal mutation setup did not interrupt")
        journal = workspace / f".wayfinder/operations/{operation_id}/events.jsonl"
        lines = journal.read_bytes().splitlines(keepends=True)
        if case_id == "apply-journal-altered":
            lines[1] = lines[1].replace(b"staging-started", b"staging-started-x")
        elif case_id == "apply-journal-reordered":
            lines[2], lines[3] = lines[3], lines[2]
        elif case_id == "apply-journal-rehashed-reorder":
            events = [json.loads(line) for line in lines]
            events[2], events[3] = events[3], events[2]
            previous = None
            rebuilt = []
            for index, event in enumerate(events, 1):
                event["sequence"] = index
                event["previousEventSha256"] = previous
                basis = {key: event[key] for key in ("format", "schemaVersion", "operationId", "sequence", "timestamp", "type", "previousEventSha256", "data")}
                event["eventSha256"] = sha256(json.dumps(basis, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
                previous = event["eventSha256"]
                rebuilt.append(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
            lines = rebuilt
        elif case_id == "apply-journal-truncated":
            lines[-1] = lines[-1][:-2]
        elif case_id == "apply-journal-duplicated":
            lines.append(lines[-1])
        else:
            lines.append(lines[2])
        journal.write_bytes(b"".join(lines))
        completed, result = invoke_recover(adapter, workspace, operation_id, "inspect")
        assert_expected(case, completed, result)
        if result["data"]["status"] != "manual-recovery":
            raise CaseFailure("journal mutation was not classified manual-recovery")
    elif case_id == "apply-recovery-bundle-altered":
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-file-0001"})
        if interrupted.returncode != 5:
            raise CaseFailure("imported-bundle mutation setup did not interrupt")
        imported = next((workspace / f".wayfinder/operations/{operation_id}/bundle/payload").iterdir())
        imported.write_bytes(imported.read_bytes() + b"altered")
        inspected, inspected_result = invoke_recover(adapter, workspace, operation_id, "inspect")
        assert_expected(case, inspected, inspected_result)
        if inspected_result["data"]["status"] != "manual-recovery":
            raise CaseFailure("altered imported bundle was not classified manual-recovery")
    elif case_id in {"apply-created-modified", "apply-created-missing", "apply-target-race-after-preflight", "apply-premature-manifest", "apply-manifest-altered", "apply-manifest-missing", "apply-post-validation-failure"}:
        boundary = "after-manifest-publication" if case_id in {"apply-manifest-altered", "apply-manifest-missing", "apply-post-validation-failure"} else "after-file-0002"
        if case_id in {"apply-target-race-after-preflight", "apply-premature-manifest"}:
            boundary = "after-preconditions-rechecked"
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": boundary})
        if interrupted.returncode != 5:
            raise CaseFailure("manual recovery setup did not interrupt")
        plan = json.loads((bundle / "plan.json").read_text())
        if case_id == "apply-created-modified":
            (workspace / plan["operations"][5]["path"]).write_bytes(b"external change\n")
        elif case_id == "apply-created-missing":
            created = [event for event in (workspace / f".wayfinder/operations/{operation_id}/events.jsonl").read_text().splitlines() if '"type":"file-created"' in event]
            path = json.loads(created[-1])["data"]["path"]
            (workspace / path).unlink()
        elif case_id == "apply-target-race-after-preflight":
            target = workspace / plan["operations"][4]["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"race\n")
        elif case_id == "apply-premature-manifest":
            manifest_item = next(item for item in plan["payloads"] if item["role"] == "manifest")
            target = workspace / manifest_item["targetPath"]
            target.write_bytes((bundle / manifest_item["bundlePath"]).read_bytes())
        elif case_id in {"apply-manifest-altered", "apply-post-validation-failure"}:
            target = workspace / (".wayfinder/manifest.json" if case_id == "apply-manifest-altered" else "record/plan-brief.md")
            target.write_bytes(b"external change\n")
        else:
            (workspace / ".wayfinder/manifest.json").unlink()
        completed, result = invoke_recover(adapter, workspace, operation_id, "inspect")
        assert_expected(case, completed, result)
        if result["data"]["status"] != "manual-recovery":
            raise CaseFailure(f"{case_id} was not classified manual-recovery")
    elif case_id in {"apply-receipt-altered", "apply-receipt-missing"}:
        completed, result = invoke_apply(adapter, workspace, bundle, digest, env=test_env)
        if completed.returncode != 0:
            raise CaseFailure("receipt mutation setup failed")
        receipt = workspace / f".wayfinder/operations/{operation_id}/receipt.json"
        if case_id == "apply-receipt-altered":
            receipt.write_bytes(receipt.read_bytes() + b" ")
        else:
            receipt.unlink()
        inspected, inspected_result = invoke_recover(adapter, workspace, operation_id, "inspect")
        assert_expected(case, inspected, inspected_result)
        if inspected_result["data"]["status"] != "manual-recovery":
            raise CaseFailure("receipt mutation was not classified manual-recovery")
    elif case_id == "apply-inspect-idempotent":
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-file-0001"})
        if interrupted.returncode != 5:
            raise CaseFailure("inspection setup did not interrupt")
        first, first_result = invoke_recover(adapter, workspace, operation_id, "inspect")
        middle = snapshot(workspace)
        second, second_result = invoke_recover(adapter, workspace, operation_id, "inspect")
        assert_expected(case, second, second_result)
        if first.returncode != 0 or first.stdout != second.stdout or snapshot(workspace) != middle:
            raise CaseFailure("repeated recovery inspection is not byte-idempotent and read-only")
    elif case_id == "apply-failure-boundary-matrix":
        boundaries = ["after-lock-acquired", "after-bundle-imported", "after-staging-started"]
        boundaries += [f"after-stage-{index:04d}" for index in range(1, 7)]
        boundaries += ["after-staging-complete", "after-preconditions-rechecked", "after-publication-started"]
        boundaries += [f"after-directory-{index:04d}" for index in range(2, 5)]
        boundaries += [name for index in range(1, 6) for name in (f"before-file-{index:04d}", f"after-file-{index:04d}")]
        boundaries += ["before-manifest-publication", "after-manifest-publication", "after-live-validation-started", "after-live-validation-complete", "after-receipt-written", "after-complete"]
        for index, boundary in enumerate(boundaries):
            nested = temporary / f"boundary-{index:02d}"
            nested.mkdir()
            ws, candidate_bundle, candidate_digest, candidate_id, _ = prepare_apply(skill_root, adapter, nested)
            interrupted, _ = invoke_apply(adapter, ws, candidate_bundle, candidate_digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": boundary})
            if interrupted.returncode != 5:
                raise CaseFailure(f"failure boundary was not reached: {boundary}")
            inspected, inspected_result = invoke_recover(adapter, ws, candidate_id, "inspect")
            if inspected.returncode != 0 or inspected_result["data"]["status"] not in {"blocked", "resumable", "completed"}:
                raise CaseFailure(f"injected state lacks documented classification: {boundary}: {inspected_result}")
            if inspected_result["data"]["status"] == "resumable":
                resumed, resumed_result = invoke_recover(adapter, ws, candidate_id, "resume", env=test_env)
                if resumed.returncode != 0 or resumed_result["data"]["status"] != "completed":
                    raise CaseFailure(f"injected state did not resume: {boundary}: {resumed_result}")
            elif inspected_result["data"]["status"] == "blocked":
                rolled, rolled_result = invoke_recover(adapter, ws, candidate_id, "rollback", env=test_env)
                if rolled.returncode != 0 or rolled_result["data"]["status"] != "rolled-back":
                    raise CaseFailure(f"lock-only state did not roll back: {boundary}: {rolled_result}")
        completed = subprocess.CompletedProcess([], 0, b'{"format":"wayfinder-command-result","schemaVersion":1,"ok":true,"command":"initialize-apply","code":"ok","data":{},"diagnostics":[]}\n', b"")
        result = json.loads(completed.stdout)
        assert_expected(case, completed, result)
    elif case_id == "apply-seeded-target-races":
        rng = random.Random(20260913)
        for index in range(16):
            nested = temporary / f"race-{index:02d}"
            nested.mkdir()
            ws, candidate_bundle, candidate_digest, candidate_id, _ = prepare_apply(skill_root, adapter, nested)
            interrupted, _ = invoke_apply(adapter, ws, candidate_bundle, candidate_digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-preconditions-rechecked"})
            if interrupted.returncode != 5:
                raise CaseFailure("seeded race setup did not interrupt")
            plan = json.loads((candidate_bundle / "plan.json").read_text())
            targets = [item for item in plan["payloads"] if item["role"] != "manifest"]
            item = targets[rng.randrange(len(targets))]
            target = ws / item["targetPath"]
            target.parent.mkdir(parents=True, exist_ok=True)
            marker = f"seeded race {index}\n".encode()
            target.write_bytes(marker)
            inspected, inspected_result = invoke_recover(adapter, ws, candidate_id, "inspect")
            if inspected.returncode != 0 or inspected_result["data"]["status"] != "manual-recovery" or target.read_bytes() != marker:
                raise CaseFailure("seeded target race was not preserved and classified")
        completed = subprocess.CompletedProcess([], 0, b'{"format":"wayfinder-command-result","schemaVersion":1,"ok":true,"command":"initialize-apply","code":"ok","data":{},"diagnostics":[]}\n', b"")
        result = json.loads(completed.stdout)
        assert_expected(case, completed, result)
    elif case_id == "apply-deterministic-bytes":
        first, first_result = invoke_apply(adapter, workspace, bundle, digest, env=test_env)
        if first.returncode != 0:
            raise CaseFailure("first deterministic apply failed")
        first_journal = (workspace / f".wayfinder/operations/{operation_id}/events.jsonl").read_bytes()
        first_receipt = (workspace / f".wayfinder/operations/{operation_id}/receipt.json").read_bytes()
        first_targets = {item["targetPath"]: (workspace / item["targetPath"]).read_bytes() for item in json.loads((bundle / "plan.json").read_text())["payloads"]}
        shutil.rmtree(workspace)
        workspace.mkdir()
        make_git_baseline(workspace)
        (workspace / "unrelated.txt").write_bytes(b"preserve me\n")
        second, second_result = invoke_apply(adapter, workspace, bundle, digest, env=test_env)
        assert_expected(case, second, second_result)
        if first.stdout != second.stdout or first_journal != (workspace / f".wayfinder/operations/{operation_id}/events.jsonl").read_bytes() or first_receipt != (workspace / f".wayfinder/operations/{operation_id}/receipt.json").read_bytes():
            raise CaseFailure("repeated identical controlled apply bytes differ")
        if any((workspace / path).read_bytes() != raw for path, raw in first_targets.items()):
            raise CaseFailure("repeated final target bytes differ")
    elif case_id == "apply-golden-outputs":
        completed, result = invoke_apply(adapter, workspace, bundle, digest, env=test_env)
        assert_expected(case, completed, result)
        plan = json.loads((bundle / "plan.json").read_text())
        events = [json.loads(line) for line in (workspace / f".wayfinder/operations/{operation_id}/events.jsonl").read_text().splitlines()]
        receipt = json.loads((workspace / f".wayfinder/operations/{operation_id}/receipt.json").read_text())
        observed = {
            "eventTypes": [item["type"] for item in events],
            "eventSequences": [item["sequence"] for item in events],
            "receiptFields": list(receipt),
            "receiptGateStatus": [receipt["operationalIntegrity"]["status"], receipt["semanticReadiness"]["status"]],
            "resultDataFields": list(result["data"]),
            "finalTargets": [{"path": item["targetPath"], "sha256": sha256((workspace / item["targetPath"]).read_bytes())} for item in plan["payloads"]],
        }
        expected = json.loads((skill_root / CONFORMANCE_REL / "expected/initialize-apply-golden.json").read_text())
        if observed != expected:
            raise CaseFailure(f"apply golden projection differs: {observed!r}")
    elif case_id == "apply-rollback-boundary-matrix":
        boundaries = ["after-rollback-started", *(f"after-rollback-file-{index:04d}" for index in range(1, 7)), *(f"after-rollback-directory-{index:04d}" for index in range(1, 4))]
        for index, rollback_boundary in enumerate(boundaries):
            nested = temporary / f"rollback-boundary-{index:02d}"
            nested.mkdir()
            ws, candidate_bundle, candidate_digest, candidate_id, _ = prepare_apply(skill_root, adapter, nested)
            interrupted, _ = invoke_apply(adapter, ws, candidate_bundle, candidate_digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-manifest-publication"})
            if interrupted.returncode != 5:
                raise CaseFailure("rollback boundary setup did not interrupt apply")
            rolled, _ = invoke_recover(adapter, ws, candidate_id, "rollback", env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": rollback_boundary})
            if rolled.returncode != 5:
                raise CaseFailure(f"rollback failure boundary was not reached: {rollback_boundary}")
            inspected, inspected_result = invoke_recover(adapter, ws, candidate_id, "inspect")
            if inspected.returncode != 0 or inspected_result["data"].get("status") != "resumable" or inspected_result["data"].get("recoveryAction") != "rollback":
                raise CaseFailure(f"interrupted rollback lacks resumable rollback classification: {rollback_boundary}")
            resumed, resumed_result = invoke_recover(adapter, ws, candidate_id, "rollback", env=test_env)
            if resumed.returncode != 0 or resumed_result["data"]["status"] != "rolled-back" or (ws / ".wayfinder/manifest.json").exists():
                raise CaseFailure(f"interrupted rollback did not complete conservatively: {rollback_boundary}")
        completed = subprocess.CompletedProcess([], 0, b'{"format":"wayfinder-command-result","schemaVersion":1,"ok":true,"command":"initialize-apply","code":"ok","data":{},"diagnostics":[]}\n', b"")
        result = json.loads(completed.stdout)
        assert_expected(case, completed, result)
    elif case_id in {"apply-rollback-before-manifest", "apply-rollback-after-manifest", "apply-rollback-preserves-modified", "apply-rollback-interrupted"}:
        boundary = "after-file-0002" if case_id == "apply-rollback-before-manifest" else "after-manifest-publication"
        interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": boundary})
        if interrupted.returncode != 5:
            raise CaseFailure("rollback setup did not interrupt")
        if case_id == "apply-rollback-preserves-modified":
            (workspace / "record/plan-brief.md").write_bytes(b"external change\n")
        rollback_env = test_env if case_id != "apply-rollback-interrupted" else {**test_env, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-rollback-file-0001"}
        rolled, rolled_result = invoke_recover(adapter, workspace, operation_id, "rollback", env=rollback_env)
        if case_id == "apply-rollback-interrupted":
            if rolled.returncode != 5:
                raise CaseFailure("rollback interruption was not injected")
            inspected, inspected_result = invoke_recover(adapter, workspace, operation_id, "inspect")
            if inspected.returncode != 0 or inspected_result["data"].get("status") != "resumable" or inspected_result["data"].get("recoveryAction") != "rollback":
                raise CaseFailure("interrupted rollback lacks conservative classification")
            resumed_rollback, resumed_result = invoke_recover(adapter, workspace, operation_id, "rollback", env=test_env)
            assert_expected(case, resumed_rollback, resumed_result)
            if resumed_result["data"]["status"] != "rolled-back":
                raise CaseFailure("interrupted rollback did not resume to rolled-back")
        else:
            assert_expected(case, rolled, rolled_result)
            expected_status = "manual-recovery" if case_id == "apply-rollback-preserves-modified" else "rolled-back"
            if rolled_result["data"]["status"] != expected_status:
                raise CaseFailure("rollback classification differs")
            if case_id == "apply-rollback-preserves-modified" and (workspace / "record/plan-brief.md").read_bytes() != b"external change\n":
                raise CaseFailure("rollback overwrote or removed externally modified bytes")
            if (workspace / ".wayfinder/manifest.json").exists():
                raise CaseFailure("rollback did not remove exact operation manifest first")
    else:
        completed, result = invoke_apply(adapter, workspace, bundle, digest, env=test_env)
        assert_expected(case, completed, result)
        if completed.returncode != 0:
            return
        if result["data"]["status"] != "completed":
            raise CaseFailure("successful apply did not report completed")
        plan = json.loads((bundle / "plan.json").read_text())
        for item in plan["payloads"]:
            target = workspace / item["targetPath"]
            if sha256(target.read_bytes()) != item["sha256"]:
                raise CaseFailure("successful apply target differs from planned exact bytes")
        events = [json.loads(line) for line in (workspace / f".wayfinder/operations/{operation_id}/events.jsonl").read_text().splitlines()]
        if events[-1]["type"] != "complete" or next(item for item in events if item["type"] == "manifest-published")["sequence"] >= next(item for item in events if item["type"] == "live-validation-started")["sequence"]:
            raise CaseFailure("journal completion or manifest-last ordering differs")
        receipt = json.loads((workspace / f".wayfinder/operations/{operation_id}/receipt.json").read_text())
        if receipt["operationalIntegrity"]["status"] != "passed" or receipt["semanticReadiness"]["status"] != "passed" or receipt["nextWorkflow"] != "interview":
            raise CaseFailure("receipt lacks completion gates or durable Interview handoff")
        if (workspace / f".wayfinder/operations/{operation_id}/staging").exists():
            raise CaseFailure("successful apply retained private staging bytes")

    git_changed_unexpectedly = case_id != "apply-baseline-stale" and snapshot(workspace / ".git") != before_git
    if (workspace / "unrelated.txt").read_bytes() != before_unrelated or git_changed_unexpectedly or snapshot(skill_root) != before_skill:
        raise CaseFailure("apply or recovery mutated unrelated, Git, source-package, or project-record bytes")


def harness_case(skill_root: Path, adapter: Path, case: dict[str, Any], temporary: Path) -> None:
    disabled = TestControls.from_environment({})
    if disabled.as_dict() != {"clock": None, "operationId": None, "failureBoundary": None}:
        raise CaseFailure("test controls did not default to disabled")
    injected = TestControls.from_environment({
        "WAYFINDER_TEST_MODE": "1",
        "WAYFINDER_TEST_CLOCK": "2026-09-13T12:34:56Z",
        "WAYFINDER_TEST_OPERATION_ID": "wfinit-test-known-operation",
        "WAYFINDER_TEST_FAILURE_BOUNDARY": "before-first-write",
    })
    if injected.as_dict() != {
        "clock": "2026-09-13T12:34:56Z",
        "operationId": "wfinit-test-known-operation",
        "failureBoundary": "before-first-write",
    }:
        raise CaseFailure("enabled test controls changed values")
    try:
        TestControls.from_environment({"WAYFINDER_TEST_CLOCK": "2026-09-13T12:34:56Z"})
    except ValueError:
        return
    raise CaseFailure("test controls were accepted outside maintainer test mode")


def execute_case(skill_root: Path, adapter: Path, case: dict[str, Any]) -> None:
    global OBSERVATION_CASE, OBSERVATION_ROOT
    with tempfile.TemporaryDirectory(prefix=f"wayfinder-{case['id']}-") as raw_temp:
        temporary = Path(raw_temp)
        OBSERVATION_CASE = case["id"]
        OBSERVATION_ROOT = temporary
        dispatch = {
            "harness": harness_case,
            "package": package_case,
            "json": json_case,
            "discovery": discovery_case,
            "manifest": manifest_case,
            "inventory": inventory_case,
            "intake": intake_case,
            "record": record_case,
            "render": render_case,
            "generation": generation_case,
            "initialize": initialize_case,
            "apply": apply_case,
            "property": property_case,
            "command": command_case,
        }
        dispatch[case["category"]](skill_root, adapter, case, temporary)


def write_evidence(skill_root: Path, adapter: Path, cases_path: Path, results: list[dict[str, Any]], evidence_dir: Path) -> tuple[Path, Path]:
    release_path = skill_root / "assets/contract-v1/release.json"
    contract_path = skill_root / "assets/contract-v1/contract.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    counts = Counter(result["category"] for result in results)
    result_basis = {
        "releaseSha256": sha256(release_path.read_bytes()),
        "contractSha256": sha256(contract_path.read_bytes()),
        "adapterSha256": sha256(adapter.read_bytes()),
        "casesSha256": sha256(cases_path.read_bytes()),
        "results": results,
    }
    result_digest = sha256(json.dumps(result_basis, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    candidate_revision = json.loads(contract_path.read_text(encoding="utf-8"))["candidateRevision"]
    report = {
        "format": "wayfinder-local-conformance-evidence",
        "schemaVersion": 1,
        "scope": f"cumulative-stage-0-through-slice-5-candidate-revision-{candidate_revision}",
        "status": "passing-local-evidence-not-full-certification",
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "package": {
            "releaseId": release["releaseId"],
            "releaseSha256": result_basis["releaseSha256"],
            "contractVersion": release["contractVersion"],
            "contractSha256": result_basis["contractSha256"],
            "adapterId": next(
                item["id"]
                for item in release["adapters"]
                if item["path"] == adapter.relative_to(skill_root).as_posix()
            ),
            "adapterSha256": result_basis["adapterSha256"],
            "casesSha256": result_basis["casesSha256"],
        },
        "environment": {
            "pythonImplementation": platform.python_implementation(),
            "pythonVersion": platform.python_version(),
            "operatingSystem": platform.platform(),
            "filesystem": "local temporary directories; case sensitivity not independently characterized",
            "locale": os.environ.get("LC_ALL") or os.environ.get("LANG") or "unreported",
            "timezone": os.environ.get("TZ") or "host default",
        },
        "summary": {
            "total": len(results),
            "passed": sum(result["status"] == "passed" for result in results),
            "failed": sum(result["status"] == "failed" for result in results),
            "acceptedStage0ThroughSlice4Regressions": sum(result["category"] != "apply" for result in results),
            "slice5Cases": sum(result["category"] == "apply" for result in results),
            "byCategory": dict(sorted(counts.items())),
        },
        "resultsDigest": result_digest,
        "results": results,
        "limitations": [
            "This is maintainer-run cumulative local Slice 5 evidence, not independent validation or complete family certification.",
            "Node.js and PowerShell adapters do not exist yet.",
            "The required macOS, Linux, Windows, case-sensitive, and case-insensitive release matrix is incomplete.",
            "Cross-adapter recovery, the complete release environment matrix, independent evaluation, freeze acceptance, and runtime activation remain unavailable."
        ]
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stem = f"candidate-revision-{candidate_revision}-local"
    json_path = evidence_dir / f"{stem}.json"
    markdown_path = evidence_dir / f"{stem}.md"
    if json_path.exists() or markdown_path.exists():
        raise CaseFailure(f"evidence target already exists: {json_path} or {markdown_path}")
    json_raw = pretty(report)
    lines = [
        f"# Wayfinder cumulative Stage 0 through Slice 5 candidate revision {candidate_revision} local evidence",
        "",
        "- **Status:** Passing local evidence; not full adapter certification",
        f"- **Generated:** {report['generatedAt']}",
        f"- **Release:** `{release['releaseId']}`",
        f"- **Contract SHA-256:** `{result_basis['contractSha256']}`",
        f"- **Adapter SHA-256:** `{result_basis['adapterSha256']}`",
        f"- **Fixture index SHA-256:** `{result_basis['casesSha256']}`",
        f"- **Results SHA-256:** `{result_digest}`",
        "",
        f"All {report['summary']['passed']} of {report['summary']['total']} cases passed.",
        "",
        "## Categories",
        "",
    ]
    lines.extend(f"- `{category}`: {count}" for category, count in sorted(counts.items()))
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", f"See `{stem}.json` for the per-case rule mapping and environment evidence.", ""])
    markdown_raw = "\n".join(lines).encode("utf-8")
    published: list[Path] = []
    try:
        for path, raw in ((json_path, json_raw), (markdown_path, markdown_raw)):
            with path.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            published.append(path)
    except Exception:
        for path in published:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    return json_path, markdown_path


def main(argv: list[str]) -> int:
    global DIFFERENTIAL_MODE, OBSERVATIONS
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--category", action="append", dest="categories")
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--differential-mode", action="store_true")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        print("conformance runner requires Python 3.11 or newer", file=sys.stderr)
        return 2
    maintainer_root = Path(__file__).resolve().parents[3]
    packaged_root = maintainer_root.parents[2] / "wayfinder" / "skills" / "wayfinder"
    configured_root = os.environ.get("WAYFINDER_SKILL_ROOT")
    skill_root = (
        Path(configured_root).expanduser()
        if configured_root
        else packaged_root if packaged_root.is_dir() else maintainer_root.parent / "wayfinder"
    ).resolve()
    adapter = (args.adapter or (skill_root / "scripts/adapters/wayfinder.py")).resolve()
    if args.observations is not None:
        if args.observations.exists() or args.observations.is_symlink():
            print(f"observation target already exists: {args.observations}", file=sys.stderr)
            return 2
        OBSERVATIONS = []
    DIFFERENTIAL_MODE = args.differential_mode
    if args.evidence_dir is not None and not args.write_evidence:
        print("--evidence-dir requires --write-evidence", file=sys.stderr)
        return 2
    if args.write_evidence and (args.case_ids or args.categories):
        print("filtered runs cannot write certification evidence", file=sys.stderr)
        return 2
    evidence_dir = (args.evidence_dir or (maintainer_root / "certification/v1")).resolve()
    cases_path = skill_root / CONFORMANCE_REL / "cases.json"
    suite = json.loads(cases_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    selected = suite["cases"]
    if args.categories:
        wanted_categories = set(args.categories)
        known_categories = {case["category"] for case in selected}
        missing_categories = sorted(wanted_categories - known_categories)
        if missing_categories:
            print(f"unknown categories: {', '.join(missing_categories)}", file=sys.stderr)
            return 2
        selected = [case for case in selected if case["category"] in wanted_categories]
    if args.case_ids:
        wanted = set(args.case_ids)
        selected = [case for case in selected if case["id"] in wanted]
        missing = sorted(wanted - {case["id"] for case in selected})
        if missing:
            print(f"unknown cases: {', '.join(missing)}", file=sys.stderr)
            return 2
    for case in selected:
        try:
            execute_case(skill_root, adapter, case)
            results.append({"id": case["id"], "category": case["category"], "rules": case["rules"], "status": "passed"})
            print(f"PASS {case['id']}")
        except Exception as exc:
            results.append({"id": case["id"], "category": case["category"], "rules": case["rules"], "status": "failed", "detail": str(exc)})
            print(f"FAIL {case['id']}: {exc}")
    failed = [result for result in results if result["status"] == "failed"]
    if args.observations is not None:
        args.observations.parent.mkdir(parents=True, exist_ok=True)
        with args.observations.open("xb") as handle:
            handle.write(pretty({"format": "wayfinder-local-observations", "schemaVersion": 1, "results": results, "invocations": OBSERVATIONS}))
    if args.write_evidence and not failed:
        json_path, markdown_path = write_evidence(skill_root, adapter, cases_path, results, evidence_dir)
        print(f"evidence-json={json_path}")
        print(f"evidence-markdown={markdown_path}")
    elif args.write_evidence:
        print("evidence=not-written-failed-suite")
    else:
        print("evidence=not-written")
    print(f"summary passed={len(results) - len(failed)} failed={len(failed)} total={len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
