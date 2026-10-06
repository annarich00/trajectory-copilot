"""Host-side contract for optional isolated Poliastro two-body verification.

This module never imports Poliastro or Astropy.  It invokes the explicitly configured
Python 3.10 verifier subprocess and preserves its raw JSON response as evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Literal

import numpy as np

from .twobody import STATE_FRAME, TwoBodyCase, propagate_cartesian_state

SCHEMA_VERSION = "1.0"
POLIASTRO_RELEASE = "0.17.0"
POLIASTRO_COMMIT = "c7d12e9b715d3fd60f2be233af707d5b97617d39"
LOCK_IDENTIFIER = "verification/poliastro/requirements.lock"
ADAPTER = Path(__file__).resolve().parents[1] / "verification/poliastro/adapter.py"


@dataclass(frozen=True)
class Tolerances:
    position_m: float
    velocity_mps: float
    rationale: str


@dataclass(frozen=True)
class PoliastroVerificationResult:
    schema_version: str
    case_id: str
    status: Literal["PASS", "FAIL", "UNSUPPORTED", "UNAVAILABLE"]
    candidate_state_m_mps: list[float] | None
    poliastro_state_m_mps: list[float] | None
    position_error_m: float | None
    velocity_error_mps: float | None
    tolerances: dict[str, Any]
    request: dict[str, Any]
    provenance: dict[str, Any]
    diagnostics: list[str]
    raw_adapter_response: dict[str, Any] | None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _result(case: TwoBodyCase, status: str, tolerances: Tolerances, diagnostics: list[str], **kwargs: Any) -> PoliastroVerificationResult:
    request = {
        "schema_version": SCHEMA_VERSION, "case_id": case.case_id,
        "initial_state_m_mps": list(case.state0_m_mps), "mu_m3_s2": case.mu_m3_s2,
        "duration_s": case.duration_s, "frame": case.frame, "central_body": case.central_body,
        "epoch": case.epoch, "dynamics": case.dynamics, "method": "farnocchia",
    }
    provenance = {"poliastro_release": POLIASTRO_RELEASE, "poliastro_commit": POLIASTRO_COMMIT,
                  "dependency_lock": LOCK_IDENTIFIER, "host_python": sys.version.split()[0]}
    return PoliastroVerificationResult(SCHEMA_VERSION, case.case_id, status,
        kwargs.get("candidate_state_m_mps"), kwargs.get("poliastro_state_m_mps"),
        kwargs.get("position_error_m"), kwargs.get("velocity_error_mps"), asdict(tolerances),
        request, provenance, diagnostics, kwargs.get("raw_adapter_response"))


def verify_against_poliastro(case: TwoBodyCase, tolerances: Tolerances, *, python_executable: str | None = None,
                             candidate_state_m_mps: np.ndarray | None = None) -> PoliastroVerificationResult:
    """Compare a supported RK4 result to the isolated external implementation."""
    if case.frame != STATE_FRAME or case.dynamics != "point-mass-two-body":
        return _result(case, "UNSUPPORTED", tolerances, ["Only SI inertial Cartesian point-mass coast cases are supported."],
                       candidate_state_m_mps=None, poliastro_state_m_mps=None, position_error_m=None, velocity_error_mps=None, raw_adapter_response=None)
    executable = python_executable or os.environ.get("TRAJECTORY_COPILOT_POLIASTRO_PYTHON")
    if not executable:
        return _result(case, "UNAVAILABLE", tolerances, ["Set TRAJECTORY_COPILOT_POLIASTRO_PYTHON to the isolated Python 3.10 environment."],
                       candidate_state_m_mps=None, poliastro_state_m_mps=None, position_error_m=None, velocity_error_mps=None, raw_adapter_response=None)
    candidate = np.asarray(candidate_state_m_mps if candidate_state_m_mps is not None else propagate_cartesian_state(
        np.asarray(case.state0_m_mps), case.mu_m3_s2, case.duration_s, case.steps), dtype=float)
    request = {"schema_version": SCHEMA_VERSION, "case_id": case.case_id, "initial_state_m_mps": list(case.state0_m_mps),
               "mu_m3_s2": case.mu_m3_s2, "duration_s": case.duration_s, "frame": case.frame,
               "central_body": case.central_body, "epoch": case.epoch, "dynamics": case.dynamics, "method": "farnocchia"}
    try:
        completed = subprocess.run([executable, str(ADAPTER)], input=json.dumps(request), text=True,
                                   capture_output=True, timeout=30, check=False)
        raw = json.loads(completed.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        return _result(case, "UNAVAILABLE", tolerances, [f"Verifier subprocess unavailable: {error}"],
                       candidate_state_m_mps=candidate.tolist(), poliastro_state_m_mps=None, position_error_m=None, velocity_error_mps=None, raw_adapter_response=None)
    provenance = {"poliastro_release": POLIASTRO_RELEASE, "poliastro_commit": POLIASTRO_COMMIT, "dependency_lock": LOCK_IDENTIFIER,
                  "host_python": sys.version.split()[0], "command_exit_status": completed.returncode, "adapter_provenance": raw.get("provenance", {})}
    if completed.returncode != 0 or raw.get("status") != "OK":
        return PoliastroVerificationResult(SCHEMA_VERSION, case.case_id, "UNSUPPORTED" if raw.get("status") == "UNSUPPORTED" else "UNAVAILABLE",
            candidate.tolist(), None, None, None, asdict(tolerances), request, provenance,
            raw.get("diagnostics", []) + ([completed.stderr] if completed.stderr else []), raw)
    reference = np.asarray(raw["state_m_mps"], dtype=float)
    position_error = float(np.linalg.norm(candidate[:3] - reference[:3]))
    velocity_error = float(np.linalg.norm(candidate[3:] - reference[3:]))
    status = "PASS" if position_error <= tolerances.position_m and velocity_error <= tolerances.velocity_mps else "FAIL"
    return PoliastroVerificationResult(SCHEMA_VERSION, case.case_id, status, candidate.tolist(), reference.tolist(), position_error,
        velocity_error, asdict(tolerances), request, provenance, raw.get("diagnostics", []), raw)
