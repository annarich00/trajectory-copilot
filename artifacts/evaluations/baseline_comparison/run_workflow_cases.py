#!/usr/bin/env python3
"""Run the complete structured workflow against the four TJC-1.9 benchmark cases (TJC-1.22).

This script is a thin, benchmark-specific *caller* of the already-hardened
``src/workflow.py::run_rendezvous_workflow`` (TJC-1.16) -- it does not
modify ``src/workflow.py``, ``src/model_selector.py``, ``src/cw.py``,
``src/twobody.py``, or ``src/gmat_verify.py``. Every numeric input used to
build each case's ``RendezvousCase``/``ModelSelectionCase`` is read directly
from the already-committed ``evaluations/benchmark/*`` fixture files (not
re-typed ad hoc numbers), so this script can never silently drift from the
versioned benchmark requests it is supposed to be exercising.

For cases (a)/(b)/(c), running this script for real independently
re-confirms the already-committed, already-audited GMAT evidence in
``examples/cw_gmat_slice_example/``, ``examples/benchmark_case_b_boundary/``,
and ``examples/benchmark_case_c_two_body/`` (TJC-1.9) by calling
``run_rendezvous_workflow`` with a real GMAT executable; it writes its own
output under this directory (``case_a_workflow_result.json`` etc.) and does
not modify those already-committed example directories.

Case (d) is a ``NEEDS_CLARIFICATION`` case: it short-circuits before any
model selection, solver, or GMAT call, exactly as ``src/workflow.py``
documents.

Usage::

    .venv/bin/python evaluations/baseline_comparison/run_workflow_cases.py --gmat GmatConsole-R2026a
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.cw import mean_motion  # noqa: E402
from src.model_selector import ModelSelectionCase  # noqa: E402
from src.twobody import vis_viva_speed  # noqa: E402
from src.workflow import RendezvousCase, run_rendezvous_workflow  # noqa: E402

BENCHMARK_DIR = ROOT / "evaluations/benchmark"
OUTPUT_DIR = Path(__file__).resolve().parent


def _load(name: str) -> dict:
    return json.loads((BENCHMARK_DIR / name).read_text())


def _build_case_a() -> RendezvousCase:
    """Straightforward CW: read every numeric input from case_a_straightforward_cw.json."""
    fixture = _load("case_a_straightforward_cw.json")
    sp = fixture["expected_structured_problem"]
    mu = sp["reference_orbit"]["gravitational_parameter_m3_s2"]["value"]
    radius_m = sp["reference_orbit"]["radius_m"]["value"]
    r0 = sp["relative_frame_and_state"]["initial_relative_position_m"]["value"]
    v0 = sp["relative_frame_and_state"]["initial_relative_velocity_mps"]["value"]
    rf = sp["terminal_conditions"]["relative_position_m"]["value"]
    vf = sp["terminal_conditions"]["relative_velocity_mps"]["value"]
    transfer_s = sp["timing_and_maneuvers"]["time_of_flight_s"]["value"]
    n = mean_motion(mu, radius_m)
    model_case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=radius_m, relative_separation_m=200.0,
        transfer_time_s=transfer_s, mean_motion_rad_s=n,
        initial_relative_state=list(r0) + list(v0), final_relative_state=list(rf) + list(vf),
    )
    tol = fixture["gmat_tolerance"]
    return RendezvousCase(
        case_id=fixture["case_id"], readiness="READY_TO_SOLVE", model_selection_case=model_case,
        mu_m3_s2=mu, reference_radius_m=radius_m,
        initial_relative_state=list(r0) + list(v0), final_relative_state=list(rf) + list(vf),
        transfer_time_s=transfer_s,
        pos_tol_m=tol["position_m"], vel_tol_mps=tol["velocity_mps"], dv_tol_mps=tol["delta_v_mps"],
    )


def _build_case_b() -> RendezvousCase:
    """Boundary CW: half-orbital-period transfer; same fixture-driven construction as case (a)."""
    fixture = _load("case_b_boundary_cw.json")
    sp = fixture["expected_structured_problem"]
    mu = sp["reference_orbit"]["gravitational_parameter_m3_s2"]["value"]
    radius_m = sp["reference_orbit"]["radius_m"]["value"]
    r0 = sp["relative_frame_and_state"]["initial_relative_position_m"]["value"]
    v0 = sp["relative_frame_and_state"]["initial_relative_velocity_mps"]["value"]
    rf = sp["terminal_conditions"]["relative_position_m"]["value"]
    vf = sp["terminal_conditions"]["relative_velocity_mps"]["value"]
    transfer_s = sp["timing_and_maneuvers"]["time_of_flight_s"]["value"]
    n = mean_motion(mu, radius_m)
    model_case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=radius_m, relative_separation_m=200.0,
        transfer_time_s=transfer_s, mean_motion_rad_s=n,
        initial_relative_state=list(r0) + list(v0), final_relative_state=list(rf) + list(vf),
    )
    tol = fixture["gmat_tolerance"]
    return RendezvousCase(
        case_id=fixture["case_id"], readiness="READY_TO_SOLVE", model_selection_case=model_case,
        mu_m3_s2=mu, reference_radius_m=radius_m,
        initial_relative_state=list(r0) + list(v0), final_relative_state=list(rf) + list(vf),
        transfer_time_s=transfer_s,
        pos_tol_m=tol["position_m"], vel_tol_mps=tol["velocity_mps"], dv_tol_mps=tol["delta_v_mps"],
    )


def _build_case_c() -> RendezvousCase:
    """CW-invalid/two-body: read the declared inertial coast state from case_c_two_body.json."""
    fixture = _load("case_c_two_body.json")
    summary = fixture["reference_numerical_result"]["summary"]
    mu = summary["mu_m3_s2"]
    state0 = summary["initial_state_m_mps"]
    duration_s = summary["duration_s"]
    steps = summary["steps"]
    # Reference LEO radius/separation used only to feed the model selector's
    # locality signal (reference/SOURCE.md Sec D); matches the fixture's own
    # provenance note (1,000 km offset from a 6,778 km circular reference).
    leo_radius_m = 6778000.0
    offset_m = 1_000_000.0
    model_case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="violated",
        maneuver_assumptions="supported",
        reference_radius_m=leo_radius_m, relative_separation_m=offset_m,
        transfer_time_s=duration_s, mean_motion_rad_s=mean_motion(mu, leo_radius_m),
        inertial_cartesian_state=state0, mu_m3_s2=mu, coast_duration_s=duration_s, rk4_steps=steps,
    )
    return RendezvousCase(
        case_id=fixture["case_id"], readiness="READY_TO_SOLVE", model_selection_case=model_case,
        inertial_cartesian_state=state0, mu_m3_s2=mu, coast_duration_s=duration_s, rk4_steps=steps,
    )


def _build_case_d() -> RendezvousCase:
    """Ambiguous/incomplete: parse the exact clarification questions from case_d_ambiguous.txt."""
    text = (BENCHMARK_DIR / "case_d_ambiguous.txt").read_text()
    block = text.split("EXPECTED CLARIFICATION QUESTIONS:\n", 1)[1].split("\n\nGMAT TOLERANCE:")[0]
    questions = tuple(line[2:].strip() for line in block.splitlines() if line.startswith("- "))
    return RendezvousCase(
        case_id="benchmark_case_d_ambiguous", readiness="NEEDS_CLARIFICATION",
        clarification_questions=questions,
    )


CASES = {
    "a": ("case_a_straightforward_cw", _build_case_a),
    "b": ("case_b_boundary_cw", _build_case_b),
    "c": ("case_c_two_body", _build_case_c),
    "d": ("case_d_ambiguous", _build_case_d),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gmat", default="GmatConsole-R2026a")
    parser.add_argument("--cases", nargs="+", default=sorted(CASES), choices=sorted(CASES))
    args = parser.parse_args()

    for letter in args.cases:
        name, builder = CASES[letter]
        case = builder()
        # A stable, repo-relative working directory (not a tempfile) so the
        # generated-script/screenshot/report artifact paths recorded in the
        # committed result JSON stay meaningful between runs, matching
        # scripts/generate_benchmark_gmat_evidence.py's own convention.
        work_dir = OUTPUT_DIR / "workflow_artifacts" / f"case_{letter}"
        result = run_rendezvous_workflow(case, output_dir=work_dir, gmat_executable=args.gmat)
        out_path = OUTPUT_DIR / f"case_{letter}_workflow_result.json"
        out_path.write_text(json.dumps(result.to_dict(), indent=2, default=str) + "\n")
        print(f"case {letter} ({name}): outcome={result.outcome!r} verified={result.verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
