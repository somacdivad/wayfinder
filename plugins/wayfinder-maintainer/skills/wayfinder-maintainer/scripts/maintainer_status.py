"""Canonical status parsing and deterministic public projection."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


STATUS_BEGIN = "<!-- WAYFINDER-STATUS-OBJECT:BEGIN -->"
STATUS_END = "<!-- WAYFINDER-STATUS-OBJECT:END -->"


def parse_status(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    pattern = re.escape(STATUS_BEGIN) + r"\n```json\n(.*?)\n```\n" + re.escape(STATUS_END)
    matches = re.findall(pattern, text, flags=re.DOTALL)
    if len(matches) != 1:
        raise ValueError("current state must contain exactly one canonical status object")
    def pairs(values):
        result = {}
        for key, item in values:
            if key in result:
                raise ValueError(f"duplicate status member: {key}")
            result[key] = item
        return result
    value = json.loads(matches[0], object_pairs_hook=pairs)
    required = {"format", "schemaVersion", "asOf", "requirements", "candidate", "conformance", "hostedEvidence", "publication", "releaseRegistry", "runtimes", "claims"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("canonical status object fields differ")
    if value.get("format") != "wayfinder-maintainer-status" or value.get("schemaVersion") != 1:
        raise ValueError("canonical status object identity differs")
    nested = {
        "candidate": {"releaseId", "candidateRevision", "packageVersion", "contractStatus", "releaseStatus", "activation", "contractSha256", "releaseSha256"},
        "requirements": {"maintainerPythonMinimum"},
        "conformance": {"caseCount"},
        "hostedEvidence": {"exists", "accepted", "runId", "attempt", "sourceCommit", "path", "fileCount", "matrixEntries", "casesPerEntry", "aggregateJsonSha256", "aggregateMarkdownSha256", "matrixSha256"},
        "publication": {"readiness", "dispatchAuthorized", "published", "sourcePublicationCommit", "blockerCode", "checkedOutSourceCommit", "verifierCandidateRevision", "missingArguments", "failureStage"},
        "releaseRegistry": {"updated", "certificationEntries"},
        "claims": {"fullFamilyCertification", "crossAdapterRecovery"},
    }
    for key, fields in nested.items():
        if not isinstance(value[key], dict) or set(value[key]) != fields:
            raise ValueError(f"status {key} fields differ")
    if value["candidate"]["activation"] not in {"enabled", "disabled"} or value["publication"]["readiness"] not in {"ready", "not-ready", "pending"}:
        raise ValueError("invalid lifecycle enum")
    for section, fields in (("hostedEvidence", ("exists", "accepted")), ("publication", ("dispatchAuthorized", "published")), ("releaseRegistry", ("updated",)), ("claims", ("fullFamilyCertification", "crossAdapterRecovery"))):
        if any(type(value[section][field]) is not bool for field in fields):
            raise ValueError(f"status {section} flags must be booleans")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["asOf"]):
        raise ValueError("status date differs")
    for item in value["runtimes"]:
        if not isinstance(item, dict) or set(item) != {"adapterId", "implementation", "version", "operatingSystems"}:
            raise ValueError("runtime observation fields differ")
    return value


def _region(text: str, name: str, body: str) -> str:
    begin = f"<!-- WAYFINDER-GENERATED:{name}:BEGIN -->"
    end = f"<!-- WAYFINDER-GENERATED:{name}:END -->"
    pattern = re.escape(begin) + r"\n.*?\n" + re.escape(end)
    replacement = f"{begin}\n{body.rstrip()}\n{end}"
    if len(re.findall(pattern, text, flags=re.DOTALL)) != 1:
        raise ValueError(f"generated region {name} missing or ambiguous")
    return re.sub(pattern, replacement, text, count=1, flags=re.DOTALL)


def _json_string(text: str, key: str, value: str) -> str:
    pattern = rf'(\"{re.escape(key)}\"\s*:\s*)\"(?:[^\"\\]|\\.)*\"'
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise ValueError(f"JSON field {key} missing or ambiguous")
    encoded = json.dumps(value, ensure_ascii=False)
    return re.sub(pattern, lambda match: match.group(1) + encoded, text, count=1)


def rendered_targets(root: Path, status: dict[str, Any]) -> dict[Path, bytes]:
    relatives = (
        "README.md", "docs/certification.md", "plugins/wayfinder/plugin.json",
        "plugins/wayfinder/.codex-plugin/plugin.json", "plugins/wayfinder/.claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
    )
    for relative in relatives:
        path = root / relative
        parts = Path(relative).parts
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()) or any((root / Path(*parts[:index])).is_symlink() for index in range(1, len(parts) + 1)):
            raise ValueError(f"unsafe projection target: {relative}")
    candidate = status["candidate"]
    evidence = status["hostedEvidence"]
    publication = status["publication"]
    lifecycle = "unactivated" if candidate["activation"] == "disabled" else "activated"
    evidence_claim = "accepted passing hosted evidence" if evidence["accepted"] else ("hosted evidence awaiting acceptance" if evidence["exists"] else "no hosted evidence")
    blocker = (
        f"The workflow at `{publication['sourcePublicationCommit']}` checks out `{publication['checkedOutSourceCommit']}` "
        f"before invoking its revision-{publication['verifierCandidateRevision']} verifier, which lacks "
        + ", ".join(f"`{argument}`" for argument in publication["missingArguments"])
        + "; argument parsing would fail before draft-release creation."
    )
    banner = (
        "> [!IMPORTANT]\n"
        f"> Wayfinder `{candidate['releaseId']}` has {evidence_claim}; evidence publication is "
        f"**{publication['readiness'].upper()}**; dispatch authorized: {str(publication['dispatchAuthorized']).lower()}. Runtime activation is {candidate['activation']}. Installing or forking this repository does not change that status."
    )
    repository_status = "\n".join([
        "## Repository status", "",
        f"- Candidate: `{candidate['releaseId']}`",
        f"- Contract: {candidate['contractStatus']}",
        f"- Release: {candidate['releaseStatus']}",
        f"- Activation: {candidate['activation']}",
        f"- Common conformance suite: {status['conformance']['caseCount']} cases",
        f"- Hosted evidence exists: {str(evidence['exists']).lower()}; accepted: {str(evidence['accepted']).lower()}; run `{evidence['runId']}`, attempt `{evidence['attempt']}`, source `{evidence['sourceCommit']}`; all {evidence['matrixEntries']} entries passed",
        f"- Evidence publication: {publication['readiness']}; dispatch authorized: {str(publication['dispatchAuthorized']).lower()}",
        f"- Evidence published: {str(publication['published']).lower()}",
        f"- Release registry updated: {str(status['releaseRegistry']['updated']).lower()}",
        f"- Full-family certification claimed: {str(status['claims']['fullFamilyCertification']).lower()}; cross-adapter recovery claimed: {str(status['claims']['crossAdapterRecovery']).lower()}",
    ])
    readme = (root / "README.md").read_text(encoding="utf-8")
    readme = _region(readme, "README-BANNER", banner)
    readme = _region(readme, "README-STATUS", repository_status)
    packages = "\n".join([
        "| Package | Audience | Status |", "| --- | --- | --- |",
        f"| [`wayfinder`](plugins/wayfinder) | Project-record users | Runtime activation: {candidate['activation']} |",
        "| [`wayfinder-maintainer`](plugins/wayfinder-maintainer) | Contributors and certifiers | Opt-in package; not listed in the end-user catalog |",
    ])
    readme = _region(readme, "README-PACKAGES", packages)
    readme = _region(readme, "DEVELOPMENT-REQUIREMENTS", f"Use Python {status['requirements']['maintainerPythonMinimum']} or newer.")

    runtime_lines = [
        f"- `{item['adapterId']}`: {item['implementation']} `{item['version']}` on {', '.join(item['operatingSystems'])}"
        for item in status["runtimes"]
    ]
    certification = "\n".join([
        f"- **Status:** Candidate {candidate['candidateRevision']} publication readiness **{publication['readiness'].upper()}**; dispatch authorized: {str(publication['dispatchAuthorized']).lower()}; activation {candidate['activation']}",
        f"- **Last updated:** {status['asOf']}", "",
        f"The current target is `{candidate['releaseId']}` (contract {candidate['contractStatus']}, release {candidate['releaseStatus']}). Hosted evidence accepted: {str(evidence['accepted']).lower()}. GitHub Actions run `{evidence['runId']}`, attempt `{evidence['attempt']}`, at source commit `{evidence['sourceCommit']}` passed all {evidence['matrixEntries']} exact entries with {evidence['casesPerEntry']}/{evidence['casesPerEntry']} cases each. The exact {evidence['fileCount']} files remain preserved at `{evidence['path']}`.", "",
        "## Verified hosted observations", "", *runtime_lines, "",
        f"Aggregate JSON: `{evidence['aggregateJsonSha256']}`. Aggregate Markdown: `{evidence['aggregateMarkdownSha256']}`. Matrix digest: `{evidence['matrixSha256']}`.", "",
        "These are exact accepted observations, not a general support guarantee, independent evaluation, forward testing, cross-adapter recovery, or full-family certification.", "",
        "## Publication boundary", "",
        f"Evidence publication is **{publication['readiness'].upper()}**; dispatch authorized: {str(publication['dispatchAuthorized']).lower()}; evidence published: {str(publication['published']).lower()}. {blocker} Release registry updated: {str(status['releaseRegistry']['updated']).lower()}; runtime activation: {candidate['activation']}.",
    ])
    cert = (root / "docs/certification.md").read_text(encoding="utf-8")
    cert = _region(cert, "CERTIFICATION-STATUS", certification)

    description = f"Build, maintain, validate, and selectively consult a durable repository-owned project record. Current candidate is {lifecycle}."
    targets: dict[Path, bytes] = {
        root / "README.md": readme.encode("utf-8"),
        root / "docs/certification.md": cert.encode("utf-8"),
    }
    for relative in (
        "plugins/wayfinder/plugin.json",
        "plugins/wayfinder/.codex-plugin/plugin.json",
        "plugins/wayfinder/.claude-plugin/plugin.json",
    ):
        path = root / relative
        text = path.read_text(encoding="utf-8")
        parsed = json.loads(text)
        if parsed.get("name") != "wayfinder" or not all(isinstance(parsed.get(key), str) for key in ("version", "description")):
            raise ValueError(f"runtime manifest shape differs: {relative}")
        if relative.endswith(".codex-plugin/plugin.json") and (not isinstance(parsed.get("interface"), dict) or not isinstance(parsed["interface"].get("longDescription"), str)):
            raise ValueError("Codex runtime interface shape differs")
        text = _json_string(text, "version", candidate["packageVersion"])
        text = _json_string(text, "description", description)
        if relative.endswith(".codex-plugin/plugin.json"):
            text = _json_string(text, "longDescription", f"Wayfinder provides contract-governed workflows for a durable repository-owned project record. The current candidate is {lifecycle}.")
        targets[path] = text.encode("utf-8")
    market = root / ".claude-plugin/marketplace.json"
    market_text = market.read_text(encoding="utf-8")
    parsed_market = json.loads(market_text)
    if [item.get("name") for item in parsed_market.get("plugins", [])] != ["wayfinder"]:
        raise ValueError("Claude marketplace projection shape differs")
    market_text = _json_string(market_text, "version", candidate["packageVersion"])
    market_text = _json_string(market_text, "description", f"Build and maintain a durable project record. Current candidate is {lifecycle}.")
    targets[market] = market_text.encode("utf-8")
    return targets


def projection_drift(root: Path, status: dict[str, Any]) -> list[str]:
    return [str(path.relative_to(root)) for path, expected in rendered_targets(root, status).items() if path.read_bytes() != expected]


def write_targets(root: Path, status: dict[str, Any]) -> list[str]:
    targets = rendered_targets(root, status)
    for path in targets:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unsafe projection target: {path}")
    changed = [(path, data) for path, data in targets.items() if path.read_bytes() != data]
    originals = {path: path.read_bytes() for path, _ in changed}
    written: list[Path] = []
    try:
        for path, data in changed:
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"unsafe projection target: {path}")
            fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
                os.chmod(temporary, path.stat().st_mode & 0o777)
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            written.append(path)
    except Exception:
        for path in reversed(written):
            path.write_bytes(originals[path])
        raise
    return [str(path.relative_to(root)) for path, _ in changed]
