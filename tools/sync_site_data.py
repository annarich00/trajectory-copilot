#!/usr/bin/env python3
"""Synchronize verbatim educational-site mirrors using Python built-ins only."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Repository source -> read-only presentation mirror. Add explicit mappings when
# later tasks expose another authoritative file. site/js/physics.js is excluded:
# it is a pedagogical hand port, never an authoritative mirror.
MAPPINGS = {
    "baseline_comparison.md": "site/data/baseline_comparison.md",
    "reference/SOURCE.md": "site/data/reference/SOURCE.md",
    "docs/poliastro-verification-architecture.md": "site/data/docs/poliastro-verification-architecture.md",
    "src/cw.py": "site/data/src/cw.py",
    "src/optimization.py": "site/data/src/optimization.py",
    "src/twobody.py": "site/data/src/twobody.py",
    "src/verify.py": "site/data/src/verify.py",
    "tests/test_cw.py": "site/data/tests/test_cw.py",
    "tests/test_twobody.py": "site/data/tests/test_twobody.py",
    "tests/test_validation.py": "site/data/tests/test_validation.py",
    ".pi/skills/orbital-problem-formalizer/SKILL.md": "site/data/skills/formalizer.SKILL.md",
    ".pi/skills/orbital-model-selector/SKILL.md": "site/data/skills/model-selector.SKILL.md",
    ".pi/skills/orbital-targeting-planner/SKILL.md": "site/data/skills/targeting-planner.SKILL.md",
    "examples/geo_failure_case.yaml": "site/data/examples/geo_failure_case.yaml",
    "examples/rendezvous_case_01.yaml": "site/data/examples/rendezvous_case_01.yaml",
    "examples/rendezvous_case_02.yaml": "site/data/examples/rendezvous_case_02.yaml",
    "evaluations/formalizer/test_01_underspecified.txt": "site/data/evaluations/test_01_underspecified.txt",
    "evaluations/formalizer/test_02_cw_complete.txt": "site/data/evaluations/test_02_cw_complete.txt",
    "evaluations/formalizer/test_03_cw_validity.txt": "site/data/evaluations/test_03_cw_validity.txt",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without modifying mirrors")
    args = parser.parse_args()
    drift = []
    for source_name, mirror_name in MAPPINGS.items():
        source, mirror = ROOT / source_name, ROOT / mirror_name
        if not source.is_file():
            print(f"missing authoritative source: {source_name}", file=sys.stderr)
            return 2
        if not mirror.is_file() or source.read_bytes() != mirror.read_bytes():
            drift.append((source_name, mirror_name))
            if not args.check:
                mirror.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, mirror)
                print(f"updated {mirror_name} <- {source_name}")
    if args.check and drift:
        for source_name, mirror_name in drift:
            print(f"DRIFT: {mirror_name} != {source_name}", file=sys.stderr)
        print("Run: python3 tools/sync_site_data.py", file=sys.stderr)
        return 1
    print(f"site data mirrors {'match' if args.check else 'synchronized'} ({len(MAPPINGS)} mappings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
