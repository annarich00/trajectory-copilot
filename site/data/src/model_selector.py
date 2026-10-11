"""Assumption-based CW-versus-two-body model selection.

This module implements the deterministic *combination* step described in
``reference/SOURCE.md`` §D and ``.pi/skills/orbital-model-selector/SKILL.md``:
once a structured rendezvous case has recorded its physical assumptions, this
module decides which of the two scoped deterministic implementations
(``src/cw.py`` or ``src/twobody.py``) applies, or whether the case needs more
information or is outside both contracts.

It is explicitly **not** a learned or universal numeric-threshold classifier.
The only numeric heuristics used are the ones already documented and
implemented in ``src/cw.py`` (``validate_cw_use``'s separation-ratio and
~two-orbit duration heuristics, and the two-impulse targeting conditioning
reported by ``two_burn_targeting``). Those heuristics are each one signal
among several required assumption items; the final selection never rests on
a single one of them in isolation.

Required assumption items (``reference/SOURCE.md`` §B.1 and the model-selector
skill's checklist):

1. circularity (reference-orbit circular or justified near-circular);
2. locality (small relative separation vs. orbital radius, not global
   phasing);
3. duration/regime (fixed transfer duration compatible with linearization);
4. frame (explicit right-handed LVLH/RIC convention and state ordering);
5. other physics (central-body dominance, negligible perturbations, small
   relative velocity); and
6. maneuver assumptions (impulsive-burn suitability).

A seventh, optional signal -- CW two-impulse targeting conditioning -- is
computed from ``src/cw.py::two_burn_targeting`` when enough state is supplied,
and is used only to qualify an otherwise-clean CW decision, never to select a
model on its own.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal, Optional, Sequence

import numpy as np

from .cw import CWSingularTransferError, two_burn_targeting, validate_cw_use

Assessment = Literal["supported", "violated", "boundary", "unknown"]

Selection = Literal[
    "CW rendezvous",
    "bounded two-body fallback",
    "UNSUPPORTED",
    "NEEDS MORE INFORMATION",
]

REQUIRED_ITEMS: tuple[str, ...] = (
    "circularity",
    "locality",
    "duration_regime",
    "frame",
    "other_physics",
    "maneuver_assumptions",
)

# The exact separation-ratio warning text produced by src.cw.validate_cw_use.
# Matched verbatim rather than re-deriving its 1% threshold here, so this
# module never maintains a second copy of that documented heuristic.
_SEPARATION_WARNING = "Relative separation is large compared with orbit radius."
_DURATION_WARNING = "Transfer spans more than about two orbital periods."


@dataclass(frozen=True)
class ModelSelectionCase:
    """Structured, assumption-based inputs for :func:`select_model`.

    Each of the six required items (see module docstring) is either stated
    directly as an :data:`Assessment` ("supported" / "violated" / "boundary" /
    "unknown", default "unknown"), or -- for ``locality`` and
    ``duration_regime`` only -- left as ``None`` so it is computed from raw
    numeric fields using the existing ``src.cw.validate_cw_use`` heuristic.
    An explicit assessment always takes priority over a computed one.

    This case is not a free-text problem description; it is the already
    distilled output of problem formalization (``orbital-problem-formalizer``)
    plus assumption review (``orbital-model-selector``). Supplying an
    assumption here is itself an assumption-based judgment call made upstream
    of this deterministic combination step.
    """

    # 1. Circularity (not numerically derivable here; must be stated).
    circularity: Assessment = "unknown"

    # 2. Locality / separation vs. reference-orbit radius.
    locality: Optional[Assessment] = None
    reference_radius_m: Optional[float] = None
    relative_separation_m: Optional[float] = None

    # 3. Duration / regime.
    duration_regime: Optional[Assessment] = None
    transfer_time_s: Optional[float] = None
    mean_motion_rad_s: Optional[float] = None

    # 4. Frame / LVLH-RIC convention and state ordering.
    frame: Assessment = "unknown"

    # 5. Other physics: central-body dominance, negligible perturbations,
    #    small relative velocity.
    other_physics: Assessment = "unknown"

    # 6. Maneuver assumptions (impulsive-burn suitability).
    maneuver_assumptions: Assessment = "unknown"

    # Optional 7th signal: CW two-impulse targeting conditioning. Supply the
    # assessment directly, or supply the state below to compute it from
    # src.cw.two_burn_targeting.
    targeting_conditioning: Optional[Assessment] = None
    initial_relative_state: Optional[Sequence[float]] = None
    final_relative_state: Optional[Sequence[float]] = None

    # Bounded two-body coast contract fields (src/twobody.py), used only to
    # decide whether a CW-rejected case may be routed to the fallback.
    inertial_cartesian_state: Optional[Sequence[float]] = None
    mu_m3_s2: Optional[float] = None
    coast_duration_s: Optional[float] = None
    rk4_steps: Optional[int] = None
    is_coast_only_request: bool = True

    notes: str = ""


@dataclass(frozen=True)
class ModelSelectionResult:
    """Assumption-based model-selection outcome.

    ``selection`` is restricted to the four semester-scoped outcomes named in
    ``.pi/skills/orbital-model-selector/SKILL.md``. ``qualified`` is ``True``
    only for a boundary/ambiguous CW case: the selection is still "CW
    rendezvous", but at least one required or supporting assumption is
    marginal rather than clearly supported, so the result and its
    verification sensitivity must stay visible to the user rather than being
    reported as a clean pass.
    """

    selection: Selection
    qualified: bool
    reasons: tuple[str, ...]
    assumptions: tuple[str, ...]
    concerns: tuple[str, ...]
    deterministic_tool: Optional[str]
    missing_items: tuple[str, ...] = field(default_factory=tuple)


def _separation_signal(reference_radius_m: float, relative_separation_m: float) -> Assessment:
    if reference_radius_m <= 0:
        return "violated"
    validity = validate_cw_use(
        reference_radius_m,
        np.array([relative_separation_m, 0.0, 0.0]),
        transfer_time_s=1.0,
        n=None,
    )
    return "violated" if _SEPARATION_WARNING in validity.warnings else "supported"


def _duration_signal(transfer_time_s: float, mean_motion_rad_s: float) -> Assessment:
    if transfer_time_s <= 0 or mean_motion_rad_s <= 0:
        return "violated"
    validity = validate_cw_use(
        reference_radius_m=1.0,
        relative_position_m=np.zeros(3),
        transfer_time_s=transfer_time_s,
        n=mean_motion_rad_s,
    )
    return "violated" if _DURATION_WARNING in validity.warnings else "supported"


def _assess_locality(case: ModelSelectionCase) -> Assessment:
    if case.locality is not None:
        return case.locality
    if case.reference_radius_m is None or case.relative_separation_m is None:
        return "unknown"
    return _separation_signal(case.reference_radius_m, case.relative_separation_m)


def _assess_duration_regime(case: ModelSelectionCase) -> Assessment:
    if case.duration_regime is not None:
        return case.duration_regime
    if case.transfer_time_s is None or case.mean_motion_rad_s is None:
        return "unknown"
    return _duration_signal(case.transfer_time_s, case.mean_motion_rad_s)


def _assess_targeting_conditioning(case: ModelSelectionCase) -> Optional[Assessment]:
    """Return the optional CW targeting-conditioning signal, or ``None``.

    ``None`` means the signal was neither supplied nor computable; it is a
    secondary, supporting check and must not block or force a selection on
    its own (see module docstring).
    """
    if case.targeting_conditioning is not None:
        return case.targeting_conditioning
    if (
        case.initial_relative_state is None
        or case.transfer_time_s is None
        or case.mean_motion_rad_s is None
    ):
        return None
    state0 = np.asarray(case.initial_relative_state, dtype=float)
    if state0.shape != (6,) or not np.isfinite(state0).all():
        return None
    target = (
        np.asarray(case.final_relative_state, dtype=float)
        if case.final_relative_state is not None
        else None
    )
    try:
        result = two_burn_targeting(state0, case.mean_motion_rad_s, case.transfer_time_s, target)
    except CWSingularTransferError:
        return "violated"
    if result.status == "unique":
        return "supported"
    if result.status == "singular-reachable":
        return "boundary"
    return "violated"


def _two_body_contract_satisfied(case: ModelSelectionCase) -> bool:
    """Return whether the case fits the bounded two-body coast contract.

    Mirrors the required inputs of ``src/twobody.py``: a finite six-element
    inertial Cartesian state, positive ``mu``, finite duration, and a
    positive fixed RK4 step count, for a coast-only request.
    """
    if not case.is_coast_only_request:
        return False
    if case.inertial_cartesian_state is None:
        return False
    state = np.asarray(case.inertial_cartesian_state, dtype=float)
    if state.shape != (6,) or not np.isfinite(state).all():
        return False
    if case.mu_m3_s2 is None or not math.isfinite(case.mu_m3_s2) or case.mu_m3_s2 <= 0:
        return False
    if case.coast_duration_s is None or not math.isfinite(case.coast_duration_s):
        return False
    if case.rk4_steps is None or case.rk4_steps <= 0:
        return False
    return True


def select_model(case: ModelSelectionCase) -> ModelSelectionResult:
    """Select CW, the bounded two-body fallback, or request clarification.

    Combines all required assumption items (never a single one alone). See
    the module docstring and ``reference/SOURCE.md`` §D for the governing
    contract.
    """
    assessments: dict[str, Assessment] = {
        "circularity": case.circularity,
        "locality": _assess_locality(case),
        "duration_regime": _assess_duration_regime(case),
        "frame": case.frame,
        "other_physics": case.other_physics,
        "maneuver_assumptions": case.maneuver_assumptions,
    }
    targeting = _assess_targeting_conditioning(case)

    assumptions = tuple(f"{item}: {status}" for item, status in assessments.items())
    if targeting is not None:
        assumptions = assumptions + (f"targeting_conditioning: {targeting}",)

    unknown_items = tuple(item for item, status in assessments.items() if status == "unknown")
    violated_items = tuple(item for item, status in assessments.items() if status == "violated")
    boundary_items = tuple(item for item, status in assessments.items() if status == "boundary")

    reasons: list[str] = []
    concerns: list[str] = []

    if unknown_items:
        reasons.append(
            "Required assumption(s) "
            + ", ".join(unknown_items)
            + " are unknown; a model cannot be selected until the problem "
            "record states them."
        )
        if violated_items:
            concerns.append(
                "Already-known violated assumption(s) "
                + ", ".join(violated_items)
                + " indicate the requested model may remain unsuitable even "
                "once the missing information is supplied."
            )
        return ModelSelectionResult(
            selection="NEEDS MORE INFORMATION",
            qualified=False,
            reasons=tuple(reasons),
            assumptions=assumptions,
            concerns=tuple(concerns),
            deterministic_tool=None,
            missing_items=unknown_items,
        )

    # All six required items are known (none "unknown").
    if violated_items:
        reasons.append("Violated CW assumption(s): " + ", ".join(violated_items) + ".")
        if _two_body_contract_satisfied(case):
            if targeting is not None:
                concerns.append(f"CW targeting-conditioning signal (not used for this selection): {targeting}.")
            return ModelSelectionResult(
                selection="bounded two-body fallback",
                qualified=False,
                reasons=tuple(reasons),
                assumptions=assumptions,
                concerns=tuple(concerns),
                deterministic_tool="src.twobody.propagate_cartesian_state",
            )
        reasons.append(
            "The case does not satisfy the bounded two-body coast contract "
            "(finite six-element inertial Cartesian state, positive mu, "
            "finite duration, positive RK4 step count, coast-only request) "
            "or requests an unsupported capability (targeting, maneuvers, "
            "optimization, thrust, or perturbations)."
        )
        return ModelSelectionResult(
            selection="UNSUPPORTED",
            qualified=False,
            reasons=tuple(reasons),
            assumptions=assumptions,
            concerns=tuple(concerns),
            deterministic_tool=None,
        )

    # No violated, no unknown required items: CW is a candidate.
    if boundary_items or targeting in ("boundary", "violated"):
        if boundary_items:
            concerns.append("Boundary assumption(s): " + ", ".join(boundary_items) + ".")
        if targeting == "boundary":
            concerns.append(
                "CW two-impulse targeting is singular but reachable at this transfer "
                "time; the returned velocity would be a non-unique SVD minimum-norm "
                "solution."
            )
        elif targeting == "violated":
            concerns.append(
                "CW two-impulse targeting is singular and the requested terminal "
                "state is unreachable at this transfer time."
            )
        concerns.append(
            "Qualified selection: verify this result against an independent "
            "numerical propagation (gmat-rendezvous-verification) before treating "
            "it as a clean pass."
        )
        reasons.append(
            "All required assumptions are supported, but at least one required "
            "or supporting signal is boundary/marginal rather than clearly "
            "supported."
        )
        return ModelSelectionResult(
            selection="CW rendezvous",
            qualified=True,
            reasons=tuple(reasons),
            assumptions=assumptions,
            concerns=tuple(concerns),
            deterministic_tool="src.cw.two_burn_targeting",
        )

    reasons.append(
        "All required CW assumptions (circularity, locality, duration/regime, "
        "frame, other physics, maneuver assumptions) are supported."
    )
    return ModelSelectionResult(
        selection="CW rendezvous",
        qualified=False,
        reasons=tuple(reasons),
        assumptions=assumptions,
        concerns=tuple(concerns),
        deterministic_tool="src.cw.two_burn_targeting",
    )
