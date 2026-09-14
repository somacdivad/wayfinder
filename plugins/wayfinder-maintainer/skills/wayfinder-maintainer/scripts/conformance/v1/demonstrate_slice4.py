#!/usr/bin/env python3
"""Create a synthetic workspace and demonstrate Slice 4 planning."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    maintainer_root = Path(__file__).resolve().parents[3]
    packaged_root = maintainer_root.parents[2] / "wayfinder" / "skills" / "wayfinder"
    configured_root = os.environ.get("WAYFINDER_SKILL_ROOT")
    skill_root = (Path(configured_root).expanduser() if configured_root else packaged_root if packaged_root.is_dir() else maintainer_root.parent / "wayfinder").resolve()
    adapter = skill_root / "scripts/adapters/wayfinder.py"
    proposal = skill_root / "assets/contract-v1/conformance/v1/inputs/initialize-minimal.json"
    with tempfile.TemporaryDirectory(prefix="wayfinder-slice4-demo-") as raw:
        root = Path(raw)
        workspace = root / "workspace"
        ref = workspace / ".git/refs/heads/main"
        ref.parent.mkdir(parents=True)
        ref.write_text("1111111111111111111111111111111111111111\n", encoding="ascii", newline="\n")
        bundle = root / "bundle"
        completed = subprocess.run(
            [str(adapter), "initialize-plan", "--workspace-root", str(workspace), "--proposal", str(proposal), "--bundle-root", str(bundle)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result = json.loads(completed.stdout)
        plan_raw = (bundle / "plan.json").read_bytes() if bundle.exists() else b""
        preview_raw = (bundle / "preview.md").read_bytes() if bundle.exists() else b""
        normalized_plan = plan_raw.replace(str(workspace).encode("utf-8"), b"<WORKSPACE>")
        if plan_raw:
            normalized_plan = normalized_plan.replace(json.loads(plan_raw)["contractSha256"].encode("ascii"), b"<CONTRACT_SHA256>")
        if result.get("ok"):
            normalized_preview = preview_raw.replace(str(workspace).encode("utf-8"), b"<WORKSPACE>")
            normalized_preview = normalized_preview.replace(result["data"]["planSha256"].encode("ascii"), b"<PLAN_SHA256>")
            normalized_preview = normalized_preview.replace(result["data"]["operationId"].encode("ascii"), b"<OPERATION_ID>")
        else:
            normalized_preview = preview_raw
        summary = {
            "exit": completed.returncode,
            "code": result["code"],
            "planSha256": result.get("data", {}).get("planSha256"),
            "operationId": result.get("data", {}).get("operationId"),
            "targetTree": result.get("data", {}).get("targetTree"),
            "workspaceManifestExists": (workspace / ".wayfinder/manifest.json").exists(),
            "workspaceRecordExists": (workspace / "record").exists(),
            "bundleFiles": sorted(path.relative_to(bundle).as_posix() for path in bundle.rglob("*") if path.is_file()) if bundle.exists() else [],
            "golden": {
                "normalizedPlanSha256": hashlib.sha256(normalized_plan).hexdigest(),
                "normalizedPreviewSha256": hashlib.sha256(normalized_preview).hexdigest(),
                "payloadSha256": [hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((bundle / "payload").glob("*"))] if bundle.exists() else [],
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
