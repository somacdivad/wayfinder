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


def parse_maintainer_result(stdout: str) -> dict[str, object] | None:
    for line in reversed(stdout.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("data"), dict):
            return value
    return None


def _workflow_escape(value: object) -> str:
    return str(value).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _markdown_cell(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def report_failures(result: dict[str, object] | None, entry_id: str) -> None:
    data = result.get("data", {}) if result else {}
    failures = data.get("failedCases", []) if isinstance(data, dict) else []
    failed_ids = data.get("failedCaseIds", []) if isinstance(data, dict) else []
    if not isinstance(failures, list):
        failures = []
    if not isinstance(failed_ids, list):
        failed_ids = []
    for item in failures:
        if not isinstance(item, dict):
            continue
        case_id = _workflow_escape(item.get("id", "unknown"))
        detail = _workflow_escape(item.get("detail", "no diagnostic supplied"))
        print(f"::error title=Wayfinder case {case_id}::{detail}")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [
        f"## Wayfinder matrix entry `{entry_id}`",
        "",
        f"- Result: `{'passed' if result and result.get('ok') is True else 'failed'}`",
        f"- Code: `{result.get('code', 'unavailable') if result else 'unavailable'}`",
        f"- Failed case IDs: {', '.join(f'`{_markdown_cell(item)}`' for item in failed_ids) if failed_ids else 'none'}",
        "",
    ]
    if failures:
        lines.extend(["| Case | Category | Rules | Diagnostic |", "| --- | --- | --- | --- |"])
        for item in failures:
            if not isinstance(item, dict):
                continue
            rules = ", ".join(str(rule) for rule in item.get("rules", []))
            lines.append(
                f"| `{_markdown_cell(item.get('id', 'unknown'))}` | {_markdown_cell(item.get('category', 'unknown'))} "
                f"| {_markdown_cell(rules)} | {_markdown_cell(item.get('detail', 'no diagnostic supplied'))} |"
            )
        truncated = data.get("failureDetailsTruncated", 0) if isinstance(data, dict) else 0
        if truncated:
            lines.extend(["", f"{truncated} additional diagnostics remain in the JSON report."])
        lines.append("")
    with Path(summary_path).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))


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
    result = parse_maintainer_result(completed.stdout)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    report_failures(result, args.id)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
