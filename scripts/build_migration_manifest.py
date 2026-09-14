#!/usr/bin/env python3
"""Build the one-time byte-level import manifest from the MyPond source tree."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSFORMED = {
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/SKILL.md": "Document the new source-repository path and explicit external runtime root.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/design-record.md": "Record the accepted public-repository migration checkpoint.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/workflow.md": "Document the new source-repository path and standalone target binding.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/research/2026-09-14-public-repository-plugin-structure.md": "Mark the researched migration design as accepted.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py": "Discover the two-plugin topology and capture hosted execution provenance.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/build_package.py": "Discover the two-plugin topology or an explicitly supplied runtime root.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/run.py": "Discover the two-plugin topology or an explicitly supplied runtime root.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/demonstrate_slice2.py": "Discover the two-plugin topology or an explicitly supplied runtime root.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/demonstrate_slice4.py": "Discover the two-plugin topology or an explicitly supplied runtime root.",
    "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/conformance/v1/demonstrate_slice5.py": "Discover the two-plugin topology or an explicitly supplied runtime root.",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    files = []
    for name in ("wayfinder", "wayfinder-maintainer"):
        source_skill = source_root / "skills" / name
        destination_skill = ROOT / "plugins" / name / "skills" / name
        for source in sorted(path for path in source_skill.rglob("*") if path.is_file()):
            relative = source.relative_to(source_skill)
            destination = destination_skill / relative
            destination_relative = destination.relative_to(ROOT).as_posix()
            if not destination.is_file():
                raise SystemExit(f"missing imported destination: {destination_relative}")
            source_digest = digest(source)
            destination_digest = digest(destination)
            transformed = destination_relative in TRANSFORMED
            if source_digest != destination_digest and not transformed:
                raise SystemExit(f"unapproved byte change: {destination_relative}")
            files.append({
                "sourcePath": source.relative_to(source_root).as_posix(),
                "destinationPath": destination_relative,
                "sourceSha256": source_digest,
                "destinationSha256": destination_digest,
                "status": "maintainer-owned-migration-change" if transformed else "byte-identical",
                **({"reason": TRANSFORMED[destination_relative]} if transformed else {}),
            })
    report = {
        "format": "wayfinder-migration-manifest",
        "schemaVersion": 1,
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": {"repository": "somacdivad/mypond", "paths": ["skills/wayfinder", "skills/wayfinder-maintainer"]},
        "destination": {"repository": "somacdivad/wayfinder", "layout": "two-plugin-monorepo"},
        "files": files,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"wrote {len(files)} entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
