#!/usr/bin/env python3
"""Verify the exact revision-10 evidence set and prepare a draft-release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any


CANDIDATE = "v1-candidate-revision-10"
SOURCE_COMMIT = "82a2bb994e7ef8d2ffda7317e0687b0c7230aa54"
RUN_ID = "34921918384"
RUN_ATTEMPT = "1"
MATRIX_SHA256 = "2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0"
AGGREGATE_JSON = "matrix-revision-10-aggregate.json"
AGGREGATE_MARKDOWN = "matrix-revision-10-aggregate.md"
EXPECTED_PACKAGE = {
    "releaseId": CANDIDATE,
    "releaseSha256": "581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083",
    "contractVersion": 1,
    "contractSha256": "0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341",
    "fixtureIndexSha256": "a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6",
    "expectedOutputsSha256": "9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94",
}
EXPECTED_ADAPTERS = {
    "python-reference-v1": "e0b89ba35f223567efe2545d323d816dbaeeedfa8de8fb784fcc7b1c347cb596",
    "node-v1": "f6d695e60e5964448947ed9f835526efa0f84e3764fb8acdd7f765e3bbe4fa3e",
    "powershell-v1": "b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9",
}
EXPECTED_FILES = {
    "artifact-inventory.json": "a476bc3fccc0f4ead98f2ada1b9e3589d09ec59a4a2d34a118e0478f08ed009e",
    "execution-node-linux.json": "83f0c6adb8b80aa69122560635225b96e3ceeca2c99e97d477794873632a6485",
    "execution-node-macos.json": "3fcb9201a9111f3d3518396effd459606cba5e5900b83898b16c6c2f0ce8bde7",
    "execution-node-windows.json": "d2594c8965483995aad75c795f5f3a9acc64f2e58d00ba328762baf0c5ade9d0",
    "execution-powershell-linux.json": "d151ca2d2836b80a07918875b171814953b5a59d2f0103a28bb80a363490f85c",
    "execution-powershell-windows.json": "860f4a326596ec2e7f43a96d5b654fc164e38346e97dbf107486cc4a2e6904a7",
    "execution-python-linux.json": "b2ec0971aca62337e2f1bdff91bdeb2f4fe1f5b671afb7ce59ffeb9bc0d73ffc",
    "execution-python-macos.json": "659fd97473512cdb4927349783a8bc626ea1fe5f22f3d38eb540923b90f3c7f2",
    "execution-python-windows.json": "a5ec00dc5055a95c4048763dce94d08e76f001932e5e98c6647d889c1b15fd8d",
    AGGREGATE_JSON: "be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50",
    AGGREGATE_MARKDOWN: "ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18",
    "matrix-revision-10-node-v1-linux-20260915T023856Z.json": "96d41381d0ad5b46cb877523ab6743e85288e571133153b5df86898952147cf4",
    "matrix-revision-10-node-v1-linux-20260915T023856Z.md": "9cf0c46fd435d1feee6d9bdd7116484bad472cf9676dd1b3d5a07f871fd563a6",
    "matrix-revision-10-node-v1-macos-20260915T024109Z.json": "60528f64e878d9a11054b9457a3bf0e578139abec27c41633a7e69e7d57e589e",
    "matrix-revision-10-node-v1-macos-20260915T024109Z.md": "1888a82b8d9bbc6edfc9adafdf1a3b38ec2c34dbc9655fa65ab7b8461ee34f5f",
    "matrix-revision-10-node-v1-windows-20260915T024008Z.json": "0378ac26624fe8f0da50946af03f3332e4603ca6d9f172be984cd82060d50490",
    "matrix-revision-10-node-v1-windows-20260915T024008Z.md": "411feb98c44d9aaadbeab31dcb6450ac1d89389f059e3c0d65fa98bed123e1ba",
    "matrix-revision-10-powershell-v1-linux-20260915T030009Z.json": "448e55a4eb78d1c36b39fe512ff8a06df52714a8f84a712d0e177b1e653913c7",
    "matrix-revision-10-powershell-v1-linux-20260915T030009Z.md": "3aab4c3bfcc09aabb9157540d757dee88e564a8e92c1f3c17adba8ac81c5dc0d",
    "matrix-revision-10-powershell-v1-windows-20260915T030016Z.json": "9bdcd2a7c38da06f41f6b6a929454b9a0d52ec1c0d165a4f1f4e5b7065dfe418",
    "matrix-revision-10-powershell-v1-windows-20260915T030016Z.md": "dc57228ee31837474e6f58d352f5ec858588e1a4d70dc11485829df32c875dfe",
    "matrix-revision-10-python-reference-v1-linux-20260915T024310Z.json": "93f1d5d274d220310446d827aa15c2a6236086dc8299050f61531e96631fd15c",
    "matrix-revision-10-python-reference-v1-linux-20260915T024310Z.md": "b52f200c68ef2f95589d3a7be401cd64362ba1627fc8a63f2d449126d6b69a02",
    "matrix-revision-10-python-reference-v1-macos-20260915T024554Z.json": "fc6a9c11fad47699474cf83cc6aa4ceb05ce5d3632712ae7108c9a5cf2744584",
    "matrix-revision-10-python-reference-v1-macos-20260915T024554Z.md": "9bc38eb6516f493a48023606d3b003d83562ae3837f8883101b730de39ffd880",
    "matrix-revision-10-python-reference-v1-windows-20260915T024659Z.json": "1fe12a77ebf5c6c1e2ae7f1161f80685473924503fcb210af0d6cb7d0f806e1d",
    "matrix-revision-10-python-reference-v1-windows-20260915T024659Z.md": "72c73942a28332450522527714feef71b1e36a88d733b604921ea988cc3affa0",
}
ENTRIES = {
    "node-linux": ("execution-node-linux.json", "matrix-revision-10-node-v1-linux-20260915T023856Z.json", "matrix-revision-10-node-v1-linux-20260915T023856Z.md", "node-v1", "Linux", "node-v1:Node.js-24.21.0:Linux"),
    "node-macos": ("execution-node-macos.json", "matrix-revision-10-node-v1-macos-20260915T024109Z.json", "matrix-revision-10-node-v1-macos-20260915T024109Z.md", "node-v1", "macOS", "node-v1:Node.js-24.21.0:macOS"),
    "node-windows": ("execution-node-windows.json", "matrix-revision-10-node-v1-windows-20260915T024008Z.json", "matrix-revision-10-node-v1-windows-20260915T024008Z.md", "node-v1", "Windows", "node-v1:Node.js-24.21.0:Windows"),
    "powershell-linux": ("execution-powershell-linux.json", "matrix-revision-10-powershell-v1-linux-20260915T030009Z.json", "matrix-revision-10-powershell-v1-linux-20260915T030009Z.md", "powershell-v1", "Linux", "powershell-v1:PowerShell-7.6.6:Linux"),
    "powershell-windows": ("execution-powershell-windows.json", "matrix-revision-10-powershell-v1-windows-20260915T030016Z.json", "matrix-revision-10-powershell-v1-windows-20260915T030016Z.md", "powershell-v1", "Windows", "powershell-v1:PowerShell-7.6.6:Windows"),
    "python-linux": ("execution-python-linux.json", "matrix-revision-10-python-reference-v1-linux-20260915T024310Z.json", "matrix-revision-10-python-reference-v1-linux-20260915T024310Z.md", "python-reference-v1", "Linux", "python-reference-v1:CPython-3.14.7:Linux"),
    "python-macos": ("execution-python-macos.json", "matrix-revision-10-python-reference-v1-macos-20260915T024554Z.json", "matrix-revision-10-python-reference-v1-macos-20260915T024554Z.md", "python-reference-v1", "macOS", "python-reference-v1:CPython-3.14.7:macOS"),
    "python-windows": ("execution-python-windows.json", "matrix-revision-10-python-reference-v1-windows-20260915T024659Z.json", "matrix-revision-10-python-reference-v1-windows-20260915T024659Z.md", "python-reference-v1", "Windows", "python-reference-v1:CPython-3.14.7:Windows"),
}


def strict_json_bytes(raw: bytes, label: str) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON member {key!r} in {label}")
            result[key] = value
        return result

    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def recorded_basename(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.endswith(("/", "\\")):
        raise ValueError(f"{label} is missing or malformed")
    name = value.replace("\\", "/").rsplit("/", 1)[-1]
    if name in {"", ".", ".."}:
        raise ValueError(f"{label} is missing or malformed")
    return name


def verified_files(root: Path) -> dict[str, bytes]:
    try:
        root_stat = root.lstat()
    except FileNotFoundError as exc:
        raise ValueError("input directory is missing") from exc
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise ValueError("input must be a real, non-symlinked directory")
    entries = list(os.scandir(root))
    unsafe = sorted(entry.name for entry in entries if entry.is_symlink() or not entry.is_file(follow_symlinks=False))
    if unsafe:
        raise ValueError(f"input contains ambiguous, symlinked, or non-file paths: {', '.join(unsafe)}")
    actual = {entry.name for entry in entries}
    missing = sorted(set(EXPECTED_FILES) - actual)
    extra = sorted(actual - set(EXPECTED_FILES))
    if missing or extra:
        raise ValueError(f"evidence membership differs; missing={missing}; extra={extra}")
    verified: dict[str, bytes] = {}
    for name, expected_digest in EXPECTED_FILES.items():
        path = root / name
        before = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"evidence file is not regular: {name}")
        raw = path.read_bytes()
        after = path.stat(follow_symlinks=False)
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after:
            raise ValueError(f"evidence file changed during verification: {name}")
        actual_digest = hashlib.sha256(raw).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(f"evidence digest differs for {name}")
        verified[name] = raw
    return verified


def verify_bindings(files: dict[str, bytes], expected_commit: str, expected_run_id: str, expected_attempt: str, expected_matrix: str) -> None:
    if (expected_commit, expected_run_id, expected_attempt, expected_matrix) != (SOURCE_COMMIT, RUN_ID, RUN_ATTEMPT, MATRIX_SHA256):
        raise ValueError("requested publication identity is not the approved revision-10 source/run/attempt/matrix")
    reports: dict[str, dict[str, Any]] = {}
    for entry_id, (execution_name, json_name, markdown_name, adapter_id, os_family, target_id) in ENTRIES.items():
        execution = strict_json_bytes(files[execution_name], execution_name)
        required_execution = {
            "format": "wayfinder-matrix-execution-status", "schemaVersion": 1, "entryId": entry_id,
            "adapterId": adapter_id, "operatingSystemFamily": os_family, "sourceCommit": expected_commit,
            "workflowRunId": expected_run_id, "workflowRunAttempt": expected_attempt, "exitCode": 0, "stderr": "",
        }
        if any(execution.get(key) != value for key, value in required_execution.items()):
            raise ValueError(f"execution binding differs for {execution_name}")
        command = strict_json_bytes(execution.get("stdout", "").encode("utf-8"), f"{execution_name} stdout")
        data = command.get("data", {})
        if command.get("ok") is not True or command.get("code") != "ok":
            raise ValueError(f"execution did not record success: {execution_name}")
        if recorded_basename(data.get("json"), f"{execution_name} JSON report") != json_name:
            raise ValueError(f"execution JSON report path differs for {execution_name}")
        if recorded_basename(data.get("markdown"), f"{execution_name} Markdown report") != markdown_name:
            raise ValueError(f"execution Markdown report path differs for {execution_name}")
        if data.get("jsonSha256") != EXPECTED_FILES[json_name] or data.get("markdownSha256") != EXPECTED_FILES[markdown_name]:
            raise ValueError(f"execution report digest binding differs for {execution_name}")
        if data.get("target") != target_id or data.get("status") != "passing-environment-entry-not-full-family-certification":
            raise ValueError(f"execution target or status differs for {execution_name}")
        summary = data.get("summary", {})
        if summary.get("total") != 305 or summary.get("passed") != 305 or summary.get("failed") != 0:
            raise ValueError(f"execution summary differs for {execution_name}")
        report = strict_json_bytes(files[json_name], json_name)
        provenance = report.get("executionProvenance", {})
        target = report.get("target", {})
        if report.get("format") != "wayfinder-environment-certification-evidence" or report.get("scope") != "bounded-certification-matrix-candidate-revision-10":
            raise ValueError(f"report identity differs for {json_name}")
        if provenance.get("sourceCommit") != expected_commit or provenance.get("workflowRunId") != expected_run_id or provenance.get("workflowRunAttempt") != expected_attempt:
            raise ValueError(f"report provenance differs for {json_name}")
        if target.get("adapterId") != adapter_id or target.get("operatingSystemFamily") != os_family:
            raise ValueError(f"report target differs for {json_name}")
        if report.get("package", {}).get("releaseId") != CANDIDATE or report.get("status") != "passing-environment-entry-not-full-family-certification":
            raise ValueError(f"report candidate or status differs for {json_name}")
        if report.get("summary", {}).get("total") != 305 or report.get("summary", {}).get("passed") != 305 or report.get("summary", {}).get("failed") != 0:
            raise ValueError(f"report summary differs for {json_name}")
        reports[target_id] = report

    aggregate = strict_json_bytes(files[AGGREGATE_JSON], AGGREGATE_JSON)
    if aggregate.get("format") != "wayfinder-certification-matrix-evidence" or aggregate.get("scope") != "bounded-certification-matrix-candidate-revision-10":
        raise ValueError("aggregate identity differs")
    if aggregate.get("status") != "passing-bounded-matrix-not-full-family-certification" or aggregate.get("package") != EXPECTED_PACKAGE or aggregate.get("adapters") != EXPECTED_ADAPTERS:
        raise ValueError("aggregate status or package bindings differ")
    aggregate_entries = aggregate.get("entries")
    if not isinstance(aggregate_entries, list) or len(aggregate_entries) != 8:
        raise ValueError("aggregate does not contain exactly eight entries")
    by_target = {entry.get("target"): entry for entry in aggregate_entries if isinstance(entry, dict)}
    if set(by_target) != set(reports):
        raise ValueError("aggregate target membership differs")
    for target_id, report in reports.items():
        entry = by_target[target_id]
        json_name = next(values[1] for values in ENTRIES.values() if values[5] == target_id)
        if recorded_basename(entry.get("path"), f"aggregate path for {target_id}") != json_name:
            raise ValueError(f"aggregate report path differs for {target_id}")
        if entry.get("sha256") != EXPECTED_FILES[json_name] or entry.get("resultSetSha256") != report.get("resultSetSha256"):
            raise ValueError(f"aggregate report binding differs for {target_id}")
    computed_matrix = canonical_sha256({"package": EXPECTED_PACKAGE, "adapters": EXPECTED_ADAPTERS, "entries": aggregate_entries})
    if aggregate.get("matrixSha256") != expected_matrix or computed_matrix != expected_matrix:
        raise ValueError("aggregate matrix digest differs from approved input or recomputation")

    inventory = strict_json_bytes(files["artifact-inventory.json"], "artifact-inventory.json")
    if inventory.get("format") != "wayfinder-matrix-artifact-inventory" or inventory.get("schemaVersion") != 1:
        raise ValueError("artifact inventory identity differs")
    passing = {recorded_basename(path, "inventory passing report") for path in inventory.get("passingEvidenceReports", [])}
    expected_reports = {values[1] for values in ENTRIES.values()}
    if passing != expected_reports:
        raise ValueError("artifact inventory passing-report membership differs")
    statuses = inventory.get("executionStatuses")
    if not isinstance(statuses, list) or len(statuses) != 8:
        raise ValueError("artifact inventory does not contain exactly eight execution statuses")
    observed_statuses = {(item.get("entryId"), recorded_basename(item.get("path"), "inventory execution status"), item.get("exitCode")) for item in statuses if isinstance(item, dict)}
    expected_statuses = {(entry_id, values[0], 0) for entry_id, values in ENTRIES.items()}
    if observed_statuses != expected_statuses:
        raise ValueError("artifact inventory execution-status bindings differ")
    aggregate_command = strict_json_bytes(inventory.get("aggregateStdout", "").encode("utf-8"), "artifact inventory aggregate stdout")
    aggregate_data = aggregate_command.get("data", {})
    aggregate_binding = (
        aggregate_command.get("ok") is True
        and aggregate_command.get("code") == "ok"
        and recorded_basename(aggregate_data.get("json"), "inventory aggregate JSON") == AGGREGATE_JSON
        and recorded_basename(aggregate_data.get("markdown"), "inventory aggregate Markdown") == AGGREGATE_MARKDOWN
        and aggregate_data.get("jsonSha256") == EXPECTED_FILES[AGGREGATE_JSON]
        and aggregate_data.get("markdownSha256") == EXPECTED_FILES[AGGREGATE_MARKDOWN]
        and aggregate_data.get("matrixSha256") == expected_matrix
        and inventory.get("aggregateExitCode") == 0
        and inventory.get("aggregateStderr") == ""
        and inventory.get("matrixComplete") is True
    )
    if not aggregate_binding:
        raise ValueError("artifact inventory aggregate binding differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-attempt", required=True)
    parser.add_argument("--expected-matrix-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("output path already exists")
    try:
        files = verified_files(args.input)
        verify_bindings(files, args.expected_commit, args.expected_run_id, args.expected_attempt, args.expected_matrix_sha256)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    report = {
        "format": "wayfinder-evidence-release-manifest",
        "schemaVersion": 1,
        "candidate": CANDIDATE,
        "sourceCommit": args.expected_commit,
        "workflowRunId": args.expected_run_id,
        "workflowRunAttempt": args.expected_attempt,
        "matrixSha256": args.expected_matrix_sha256,
        "aggregateReportSha256": EXPECTED_FILES[AGGREGATE_JSON],
        "artifactInventorySha256": EXPECTED_FILES["artifact-inventory.json"],
        "files": [{"path": name, "sha256": EXPECTED_FILES[name], "byteLength": len(files[name])} for name in sorted(files)],
        "limitations": [
            "Exact maintainer-run bounded eight-entry matrix evidence only; not independent evaluation or full-family certification.",
            "Does not add release certification entries, change runtime guidance, or authorize activation.",
        ],
    }
    args.output.mkdir(parents=False)
    manifest_path = args.output / "publication-manifest.json"
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    sums = [f"{EXPECTED_FILES[name]}  {name}" for name in sorted(files)]
    (args.output / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8", newline="\n")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
