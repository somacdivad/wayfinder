#!/usr/bin/env python3
"""Inventory downloaded entry artifacts and invoke the strict matrix aggregator."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAINTAIN = ROOT / "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reports = []
    statuses = []
    for path in sorted(args.input.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("format") == "wayfinder-environment-certification-evidence":
            reports.append(path)
        elif payload.get("format") == "wayfinder-matrix-execution-status":
            statuses.append({"path": str(path), "entryId": payload.get("entryId"), "exitCode": payload.get("exitCode")})
    args.output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(MAINTAIN), "matrix-aggregate"]
    for path in reports:
        command.extend(["--entry", str(path)])
    command.extend(["--output", str(args.output)])
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    inventory = {
        "format": "wayfinder-matrix-artifact-inventory",
        "schemaVersion": 1,
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "passingEvidenceReports": [str(path) for path in reports],
        "executionStatuses": statuses,
        "aggregateExitCode": completed.returncode,
        "aggregateStdout": completed.stdout,
        "aggregateStderr": completed.stderr,
        "matrixComplete": completed.returncode == 0,
    }
    (args.output / "artifact-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
