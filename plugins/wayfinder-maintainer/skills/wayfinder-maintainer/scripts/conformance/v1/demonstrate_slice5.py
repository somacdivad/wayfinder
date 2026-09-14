#!/usr/bin/env python3
"""Run synthetic, temporary Slice 5 apply and recovery demonstrations."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from run import invoke_apply, invoke_recover, prepare_apply


CLOCK = {"WAYFINDER_TEST_MODE": "1", "WAYFINDER_TEST_CLOCK": "2026-09-13T12:34:56Z"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def apply_demo(skill_root: Path, adapter: Path, root: Path, source_assisted: bool) -> dict[str, object]:
    root.mkdir()
    workspace, bundle, digest, operation_id, _ = prepare_apply(skill_root, adapter, root, source_assisted=source_assisted)
    completed, result = invoke_apply(adapter, workspace, bundle, digest, env=CLOCK)
    require(completed.returncode == 0, completed.stderr.decode())
    receipt = json.loads((workspace / f".wayfinder/operations/{operation_id}/receipt.json").read_text())
    return {
        "mode": "source-assisted" if source_assisted else "fresh",
        "status": result["data"]["status"],
        "planSha256": digest,
        "operationId": operation_id,
        "manifestPresent": (workspace / ".wayfinder/manifest.json").is_file(),
        "receiptGates": [receipt["operationalIntegrity"]["status"], receipt["semanticReadiness"]["status"]],
        "nextWorkflow": receipt["nextWorkflow"],
    }


def interruption_demo(skill_root: Path, adapter: Path, root: Path, *, rollback: bool) -> dict[str, object]:
    root.mkdir()
    workspace, bundle, digest, operation_id, _ = prepare_apply(skill_root, adapter, root)
    boundary = "after-manifest-publication" if rollback else "after-file-0002"
    interrupted, interrupted_result = invoke_apply(adapter, workspace, bundle, digest, env={**CLOCK, "WAYFINDER_TEST_FAILURE_BOUNDARY": boundary})
    require(interrupted.returncode == 5, "failure injection did not interrupt")
    inspected, inspection = invoke_recover(adapter, workspace, operation_id, "inspect")
    require(inspected.returncode == 0, inspected.stderr.decode())
    action = "rollback" if rollback else "resume"
    recovered, recovery = invoke_recover(adapter, workspace, operation_id, action, env=CLOCK)
    require(recovered.returncode == 0, recovered.stderr.decode())
    return {
        "boundary": boundary,
        "interruptionCode": interrupted_result["code"],
        "inspection": inspection["data"]["status"],
        "action": action,
        "outcome": recovery["data"]["status"],
        "manifestPresent": (workspace / ".wayfinder/manifest.json").exists(),
    }


def manual_demo(skill_root: Path, adapter: Path, root: Path) -> dict[str, object]:
    root.mkdir()
    workspace, bundle, digest, operation_id, _ = prepare_apply(skill_root, adapter, root)
    interrupted, _ = invoke_apply(adapter, workspace, bundle, digest, env={**CLOCK, "WAYFINDER_TEST_FAILURE_BOUNDARY": "after-file-0002"})
    require(interrupted.returncode == 5, "manual recovery setup did not interrupt")
    changed = workspace / "record/plan-brief.md"
    changed.write_bytes(b"external owner change\n")
    inspected, inspection = invoke_recover(adapter, workspace, operation_id, "inspect")
    require(inspected.returncode == 0, inspected.stderr.decode())
    return {
        "status": inspection["data"]["status"],
        "preservedBytes": changed.read_text(),
        "issueCodes": [item["code"] for item in inspection["data"]["issues"]],
    }


def main() -> int:
    if sys.version_info < (3, 11):
        print("demonstration requires Python 3.11 or newer", file=sys.stderr)
        return 2
    maintainer_root = Path(__file__).resolve().parents[3]
    packaged_root = maintainer_root.parents[2] / "wayfinder" / "skills" / "wayfinder"
    configured_root = os.environ.get("WAYFINDER_SKILL_ROOT")
    skill_root = (Path(configured_root).expanduser() if configured_root else packaged_root if packaged_root.is_dir() else maintainer_root.parent / "wayfinder").resolve()
    adapter = skill_root / "scripts/adapters/wayfinder.py"
    with tempfile.TemporaryDirectory(prefix="wayfinder-slice5-demo-") as raw:
        root = Path(raw)
        report = {
            "format": "wayfinder-slice5-demonstration",
            "schemaVersion": 1,
            "fresh": apply_demo(skill_root, adapter, root / "fresh", False),
            "sourceAssisted": apply_demo(skill_root, adapter, root / "source", True),
            "resume": interruption_demo(skill_root, adapter, root / "resume", rollback=False),
            "rollback": interruption_demo(skill_root, adapter, root / "rollback", rollback=True),
            "manualRecovery": manual_demo(skill_root, adapter, root / "manual"),
        }
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
