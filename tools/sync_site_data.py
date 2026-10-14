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
    "src/gmat_verify.py": "site/data/src/gmat_verify.py",
    "src/verification_report.py": "site/data/src/verification_report.py",
    "src/model_selector.py": "site/data/src/model_selector.py",
    "src/optimization.py": "site/data/src/optimization.py",
    "src/poliastro_verify.py": "site/data/src/poliastro_verify.py",
    "src/twobody.py": "site/data/src/twobody.py",
    "src/verify.py": "site/data/src/verify.py",
    "src/workflow.py": "site/data/src/workflow.py",
    "scripts/run_cw_gmat_slice.py": "site/data/scripts/run_cw_gmat_slice.py",
    "tests/test_cw_gmat_slice.py": "site/data/tests/test_cw_gmat_slice.py",
    "tests/test_verification_report.py": "site/data/tests/test_verification_report.py",
    "tests/test_cw.py": "site/data/tests/test_cw.py",
    "tests/test_twobody.py": "site/data/tests/test_twobody.py",
    "tests/test_validation.py": "site/data/tests/test_validation.py",
    "tests/test_formalizer_schema.py": "site/data/tests/test_formalizer_schema.py",
    "tests/test_model_selector.py": "site/data/tests/test_model_selector.py",
    "tests/test_poliastro_verify.py": "site/data/tests/test_poliastro_verify.py",
    "tests/test_workflow.py": "site/data/tests/test_workflow.py",
    "tests/test_skill_authority_boundaries.py": "site/data/tests/test_skill_authority_boundaries.py",
    ".pi/skills/orbital-problem-formalizer/SKILL.md": "site/data/skills/formalizer.SKILL.md",
    ".pi/skills/orbital-model-selector/SKILL.md": "site/data/skills/model-selector.SKILL.md",
    ".pi/skills/orbital-targeting-planner/SKILL.md": "site/data/skills/targeting-planner.SKILL.md",
    ".pi/skills/orbital-two-body-rendezvous/SKILL.md": "site/data/skills/two-body-rendezvous.SKILL.md",
    ".pi/skills/gmat-rendezvous-verification/SKILL.md": "site/data/skills/gmat-verification.SKILL.md",
    "examples/geo_failure_case.yaml": "site/data/examples/geo_failure_case.yaml",
    "examples/rendezvous_case_01.yaml": "site/data/examples/rendezvous_case_01.yaml",
    "examples/rendezvous_case_02.yaml": "site/data/examples/rendezvous_case_02.yaml",
    "examples/cw_gmat_vertical_slice.yaml": "site/data/examples/cw_gmat_vertical_slice.yaml",
    "examples/cw_gmat_slice_example/verification_result.json": "site/data/examples/cw_gmat_slice_example/verification_result.json",
    "examples/cw_gmat_slice_example/trajectory_gmat_gui.png": "site/data/examples/cw_gmat_slice_example/trajectory_gmat_gui.png",
    "evaluations/formalizer/test_01_underspecified.txt": "site/data/evaluations/test_01_underspecified.txt",
    "evaluations/formalizer/test_02_cw_complete.txt": "site/data/evaluations/test_02_cw_complete.txt",
    "evaluations/formalizer/test_03_cw_validity.txt": "site/data/evaluations/test_03_cw_validity.txt",
    "evaluations/formalizer/test_04_contradictory.txt": "site/data/evaluations/test_04_contradictory.txt",
    "evaluations/formalizer/test_05_unit_inconsistent.txt": "site/data/evaluations/test_05_unit_inconsistent.txt",
    "evaluations/benchmark/README.md": "site/data/evaluations/benchmark/README.md",
    "evaluations/benchmark/case_a_straightforward_cw.json": "site/data/evaluations/benchmark/case_a_straightforward_cw.json",
    "evaluations/benchmark/case_b_boundary_cw.json": "site/data/evaluations/benchmark/case_b_boundary_cw.json",
    "evaluations/benchmark/case_c_two_body.json": "site/data/evaluations/benchmark/case_c_two_body.json",
    "evaluations/benchmark/case_d_ambiguous.txt": "site/data/evaluations/benchmark/case_d_ambiguous.txt",
    "examples/benchmark_case_b_boundary/verification_result.json": "site/data/examples/benchmark_case_b_boundary/verification_result.json",
    "examples/benchmark_case_b_boundary/trajectory.svg": "site/data/examples/benchmark_case_b_boundary/trajectory.svg",
    "examples/benchmark_case_c_two_body/verification_result.json": "site/data/examples/benchmark_case_c_two_body/verification_result.json",
    "examples/benchmark_case_c_two_body/trajectory.svg": "site/data/examples/benchmark_case_c_two_body/trajectory.svg",
    "tests/test_benchmark_fixtures.py": "site/data/tests/test_benchmark_fixtures.py",
    "scripts/generate_benchmark_gmat_evidence.py": "site/data/scripts/generate_benchmark_gmat_evidence.py",
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
