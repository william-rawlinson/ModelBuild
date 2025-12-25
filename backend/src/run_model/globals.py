from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, List, Callable, Set

State = str
Treatment: str

@dataclass(frozen=True)
class TransitionMatrixContext:
    cycle: int
    treatment: Treatment
    params: Dict[str, Any]
    health_states: List[State]


@dataclass(frozen=True)
class EventContext:
    cycle: int
    treatment: Treatment
    params: Dict[str, Any]
    health_states: List[State]


@dataclass
class EventImpact:
    cost_occupation: NamedVector
    qaly_occupation: NamedVector
    cost_flow: NamedMatrix
    qaly_flow: NamedMatrix

def initialise_impact(health_states: List[str]) -> EventImpact:
    n = len(health_states)

    return EventImpact(
        cost_occupation=NamedVector(np.zeros(n, dtype=float), health_states),
        qaly_occupation=NamedVector(np.zeros(n, dtype=float), health_states),
        cost_flow=NamedMatrix(np.zeros((n, n), dtype=float), health_states),
        qaly_flow=NamedMatrix(np.zeros((n, n), dtype=float), health_states),
    )

@dataclass(frozen=True)
class EventSpec:
    event_name: str
    applies_to_treatments: Optional[Set[Treatment]] = None
    enabled: bool = True
    tags: Set[str] = field(default_factory=set)
    calculation_function: Callable[[EventContext], EventImpact] = None


# -------------------------
# Helpers: build P, validate, compile accrual matrices
# -------------------------

import numpy as np
from typing import List, Dict, Iterable

class NamedVector:
    def __init__(self, data: np.ndarray, names: List[str]):
        if data.ndim != 1:
            raise ValueError("NamedVector requires a 1D numpy array")
        if len(data) != len(names):
            raise ValueError("Length of data and names must match")

        self._data = data
        self._index: Dict[str, int] = {name: i for i, name in enumerate(names)}

    # --- core access ---
    def __getitem__(self, name: str) -> float:
        return self._data[self._index[name]]

    def __setitem__(self, name: str, value: float) -> None:
        self._data[self._index[name]] = value

    def add(self, name: str, value: float) -> None:
        self._data[self._index[name]] += value

    # --- helpers ---
    def keys(self) -> Iterable[str]:
        return self._index.keys()

    def values(self) -> np.ndarray:
        return self._data

    def as_array(self) -> np.ndarray:
        """Direct access to the underlying numpy array (no copy)."""
        return self._data

class NamedMatrix:
    def __init__(self, data: np.ndarray, names: List[str]):
        if data.ndim != 2:
            raise ValueError("NamedMatrix requires a 2D numpy array")
        if data.shape[0] != data.shape[1]:
            raise ValueError("NamedMatrix must be square")
        if data.shape[0] != len(names):
            raise ValueError("Matrix size must match number of names")

        self._data = data
        self._index: Dict[str, int] = {name: i for i, name in enumerate(names)}

    # --- core access ---
    def get(self, from_state: str, to_state: str) -> float:
        return self._data[self._index[from_state], self._index[to_state]]

    def set(self, from_state: str, to_state: str, value: float) -> None:
        self._data[self._index[from_state], self._index[to_state]] = value

    def add(self, from_state: str, to_state: str, value: float) -> None:
        self._data[self._index[from_state], self._index[to_state]] += value

    # --- helpers ---
    def as_array(self) -> np.ndarray:
        """Direct access to underlying numpy matrix (no copy)."""
        return self._data


class NamedTransitionMatrix:
    def __init__(self, states: list[str]):
        self.states = list(states)
        self.idx = {s: i for i, s in enumerate(states)}
        n = len(states)
        self._data = np.zeros((n, n), dtype=float)

    def set(self, origin: str, destination: str, value: float) -> None:
        self._data[self.idx[origin], self.idx[destination]] = value

    def add(self, origin: str, destination: str, value: float) -> None:
        self._data[self.idx[origin], self.idx[destination]] += value

    def get(self, origin: str, destination: str) -> float:
        return self._data[self.idx[origin], self.idx[destination]]

    def as_array(self) -> np.ndarray:
        return self._data


def validate_transition_matrix(P: np.ndarray, *, tol: float = 1e-10) -> np.ndarray:
    if np.any(P < -tol):
        raise ValueError("Negative transition probabilities")

    row_sums = P.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=tol):
        raise ValueError(f"Row sums must equal 1. Got {row_sums}")

    return P

def event_applies(spec: EventSpec, ctx: EventContext) -> bool:
    if not spec.enabled:
        return False
    if spec.applies_to_treatments is not None and ctx.treatment not in spec.applies_to_treatments:
        return False
    return True

def compile_impacts(
    *,
    health_states: List[State],
    treatment: Treatment,
    cycle: int,
    params: Dict[str, Any],
    event_specs: List[EventSpec],
) -> Dict[str, Any]:
    """
    Returns:
      - total_impact: EventImpact with summed effects
      - per_event_impacts: dict[event_name] -> EventImpact
    """
    context = EventContext(
        cycle=cycle,
        treatment=treatment,
        params=params,
        health_states=health_states,
    )

    total_impact = initialise_impact(health_states)
    per_event_impacts: Dict[str, EventImpact] = {}

    for event_spec in event_specs:
        if not event_applies(event_spec, context):
            continue

        impact = event_spec.calculation_function(context)
        per_event_impacts[event_spec.event_name] = impact

        # --- add underlying numpy arrays ---
        total_impact.cost_occupation.as_array()[:] += impact.cost_occupation.as_array()
        total_impact.qaly_occupation.as_array()[:] += impact.qaly_occupation.as_array()
        total_impact.cost_flow.as_array()[:, :] += impact.cost_flow.as_array()
        total_impact.qaly_flow.as_array()[:, :] += impact.qaly_flow.as_array()

    return {
        "total_impact": total_impact,
        "per_event_impacts": per_event_impacts,
    }