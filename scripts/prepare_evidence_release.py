#!/usr/bin/env python3
"""Verify an aggregate and create a digest manifest for a draft evidence release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-matrix-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    aggregates = []
    for path in args.input.rglob("matrix-revision-8-aggregate.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("format") == "wayfinder-certification-matrix-evidence":
            aggregates.append((path, payload))
    if len(aggregates) != 1:
        raise SystemExit(f"expected one aggregate report, found {len(aggregates)}")
    aggregate_path, aggregate = aggregates[0]
    if aggregate.get("matrixSha256") != args.expected_matrix_sha256:
        raise SystemExit("aggregate matrix digest differs from approved input")
    entries = aggregate.get("entries", [])
    if len(entries) != 8 or aggregate.get("status") != "passing-bounded-matrix-not-full-family-certification":
        raise SystemExit("aggregate is not a passing eight-entry bounded matrix")
    reports = []
    for path in args.input.rglob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("format") == "wayfinder-environment-certification-evidence":
            reports.append((path, payload))
    if len(reports) != 8:
        raise SystemExit(f"expected eight environment reports, found {len(reports)}")
    if any(report.get("executionProvenance", {}).get("sourceCommit") != args.expected_commit for _, report in reports):
        raise SystemExit("an environment report is not bound to the approved source commit")
    aggregate_entry_digests = {entry.get("sha256") for entry in entries}
    report_digests = {sha256(path) for path, _ in reports}
    if report_digests != aggregate_entry_digests:
        raise SystemExit("aggregate entry digests do not match the downloaded environment reports")
    evidence = sorted(path for path in args.input.rglob("*") if path.is_file())
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "format": "wayfinder-evidence-release-manifest",
        "schemaVersion": 1,
        "candidate": "v1-candidate-revision-8",
        "sourceCommit": args.expected_commit,
        "matrixSha256": args.expected_matrix_sha256,
        "aggregateReportSha256": sha256(aggregate_path),
        "files": [{"path": str(path.relative_to(args.input)), "sha256": sha256(path), "byteLength": path.stat().st_size} for path in evidence],
        "limitations": ["Bounded matrix only; not full-family certification.", "Does not authorize activation."],
    }
    manifest_path = args.output / "publication-manifest.json"
    with manifest_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    sums = [f"{sha256(path)}  {path.relative_to(args.input)}" for path in evidence]
    with (args.output / "SHA256SUMS").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(sums) + "\n")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
