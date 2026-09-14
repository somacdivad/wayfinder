#!/usr/bin/env python3
"""Run direct, synthetic Slice 2 success, failure, and tamper demonstrations."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from run import invoke_inventory, ledger_source, make_source_tree, snapshot, source_request


def main() -> int:
    maintainer_root = Path(__file__).resolve().parents[3]
    packaged_root = maintainer_root.parents[2] / "wayfinder" / "skills" / "wayfinder"
    configured_root = os.environ.get("WAYFINDER_SKILL_ROOT")
    skill_root = (Path(configured_root).expanduser() if configured_root else packaged_root if packaged_root.is_dir() else maintainer_root.parent / "wayfinder").resolve()
    adapter = skill_root / "scripts/adapters/wayfinder.py"
    with tempfile.TemporaryDirectory(prefix="wayfinder-slice2-demo-") as raw:
        temporary = Path(raw)
        workspace = temporary / "workspace"
        workspace.mkdir()
        make_source_tree(workspace)

        valid_request = source_request(["sources/a.md", "sources/z.txt", "sources/nested/b.txt"])
        valid_process, valid = invoke_inventory(adapter, workspace, valid_request)
        if valid_process.returncode != 0 or not valid["ok"]:
            raise RuntimeError("valid inventory demonstration failed")

        invalid_request = source_request(["../escape"])
        invalid_process, invalid = invoke_inventory(adapter, workspace, invalid_request)
        if invalid_process.returncode != 2 or invalid["code"] != "path.traversal":
            raise RuntimeError("invalid inventory demonstration did not fail closed")

        inventory = valid["data"]["inventory"]
        indexed = {entry["path"]: entry for entry in inventory["entries"]}
        ledger = {
            "format": "wayfinder-intake-ledger",
            "schemaVersion": 1,
            "inventorySha256": valid["data"]["inventorySha256"],
            "sources": [ledger_source(indexed["sources/z.txt"], "reference")],
        }
        (workspace / "sources/z.txt").write_bytes(b"diff\n")
        before_recheck = snapshot(workspace)
        stale_process, stale = invoke_inventory(adapter, workspace, valid_request, ledger=ledger)
        after_recheck = snapshot(workspace)
        if stale_process.returncode != 3 or stale["code"] != "intake.source-stale":
            raise RuntimeError("source tampering demonstration did not report a stale source")
        if before_recheck != after_recheck:
            raise RuntimeError("read-only stale-source check changed the source tree")

        repeated_first, repeated_one = invoke_inventory(adapter, workspace, valid_request)
        repeated_second, repeated_two = invoke_inventory(adapter, workspace, valid_request)
        if repeated_first.stdout != repeated_second.stdout or repeated_one != repeated_two:
            raise RuntimeError("repeated inventory bytes differ")

        report = {
            "valid": {
                "exit": valid_process.returncode,
                "code": valid["code"],
                "entries": inventory["summary"]["entries"],
                "duplicateGroups": inventory["summary"]["duplicateGroups"],
            },
            "invalid": {"exit": invalid_process.returncode, "code": invalid["code"]},
            "tamperRecheck": {
                "exit": stale_process.returncode,
                "code": stale["code"],
                "sourceTreePreservedByCheck": before_recheck == after_recheck,
            },
            "deterministicRepeatedBytes": repeated_first.stdout == repeated_second.stdout,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
