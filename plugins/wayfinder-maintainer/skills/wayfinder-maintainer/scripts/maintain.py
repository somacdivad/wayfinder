#!/usr/bin/env python3
"""Dependency-free maintainer entry point for the Wayfinder candidate."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import json
import locale
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


COMPANION_ROOT = Path(__file__).resolve().parents[1]
PACKAGED_SKILL_ROOT = COMPANION_ROOT.parents[2] / "wayfinder" / "skills" / "wayfinder"
LEGACY_SKILL_ROOT = COMPANION_ROOT.parent / "wayfinder"
SKILL_ROOT = Path(
    os.environ.get(
        "WAYFINDER_SKILL_ROOT",
        str(PACKAGED_SKILL_ROOT if PACKAGED_SKILL_ROOT.is_dir() else LEGACY_SKILL_ROOT),
    )
).expanduser().resolve()
REPOSITORY_ROOT = Path(
    os.environ.get(
        "WAYFINDER_REPOSITORY_ROOT",
        str(COMPANION_ROOT.parents[3] if PACKAGED_SKILL_ROOT.is_dir() else COMPANION_ROOT.parents[1]),
    )
).expanduser().resolve()
CONFORMANCE_ROOT = SKILL_ROOT / "assets/contract-v1/conformance/v1"
CONFORMANCE_RUNNER = COMPANION_ROOT / "scripts/conformance/v1/run.py"
PACKAGE_BUILDER = COMPANION_ROOT / "scripts/conformance/v1/build_package.py"
CERTIFICATION_ROOT = COMPANION_ROOT / "certification/v1"
HISTORICAL_HASHES = CERTIFICATION_ROOT / "historical-sha256.json"
CURRENT_STATE_PATH = COMPANION_ROOT / "references/current-state.md"
TEXT_SUFFIXES = {".abnf", ".json", ".md", ".mjs", ".ps1", ".py", ".yaml", ".yml"}
RELEASE_ID_PATTERN = r"^v1-candidate-revision-[1-9][0-9]*$"
RELEASE_STATUS = "unactivated-frozen"
CONTRACT_STATUS = "frozen"
MATRIX_TARGETS = (
    ("python-reference-v1", "CPython", "3.14.7", "macOS"),
    ("python-reference-v1", "CPython", "3.14.7", "Linux"),
    ("python-reference-v1", "CPython", "3.14.7", "Windows"),
    ("node-v1", "Node.js", "24.21.0", "macOS"),
    ("node-v1", "Node.js", "24.21.0", "Linux"),
    ("node-v1", "Node.js", "24.21.0", "Windows"),
    ("powershell-v1", "PowerShell", "7.6.6", "Windows"),
    ("powershell-v1", "PowerShell", "7.6.6", "Linux"),
)
ACCEPTED_MATRIX_BINDINGS = {
    "releaseId": "v1-candidate-revision-9",
    "releaseSha256": "1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb",
    "contractVersion": 1,
    "contractSha256": "3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9",
    "fixtureIndexSha256": "a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6",
    "expectedOutputsSha256": "9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94",
}
ACCEPTED_ADAPTER_DIGESTS = {
    "python-reference-v1": "f8fe1a0987a37e8a9a43003ede1bcb9eda590c88511daebaafcdd5d13932337a",
    "node-v1": "df0f3c2a000454b2f7aaa8fcf6762b670aab34b9cb721da571fe334ae29f10ac",
    "powershell-v1": "b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9",
}
ACCEPTED_PARITY_EVIDENCE_DIGESTS = {
    "parity-revision-8-local.json": "28bc61ede21e0b8041c1951b1327c948642d0712170048f17ce2bab9653562ef",
    "parity-revision-8-local.md": "840641fd2b2814104a78f7fe0d4106ac70c4688056237003770d7ec7874e97c0",
}
ACCEPTED_MATRIX_EVIDENCE_DIGESTS = {
    "matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json": "6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78",
    "matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md": "8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c",
}
CURRENT_LOCAL_EVIDENCE_DIGESTS = {
    "candidate-revision-9-local.json": "b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a",
    "candidate-revision-9-local.md": "99a5ef242b1e96e966d1fe9cff3549565008520451921bc1e9d7abfc3237d264",
    "parity-revision-9-local.json": "3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c",
    "parity-revision-9-local.md": "11f3f7436b96c2be98e5efeb8fb2fb29bb373ba8826ea38b0594aeba806c00f5",
    "proposed-freeze-revision-9.json": "9baf19c1f17848b7f0b1b12ff0e821472358f2aadde3dafa4f423194cb5e916c",
    "proposed-freeze-revision-9.md": "b75d8862b47a16b13c4862643e7551d44777c98348cd9608f5c5aebd1ff8855f",
    "freeze-acceptance-revision-9.json": "a934affb933fac7ad994257453afda952b6e81d7852e791f60389ebce4767088",
    "freeze-acceptance-revision-9.md": "2f0c4bb8859bb3f7f0356038922678673544ddf45907bcdb680670813a581691",
}
RUNTIME_REQUIREMENTS = {
    "python-reference-v1": ("CPython", "3.14.7", "none; invoke maintain.py with the selected interpreter"),
    "node-v1": ("Node.js", "24.21.0", "WAYFINDER_NODE_RUNTIME"),
    "powershell-v1": ("PowerShell", "7.6.6", "WAYFINDER_POWERSHELL_RUNTIME"),
}
CURRENT_APPROVAL_BOUNDARY = (
    "The owner accepted the exact candidate-revision-9 maintainer-only Windows correction and separately authorized a full "
    "eight-entry hosted rerun. Acceptance preserves all frozen governed, registered-adapter, and accepted-evidence bytes and "
    "does not itself certify Windows or the adapter family, promote evidence, add a release-certification entry, activate "
    "Wayfinder, begin forward testing or cross-adapter recovery, add runtime guidance, or initialize a live project. Hosted "
    "execution must use one exact published source commit. The owner subsequently clarified that the authorized publication "
    "scope is every modified and untracked path present in the candidate-revision-9 certification worktree at the start of "
    "the hosted tranche."
)
CURRENT_PENDING_ACTION = (
    "Publish the complete owner-authorized dirty worktree as one exact commit on candidate-revision-9-certification, dispatch "
    "the full eight-entry hosted rerun from that commit, preserve outputs as review-only, and report the strict aggregate."
)
FREEZE_ACCEPTANCE_AUTHORIZATION = (
    "Accept the exact revision-9 frozen bytes and local candidate and parity evidence. "
    "Hosted certification and every later tranche require separate explicit authorization."
)
FREEZE_ACCEPTANCE_BOUNDARIES = {
    "hostedCertification": "not-authorized",
    "evidencePublication": "not-authorized",
    "releaseCertificationEntry": "not-authorized",
    "fullFamilyCertification": "incomplete",
    "runtimeActivation": "disabled",
    "liveProjectWork": "not-authorized",
    "gitCommitOrPush": "not-authorized",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON member {key!r} in {path}")
            result[key] = value
        return result

    return json.loads(path.read_bytes().decode("utf-8", "strict"), object_pairs_hook=pairs)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def expected_outputs_sha256(contract: dict[str, Any]) -> str:
    outputs = [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in contract["governedResources"]
        if item["role"] == "fixture-expected"
    ]
    return canonical_sha256(outputs)


def _relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT)) if path.is_relative_to(REPOSITORY_ROOT) else str(path)


def current_context() -> dict[str, Any]:
    contract_path = SKILL_ROOT / "assets/contract-v1/contract.json"
    release_path = SKILL_ROOT / "assets/contract-v1/release.json"
    cases_path = CONFORMANCE_ROOT / "cases.json"
    contract = load_json(contract_path)
    release = load_json(release_path)
    cases = load_json(cases_path)["cases"]
    counts = Counter(case["category"] for case in cases)
    registry = []
    for adapter in release["adapters"]:
        implementation, version, override = RUNTIME_REQUIREMENTS[adapter["id"]]
        registry.append({
            "id": adapter["id"],
            "path": adapter["path"],
            "sha256": adapter["sha256"],
            "runtime": {"implementation": implementation, "requiredVersion": version, "overrideVariable": override},
        })
    return {
        "format": "wayfinder-maintainer-context",
        "schemaVersion": 1,
        "candidate": {
            "releaseId": release["releaseId"],
            "candidateRevision": contract["candidateRevision"],
            "contractStatus": contract["status"],
            "releaseStatus": release["status"],
            "activation": "disabled",
        },
        "bindings": {
            **ACCEPTED_MATRIX_BINDINGS,
            "adapters": ACCEPTED_ADAPTER_DIGESTS,
            "acceptedParityEvidence": ACCEPTED_PARITY_EVIDENCE_DIGESTS,
            "acceptedMatrixEvidence": ACCEPTED_MATRIX_EVIDENCE_DIGESTS,
            "currentLocalEvidence": CURRENT_LOCAL_EVIDENCE_DIGESTS,
            "historicalEvidenceIndex": _relative(HISTORICAL_HASHES),
        },
        "conformance": {"caseCount": len(cases), "byCategory": dict(sorted(counts.items()))},
        "adapterRegistry": registry,
        "paths": {
            "repositoryRoot": str(REPOSITORY_ROOT),
            "runtimeSkillRoot": str(SKILL_ROOT),
            "maintainerSkillRoot": str(COMPANION_ROOT),
            "maintainerCommand": str(Path(__file__).resolve()),
            "conformanceRunner": str(CONFORMANCE_RUNNER),
            "designRecord": str(COMPANION_ROOT / "references/design-record.md"),
            "workflow": str(COMPANION_ROOT / "references/workflow.md"),
            "certificationRoot": str(CERTIFICATION_ROOT),
        },
        "approvalBoundary": CURRENT_APPROVAL_BOUNDARY,
        "pendingAction": CURRENT_PENDING_ACTION,
    }


def current_state_markdown() -> str:
    context = current_context()
    candidate = context["candidate"]
    bindings = context["bindings"]
    adapters = context["adapterRegistry"]
    adapter_text = ", ".join(f"`{item['id']}` `{item['sha256']}`" for item in adapters)
    parity_text = ", ".join(
        f"`{name}` `{digest}`" for name, digest in sorted(bindings["acceptedParityEvidence"].items())
    )
    matrix_text = ", ".join(
        f"`{name}` `{digest}`" for name, digest in sorted(bindings["acceptedMatrixEvidence"].items())
    )
    local_text = ", ".join(
        f"`{name}` `{digest}`" for name, digest in sorted(bindings["currentLocalEvidence"].items())
    )
    lines = [
        "# Wayfinder current maintainer state",
        "",
        "> Compact routing reference. `maintain.py doctor` validates these facts against the package, accepted evidence, and chronological record.",
        "",
        "## Current identity",
        "",
        f"- Candidate: `{candidate['releaseId']}` (contract `{candidate['contractStatus']}`, release `{candidate['releaseStatus']}`).",
        "- Activation: **disabled**. The runtime skill remains non-operational.",
        f"- Contract: `{bindings['contractSha256']}`.",
        f"- Release: `{bindings['releaseSha256']}`.",
        f"- Fixture index: `{bindings['fixtureIndexSha256']}`; expected-output set: `{bindings['expectedOutputsSha256']}`.",
        f"- Registered adapters: {adapter_text}.",
        f"- Historical revision-8 accepted parity evidence: {parity_text}.",
        f"- Historical revision-8 accepted macOS matrix evidence: {matrix_text}.",
        f"- Accepted revision-9 local evidence, proposal, and freeze acceptance: {local_text}.",
        f"- Accepted historical evidence is hash-pinned by [`historical-sha256.json`](../certification/v1/historical-sha256.json).",
        "",
        "## Approval boundary",
        "",
        CURRENT_APPROVAL_BOUNDARY,
        "",
        "## Pending action and design-record routes",
        "",
        CURRENT_PENDING_ACTION,
        "",
        "Read only the relevant exact section of the [chronological design record](design-record.md):",
        "",
        "- `## Candidate revision 8 freeze — accepted` for frozen identity and invalidation rules.",
        "- `## Candidate revision 8 adapter parity — accepted` for adapter and parity authority.",
        "- `## Candidate revision 8 bounded certification matrix — accepted` for matrix requirements.",
        "- `## Candidate revision 8 hosted certification execution — accepted with failed aggregate` for hosted evidence bindings.",
        "- `## Candidate revision 8 Windows certification investigation and correction — accepted` for current blockers.",
        "- `## Candidate revision 8 maintainer-efficiency tranche — accepted` for the current maintainer workflow and tooling baseline.",
        "- `## Candidate revision 9 Windows corrections — accepted` for the current implementation and approval boundary.",
        "- `## Candidate revision 9 hosted certification execution — accepted with failed aggregate` for the accepted bounded hosted result.",
        "- `## Candidate revision 9 maintainer reliability and efficiency — accepted` for the accepted maintainer-only tranche.",
        "- `## Candidate revision 9 Windows failure investigation — accepted` for the active correction authority and unresolved hosted obligations.",
        "- `## Candidate revision 9 maintainer-only Windows correction — accepted` for the accepted correction and authorized hosted-rerun boundary.",
        "",
        "Read the full record before reopening a decision, changing evidence governance, or recording an accepted outcome.",
        "",
    ]
    return "\n".join(lines)


def describe_command(output_format: str) -> int:
    context = current_context()
    if output_format == "json":
        print(json.dumps(context, sort_keys=True, separators=(",", ":")))
        return 0
    candidate = context["candidate"]
    print("# Wayfinder maintainer context\n")
    print(f"- Candidate: `{candidate['releaseId']}`; contract `{candidate['contractStatus']}`; release `{candidate['releaseStatus']}`; activation `{candidate['activation']}`.")
    print(f"- Cases: `{context['conformance']['caseCount']}`.")
    print(f"- Repository: `{context['paths']['repositoryRoot']}`.")
    print(f"- Maintainer command: `{context['paths']['maintainerCommand']}`.")
    print("\n## Adapter registry\n")
    for adapter in context["adapterRegistry"]:
        runtime = adapter["runtime"]
        print(f"- `{adapter['id']}` — `{adapter['sha256']}` — {runtime['implementation']} `{runtime['requiredVersion']}`; override `{runtime['overrideVariable']}`.")
    print("\n## Approval boundary\n")
    print(context["approvalBoundary"])
    print("\n## Pending action\n")
    print(context["pendingAction"])
    return 0


def freeze_proposal_issues(
    proposal: dict[str, Any],
    contract: dict[str, Any],
    release: dict[str, Any],
    cases: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    expected_top = {
        "format", "schemaVersion", "status", "decision", "candidate", "ruleCoverage",
        "expectedOutputReview", "invalidation", "certificationMatrix", "evidence",
        "runtimeActivation", "approval",
    }
    if set(proposal) != expected_top:
        issues.append("top-level fields")
    if proposal.get("format") != "wayfinder-freeze-proposal" or proposal.get("schemaVersion") != 1 or proposal.get("status") != "proposed":
        issues.append("proposal identity")
    if proposal.get("decision") != "dual-layer-package-status-and-maintainer-record":
        issues.append("accepted representation")
    candidate = proposal.get("candidate", {})
    cases_path = CONFORMANCE_ROOT / "cases.json"
    freeze_evidence_path = CERTIFICATION_ROOT / f"candidate-revision-{contract['candidateRevision']}-local.json"
    freeze_evidence = load_json(freeze_evidence_path)
    expected_candidate = {
        "releaseId": release["releaseId"],
        "candidateRevision": contract["candidateRevision"],
        "contractVersion": contract["contractVersion"],
        "contractStatus": contract["status"],
        "releaseStatus": release["status"],
        "contractSha256": sha256(SKILL_ROOT / "assets/contract-v1/contract.json"),
        "releaseSha256": freeze_evidence["package"]["releaseSha256"],
        "adapters": [
            {"id": item["id"], "path": item["path"], "sha256": item["sha256"]}
            for item in release.get("adapters", [])
        ],
        "fixtureIndexSha256": sha256(cases_path),
        "expectedOutputsSha256": expected_outputs_sha256(contract),
    }
    if candidate != expected_candidate:
        issues.append("candidate binding")
    contract_text = (SKILL_ROOT / "references/contracts/v1.md").read_text(encoding="utf-8")
    declared = set(re.findall(r"WF-[A-Z]+-[0-9]{3}", contract_text))
    citations = {rule for case in cases["cases"] for rule in case["rules"]}
    coverage = proposal.get("ruleCoverage", {})
    if coverage != {
        "normativeRules": len(declared),
        "coveredRules": len(declared & citations),
        "conformanceCases": len(cases["cases"]),
        "caseCountIsSemanticProof": False,
    }:
        issues.append("rule coverage")
    expected_paths = {
        item["path"] for item in contract["governedResources"] if item["role"] == "fixture-expected"
    }
    reviews = proposal.get("expectedOutputReview", [])
    if {item.get("path") for item in reviews if isinstance(item, dict)} != expected_paths:
        issues.append("expected-output review set")
    elif any(item.get("status") != "reviewed-against-contract" or not item.get("rules") or not set(item["rules"]) <= declared for item in reviews):
        issues.append("expected-output review authority")
    invalidation = proposal.get("invalidation", {})
    required_triggers = {"governed-byte-change", "semantic-change", "cross-artifact-disagreement"}
    required_actions = {"reopen-candidate", "advance-candidate-revision", "invalidate-affected-evidence", "rerun-every-adapter"}
    if not required_triggers <= set(invalidation.get("triggers", [])) or not required_actions <= set(invalidation.get("requiredActions", [])):
        issues.append("invalidation policy")
    matrix = proposal.get("certificationMatrix", {})
    entries = matrix.get("requiredEntries", [])
    required_pairs = {
        ("python-reference-v1", "3.14.7", family) for family in ("macOS", "Linux", "Windows")
    } | {
        ("node-v1", "24.21.0", family) for family in ("macOS", "Linux", "Windows")
    } | {
        ("powershell-v1", "7.6.6", family) for family in ("Windows", "Linux")
    }
    observed_pairs = {
        (item.get("adapterId"), item.get("runtimeVersion"), item.get("operatingSystemFamily"))
        for item in entries if isinstance(item, dict)
    }
    if matrix.get("status") != "required-future-evidence" or observed_pairs != required_pairs or any(item.get("evidenceStatus") != "missing" for item in entries):
        issues.append("certification matrix")
    if set(matrix.get("requiredFilesystemBehaviors", [])) != {"case-sensitive", "case-insensitive"}:
        issues.append("filesystem matrix")
    if proposal.get("runtimeActivation") != "disabled" or proposal.get("approval") != {"status": "pending", "requiredChoice": "Option A"}:
        issues.append("approval boundary")
    evidence = proposal.get("evidence", {})
    if evidence.get("classification") != "local-candidate-and-parity" or not evidence.get("missing"):
        issues.append("evidence boundary")
    local_report = evidence.get("localReport")
    if local_report is not None:
        report_path = CERTIFICATION_ROOT / local_report
        if not report_path.is_file() or evidence.get("localReportSha256") != sha256(report_path):
            issues.append("local evidence report")
        else:
            report = load_json(report_path)
            if evidence.get("resultSetSha256") != report.get("resultsDigest") or report.get("package", {}).get("contractSha256") != expected_candidate["contractSha256"]:
                issues.append("local evidence binding")
    parity_report = evidence.get("parityReport")
    if parity_report is not None:
        report_path = CERTIFICATION_ROOT / parity_report
        if not report_path.is_file() or evidence.get("parityReportSha256") != sha256(report_path):
            issues.append("parity evidence report")
        else:
            report = load_json(report_path)
            if (
                report.get("package", {}).get("releaseSha256") != expected_candidate["releaseSha256"]
                or report.get("agreement", {}).get("normalizedInvocationCount") != 900
                or evidence.get("normalizedInvocationsSha256") != report.get("agreement", {}).get("normalizedInvocationsSha256")
            ):
                issues.append("parity evidence binding")
    return issues


def freeze_acceptance_issues(
    acceptance: dict[str, Any],
    proposal_path: Path,
    contract: dict[str, Any],
    release: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    expected_top = {
        "format", "schemaVersion", "status", "acceptedOn", "releaseId",
        "candidateRevision", "proposal", "decision", "boundaries",
    }
    if set(acceptance) != expected_top:
        issues.append("top-level fields")
    if (
        acceptance.get("format") != "wayfinder-freeze-acceptance"
        or acceptance.get("schemaVersion") != 1
        or acceptance.get("status") != "accepted"
    ):
        issues.append("acceptance identity")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", acceptance.get("acceptedOn", "")):
        issues.append("acceptance date")
    if (
        acceptance.get("releaseId") != release["releaseId"]
        or acceptance.get("candidateRevision") != contract["candidateRevision"]
    ):
        issues.append("candidate binding")
    proposal = acceptance.get("proposal", {})
    if proposal != {
        "path": proposal_path.name,
        "sha256": sha256(proposal_path),
    }:
        issues.append("proposal binding")
    if acceptance.get("decision") != {
        "choice": "Option A",
        "authorization": FREEZE_ACCEPTANCE_AUTHORIZATION,
    }:
        issues.append("decision boundary")
    if acceptance.get("boundaries") != FREEZE_ACCEPTANCE_BOUNDARIES:
        issues.append("authorization boundaries")
    return issues


def command_environment(cache_root: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = cache_root
    return environment


def repository_bytecode_artifacts() -> list[str]:
    artifacts: list[str] = []
    for path in REPOSITORY_ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name == "__pycache__" or (path.is_file() and path.suffix == ".pyc"):
            artifacts.append(str(path.relative_to(REPOSITORY_ROOT)))
    return sorted(artifacts)


def self_test_command(output_format: str) -> int:
    before = repository_bytecode_artifacts()
    if before:
        result = {"ok": False, "code": "self-test.bytecode-present", "artifacts": before}
        print(json.dumps(result, sort_keys=True, separators=(",", ":")) if output_format == "json" else f"FAIL self-test bytecode-present: {', '.join(before)}")
        return 1
    with tempfile.TemporaryDirectory(prefix="wayfinder-maintainer-cache-") as cache_root:
        completed = subprocess.run(
            [
                sys.executable, "-m", "unittest", "discover",
                "-s", str(COMPANION_ROOT / "scripts"), "-p", "test_*.py", "-v",
            ],
            cwd=REPOSITORY_ROOT,
            env=command_environment(cache_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    combined = completed.stdout + completed.stderr
    match = re.search(r"Ran ([0-9]+) tests?", combined)
    discovered = int(match.group(1)) if match else 0
    after = repository_bytecode_artifacts()
    ok = completed.returncode == 0 and discovered > 0 and not after
    result = {
        "ok": ok,
        "code": "ok" if ok else "self-test.failed",
        "tests": discovered,
        "exitCode": completed.returncode,
        "bytecodeArtifacts": after,
    }
    if output_format == "json":
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    elif output_format == "verbose" or not ok:
        print(combined, end="" if combined.endswith("\n") else "\n")
        print(f"summary passed={str(ok).lower()} tests={discovered} bytecode={len(after)}")
    else:
        print(f"OK self-test tests={discovered} bytecode=0")
    return 0 if ok else 1


def record_section_command(heading: str) -> int:
    normalized = heading if heading.startswith("## ") else f"## {heading}"
    lines = (COMPANION_ROOT / "references/design-record.md").read_text(encoding="utf-8").splitlines(keepends=True)
    matches = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == normalized]
    if len(matches) != 1:
        detail = "not found" if not matches else f"ambiguous ({len(matches)} matches)"
        print(f"record section {detail}: {normalized}", file=sys.stderr)
        return 2
    start = matches[0]
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    sys.stdout.write("".join(lines[start:end]).rstrip("\r\n") + "\n")
    return 0


def run_python(script: Path, arguments: Iterable[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="wayfinder-maintainer-cache-") as cache_root:
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            cwd=REPOSITORY_ROOT,
            env=command_environment(cache_root),
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            check=False,
        )


def run_adapter(script: Path, arguments: Iterable[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    suffix = script.suffix.lower()
    if suffix == ".py":
        command = [sys.executable, str(script)]
    elif suffix == ".mjs":
        command = [os.environ.get("WAYFINDER_NODE_RUNTIME", "node"), str(script)]
    elif suffix == ".ps1":
        command = [
            os.environ.get("WAYFINDER_POWERSHELL_RUNTIME", "pwsh"),
            "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(script),
        ]
    else:
        raise ValueError(f"unsupported adapter suffix: {script}")
    with tempfile.TemporaryDirectory(prefix="wayfinder-maintainer-cache-") as cache_root:
        return subprocess.run(
            [*command, *arguments],
            cwd=REPOSITORY_ROOT,
            env=command_environment(cache_root),
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            check=False,
        )


def parse_frontmatter(path: Path) -> tuple[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("missing closing frontmatter delimiter") from None
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key in {"name", "description"}:
            fields[key] = value.strip().strip('"')
    if not fields.get("name") or not fields.get("description"):
        raise ValueError("name and description are required")
    if "TODO" in path.read_text(encoding="utf-8"):
        raise ValueError("unfinished TODO placeholder")
    return fields["name"], fields["description"]


def text_profile_failures(roots: Iterable[Path]) -> list[str]:
    failures: list[str] = []
    for root in roots:
        if not root.exists():
            failures.append(f"missing skill root: {root}")
            continue
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file() and candidate.suffix in TEXT_SUFFIXES):
            raw = path.read_bytes()
            relative = path.relative_to(REPOSITORY_ROOT)
            if raw.startswith(b"\xef\xbb\xbf"):
                failures.append(f"{relative}: BOM")
                continue
            if b"\r" in raw:
                failures.append(f"{relative}: CR newline")
            if not raw.endswith(b"\n"):
                failures.append(f"{relative}: missing terminal LF")
            try:
                text = raw.decode("utf-8", "strict")
            except UnicodeDecodeError:
                failures.append(f"{relative}: invalid UTF-8")
                continue
            if unicodedata.normalize("NFC", text) != text:
                failures.append(f"{relative}: non-NFC")
            for number, line in enumerate(text.splitlines(), 1):
                if line.endswith((" ", "\t")):
                    failures.append(f"{relative}:{number}: trailing whitespace")
    return failures


def _emit_doctor(checks: list[tuple[str, bool, str]], output_mode: str, yaml_available: bool) -> int:
    failures = [(name, detail) for name, passed, detail in checks if not passed]
    summary = {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks)}
    if output_mode == "json":
        print(json.dumps({
            "format": "wayfinder-maintainer-doctor",
            "schemaVersion": 1,
            "ok": not failures,
            "optionalPyYAML": "available" if yaml_available else "unavailable-dependency-free-checks-used",
            "checks": [
                {"name": name, "status": "passed" if passed else "failed", "detail": detail}
                for name, passed, detail in checks
            ],
            "summary": summary,
        }, sort_keys=True, separators=(",", ":")))
    elif output_mode == "verbose":
        print(f"INFO optional-pyyaml={'available' if yaml_available else 'unavailable; dependency-free checks used'}")
        for name, passed, detail in checks:
            suffix = f": {detail}" if detail else ""
            print(f"{'PASS' if passed else 'FAIL'} {name}{suffix}")
        print(f"summary passed={summary['passed']} failed={summary['failed']} total={summary['total']}")
    elif output_mode == "summary":
        for name, detail in failures:
            print(f"FAIL {name}{': ' + detail if detail else ''}")
        if failures:
            print(f"summary passed={summary['passed']} failed={summary['failed']} total={summary['total']}")
        else:
            print(f"OK doctor passed={summary['passed']} total={summary['total']}")
    elif output_mode == "quiet":
        for name, detail in failures:
            print(f"FAIL {name}{': ' + detail if detail else ''}")
        if failures:
            print(f"summary passed={summary['passed']} failed={summary['failed']} total={summary['total']}")
    else:
        raise ValueError(f"unknown doctor output mode: {output_mode}")
    return 1 if failures else 0


def doctor(output_mode: str = "summary", selected_adapter: str | None = None) -> int:
    checks: list[tuple[str, bool, str]] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append((name, passed, detail))

    add("python-version", sys.version_info >= (3, 11), f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if sys.version_info < (3, 11):
        return _emit_doctor(checks, output_mode, importlib.util.find_spec("yaml") is not None)

    try:
        contract = load_json(SKILL_ROOT / "assets/contract-v1/contract.json")
        release = load_json(SKILL_ROOT / "assets/contract-v1/release.json")
        release_schema = load_json(SKILL_ROOT / "assets/contract-v1/schemas/release.schema.json")
        probe_expected = load_json(CONFORMANCE_ROOT / "expected/probe-deterministic.json")
        cases = load_json(CONFORMANCE_ROOT / "cases.json")
        revision = contract["candidateRevision"]
        expected_release_id = f"v1-candidate-revision-{revision}"
        add("candidate-release-identity", release["releaseId"] == expected_release_id, f"expected={expected_release_id} actual={release['releaseId']}")
        add("freeze-status-identity", contract["status"] == CONTRACT_STATUS and release["status"] == RELEASE_STATUS, f"contract={contract['status']} release={release['status']}")
        release_constraint = release_schema["properties"]["releaseId"]
        expected_constraint = {"type": "string", "pattern": RELEASE_ID_PATTERN}
        add("release-schema-identity", release_constraint == expected_constraint and re.fullmatch(RELEASE_ID_PATTERN, release["releaseId"]) is not None, json.dumps(release_constraint, sort_keys=True))
        add("release-schema-status", release_schema["properties"]["status"] == {"enum": ["unactivated-candidate", "unactivated-frozen", "activated-frozen"]})
        add(
            "probe-oracle-identity",
            probe_expected["releaseId"] == release["releaseId"]
            and probe_expected["contractVersion"] == contract["contractVersion"]
            and probe_expected["status"] == release["status"],
            f"probe={probe_expected['releaseId']} release={release['releaseId']}",
        )
        required_meta_cases = {"package-release-schema-mismatch", "package-status-schema-mismatch", "package-adapter-registry-mismatch"}
        add("meta-conformance-cases", required_meta_cases <= {case["id"] for case in cases["cases"]})
        declared_rules = re.findall(r"WF-[A-Z]+-[0-9]{3}", (SKILL_ROOT / "references/contracts/v1.md").read_text(encoding="utf-8"))
        cited_rules = [rule for case in cases["cases"] for rule in case["rules"]]
        unique_rules = set(declared_rules)
        add("normative-rule-identifiers", len(declared_rules) == len(unique_rules), f"declared={len(declared_rules)} unique={len(unique_rules)}")
        add("case-rule-references", set(cited_rules) <= unique_rules and unique_rules <= set(cited_rules), f"declared={len(unique_rules)} cited={len(set(cited_rules))}")
        add("runtime-maintainer-boundary", not (SKILL_ROOT / "maintainers").exists())
        companion_paths = (
            COMPANION_ROOT / "references/design-record.md",
            COMPANION_ROOT / "references/research",
            COMPANION_ROOT / "scripts/conformance/v1/run.py",
            COMPANION_ROOT / "certification/v1",
        )
        add(
            "companion-owns-maintenance",
            all(path.exists() for path in companion_paths),
            ", ".join(str(path.relative_to(REPOSITORY_ROOT)) for path in companion_paths if not path.exists()),
        )

        contract_text = (SKILL_ROOT / "references/contracts/v1.md").read_text(encoding="utf-8")
        stale_contract = re.search(r"candidate Slice [0-9]+|Stage 0 through Slice [0-9]+ only|does not define application or recovery", contract_text)
        add("stable-contract-introduction", stale_contract is None, stale_contract.group(0) if stale_contract else "")
        research_text = (COMPANION_ROOT / "references/research/initialization-18-implementation-certification.md").read_text(encoding="utf-8")
        add("single-progress-authority", "See the [maintainer design record]" in research_text and "Slice 4—" not in research_text)
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        stable_runtime_status = (
            "Wayfinder version 1 remains unactivated" in skill_text
            and "Do not infer current maintenance or certification status from this stub" in skill_text
            and re.search(r"candidate revision [0-9]+", skill_text, re.IGNORECASE) is None
        )
        add("runtime-status-stable", stable_runtime_status)
        companion_config = (COMPANION_ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        add(
            "companion-explicit-only",
            "allow_implicit_invocation: false" in companion_config
            and 'Use $wayfinder-maintainer' in companion_config,
        )
        design_text = (COMPANION_ROOT / "references/design-record.md").read_text(encoding="utf-8")
        required_current_anchors = (
            "## Candidate revision 8 freeze — accepted",
            "## Candidate revision 8 adapter parity — accepted",
            "## Candidate revision 8 bounded certification matrix — accepted",
            "## Candidate revision 8 hosted certification execution — accepted with failed aggregate",
            "## Candidate revision 8 Windows certification investigation and correction — accepted",
            "## Candidate revision 8 maintainer-efficiency tranche — accepted",
            "## Candidate revision 9 Windows corrections — accepted",
            "## Candidate revision 9 hosted certification execution — accepted with failed aggregate",
            "## Candidate revision 9 maintainer reliability and efficiency — accepted",
            "## Candidate revision 9 Windows failure investigation — accepted",
            "## Candidate revision 9 maintainer-only Windows correction — accepted",
        )
        current_state_matches = (
            CURRENT_STATE_PATH.is_file()
            and CURRENT_STATE_PATH.read_text(encoding="utf-8") == current_state_markdown()
            and all(anchor in design_text for anchor in required_current_anchors)
        )
        add("current-state-drift", current_state_matches, _relative(CURRENT_STATE_PATH))

        freeze_path = CERTIFICATION_ROOT / f"proposed-freeze-revision-{revision}.json"
        if freeze_path.exists():
            freeze = load_json(freeze_path)
            freeze_issues = freeze_proposal_issues(freeze, contract, release, cases)
            add("freeze-proposal", not freeze_issues, ", ".join(freeze_issues))
            mutations: list[dict[str, Any]] = []
            for field, value in (("releaseId", "v1-candidate-revision-999"), ("contractStatus", "candidate"), ("contractSha256", "0" * 64)):
                mutation = json.loads(json.dumps(freeze))
                mutation["candidate"][field] = value
                mutations.append(mutation)
            mutation = json.loads(json.dumps(freeze))
            mutation["invalidation"]["requiredActions"] = []
            mutations.append(mutation)
            mutation = json.loads(json.dumps(freeze))
            mutation["certificationMatrix"]["status"] = "complete"
            mutations.append(mutation)
            mutation = json.loads(json.dumps(freeze))
            mutation["evidence"]["localReportSha256"] = "0" * 64
            mutations.append(mutation)
            add("freeze-proposal-mutations", all(freeze_proposal_issues(item, contract, release, cases) for item in mutations), f"mutations={len(mutations)}")
        else:
            add("freeze-proposal", True, "not yet generated")

        acceptance_path = CERTIFICATION_ROOT / f"freeze-acceptance-revision-{revision}.json"
        if acceptance_path.exists() and freeze_path.exists():
            acceptance = load_json(acceptance_path)
            acceptance_issues = freeze_acceptance_issues(acceptance, freeze_path, contract, release)
            add("freeze-acceptance", not acceptance_issues, ", ".join(acceptance_issues))
            acceptance_mutations: list[dict[str, Any]] = []
            for field, value in (("releaseId", "v1-candidate-revision-999"), ("candidateRevision", 999)):
                mutation = json.loads(json.dumps(acceptance))
                mutation[field] = value
                acceptance_mutations.append(mutation)
            mutation = json.loads(json.dumps(acceptance))
            mutation["proposal"]["sha256"] = "0" * 64
            acceptance_mutations.append(mutation)
            mutation = json.loads(json.dumps(acceptance))
            mutation["decision"]["authorization"] = "Begin parity implementation."
            acceptance_mutations.append(mutation)
            mutation = json.loads(json.dumps(acceptance))
            mutation["boundaries"]["runtimeActivation"] = "enabled"
            acceptance_mutations.append(mutation)
            add(
                "freeze-acceptance-mutations",
                all(freeze_acceptance_issues(item, freeze_path, contract, release) for item in acceptance_mutations),
                f"mutations={len(acceptance_mutations)}",
            )
        else:
            add("freeze-acceptance", True, "pending owner review")

        current_evidence = CERTIFICATION_ROOT / f"candidate-revision-{revision}-local.json"
        if current_evidence.exists():
            evidence = load_json(current_evidence)
            result_basis = {
                "releaseSha256": evidence["package"]["releaseSha256"],
                "contractSha256": sha256(SKILL_ROOT / "assets/contract-v1/contract.json"),
                "adapterSha256": sha256(SKILL_ROOT / "scripts/adapters/wayfinder.py"),
                "casesSha256": sha256(CONFORMANCE_ROOT / "cases.json"),
                "results": evidence["results"],
            }
            expected_results_digest = hashlib.sha256(
                json.dumps(result_basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            evidence_bound = (
                evidence["package"]["releaseId"] == release["releaseId"]
                and evidence["package"]["releaseSha256"] == result_basis["releaseSha256"]
                and evidence["package"]["contractSha256"] == result_basis["contractSha256"]
                and evidence["package"]["adapterSha256"] == result_basis["adapterSha256"]
                and evidence["package"]["casesSha256"] == result_basis["casesSha256"]
                and evidence["resultsDigest"] == expected_results_digest
                and evidence["summary"]["failed"] == 0
                and evidence["summary"]["passed"] == evidence["summary"]["total"] == len(evidence["results"])
            )
            add("freeze-evidence-binding", evidence_bound, str(current_evidence.relative_to(REPOSITORY_ROOT)))
        else:
            add("freeze-evidence-binding", True, "not yet generated")
    except Exception as exc:
        add("candidate-metadata", False, str(exc))

    try:
        package = run_python(PACKAGE_BUILDER, ["--check"], capture=True)
        add("package-digests", package.returncode == 0, (package.stdout + package.stderr).strip())
    except Exception as exc:
        add("package-digests", False, str(exc))

    try:
        release = load_json(SKILL_ROOT / "assets/contract-v1/release.json")
        probe_failures: list[str] = []
        runtime_details: list[str] = []
        for adapter in release["adapters"]:
            adapter_id = adapter["id"]
            if selected_adapter is not None and adapter_id != selected_adapter:
                continue
            adapter_file = SKILL_ROOT / adapter["path"]
            implementation, required_version, override = RUNTIME_REQUIREMENTS[adapter_id]
            try:
                observation = _runtime_observation(adapter_id)
                identity = observation["executableIdentity"]
                runtime_details.append(
                    f"{adapter_id}: request={identity['requested']} resolved={identity['resolvedPath']} "
                    f"observed={observation['implementation']} {observation['version']} "
                    f"required={implementation} {required_version} override={override}"
                )
                probe = run_adapter(adapter_file, ["probe"], capture=True)
                result = json.loads(probe.stdout) if probe.stdout else {}
                if probe.returncode != 0 or result.get("ok") is not True:
                    probe_failures.append(f"{adapter_id}: {(probe.stderr or result.get('code', '')).strip()}")
            except Exception as exc:
                probe_failures.append(f"{adapter_id}: {exc}; override={override}")
        add("adapter-probes", not probe_failures, "; ".join(probe_failures or runtime_details))
    except Exception as exc:
        add("adapter-probes", False, str(exc))

    try:
        pinned = load_json(HISTORICAL_HASHES)["files"]
        mismatches = [name for name, digest in pinned.items() if not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest]
        add("historical-evidence", not mismatches, ", ".join(mismatches))
    except Exception as exc:
        add("historical-evidence", False, str(exc))

    try:
        release_path = SKILL_ROOT / "assets/contract-v1/release.json"
        contract_path = SKILL_ROOT / "assets/contract-v1/contract.json"
        cases_path = CONFORMANCE_ROOT / "cases.json"
        release = load_json(release_path)
        contract = load_json(contract_path)
        actual_bindings = {
            "releaseId": release["releaseId"],
            "releaseSha256": sha256(release_path),
            "contractVersion": contract["contractVersion"],
            "contractSha256": sha256(contract_path),
            "fixtureIndexSha256": sha256(cases_path),
            "expectedOutputsSha256": expected_outputs_sha256(contract),
        }
        actual_adapters = {item["id"]: item["sha256"] for item in release["adapters"]}
        add(
            "accepted-matrix-bindings",
            actual_bindings == ACCEPTED_MATRIX_BINDINGS and actual_adapters == ACCEPTED_ADAPTER_DIGESTS,
            json.dumps({"package": actual_bindings, "adapters": actual_adapters}, sort_keys=True),
        )
    except Exception as exc:
        add("accepted-matrix-bindings", False, str(exc))

    try:
        mismatches = [
            name for name, digest in ACCEPTED_PARITY_EVIDENCE_DIGESTS.items()
            if not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest
        ]
        parity = load_json(CERTIFICATION_ROOT / "parity-revision-8-local.json")
        parity_bound = (
            parity.get("package", {}).get("releaseSha256") == "677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284"
            and parity.get("package", {}).get("contractSha256") == "75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b"
            and parity.get("agreement", {}).get("normalizedInvocationCount") == 900
            and parity.get("agreement", {}).get("normalizedInvocationsSha256")
            == "4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233"
        )
        add("accepted-parity-evidence", not mismatches and parity_bound, ", ".join(mismatches))
    except Exception as exc:
        add("accepted-parity-evidence", False, str(exc))

    try:
        revision = load_json(SKILL_ROOT / "assets/contract-v1/contract.json")["candidateRevision"]
        current_parity_path = CERTIFICATION_ROOT / f"parity-revision-{revision}-local.json"
        if current_parity_path.is_file():
            current_parity = load_json(current_parity_path)
            current_adapters = {item["id"]: item["sha256"] for item in current_parity.get("adapters", [])}
            current_parity_bound = (
                current_parity.get("package", {}).get("releaseSha256") == ACCEPTED_MATRIX_BINDINGS["releaseSha256"]
                and current_parity.get("package", {}).get("contractSha256") == ACCEPTED_MATRIX_BINDINGS["contractSha256"]
                and current_adapters == ACCEPTED_ADAPTER_DIGESTS
                and current_parity.get("summary") == {"total": 305, "passed": 305, "failed": 0}
                and current_parity.get("agreement", {}).get("normalizedInvocationCount") == 900
            )
            add("current-local-parity", current_parity_bound, _relative(current_parity_path))
        else:
            add("current-local-parity", True, "not yet generated")
    except Exception as exc:
        add("current-local-parity", False, str(exc))

    try:
        mismatches = [
            name for name, digest in CURRENT_LOCAL_EVIDENCE_DIGESTS.items()
            if not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest
        ]
        add("current-local-evidence", not mismatches, ", ".join(mismatches))
    except Exception as exc:
        add("current-local-evidence", False, str(exc))

    try:
        mismatches = [
            name for name, digest in ACCEPTED_MATRIX_EVIDENCE_DIGESTS.items()
            if not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest
        ]
        add("accepted-certification-evidence", not mismatches, ", ".join(mismatches))
    except Exception as exc:
        add("accepted-certification-evidence", False, str(exc))

    caches = sorted(str(path.relative_to(REPOSITORY_ROOT)) for path in SKILL_ROOT.parent.rglob("__pycache__"))
    pycs = sorted(str(path.relative_to(REPOSITORY_ROOT)) for path in SKILL_ROOT.parent.rglob("*.pyc"))
    add("no-bytecode-artifacts", not caches and not pycs, ", ".join(caches + pycs))

    profile_failures = text_profile_failures((SKILL_ROOT, COMPANION_ROOT))
    add("text-profile", not profile_failures, "; ".join(profile_failures[:10]))

    compile_failures: list[str] = []
    for root in (SKILL_ROOT, COMPANION_ROOT):
        for path in sorted(root.rglob("*.py")):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except Exception as exc:
                compile_failures.append(f"{path.relative_to(REPOSITORY_ROOT)}: {exc}")
    add("python-syntax-no-cache", not compile_failures, "; ".join(compile_failures))

    frontmatter_failures: list[str] = []
    for root in (SKILL_ROOT, COMPANION_ROOT):
        try:
            name, description = parse_frontmatter(root / "SKILL.md")
            if name != root.name or not description:
                raise ValueError(f"frontmatter name {name!r} does not match folder")
        except Exception as exc:
            frontmatter_failures.append(f"{root.name}: {exc}")
    add("skill-frontmatter", not frontmatter_failures, "; ".join(frontmatter_failures))

    return _emit_doctor(checks, output_mode, importlib.util.find_spec("yaml") is not None)


def adapter_path(adapter_id: str) -> Path:
    release = load_json(SKILL_ROOT / "assets/contract-v1/release.json")
    matches = [item for item in release["adapters"] if item["id"] == adapter_id]
    if len(matches) != 1:
        raise ValueError(f"release does not contain adapter {adapter_id!r}")
    return SKILL_ROOT / matches[0]["path"]


def test_command(case_ids: list[str], categories: list[str], selected_adapter: str, output_mode: str = "summary") -> int:
    if doctor("quiet", selected_adapter=selected_adapter) != 0:
        print("maintainer doctor failed; conformance run not started", file=sys.stderr)
        return 1
    try:
        selected_path = adapter_path(selected_adapter)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    arguments: list[str] = ["--adapter", str(selected_path), "--output", output_mode]
    for case_id in case_ids:
        arguments.extend(["--case", case_id])
    for category in categories:
        arguments.extend(["--category", category])
    return run_python(CONFORMANCE_RUNNER, arguments).returncode


def evidence_command(output: Path) -> int:
    if doctor("quiet") != 0:
        print("maintainer doctor failed; evidence run not started", file=sys.stderr)
        return 1
    if output.is_symlink():
        print(f"evidence output may not be a symbolic link: {output}", file=sys.stderr)
        return 2
    output = output.resolve()
    contract = load_json(SKILL_ROOT / "assets/contract-v1/contract.json")
    stem = f"candidate-revision-{contract['candidateRevision']}-local"
    targets = [output / f"{stem}.json", output / f"{stem}.md"]
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        print(f"evidence target already exists: {', '.join(existing)}", file=sys.stderr)
        return 2
    completed = run_python(CONFORMANCE_RUNNER, ["--write-evidence", "--evidence-dir", str(output)])
    if completed.returncode != 0:
        return completed.returncode
    return doctor("quiet")


def freeze_proposal_command(output: Path) -> int:
    if doctor("quiet") != 0:
        print("maintainer doctor failed; freeze proposal not created", file=sys.stderr)
        return 1
    output = output.resolve()
    contract = load_json(SKILL_ROOT / "assets/contract-v1/contract.json")
    release = load_json(SKILL_ROOT / "assets/contract-v1/release.json")
    cases = load_json(CONFORMANCE_ROOT / "cases.json")
    revision = contract["candidateRevision"]
    local_name = f"candidate-revision-{revision}-local.json"
    parity_name = f"parity-revision-{revision}-local.json"
    local_path = CERTIFICATION_ROOT / local_name
    parity_path = CERTIFICATION_ROOT / parity_name
    if not local_path.is_file() or not parity_path.is_file():
        print("passing local candidate and parity reports are required", file=sys.stderr)
        return 1
    local = load_json(local_path)
    parity = load_json(parity_path)
    historical = load_json(CERTIFICATION_ROOT / "proposed-freeze-revision-8.json")
    proposal = {
        "format": "wayfinder-freeze-proposal", "schemaVersion": 1, "status": "proposed",
        "decision": "dual-layer-package-status-and-maintainer-record",
        "candidate": {
            "releaseId": release["releaseId"], "candidateRevision": revision,
            "contractVersion": contract["contractVersion"], "contractStatus": contract["status"],
            "releaseStatus": release["status"],
            "contractSha256": sha256(SKILL_ROOT / "assets/contract-v1/contract.json"),
            "releaseSha256": sha256(SKILL_ROOT / "assets/contract-v1/release.json"),
            "adapters": [{"id": item["id"], "path": item["path"], "sha256": item["sha256"]} for item in release["adapters"]],
            "fixtureIndexSha256": sha256(CONFORMANCE_ROOT / "cases.json"),
            "expectedOutputsSha256": expected_outputs_sha256(contract),
        },
        "ruleCoverage": {"normativeRules": 96, "coveredRules": 96, "conformanceCases": len(cases["cases"]), "caseCountIsSemanticProof": False},
        "expectedOutputReview": historical["expectedOutputReview"],
        "invalidation": historical["invalidation"],
        "certificationMatrix": {
            "status": "required-future-evidence", "requiredFilesystemBehaviors": ["case-sensitive", "case-insensitive"],
            "requiredEntries": [
                {"adapterId": adapter_id, "runtimeImplementation": implementation, "runtimeVersion": version, "operatingSystemFamily": family, "evidenceStatus": "missing"}
                for adapter_id, implementation, version, family in MATRIX_TARGETS
            ],
        },
        "evidence": {
            "classification": "local-candidate-and-parity", "localReport": local_name,
            "localReportSha256": sha256(local_path), "resultSetSha256": local["resultsDigest"],
            "parityReport": parity_name, "parityReportSha256": sha256(parity_path),
            "normalizedInvocationsSha256": parity["agreement"]["normalizedInvocationsSha256"],
            "missing": ["independent-review-evidence", "cross-platform-matrix-evidence", "pinned-node-24.21.0-environment-evidence", "windows-environment-evidence", "full-family-certification"],
        },
        "runtimeActivation": "disabled", "approval": {"status": "pending", "requiredChoice": "Option A"},
    }
    issues = freeze_proposal_issues(proposal, contract, release, cases)
    if issues:
        print("freeze proposal is invalid: " + ", ".join(issues), file=sys.stderr)
        return 1
    stem = f"proposed-freeze-revision-{revision}"
    json_path, markdown_path = output / f"{stem}.json", output / f"{stem}.md"
    if any(path.exists() or path.is_symlink() for path in (json_path, markdown_path)):
        print("freeze proposal target already exists", file=sys.stderr)
        return 2
    markdown = "\n".join([
        f"# Wayfinder candidate revision {revision} proposed freeze packet", "",
        "- **Status:** Proposed; pending explicit owner approval", f"- **Prepared:** {dt.date.today().isoformat()}",
        f"- **Release:** `{release['releaseId']}`", "- **Contract status:** Frozen pending owner review",
        "- **Release status:** Unactivated frozen", "- **Runtime activation:** Disabled", "",
        "## Correction scope", "",
        "Revision 9 reopens revision 8 only for the approved Windows process-existence and unsupported-special-file corrections. The version-1 safety meaning is preserved.", "",
        "## Exact identity", "",
        f"- Contract SHA-256: `{proposal['candidate']['contractSha256']}`",
        f"- Release SHA-256: `{proposal['candidate']['releaseSha256']}`",
        f"- Fixture-index SHA-256: `{proposal['candidate']['fixtureIndexSha256']}`",
        f"- Expected-output-set SHA-256: `{proposal['candidate']['expectedOutputsSha256']}`",
        *[f"- {item['id']} SHA-256: `{item['sha256']}`" for item in proposal["candidate"]["adapters"]], "",
        "## Local evidence", "",
        f"- Candidate report: `{local_name}` (`{proposal['evidence']['localReportSha256']}`), 305/305.",
        f"- Parity report: `{parity_name}` (`{proposal['evidence']['parityReportSha256']}`), all three adapters 305/305 with 900 normalized observations agreeing.",
        "- Node.js 22.22.3 was used locally and is not the pinned Node.js 24.21.0 matrix runtime.",
        "- No Windows or hosted matrix result is claimed; every revision-9 matrix entry remains missing.", "",
        "## Approval checkpoint", "",
        "- **Option A:** Accept the exact revision-9 frozen bytes and local evidence. This does not dispatch hosted certification, publish evidence, add certification entries, or activate Wayfinder.",
        "- **Option B:** Request changes and leave revision 9 unaccepted.", "",
    ]).encode("utf-8")
    raw = (json.dumps(proposal, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    published: list[Path] = []
    try:
        for path, payload in ((json_path, raw), (markdown_path, markdown)):
            with path.open("xb") as handle:
                handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            published.append(path)
    except Exception:
        for path in published:
            path.unlink(missing_ok=True)
        raise
    print(f"freeze-proposal-json={json_path}")
    print(f"freeze-proposal-markdown={markdown_path}")
    return 0


def freeze_acceptance_command(output: Path, accept_option_a: bool) -> int:
    if not accept_option_a:
        print("freeze acceptance requires --accept-option-a after explicit owner approval", file=sys.stderr)
        return 2
    if doctor("quiet") != 0:
        print("maintainer doctor failed; freeze acceptance not created", file=sys.stderr)
        return 1
    output = output.resolve()
    contract = load_json(SKILL_ROOT / "assets/contract-v1/contract.json")
    release = load_json(SKILL_ROOT / "assets/contract-v1/release.json")
    revision = contract["candidateRevision"]
    proposal_path = CERTIFICATION_ROOT / f"proposed-freeze-revision-{revision}.json"
    if not proposal_path.is_file():
        print("validated revision-scoped freeze proposal is required", file=sys.stderr)
        return 1
    proposal = load_json(proposal_path)
    cases = load_json(CONFORMANCE_ROOT / "cases.json")
    proposal_issues = freeze_proposal_issues(proposal, contract, release, cases)
    if proposal_issues:
        print("freeze proposal is invalid: " + ", ".join(proposal_issues), file=sys.stderr)
        return 1
    acceptance = {
        "format": "wayfinder-freeze-acceptance",
        "schemaVersion": 1,
        "status": "accepted",
        "acceptedOn": dt.date.today().isoformat(),
        "releaseId": release["releaseId"],
        "candidateRevision": revision,
        "proposal": {"path": proposal_path.name, "sha256": sha256(proposal_path)},
        "decision": {"choice": "Option A", "authorization": FREEZE_ACCEPTANCE_AUTHORIZATION},
        "boundaries": FREEZE_ACCEPTANCE_BOUNDARIES,
    }
    issues = freeze_acceptance_issues(acceptance, proposal_path, contract, release)
    if issues:
        print("freeze acceptance is invalid: " + ", ".join(issues), file=sys.stderr)
        return 1
    stem = f"freeze-acceptance-revision-{revision}"
    json_path, markdown_path = output / f"{stem}.json", output / f"{stem}.md"
    if any(path.exists() or path.is_symlink() for path in (json_path, markdown_path)):
        print("freeze acceptance target already exists", file=sys.stderr)
        return 2
    markdown = "\n".join([
        f"# Wayfinder version-1 freeze acceptance — revision {revision}", "",
        "- **Status:** Accepted", f"- **Accepted:** {acceptance['acceptedOn']}",
        "- **Choice:** Option A", f"- **Release:** `{release['releaseId']}`",
        "- **Contract status:** Frozen", "- **Release status:** Unactivated frozen",
        "- **Runtime activation:** Disabled", "",
        f"The owner accepted the exact candidate revision {revision} frozen bytes and local candidate and parity evidence after reviewing the complete [freeze packet](proposed-freeze-revision-{revision}.md).", "",
        f"The accepted proposal JSON is bound at `{acceptance['proposal']['sha256']}`. The acceptance records the local evidence and exact bytes only. Hosted certification, evidence publication, a release-certification entry, full-family certification, runtime guidance or activation, live-project work, commits, and pushes remain unauthorized.", "",
        "Any governed-byte or semantic change reopens the candidate, advances its revision, invalidates affected evidence, and requires every adapter to rerun.", "",
    ]).encode("utf-8")
    raw = (json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    published: list[Path] = []
    try:
        for path, payload in ((json_path, raw), (markdown_path, markdown)):
            with path.open("xb") as handle:
                handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            published.append(path)
    except Exception:
        for path in published:
            path.unlink(missing_ok=True)
        raise
    print(f"freeze-acceptance-json={json_path}")
    print(f"freeze-acceptance-markdown={markdown_path}")
    return 0


def _parity_normalize(value: Any, adapter_ids: set[str], adapter_digests: set[str]) -> Any:
    if isinstance(value, list):
        return [_parity_normalize(item, adapter_ids, adapter_digests) for item in value]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key == "environment":
                result[key] = "<environment-evidence>"
            elif key == "adapter":
                result[key] = "<adapter-identity>"
            elif key in {"journalHeadSha256", "receiptSha256"}:
                result[key] = "<adapter-bound-audit-digest>"
            else:
                result[key] = _parity_normalize(item, adapter_ids, adapter_digests)
        return result
    if isinstance(value, str):
        if value in adapter_ids:
            return "<adapter-id>"
        if value in adapter_digests:
            return "<adapter-sha256>"
    return value


def _parity_projection(observations: dict[str, Any]) -> dict[str, Any]:
    """Compare only frozen observables; the suite owns command-specific data assertions."""
    invocations: list[dict[str, Any]] = []
    for item in observations["invocations"]:
        result = item["result"]
        arguments = list(item["arguments"])
        if arguments and arguments[0] == "initialize-apply":
            for index, value in enumerate(arguments[:-1]):
                if value == "--plan-sha256":
                    arguments[index + 1] = "<adapter-bound-plan-sha256>"
                elif value == "--confirmation-token" and arguments[index + 1].startswith("wayfinder-confirm-sha256:"):
                    arguments[index + 1] = "wayfinder-confirm-sha256:<adapter-bound-plan-sha256>"
        if arguments and arguments[0] == "initialize-recover":
            for index, value in enumerate(arguments[:-1]):
                if value == "--operation-id" and arguments[index + 1].startswith("wfinit-") and not arguments[index + 1].startswith("wfinit-test-"):
                    arguments[index + 1] = "<adapter-bound-operation-id>"
        invocations.append({
            "case": item["case"],
            "invocation": item["invocation"],
            "arguments": arguments,
            "exit": item["exit"],
            "result": {
                "format": result["format"],
                "schemaVersion": result["schemaVersion"],
                "ok": result["ok"],
                "command": result["command"],
                "code": result["code"],
                "diagnosticCodes": [diagnostic["code"] for diagnostic in result["diagnostics"]],
            },
            "stderrPresent": bool(item["stderr"]),
        })
    return {"results": observations["results"], "invocations": invocations}


def _first_difference(left: Any, right: Any, path: str = "$") -> str | None:
    if type(left) is not type(right):
        return f"{path}: type {type(left).__name__} != {type(right).__name__}"
    if isinstance(left, dict):
        if list(left) != list(right):
            return f"{path}: keys {list(left)!r} != {list(right)!r}"
        for key in left:
            difference = _first_difference(left[key], right[key], f"{path}.{key}")
            if difference is not None:
                return difference
        return None
    if isinstance(left, list):
        if len(left) != len(right):
            return f"{path}: length {len(left)} != {len(right)}"
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            difference = _first_difference(left_item, right_item, f"{path}[{index}]")
            if difference is not None:
                return difference
        return None
    if left != right:
        return f"{path}: {left!r} != {right!r}"
    return None


def _differences(left: Any, right: Any, limit: int = 50) -> list[str]:
    differences: list[str] = []

    def visit(left_value: Any, right_value: Any, path: str) -> None:
        if len(differences) >= limit:
            return
        if type(left_value) is not type(right_value):
            differences.append(f"{path}: type {type(left_value).__name__} != {type(right_value).__name__}")
            return
        if isinstance(left_value, dict):
            if list(left_value) != list(right_value):
                differences.append(f"{path}: keys {list(left_value)!r} != {list(right_value)!r}")
            for key in left_value.keys() & right_value.keys():
                visit(left_value[key], right_value[key], f"{path}.{key}")
            return
        if isinstance(left_value, list):
            if len(left_value) != len(right_value):
                differences.append(f"{path}: length {len(left_value)} != {len(right_value)}")
            for index, (left_item, right_item) in enumerate(zip(left_value, right_value)):
                visit(left_item, right_item, f"{path}[{index}]")
            return
        if left_value != right_value:
            differences.append(f"{path}: {left_value!r} != {right_value!r}")

    visit(left, right, "$")
    return differences


def parity_command(output: Path) -> int:
    if doctor("quiet") != 0:
        print("maintainer doctor failed; parity run not started", file=sys.stderr)
        return 1
    if output.is_symlink():
        print(f"parity evidence output may not be a symbolic link: {output}", file=sys.stderr)
        return 2
    output = output.resolve()
    release_path = SKILL_ROOT / "assets/contract-v1/release.json"
    contract_path = SKILL_ROOT / "assets/contract-v1/contract.json"
    cases_path = CONFORMANCE_ROOT / "cases.json"
    release = load_json(release_path)
    contract = load_json(contract_path)
    stem = f"parity-revision-{contract['candidateRevision']}-local"
    targets = [output / f"{stem}.json", output / f"{stem}.md"]
    existing = [str(target) for target in targets if target.exists() or target.is_symlink()]
    if existing:
        print(f"parity evidence target already exists: {', '.join(existing)}", file=sys.stderr)
        return 2
    expected_ids = ["python-reference-v1", "node-v1", "powershell-v1"]
    adapters = [item for adapter_id in expected_ids for item in release["adapters"] if item["id"] == adapter_id]
    if [item["id"] for item in adapters] != expected_ids:
        print("release does not contain the complete ordered parity adapter set", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="wayfinder-parity-") as raw_temp:
        temporary = Path(raw_temp)
        observations: dict[str, dict[str, Any]] = {}

        def run_parity_adapter(adapter: dict[str, Any]) -> tuple[dict[str, Any], Path, subprocess.CompletedProcess[str]]:
            observation_path = temporary / f"{adapter['id']}.json"
            completed = run_python(
                CONFORMANCE_RUNNER,
                [
                    "--adapter", str(SKILL_ROOT / adapter["path"]),
                    "--observations", str(observation_path),
                    "--differential-mode",
                ],
            )
            return adapter, observation_path, completed

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(adapters)) as executor:
            futures = [executor.submit(run_parity_adapter, adapter) for adapter in adapters]
            completed_runs = [future.result() for future in futures]
        for adapter, observation_path, completed in completed_runs:
            if completed.returncode != 0:
                print(f"{adapter['id']} conformance failed; parity evidence not written", file=sys.stderr)
                return completed.returncode
            observations[adapter["id"]] = load_json(observation_path)

        adapter_ids = {item["id"] for item in adapters}
        adapter_digests = {item["sha256"] for item in adapters}
        normalized = {
            adapter_id: _parity_normalize(_parity_projection(value), adapter_ids, adapter_digests)
            for adapter_id, value in observations.items()
        }
        reference = normalized[expected_ids[0]]
        mismatches = [adapter_id for adapter_id in expected_ids[1:] if normalized[adapter_id] != reference]
        if mismatches:
            print(f"cross-adapter observations differ: {', '.join(mismatches)}", file=sys.stderr)
            for adapter_id in mismatches:
                differences = _differences(reference, normalized[adapter_id])
                print(f"differences for {adapter_id} (showing {len(differences)}):", file=sys.stderr)
                for difference in differences:
                    print(f"- {difference}", file=sys.stderr)
            return 1
        suite = observations[expected_ids[0]]["results"]
        if any(item["status"] != "passed" for item in suite):
            print("parity observations contain failed cases", file=sys.stderr)
            return 1
        probe_environments: dict[str, Any] = {}
        for adapter_id, value in observations.items():
            probes = [
                item["result"]["data"].get("environment")
                for item in value["invocations"]
                if item["arguments"] == ["probe"] and item["exit"] == 0
            ]
            probe_environments[adapter_id] = probes[0] if probes else None
        normalized_digest = canonical_sha256(reference)
        results_digest = canonical_sha256(suite)
        report = {
            "format": "wayfinder-local-parity-evidence",
            "schemaVersion": 1,
            "scope": f"bounded-adapter-parity-candidate-revision-{contract['candidateRevision']}",
            "status": "passing-local-parity-not-certification",
            "generatedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "package": {
                "releaseId": release["releaseId"],
                "releaseSha256": sha256(release_path),
                "contractVersion": contract["contractVersion"],
                "contractSha256": sha256(contract_path),
                "fixtureIndexSha256": sha256(cases_path),
            },
            "adapters": [
                {
                    "id": item["id"],
                    "path": item["path"],
                    "sha256": item["sha256"],
                    "observedEnvironment": probe_environments[item["id"]],
                    "caseCount": len(suite),
                    "resultsSha256": results_digest,
                }
                for item in adapters
            ],
            "agreement": {
                "caseResultsEqual": True,
                "normalizedInvocationCount": len(reference["invocations"]),
                "normalizedInvocationsSha256": normalized_digest,
                "normalizations": [
                    "physical temporary roots",
                    "adapter and probe environment identity",
                    "contract-open command data and human diagnostic prose",
                    "adapter-bound journal and receipt audit digests",
                ],
                "governedDataAuthority": (
                    "The common 305-case suite separately asserts every frozen command-data projection, "
                    "golden byte artifact, mutation outcome, and stateful filesystem invariant."
                ),
            },
            "summary": {"total": len(suite), "passed": len(suite), "failed": 0},
            "limitations": [
                "This is maintainer-run local adapter parity evidence, not independent validation.",
                "It is not an environment entry or full-family certification.",
                "The later certification matrix, forward tests, cross-adapter recovery tranche, runtime guidance, activation, live-project work, and Git operations remain unperformed.",
            ],
        }
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / f"{stem}.json"
    markdown_path = output / f"{stem}.md"
    markdown = "\n".join([
        f"# Wayfinder candidate revision {contract['candidateRevision']} local adapter parity evidence",
        "", "- **Status:** Passing local parity; not environment or full-family certification",
        f"- **Generated:** {report['generatedAt']}",
        f"- **Release SHA-256:** `{report['package']['releaseSha256']}`",
        f"- **Contract SHA-256:** `{report['package']['contractSha256']}`",
        f"- **Fixture index SHA-256:** `{report['package']['fixtureIndexSha256']}`",
        f"- **Normalized invocation SHA-256:** `{normalized_digest}`",
        "", f"All three adapters passed {len(suite)}/{len(suite)} cases and produced equal normalized invocation observations.",
        "", "## Adapters", "",
        *[f"- `{item['id']}`: `{item['sha256']}`" for item in adapters],
        "", "## Limitations", "", *[f"- {item}" for item in report["limitations"]],
        "", f"See `{stem}.json` for adapter bindings and normalization details.", "",
    ]).encode("utf-8")
    published: list[Path] = []
    try:
        for target, raw in ((json_path, (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")), (markdown_path, markdown)):
            with target.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            published.append(target)
    except Exception:
        for target in published:
            target.unlink(missing_ok=True)
        raise
    print(f"parity-json={json_path}")
    print(f"parity-markdown={markdown_path}")
    return 0


def _matrix_target_id(target: tuple[str, str, str, str]) -> str:
    adapter_id, implementation, version, os_family = target
    return f"{adapter_id}:{implementation}-{version}:{os_family}"


def _print_maintainer_result(ok: bool, code: str, data: dict[str, Any]) -> None:
    print(json.dumps({"ok": ok, "code": code, "data": data}, sort_keys=True, separators=(",", ":")))


def _matrix_failure_summary(results: list[dict[str, Any]], detail_limit: int = 25) -> dict[str, Any]:
    failures = [item for item in results if item.get("status") != "passed"]
    bounded = [
        {
            "id": str(item.get("id", "missing")),
            "category": str(item.get("category", "missing")),
            "rules": [str(rule) for rule in item.get("rules", [])],
            "detail": str(item.get("detail", "no diagnostic supplied"))[:512],
        }
        for item in failures[:detail_limit]
    ]
    return {
        "failedCaseIds": [str(item.get("id", "missing")) for item in failures],
        "failedCases": bounded,
        "failureDetailsTruncated": max(0, len(failures) - len(bounded)),
    }


def _runtime_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        env=command_environment(tempfile.gettempdir()),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(f"runtime observation failed: {(completed.stderr or completed.stdout).strip()}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"runtime observation was not JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("runtime observation was not an object")
    return value


def _runtime_observation(adapter_id: str) -> dict[str, Any]:
    if adapter_id == "python-reference-v1":
        observed = {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "reportedExecutable": sys.executable,
            "runtimeArchitecture": platform.machine(),
            "runtimePlatform": platform.platform(),
            "runtimeLocale": locale.setlocale(locale.LC_ALL, None),
            "runtimeTimezone": dt.datetime.now().astimezone().tzname(),
            "runtimeUtcOffsetSeconds": int((dt.datetime.now().astimezone().utcoffset() or dt.timedelta()).total_seconds()),
        }
        requested = sys.executable
    elif adapter_id == "node-v1":
        requested = os.environ.get("WAYFINDER_NODE_RUNTIME", "node")
        observed = _runtime_json([
            requested,
            "-e",
            (
                "const os=require('node:os');"
                "const z=new Date();"
                "process.stdout.write(JSON.stringify({"
                "implementation:'Node.js',version:process.versions.node,reportedExecutable:process.execPath,"
                "runtimeArchitecture:process.arch,runtimePlatform:process.platform,"
                "runtimeLocale:Intl.DateTimeFormat().resolvedOptions().locale,"
                "runtimeTimezone:Intl.DateTimeFormat().resolvedOptions().timeZone||null,"
                "runtimeUtcOffsetSeconds:-z.getTimezoneOffset()*60,"
                "runtimeOsRelease:os.release(),runtimeOsVersion:os.version(),runtimeOsType:os.type()}));"
            ),
        ])
    elif adapter_id == "powershell-v1":
        requested = os.environ.get("WAYFINDER_POWERSHELL_RUNTIME", "pwsh")
        observed = _runtime_json([
            requested,
            "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
            (
                "$ErrorActionPreference='Stop';"
                "$offset=[System.TimeZoneInfo]::Local.GetUtcOffset([System.DateTimeOffset]::Now);"
                "[ordered]@{implementation='PowerShell';version=$PSVersionTable.PSVersion.ToString();"
                "reportedExecutable=(Get-Process -Id $PID).Path;"
                "runtimeArchitecture=[System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture.ToString().ToLowerInvariant();"
                "runtimePlatform=$PSVersionTable.Platform;"
                "runtimeLocale=[System.Globalization.CultureInfo]::CurrentCulture.Name;"
                "runtimeUiLocale=[System.Globalization.CultureInfo]::CurrentUICulture.Name;"
                "runtimeTimezone=[System.TimeZoneInfo]::Local.Id;"
                "runtimeUtcOffsetSeconds=[int]$offset.TotalSeconds;"
                "runtimeOsVersion=[System.Runtime.InteropServices.RuntimeInformation]::OSDescription}"
                "|ConvertTo-Json -Compress"
            ),
        ])
    else:
        raise ValueError(f"unknown matrix adapter: {adapter_id}")

    requested_path = Path(requested)
    located = str(requested_path) if requested_path.is_absolute() or requested_path.parent != Path(".") else shutil.which(requested)
    if not located:
        raise ValueError(f"runtime executable is unavailable: {requested}")
    resolved = Path(located).resolve(strict=True)
    reported = Path(str(observed.get("reportedExecutable", ""))).resolve(strict=True)
    observed["executableIdentity"] = {
        "requested": requested,
        "resolvedPath": str(resolved),
        "reportedPath": str(reported),
        "reportedPathMatchesResolved": reported == resolved,
        "sha256": sha256(resolved),
        "byteLength": resolved.stat().st_size,
    }
    return observed


def _operating_system_observation() -> dict[str, Any]:
    system = platform.system()
    family = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}.get(system, system or "unavailable")
    version_parts: dict[str, Any] = {
        "release": platform.release() or "unavailable",
        "version": platform.version() or "unavailable",
    }
    if family == "macOS":
        version_parts["macVersion"] = platform.mac_ver()[0] or "unavailable"
    elif family == "Windows":
        win = platform.win32_ver()
        version_parts["windowsVersion"] = win[0] or "unavailable"
        version_parts["windowsBuild"] = win[1] or "unavailable"
    return {
        "family": family,
        "system": system or "unavailable",
        "details": version_parts,
        "hostArchitecture": platform.machine() or "unavailable",
    }


def _filesystem_observation() -> dict[str, Any]:
    unavailable: list[str] = []
    with tempfile.TemporaryDirectory(prefix="wayfinder-matrix-filesystem-") as raw_root:
        root = Path(raw_root)
        first = root / "WayfinderCaseProbe"
        alias = root / "wayfindercaseprobe"
        with first.open("xb") as handle:
            handle.write(b"first")
        try:
            with alias.open("xb") as handle:
                handle.write(b"second")
            behavior = "case-sensitive"
        except FileExistsError:
            behavior = "case-insensitive"
        names = sorted(os.listdir(root))
        if behavior == "case-sensitive" and not ({first.name, alias.name} <= set(names)):
            raise ValueError("filesystem case probe created distinct files but did not enumerate both names")
        if behavior == "case-insensitive" and alias.read_bytes() != b"first":
            raise ValueError("filesystem case alias did not resolve to the exclusively created file")
        unicode_name = "wayfinder-é-probe"
        unicode_path = root / unicode_name
        with unicode_path.open("xb") as handle:
            handle.write(b"unicode")
        unicode_round_trip = unicode_name in os.listdir(root) and unicode_path.read_bytes() == b"unicode"
        stat_result = root.stat()
        statvfs: dict[str, Any] | str
        try:
            vfs = os.statvfs(root)
            statvfs = {
                "blockSize": vfs.f_bsize,
                "fragmentSize": vfs.f_frsize,
                "nameMaximum": vfs.f_namemax,
            }
        except (AttributeError, OSError):
            statvfs = "unavailable"
            unavailable.append("statvfs characteristics are unavailable on this host")
        unavailable.append("the Python standard library does not expose a portable filesystem type or stable volume serial")
        return {
            "temporaryDirectoryParent": str(Path(tempfile.gettempdir()).resolve()),
            "deviceId": str(stat_result.st_dev),
            "statvfs": statvfs,
            "encoding": sys.getfilesystemencoding(),
            "encodingErrors": sys.getfilesystemencodeerrors(),
            "unicodeFilenameRoundTrip": unicode_round_trip,
            "unicodeFilenameUtf8Hex": unicode_name.encode("utf-8").hex(),
            "caseBehavior": behavior,
            "caseProbe": {
                "firstExclusiveCreate": "created",
                "caseVariantExclusiveCreate": "created" if behavior == "case-sensitive" else "refused-existing",
                "enumeratedNames": names,
            },
            "unavailableObservations": unavailable,
        }


def _execution_provenance() -> dict[str, Any]:
    fields = {
        "sourceRepository": os.environ.get("GITHUB_REPOSITORY"),
        "sourceCommit": os.environ.get("GITHUB_SHA"),
        "workflowName": os.environ.get("GITHUB_WORKFLOW"),
        "workflowRunId": os.environ.get("GITHUB_RUN_ID"),
        "workflowRunAttempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "runnerName": os.environ.get("RUNNER_NAME"),
        "runnerEnvironment": os.environ.get("RUNNER_ENVIRONMENT"),
        "runnerImage": os.environ.get("ImageOS"),
        "runnerImageVersion": os.environ.get("ImageVersion"),
    }
    return {
        **{name: value if value else "unavailable" for name, value in fields.items()},
        "unavailableObservations": [name for name, value in fields.items() if not value],
    }


def _matrix_package_issues(adapter_id: str) -> tuple[list[str], dict[str, Any], dict[str, Any], Path]:
    issues: list[str] = []
    release_path = SKILL_ROOT / "assets/contract-v1/release.json"
    contract_path = SKILL_ROOT / "assets/contract-v1/contract.json"
    cases_path = CONFORMANCE_ROOT / "cases.json"
    release = load_json(release_path)
    contract = load_json(contract_path)
    actual_bindings = {
        "releaseId": release["releaseId"],
        "releaseSha256": sha256(release_path),
        "contractVersion": contract["contractVersion"],
        "contractSha256": sha256(contract_path),
        "fixtureIndexSha256": sha256(cases_path),
        "expectedOutputsSha256": expected_outputs_sha256(contract),
    }
    if actual_bindings != ACCEPTED_MATRIX_BINDINGS:
        issues.append("accepted candidate/package bindings differ")
    registered = {item["id"]: item for item in release.get("adapters", [])}
    if set(registered) != set(ACCEPTED_ADAPTER_DIGESTS):
        issues.append("registered adapter set differs")
    adapter = registered.get(adapter_id)
    if adapter is None:
        issues.append(f"adapter is not registered: {adapter_id}")
        adapter_path_value = SKILL_ROOT / "missing-adapter"
    else:
        adapter_path_value = SKILL_ROOT / adapter["path"]
        expected_digest = ACCEPTED_ADAPTER_DIGESTS.get(adapter_id)
        if adapter.get("sha256") != expected_digest or not adapter_path_value.is_file() or sha256(adapter_path_value) != expected_digest:
            issues.append(f"registered adapter digest differs: {adapter_id}")
    package_check = run_python(PACKAGE_BUILDER, ["--check"], capture=True)
    if package_check.returncode != 0:
        issues.append(f"package verification failed: {(package_check.stdout + package_check.stderr).strip()}")
    pinned = load_json(HISTORICAL_HASHES)["files"]
    if any(not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest for name, digest in pinned.items()):
        issues.append("historical evidence digest differs")
    if any(
        not (CERTIFICATION_ROOT / name).is_file() or sha256(CERTIFICATION_ROOT / name) != digest
        for name, digest in ACCEPTED_PARITY_EVIDENCE_DIGESTS.items()
    ):
        issues.append("accepted parity evidence digest differs")
    return issues, actual_bindings, adapter or {}, adapter_path_value


def _matrix_result_set_sha256(package: dict[str, Any], results: list[dict[str, Any]]) -> str:
    basis = {
        "releaseId": package["releaseId"],
        "releaseSha256": package["releaseSha256"],
        "contractVersion": package["contractVersion"],
        "contractSha256": package["contractSha256"],
        "adapterId": package["adapterId"],
        "adapterSha256": package["adapterSha256"],
        "fixtureIndexSha256": package["fixtureIndexSha256"],
        "expectedOutputsSha256": package["expectedOutputsSha256"],
        "results": results,
    }
    return canonical_sha256(basis)


def _write_exclusive_pair(json_path: Path, markdown_path: Path, report: dict[str, Any], markdown: bytes) -> None:
    published: list[Path] = []
    try:
        for target, raw in (
            (json_path, (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")),
            (markdown_path, markdown),
        ):
            with target.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            published.append(target)
    except Exception:
        for target in published:
            target.unlink(missing_ok=True)
        raise


def _matrix_entry_markdown(report: dict[str, Any], json_digest: str) -> bytes:
    target = report["target"]
    environment = report["environment"]
    runtime = environment["runtime"]
    filesystem = environment["filesystem"]
    package = report["package"]
    provenance = report["executionProvenance"]
    summary = report["summary"]
    lines = [
        f"# Wayfinder revision 9 environment evidence — {target['adapterId']} on {target['operatingSystemFamily']}",
        "",
        f"- **Status:** {report['status']}",
        f"- **Generated:** {report['generatedAt']}",
        f"- **JSON report SHA-256:** `{json_digest}`",
        f"- **Result-set SHA-256:** `{report['resultSetSha256']}`",
        "",
        "## Exact target and observed environment",
        "",
        "| Field | Required | Observed |",
        "| --- | --- | --- |",
        f"| Adapter | `{target['adapterId']}` | `{package['adapterId']}` |",
        f"| Runtime | `{target['runtimeImplementation']} {target['runtimeVersion']}` | `{runtime['implementation']} {runtime['version']}` |",
        f"| OS family | `{target['operatingSystemFamily']}` | `{environment['operatingSystem']['family']}` |",
        f"| Architecture | — | `{runtime['runtimeArchitecture']}` (host `{environment['operatingSystem']['hostArchitecture']}`) |",
        f"| Locale | — | `{environment['locale']['effective']}` |",
        f"| Timezone | — | `{environment['timezone']['effectiveName']}` (UTC offset {environment['timezone']['effectiveUtcOffsetSeconds']} seconds) |",
        f"| Filesystem encoding | — | `{filesystem['encoding']}` with `{filesystem['encodingErrors']}` errors |",
        f"| Filesystem case behavior | matrix requires both collectively | `{filesystem['caseBehavior']}` (observed by exclusive create) |",
        f"| Runtime executable | exact identity required | `{runtime['executableIdentity']['resolvedPath']}` (`{runtime['executableIdentity']['sha256']}`) |",
        f"| Source commit | exact workflow checkout | `{provenance['sourceCommit']}` |",
        f"| Workflow run | hosted provenance | `{provenance['workflowRunId']}` attempt `{provenance['workflowRunAttempt']}` |",
        "",
        "## Conformance and bindings",
        "",
        f"- Cases: {summary['passed']}/{summary['total']} passed; {summary['failed']} failed.",
        f"- Contract: `{package['contractSha256']}`",
        f"- Release: `{package['releaseSha256']}`",
        f"- Adapter: `{package['adapterSha256']}`",
        f"- Fixture index: `{package['fixtureIndexSha256']}`",
        f"- Expected-output set: `{package['expectedOutputsSha256']}`",
        f"- Invocation observations: {report['invocations']['count']} at `{report['invocations']['sha256']}`",
        "",
    ]
    failures = _matrix_failure_summary(report["results"])
    if failures["failedCaseIds"]:
        lines.extend(["## Failed cases", ""])
        for item in failures["failedCases"]:
            rules = ", ".join(f"`{rule}`" for rule in item["rules"])
            lines.append(f"- `{item['id']}` ({item['category']}; {rules}): {item['detail']}")
        if failures["failureDetailsTruncated"]:
            lines.append(f"- {failures['failureDetailsTruncated']} additional failure diagnostics are present in the JSON report.")
        lines.append("")
    lines.extend(["## Limitations and unavailable observations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def matrix_entry_command(adapter_id: str, operating_system_family: str, output: Path) -> int:
    targets = [target for target in MATRIX_TARGETS if target[0] == adapter_id and target[3] == operating_system_family]
    if len(targets) != 1:
        _print_maintainer_result(False, "matrix.unknown-target", {"adapterId": adapter_id, "operatingSystemFamily": operating_system_family})
        return 2
    target = targets[0]
    if output.is_symlink():
        _print_maintainer_result(False, "matrix.output-symlink", {"output": str(output)})
        return 2
    try:
        issues, bindings, adapter, selected_adapter_path = _matrix_package_issues(adapter_id)
        runtime = _runtime_observation(adapter_id)
        operating_system = _operating_system_observation()
        filesystem = _filesystem_observation()
    except Exception as exc:
        _print_maintainer_result(False, "matrix.environment-unavailable", {"target": _matrix_target_id(target), "detail": str(exc)})
        return 2
    expected_implementation, expected_version = target[1], target[2]
    if runtime.get("implementation") != expected_implementation:
        issues.append(f"runtime implementation required={expected_implementation} observed={runtime.get('implementation')}")
    if runtime.get("version") != expected_version:
        issues.append(f"runtime version required={expected_version} observed={runtime.get('version')}")
    if operating_system["family"] != operating_system_family:
        issues.append(f"OS family required={operating_system_family} observed={operating_system['family']}")
    if runtime["executableIdentity"]["reportedPathMatchesResolved"] is not True:
        issues.append("runtime-reported executable does not match the resolved invoked executable")
    if not runtime.get("runtimeArchitecture") or runtime.get("runtimeArchitecture") == "unavailable":
        issues.append("runtime architecture is unavailable")
    if not filesystem.get("encoding") or filesystem.get("unicodeFilenameRoundTrip") is not True:
        issues.append("filesystem encoding or Unicode filename round trip is unavailable")
    if filesystem.get("caseBehavior") not in {"case-sensitive", "case-insensitive"}:
        issues.append("filesystem case behavior was not established")
    probe = run_adapter(selected_adapter_path, ["probe"], capture=True) if not issues else None
    if probe is not None:
        try:
            probe_result = json.loads(probe.stdout)
            probe_adapter = probe_result.get("data", {}).get("adapter", {})
            if probe.returncode != 0 or probe_result.get("ok") is not True or probe_adapter.get("id") != adapter_id:
                issues.append("registered adapter probe did not verify the selected adapter")
        except Exception as exc:
            issues.append(f"registered adapter probe was invalid: {exc}")
    if issues:
        _print_maintainer_result(False, "matrix.environment-mismatch", {"target": _matrix_target_id(target), "issues": issues})
        return 2

    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cases_path = CONFORMANCE_ROOT / "cases.json"
    case_index = load_json(cases_path)["cases"]
    with tempfile.TemporaryDirectory(prefix="wayfinder-matrix-observations-") as raw_temporary:
        observation_path = Path(raw_temporary) / "observations.json"
        completed = run_python(
            CONFORMANCE_RUNNER,
            ["--adapter", str(selected_adapter_path), "--observations", str(observation_path)],
            capture=True,
        )
        if not observation_path.is_file():
            _print_maintainer_result(False, "matrix.suite-no-results", {"target": _matrix_target_id(target), "detail": (completed.stderr or completed.stdout).strip()})
            return 1
        observations = load_json(observation_path)
    results = observations.get("results", [])
    expected_ids = [item["id"] for item in case_index]
    complete_suite = (
        len(results) == len(case_index) == 305
        and [item.get("id") for item in results] == expected_ids
    )
    passed = complete_suite and completed.returncode == 0 and all(item.get("status") == "passed" for item in results)
    counts = Counter(item.get("category") for item in results)
    expected_negative = [item["id"] for item in case_index if item["exit"] != 0]
    negative_passed = [item["id"] for item in results if item.get("id") in set(expected_negative) and item.get("status") == "passed"]
    interruption_ids = ["apply-failure-boundary-matrix", "apply-rollback-boundary-matrix", "apply-rollback-interrupted"]
    result_by_id = {item.get("id"): item.get("status") for item in results}
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    package = {
        **bindings,
        "adapterId": adapter_id,
        "adapterPath": adapter["path"],
        "adapterSha256": adapter["sha256"],
    }
    result_set_digest = _matrix_result_set_sha256(package, results)
    locale_observation = {
        "environment": {key: os.environ.get(key) or "unset" for key in ("LC_ALL", "LC_CTYPE", "LANG")},
        "effective": locale.setlocale(locale.LC_ALL, None),
        "preferredEncoding": locale.getpreferredencoding(False),
        "runtime": runtime.get("runtimeLocale") or "unavailable",
    }
    timezone_observation = {
        "environmentTZ": os.environ.get("TZ") or "unset-host-default",
        "effectiveName": dt.datetime.now().astimezone().tzname() or "unavailable",
        "effectiveUtcOffsetSeconds": int((dt.datetime.now().astimezone().utcoffset() or dt.timedelta()).total_seconds()),
        "runtimeName": runtime.get("runtimeTimezone") or "unavailable",
        "runtimeUtcOffsetSeconds": runtime.get("runtimeUtcOffsetSeconds", "unavailable"),
    }
    execution_provenance = _execution_provenance()
    limitations = [
        "This is maintainer-run evidence for one exact matrix entry, not independent validation.",
        "This environment report is not the aggregate matrix and is not full-family certification.",
        "It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.",
        *filesystem["unavailableObservations"],
        *[
            f"Execution provenance field {name} is unavailable in this environment."
            for name in execution_provenance["unavailableObservations"]
        ],
    ]
    report = {
        "format": "wayfinder-environment-certification-evidence",
        "schemaVersion": 1,
        "scope": "bounded-certification-matrix-candidate-revision-9",
        "status": "passing-environment-entry-not-full-family-certification" if passed else "failing-environment-entry",
        "generatedAt": generated_at.isoformat().replace("+00:00", "Z"),
        "target": {
            "adapterId": target[0],
            "runtimeImplementation": target[1],
            "runtimeVersion": target[2],
            "operatingSystemFamily": target[3],
        },
        "package": package,
        "environment": {
            "runtime": runtime,
            "operatingSystem": operating_system,
            "locale": locale_observation,
            "timezone": timezone_observation,
            "filesystem": filesystem,
        },
        "executionProvenance": execution_provenance,
        "summary": {
            "total": len(results),
            "passed": sum(item.get("status") == "passed" for item in results),
            "failed": sum(item.get("status") != "passed" for item in results),
            "completeRegisteredSuite": complete_suite,
            "byCategory": dict(sorted(counts.items())),
            "negativeAndMutationCases": {
                "required": len(expected_negative),
                "passed": len(negative_passed),
                "caseIdsSha256": canonical_sha256(expected_negative),
            },
            "interruptionBoundaryCases": {case_id: result_by_id.get(case_id, "missing") for case_id in interruption_ids},
        },
        "resultSetSha256": result_set_digest,
        "results": results,
        "invocations": {
            "count": len(observations.get("invocations", [])),
            "sha256": canonical_sha256(observations.get("invocations", [])),
        },
        "expiryConditions": [
            "candidate, contract, release, adapter, fixture-index, expected-output, or result-set binding changes",
            "runtime implementation or exact version changes",
            "operating-system family or version changes",
            "architecture, locale, timezone, filesystem encoding, or filesystem case behavior changes",
        ],
        "limitations": limitations,
    }
    timestamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    stem = f"matrix-revision-9-{adapter_id}-{operating_system_family.lower()}-{timestamp}"
    json_path = output / f"{stem}.json"
    markdown_path = output / f"{stem}.md"
    if json_path.exists() or json_path.is_symlink() or markdown_path.exists() or markdown_path.is_symlink():
        _print_maintainer_result(False, "matrix.evidence-exists", {"json": str(json_path), "markdown": str(markdown_path)})
        return 2
    json_raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    json_digest = hashlib.sha256(json_raw).hexdigest()
    _write_exclusive_pair(json_path, markdown_path, report, _matrix_entry_markdown(report, json_digest))
    result_data = {
        "target": _matrix_target_id(target),
        "status": report["status"],
        "json": str(json_path),
        "jsonSha256": sha256(json_path),
        "markdown": str(markdown_path),
        "markdownSha256": sha256(markdown_path),
        "resultSetSha256": result_set_digest,
        "summary": report["summary"],
        **_matrix_failure_summary(results),
    }
    _print_maintainer_result(passed, "ok" if passed else "matrix.entry-failed", result_data)
    return 0 if passed else 1


def _matrix_report_issues(path: Path, report: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if report.get("format") != "wayfinder-environment-certification-evidence" or report.get("schemaVersion") != 1:
        issues.append(f"{path}: report identity")
        return issues
    target_value = report.get("target", {})
    target = (
        target_value.get("adapterId"), target_value.get("runtimeImplementation"),
        target_value.get("runtimeVersion"), target_value.get("operatingSystemFamily"),
    )
    if target not in MATRIX_TARGETS:
        issues.append(f"{path}: target is not required")
    package = report.get("package", {})
    expected_package = {
        **ACCEPTED_MATRIX_BINDINGS,
        "adapterId": target[0],
        "adapterPath": next((item["path"] for item in load_json(SKILL_ROOT / "assets/contract-v1/release.json")["adapters"] if item["id"] == target[0]), ""),
        "adapterSha256": ACCEPTED_ADAPTER_DIGESTS.get(target[0]),
    }
    if package != expected_package:
        issues.append(f"{path}: package binding differs")
    results = report.get("results", [])
    if not isinstance(results, list) or report.get("resultSetSha256") != _matrix_result_set_sha256(package, results):
        issues.append(f"{path}: result-set digest differs")
    summary = report.get("summary", {})
    if (
        report.get("status") != "passing-environment-entry-not-full-family-certification"
        or summary.get("total") != 305 or summary.get("passed") != 305 or summary.get("failed") != 0
        or summary.get("completeRegisteredSuite") is not True
    ):
        issues.append(f"{path}: entry is not passing 305/305")
    environment = report.get("environment", {})
    if environment.get("runtime", {}).get("implementation") != target[1] or environment.get("runtime", {}).get("version") != target[2]:
        issues.append(f"{path}: runtime observation differs")
    if environment.get("operatingSystem", {}).get("family") != target[3]:
        issues.append(f"{path}: OS observation differs")
    if environment.get("filesystem", {}).get("caseBehavior") not in {"case-sensitive", "case-insensitive"}:
        issues.append(f"{path}: filesystem case behavior unavailable")
    return issues


def matrix_aggregate_command(entries: list[Path], output: Path) -> int:
    reports: dict[tuple[str, str, str, str], tuple[Path, dict[str, Any]]] = {}
    issues: list[str] = []
    for entry in entries:
        path = entry.resolve()
        if not path.is_file() or path.is_symlink():
            issues.append(f"{entry}: entry is missing or symbolic")
            continue
        try:
            report = load_json(path)
            report_issues = _matrix_report_issues(path, report)
        except Exception as exc:
            issues.append(f"{entry}: {exc}")
            continue
        issues.extend(report_issues)
        target_value = report.get("target", {})
        target = (
            target_value.get("adapterId"), target_value.get("runtimeImplementation"),
            target_value.get("runtimeVersion"), target_value.get("operatingSystemFamily"),
        )
        if target in reports:
            issues.append(f"duplicate matrix entry: {_matrix_target_id(target)}")
        else:
            reports[target] = (path, report)
    if issues:
        _print_maintainer_result(False, "matrix.invalid-entry", {"issues": issues})
        return 2
    missing = [target for target in MATRIX_TARGETS if target not in reports]
    behaviors = sorted({report["environment"]["filesystem"]["caseBehavior"] for _, report in reports.values()})
    if missing or set(behaviors) != {"case-sensitive", "case-insensitive"}:
        _print_maintainer_result(False, "matrix.incomplete", {
            "passing": [_matrix_target_id(target) for target in MATRIX_TARGETS if target in reports],
            "missing": [_matrix_target_id(target) for target in missing],
            "observedFilesystemBehaviors": behaviors,
            "requiredFilesystemBehaviors": ["case-sensitive", "case-insensitive"],
            "aggregateWritten": False,
        })
        return 2
    if output.is_symlink():
        _print_maintainer_result(False, "matrix.output-symlink", {"output": str(output)})
        return 2
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    stem = "matrix-revision-9-aggregate"
    json_path = output / f"{stem}.json"
    markdown_path = output / f"{stem}.md"
    if json_path.exists() or json_path.is_symlink() or markdown_path.exists() or markdown_path.is_symlink():
        _print_maintainer_result(False, "matrix.evidence-exists", {"json": str(json_path), "markdown": str(markdown_path)})
        return 2
    entry_bindings = [
        {
            "target": _matrix_target_id(target),
            "path": str(path.relative_to(REPOSITORY_ROOT)) if path.is_relative_to(REPOSITORY_ROOT) else str(path),
            "sha256": sha256(path),
            "resultSetSha256": report["resultSetSha256"],
            "filesystemCaseBehavior": report["environment"]["filesystem"]["caseBehavior"],
        }
        for target in MATRIX_TARGETS
        for path, report in [reports[target]]
    ]
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    aggregate_digest = canonical_sha256({"package": ACCEPTED_MATRIX_BINDINGS, "adapters": ACCEPTED_ADAPTER_DIGESTS, "entries": entry_bindings})
    report = {
        "format": "wayfinder-certification-matrix-evidence",
        "schemaVersion": 1,
        "scope": "bounded-certification-matrix-candidate-revision-9",
        "status": "passing-bounded-matrix-not-full-family-certification",
        "generatedAt": generated_at,
        "package": ACCEPTED_MATRIX_BINDINGS,
        "adapters": ACCEPTED_ADAPTER_DIGESTS,
        "entries": entry_bindings,
        "filesystemCaseBehaviors": behaviors,
        "matrixSha256": aggregate_digest,
        "limitations": [
            "This aggregate covers only the bounded eight-entry environment matrix.",
            "It is not independent evaluation or full-family certification.",
            "It does not include forward tests, cross-adapter recovery, runtime guidance, activation, live-project work, or Git operations.",
            "It does not create release certification entries or authorize activation.",
        ],
    }
    json_raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    json_digest = hashlib.sha256(json_raw).hexdigest()
    markdown_lines = [
        "# Wayfinder candidate revision 9 bounded certification matrix",
        "",
        "- **Status:** Passing bounded matrix; not full-family certification",
        f"- **Generated:** {generated_at}",
        f"- **JSON report SHA-256:** `{json_digest}`",
        f"- **Matrix SHA-256:** `{aggregate_digest}`",
        "",
        "All eight exact runtime/OS entries passed 305/305 cases and collectively observed case-sensitive and case-insensitive filesystems.",
        "",
        "## Entries",
        "",
        *[f"- `{item['target']}` — `{item['sha256']}` — `{item['filesystemCaseBehavior']}`" for item in entry_bindings],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report["limitations"]],
        "",
    ]
    _write_exclusive_pair(json_path, markdown_path, report, "\n".join(markdown_lines).encode("utf-8"))
    _print_maintainer_result(True, "ok", {
        "json": str(json_path), "jsonSha256": sha256(json_path),
        "markdown": str(markdown_path), "markdownSha256": sha256(markdown_path),
        "matrixSha256": aggregate_digest,
    })
    return 0


def _review_matrix_report(path: Path, report: dict[str, Any]) -> tuple[tuple[str, str, str, str] | None, list[str]]:
    issues: list[str] = []
    if report.get("format") != "wayfinder-environment-certification-evidence" or report.get("schemaVersion") != 1:
        return None, [f"{path}: report identity"]
    target_value = report.get("target", {})
    target = (
        target_value.get("adapterId"), target_value.get("runtimeImplementation"),
        target_value.get("runtimeVersion"), target_value.get("operatingSystemFamily"),
    )
    if target not in MATRIX_TARGETS:
        issues.append(f"{path}: target is not required")
    package = report.get("package", {})
    expected_adapter_path = next(
        (item["path"] for item in load_json(SKILL_ROOT / "assets/contract-v1/release.json")["adapters"] if item["id"] == target[0]),
        "",
    )
    expected_package = {
        **ACCEPTED_MATRIX_BINDINGS,
        "adapterId": target[0],
        "adapterPath": expected_adapter_path,
        "adapterSha256": ACCEPTED_ADAPTER_DIGESTS.get(target[0]),
    }
    if package != expected_package:
        issues.append(f"{path}: package or registered-adapter binding differs")
    case_index = load_json(CONFORMANCE_ROOT / "cases.json")["cases"]
    results = report.get("results")
    expected_ids = [case["id"] for case in case_index]
    if not isinstance(results, list) or len(results) != 305 or [item.get("id") for item in results] != expected_ids:
        issues.append(f"{path}: result set is not the exact ordered 305-case suite")
        results = results if isinstance(results, list) else []
    elif report.get("resultSetSha256") != _matrix_result_set_sha256(package, results):
        issues.append(f"{path}: result-set digest differs")
    summary = report.get("summary", {})
    passed = sum(item.get("status") == "passed" for item in results)
    failed = len(results) - passed
    expected_by_category = dict(sorted(Counter(case["category"] for case in case_index).items()))
    expected_negative = [case["id"] for case in case_index if case["exit"] != 0]
    negative_passed = sum(
        item.get("id") in set(expected_negative) and item.get("status") == "passed" for item in results
    )
    negative = summary.get("negativeAndMutationCases", {})
    interruptions = summary.get("interruptionBoundaryCases", {})
    interruption_ids = ("apply-failure-boundary-matrix", "apply-rollback-boundary-matrix", "apply-rollback-interrupted")
    if (
        summary.get("total") != len(results)
        or summary.get("passed") != passed
        or summary.get("failed") != failed
        or summary.get("completeRegisteredSuite") is not True
        or summary.get("byCategory") != expected_by_category
        or negative != {
            "required": len(expected_negative),
            "passed": negative_passed,
            "caseIdsSha256": canonical_sha256(expected_negative),
        }
        or set(interruptions) != set(interruption_ids)
    ):
        issues.append(f"{path}: coverage metadata differs")
    invocations = report.get("invocations")
    if (
        not isinstance(invocations, dict)
        or set(invocations) != {"count", "sha256"}
        or not isinstance(invocations.get("count"), int)
        or not re.fullmatch(r"[0-9a-f]{64}", str(invocations.get("sha256", "")))
        or invocations.get("sha256") == report.get("resultSetSha256")
    ):
        issues.append(f"{path}: aggregate invocation digest metadata is missing or conflated with results")
    provenance = report.get("executionProvenance", {})
    for name in ("sourceRepository", "sourceCommit", "workflowRunId", "workflowRunAttempt"):
        if provenance.get(name) in {None, "", "unavailable"}:
            issues.append(f"{path}: execution provenance {name} is unavailable")
    return target if target in MATRIX_TARGETS else None, issues


def _recorded_report_basename(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\0" in value or value.endswith(("/", "\\")):
        return None
    basename = re.split(r"[\\/]", value)[-1]
    if basename in {"", ".", ".."}:
        return None
    return basename


def _local_report_matches(root: Path, basename: str | None) -> list[Path]:
    if basename is None:
        return []
    return [path for path in root.rglob(basename) if path.is_file() and not path.is_symlink()]


def matrix_review_command(artifact_dir: Path, output_format: str) -> int:
    root = artifact_dir.resolve()
    if not root.is_dir() or artifact_dir.is_symlink():
        _print_maintainer_result(False, "matrix.review-invalid-input", {"artifactDirectory": str(artifact_dir)})
        return 2
    reports: dict[tuple[str, str, str, str], tuple[Path, dict[str, Any]]] = {}
    statuses: list[tuple[Path, dict[str, Any]]] = []
    issues: list[str] = []
    for path in sorted(root.rglob("*.json")):
        if path.is_symlink():
            issues.append(f"{path}: symbolic JSON input")
            continue
        try:
            value = load_json(path)
        except Exception as exc:
            issues.append(f"{path}: {exc}")
            continue
        if value.get("format") == "wayfinder-environment-certification-evidence":
            target, report_issues = _review_matrix_report(path, value)
            issues.extend(report_issues)
            if target is not None:
                if target in reports:
                    issues.append(f"duplicate matrix report: {_matrix_target_id(target)}")
                else:
                    reports[target] = (path, value)
        elif value.get("format") == "wayfinder-matrix-execution-status":
            statuses.append((path, value))
    missing = [target for target in MATRIX_TARGETS if target not in reports]
    if missing:
        issues.append("missing matrix reports: " + ", ".join(_matrix_target_id(target) for target in missing))
    status_by_target: dict[tuple[str, str], tuple[Path, dict[str, Any]]] = {}
    for path, status in statuses:
        key = (status.get("adapterId"), status.get("operatingSystemFamily"))
        if status.get("format") != "wayfinder-matrix-execution-status" or status.get("schemaVersion") != 1:
            issues.append(f"{path}: execution status identity")
        if key in status_by_target:
            issues.append(f"duplicate execution status: {key}")
        status_by_target[key] = (path, status)
    failing: dict[str, list[str]] = {}
    sources: set[tuple[str, str, str]] = set()
    for target, (report_path, report) in reports.items():
        status_pair = status_by_target.get((target[0], target[3]))
        if status_pair is None:
            issues.append(f"{report_path}: matching execution status is missing")
            continue
        status_path, execution = status_pair
        provenance = report.get("executionProvenance", {})
        source_binding = (
            str(execution.get("sourceCommit")), str(execution.get("workflowRunId")), str(execution.get("workflowRunAttempt"))
        )
        sources.add(source_binding)
        if source_binding != (
            str(provenance.get("sourceCommit")), str(provenance.get("workflowRunId")), str(provenance.get("workflowRunAttempt"))
        ):
            issues.append(f"{status_path}: source/run binding differs from report")
        try:
            command_result = json.loads(execution.get("stdout", ""))
        except Exception as exc:
            issues.append(f"{status_path}: maintainer result is not JSON: {exc}")
            command_result = {}
        data = command_result.get("data", {}) if isinstance(command_result, dict) else {}
        if not isinstance(data, dict):
            issues.append(f"{status_path}: maintainer result data is not an object")
            data = {}
        json_name = _recorded_report_basename(data.get("json"))
        json_matches = _local_report_matches(root, json_name)
        if json_name is None:
            issues.append(f"{status_path}: recorded JSON report path is malformed or empty")
        elif len(json_matches) != 1 or json_matches[0] != report_path:
            issues.append(f"{report_path}: recorded JSON report basename is missing or ambiguous")
        if data.get("jsonSha256") != sha256(report_path):
            issues.append(f"{report_path}: report hash differs from execution status")
        markdown_name = _recorded_report_basename(data.get("markdown"))
        markdown_matches = _local_report_matches(root, markdown_name)
        if markdown_name is None:
            issues.append(f"{status_path}: recorded Markdown report path is malformed or empty")
        elif len(markdown_matches) != 1:
            issues.append(f"{report_path}: recorded Markdown report basename is missing or ambiguous")
        elif data.get("markdownSha256") != sha256(markdown_matches[0]):
            issues.append(f"{report_path}: Markdown report hash differs or is unavailable")
        failed_ids = [item["id"] for item in report.get("results", []) if item.get("status") != "passed"]
        if failed_ids:
            failing[_matrix_target_id(target)] = failed_ids
    if len(sources) != 1:
        issues.append("matrix reports do not share one exact source commit/workflow run/attempt")
    result = {
        "format": "wayfinder-matrix-artifact-review",
        "schemaVersion": 1,
        "ok": not issues,
        "classification": "GitHub Actions material; review-only; not accepted evidence",
        "artifactDirectory": str(root),
        "sourceRunBindings": [
            {"sourceCommit": source, "workflowRunId": run, "workflowRunAttempt": attempt}
            for source, run, attempt in sorted(sources)
        ],
        "reports": len(reports),
        "executionStatuses": len(statuses),
        "registeredAdapters": ACCEPTED_ADAPTER_DIGESTS,
        "failingCasesByEnvironment": failing,
        "issues": issues,
        "writesPerformed": False,
        "promotionPerformed": False,
    }
    if output_format == "json":
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    elif output_format == "markdown":
        print("# Wayfinder matrix artifact review\n")
        print(f"- Status: {'valid review material' if not issues else 'invalid'}.")
        print("- Classification: GitHub Actions material; review-only; not accepted evidence.")
        print(f"- Reports: {len(reports)}; execution statuses: {len(statuses)}.")
        print("- Writes or promotion: none.")
        if failing:
            print("\n## Failing cases by environment\n")
            for environment, case_ids in sorted(failing.items()):
                print(f"- `{environment}`: {', '.join(f'`{case_id}`' for case_id in case_ids)}")
        if issues:
            print("\n## Review issues\n")
            for issue in issues:
                print(f"- {issue}")
    else:
        print(
            f"{'OK' if not issues else 'FAIL'} matrix-review reports={len(reports)} statuses={len(statuses)} "
            f"failing-environments={len(failing)} issues={len(issues)} review-only=true writes=0"
        )
    return 0 if not issues else 2


def expect_command(expected_exit: int, expected_code: str, command: list[str]) -> int:
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("expect requires a command after --", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="wayfinder-maintainer-cache-") as cache_root:
        completed = subprocess.run(
            command,
            cwd=REPOSITORY_ROOT,
            env=command_environment(cache_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    try:
        result = json.loads(completed.stdout)
        actual_code = result.get("code")
    except (json.JSONDecodeError, AttributeError):
        actual_code = None
    passed = completed.returncode == expected_exit and actual_code == expected_code
    print(f"target-exit={completed.returncode} target-code={actual_code}")
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    print(f"expectation={'passed' if passed else 'failed'}")
    return 0 if passed else 1


def handoff_command(kind: str, objective: str, exclusions: list[str]) -> int:
    if doctor("quiet") != 0:
        print("maintainer doctor failed; handoff not generated", file=sys.stderr)
        return 1
    contract_path = SKILL_ROOT / "assets/contract-v1/contract.json"
    release_path = SKILL_ROOT / "assets/contract-v1/release.json"
    cases_path = CONFORMANCE_ROOT / "cases.json"
    contract = load_json(contract_path)
    release = load_json(release_path)
    cases = load_json(cases_path)["cases"]
    counts = Counter(case["category"] for case in cases)
    print("Continue maintaining Wayfinder with:")
    print(f"\n{COMPANION_ROOT}\n")
    print("Objective\n")
    print(objective)
    print("\nCurrent candidate\n")
    print(f"- Release: `{release['releaseId']}`")
    print(f"- Candidate revision: `{contract['candidateRevision']}`")
    print(f"- Contract SHA-256: `{sha256(contract_path)}`")
    print(f"- Release SHA-256: `{sha256(release_path)}`")
    print(f"- Conformance cases: `{len(cases)}` ({', '.join(f'{key}={value}' for key, value in sorted(counts.items()))})")
    print(f"- Runtime status: {release['status']}; activation disabled")
    print("\nRequired preparation\n")
    print("1. Read the repository instructions, `$wayfinder-maintainer`, and `references/current-state.md`; load only routed chronology unless governance changes.")
    print("2. Resolve runtimes once and run `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py doctor --verbose` with Python 3.11+ before editing.")
    print("3. Apply the action-authorization gate before authentication, downloads, dispatch, publication, destructive work, or another consequential external action.")
    print("4. Use `maintain.py self-test` for maintainer regressions and `maintain.py record-section --heading HEADING` for exact chronology retrieval.")
    print("\nTranche mode\n")
    print(f"- Kind: `{kind}`")
    if kind == "investigation":
        print("- Inspect and report only; do not create evidence, freeze records, publish, activate, or mutate governed bytes unless the objective separately grants that authority.")
    elif kind == "implementation":
        print("- Change only the objective's authorized surfaces; use focused tests, canonical self-tests, repository validation, diff checking, and one final doctor.")
    elif kind == "hosted-review":
        print("- Read public run metadata and failed logs first. Download exact named artifacts only when the active tranche explicitly authorizes it and existing authentication is sufficient.")
    elif kind == "acceptance-record":
        print("- Record only the explicitly accepted outcome through the applicable exclusive command; do not begin the next tranche.")
    if exclusions:
        print("\nExplicit exclusions\n")
        for item in exclusions:
            print(f"- {item}")
    print("\nDo not infer authorization for later work. Present material changes for explicit approval and stop at the active tranche boundary.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Offline, dependency-free maintenance commands for the frozen Wayfinder candidate.",
        epilog=(
            "Examples:\n"
            "  maintain.py doctor --verbose\n"
            "  maintain.py self-test\n"
            "  maintain.py test --adapter python-reference-v1 --case package-valid --case inventory-files-roots\n"
            "  maintain.py describe --format json\n"
            "  maintain.py record-section --heading 'Candidate revision 9 Windows corrections — accepted'\n"
            "  maintain.py matrix-review --artifact-dir downloaded --format markdown"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subparsers.add_parser("doctor", help="Check maintainer, package, adapter, and evidence integrity.")
    doctor_modes = doctor_parser.add_mutually_exclusive_group()
    doctor_modes.add_argument("--summary", action="store_const", dest="output_mode", const="summary", help="Emit failures and one compact summary (default).")
    doctor_modes.add_argument("--verbose", action="store_const", dest="output_mode", const="verbose", help="Emit every canonical doctor check and runtime diagnostic.")
    doctor_modes.add_argument("--json", action="store_const", dest="output_mode", const="json", help="Emit stable compact JSON.")
    doctor_parser.set_defaults(output_mode="summary")
    self_test_parser = subparsers.add_parser("self-test", help="Run every maintainer regression without repository bytecode.")
    self_test_parser.add_argument("--format", choices=("summary", "verbose", "json"), default="summary")
    test_parser = subparsers.add_parser("test", help="Run the full or focused unchanged conformance suite.")
    test_parser.add_argument("--case", action="append", default=[], help="Select one case; repeat in the same invocation to batch cases.")
    test_parser.add_argument("--category", action="append", default=[], help="Select one category; repeat to batch categories.")
    test_parser.add_argument("--adapter", default="python-reference-v1", choices=sorted(ACCEPTED_ADAPTER_DIGESTS), help="Registered adapter to validate.")
    test_parser.add_argument("--output", choices=("summary", "verbose", "json"), default="summary", help="Conformance output mode (default: summary).")
    describe_parser = subparsers.add_parser("describe", aliases=["context"], help="Show canonical paths, identities, runtimes, cases, and approval boundary.")
    describe_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    record_section_parser = subparsers.add_parser("record-section", help="Print one exact level-two design-record section.")
    record_section_parser.add_argument("--heading", required=True)
    evidence_parser = subparsers.add_parser("evidence", help="Create new local evidence without overwrite.")
    evidence_parser.add_argument("--output", type=Path, required=True)
    freeze_proposal_parser = subparsers.add_parser("freeze-proposal", help="Create a revision-scoped freeze proposal without overwrite.")
    freeze_proposal_parser.add_argument("--output", type=Path, required=True)
    freeze_acceptance_parser = subparsers.add_parser("freeze-acceptance", help="Record an explicitly approved revision-scoped freeze without overwrite.")
    freeze_acceptance_parser.add_argument("--output", type=Path, required=True)
    freeze_acceptance_parser.add_argument("--accept-option-a", action="store_true", help="Confirm that the owner explicitly accepted Option A.")
    parity_parser = subparsers.add_parser("parity", help="Run full registered-adapter parity and create a new report.")
    parity_parser.add_argument("--output", type=Path, required=True)
    matrix_entry_parser = subparsers.add_parser("matrix-entry", help="Run one exact certification-matrix entry.")
    matrix_entry_parser.add_argument("--adapter", required=True, choices=sorted(ACCEPTED_ADAPTER_DIGESTS))
    matrix_entry_parser.add_argument("--os-family", required=True, choices=["macOS", "Linux", "Windows"])
    matrix_entry_parser.add_argument("--output", type=Path, required=True)
    matrix_aggregate_parser = subparsers.add_parser("matrix-aggregate", help="Create an aggregate only from eight passing exact entries.")
    matrix_aggregate_parser.add_argument("--entry", type=Path, action="append", default=[])
    matrix_aggregate_parser.add_argument("--output", type=Path, required=True)
    matrix_review_parser = subparsers.add_parser("matrix-review", help="Read and verify an already-downloaded Actions artifact directory without writes or network access.")
    matrix_review_parser.add_argument("--artifact-dir", type=Path, required=True)
    matrix_review_parser.add_argument("--format", choices=("summary", "markdown", "json"), default="summary")
    expect_parser = subparsers.add_parser("expect")
    expect_parser.add_argument("--exit", dest="expected_exit", type=int, required=True)
    expect_parser.add_argument("--code", dest="expected_code", required=True)
    expect_parser.add_argument("target", nargs=argparse.REMAINDER)
    handoff_parser = subparsers.add_parser("handoff", help="Generate mode-aware factual handoff scaffolding.")
    handoff_parser.add_argument("--kind", required=True, choices=("investigation", "implementation", "hosted-review", "acceptance-record"))
    handoff_parser.add_argument("--objective", required=True)
    handoff_parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return doctor(args.output_mode)
    if args.command == "self-test":
        return self_test_command(args.format)
    if args.command == "test":
        return test_command(args.case, args.category, args.adapter, args.output)
    if args.command in {"describe", "context"}:
        return describe_command(args.format)
    if args.command == "record-section":
        return record_section_command(args.heading)
    if args.command == "evidence":
        return evidence_command(args.output)
    if args.command == "freeze-proposal":
        return freeze_proposal_command(args.output)
    if args.command == "freeze-acceptance":
        return freeze_acceptance_command(args.output, args.accept_option_a)
    if args.command == "parity":
        return parity_command(args.output)
    if args.command == "matrix-entry":
        return matrix_entry_command(args.adapter, args.os_family, args.output)
    if args.command == "matrix-aggregate":
        return matrix_aggregate_command(args.entry, args.output)
    if args.command == "matrix-review":
        return matrix_review_command(args.artifact_dir, args.format)
    if args.command == "expect":
        return expect_command(args.expected_exit, args.expected_code, args.target)
    if args.command == "handoff":
        return handoff_command(args.kind, args.objective, args.exclude)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
