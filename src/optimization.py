"""Simple rendezvous optimization problem definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ObjectiveType = Literal["min_delta_v", "min_transfer_time", "pareto_delta_v_time", "delta_v_budget"]


@dataclass
class RendezvousOptimizationProblem:
    objective: ObjectiveType
    decision_variables: list[str]
    constraints: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def minimize_delta_v_problem() -> RendezvousOptimizationProblem:
    return RendezvousOptimizationProblem(
        objective="min_delta_v",
        decision_variables=["dv0", "dv1", "transfer_time"],
        constraints=["terminal rendezvous conditions", "dynamics consistency"],
        notes=["Suitable for CW STM targeting or nonlinear least-squares."],
    )


def minimize_transfer_time_problem() -> RendezvousOptimizationProblem:
    return RendezvousOptimizationProblem(
        objective="min_transfer_time",
        decision_variables=["dv0", "dv1", "transfer_time"],
        constraints=["terminal rendezvous conditions", "delta-v feasibility"],
        notes=["May require integer or multi-revolution handling."],
    )


def delta_v_constrained_rendezvous_problem(budget_mps: float) -> RendezvousOptimizationProblem:
    return RendezvousOptimizationProblem(
        objective="delta_v_budget",
        decision_variables=["dv0", "dv1", "transfer_time"],
        constraints=[f"total_delta_v <= {budget_mps} m/s", "terminal rendezvous conditions"],
        notes=["Optimize feasibility or time subject to burn budget."],
    )
