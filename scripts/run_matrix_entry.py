#!/usr/bin/env python3
"""Run one exact matrix entry and preserve a non-certifying execution status."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAINTAIN = ROOT / "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--os-family", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(MAINTAIN), "matrix-entry", "--adapter", args.adapter, "--os-family", args.os_family, "--output", str(output)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    status = {
        "format": "wayfinder-matrix-execution-status",
        "schemaVersion": 1,
        "entryId": args.id,
        "adapterId": args.adapter,
        "operatingSystemFamily": args.os_family,
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sourceCommit": os.environ.get("GITHUB_SHA", "unavailable"),
        "workflowRunId": os.environ.get("GITHUB_RUN_ID", "unavailable"),
        "workflowRunAttempt": os.environ.get("GITHUB_RUN_ATTEMPT", "unavailable"),
        "exitCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    with (output / f"execution-{args.id}.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(status, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
