#!/usr/bin/env python3
"""Python-3.10-only JSON-lines adapter for the isolated Poliastro verifier."""
from __future__ import annotations

import json
import platform
import sys

SCHEMA_VERSION = "1.0"
POLIASTRO_RELEASE = "0.17.0"
POLIASTRO_COMMIT = "c7d12e9b715d3fd60f2be233af707d5b97617d39"
SUPPORTED_FRAME = "inertial-cartesian"
SUPPORTED_DYNAMICS = "point-mass-two-body"


def unavailable(case_id: str | None, diagnostic: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "status": "UNAVAILABLE",
        "diagnostics": [diagnostic],
        "provenance": {"poliastro_release": POLIASTRO_RELEASE, "poliastro_commit": POLIASTRO_COMMIT, "python_version": platform.python_version()},
    }


def unsupported(request: dict, diagnostic: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": request.get("case_id"),
        "status": "UNSUPPORTED",
        "diagnostics": [diagnostic],
        "recommended_next_step": "Use a named verifier that supports the requested model or frame; GMAT remains required end-to-end.",
        "provenance": {"poliastro_release": POLIASTRO_RELEASE, "poliastro_commit": POLIASTRO_COMMIT, "python_version": platform.python_version()},
    }


def main() -> int:
    try:
        request = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(json.dumps(unavailable(None, f"malformed JSON request: {error}")))
        return 2
    if request.get("schema_version") != SCHEMA_VERSION:
        print(json.dumps(unsupported(request, "unsupported adapter schema version")))
        return 0
    if request.get("frame") != SUPPORTED_FRAME or request.get("dynamics") != SUPPORTED_DYNAMICS:
        print(json.dumps(unsupported(request, "pinned Poliastro adapter supports only SI inertial Cartesian point-mass coast propagation")))
        return 0
    try:
        from astropy import units as u
        from astropy.time import Time
        from poliastro.bodies import Earth
        from poliastro.twobody import Orbit
    except Exception as error:  # package/import defect is externally unavailable, never PASS
        print(json.dumps(unavailable(request.get("case_id"), f"Poliastro environment import failed: {error}")))
        return 0
    try:
        state = request["initial_state_m_mps"]
        if len(state) != 6 or request["mu_m3_s2"] <= 0 or request["duration_s"] < 0:
            raise ValueError("invalid SI Cartesian state, mu, or duration")
        epoch = Time(request.get("epoch") or "2000-01-01T12:00:00", scale="utc")
        orbit = Orbit.from_vectors(
            Earth,
            state[:3] * u.m,
            state[3:] * u.m / u.s,
            epoch=epoch,
            plane=request.get("plane", "EARTH_EQUATOR"),
        )
        propagated = orbit.propagate(request["duration_s"] * u.s)
        result_state = [*propagated.r.to_value(u.m).tolist(), *propagated.v.to_value(u.m / u.s).tolist()]
    except Exception as error:
        print(json.dumps(unavailable(request.get("case_id"), f"Poliastro propagation failed: {error}")))
        return 0
    print(json.dumps({
        "schema_version": SCHEMA_VERSION,
        "case_id": request["case_id"],
        "status": "OK",
        "state_m_mps": result_state,
        "frame": SUPPORTED_FRAME,
        "dynamics": SUPPORTED_DYNAMICS,
        "provenance": {"poliastro_release": POLIASTRO_RELEASE, "poliastro_commit": POLIASTRO_COMMIT, "python_version": platform.python_version()},
        "diagnostics": [],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
