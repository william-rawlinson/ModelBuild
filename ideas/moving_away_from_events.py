from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, List, Callable, Set
import time
from copy import deepcopy

State = str
Treatment = str

# -------------------------
# Contexts
# -------------------------

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

def event_applies(spec: EventSpec, ctx: EventContext) -> bool:
    if not spec.enabled:
        return False
    if spec.applies_to_treatments is not None and ctx.treatment not in spec.applies_to_treatments:
        return False
    return True


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

def build_transition_matrix(context: TransitionMatrixContext) -> np.ndarray:
    tm = NamedTransitionMatrix(context.health_states)

    # ---- shared calculations ----
    if context.treatment == "treatment_a":
        prog_rr = float(context.params["treatment_a_progression_rr"])
    elif context.treatment == "treatment_b":
        prog_rr = float(context.params["treatment_b_progression_rr"])
    else:
        prog_rr = 1.0

    # ---- PFS ----
    p_prog = float(context.params["progression_prob_per_cycle_untreated"]) * prog_rr
    p_death = float(context.params["death_prob_pfs"])
    p_stay = 1.0 - (p_prog + p_death)

    tm.set("PFS", "PPS", max(p_prog, 0.0))
    tm.set("PFS", "Death", max(p_death, 0.0))
    tm.set("PFS", "PFS", max(p_stay, 0.0))

    # ---- PPS ----
    p_death_pps = float(context.params["death_prob_pps"])
    p_stay_pps = 1.0 - p_death_pps

    tm.set("PPS", "Death", max(p_death_pps, 0.0))
    tm.set("PPS", "PPS", max(p_stay_pps, 0.0))

    # ---- Death ----
    tm.set("Death", "Death", 1.0)

    return tm.as_array()



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



# -------------------------
# Your original example: transformed
# -------------------------

parameters = {
    "treatment_a_cost": 100,
    "treatment_b_cost": 200,
    "progression_prob_per_cycle_untreated": 0.3,
    "death_prob_pfs": 0.1,
    "death_prob_pps": 0.2,
    "treatment_a_progression_rr": 0.75,
    "treatment_b_progression_rr": 0.80,
    "pfs_utility": 0.7,
    "pps_utility": 0.65,
    "initial_occupancy": {"PFS": 1, "PPS": 0, "Death": 0},
    "cycle_length": 1,
    "time_horizon": 30,
    "disc_rate_cost_annual": 0.05,
    "discount_rate_QALY": 0.05,
    "health_states": ["PFS", "PPS", "Death"],
    "treatments": ["treatment_a", "treatment_b"],
    "progression_cost": 1000,
}

# --- Accrual event 1: treatment cost (cycle 0, all states, occupancy-based) ---
def treatment_cost_event(context: EventContext) -> EventImpact:
    impact = initialise_impact(context.health_states)

    if context.cycle != 0:
        return impact

    if context.treatment == "treatment_a":
        unit_cost = float(context.params["treatment_a_cost"])
    elif context.treatment == "treatment_b":
        unit_cost = float(context.params["treatment_b_cost"])
    else:
        unit_cost = 0.0

    impact.cost_occupation.add("PFS", unit_cost)
    return impact

treatment_cost_event = EventSpec(
    event_name="Treatment cost",
    tags={"cost"},
    calculation_function=treatment_cost_event,
)

def progression_cost_event(context: EventContext) -> EventImpact:
    impact = initialise_impact(context.health_states)

    cost = float(context.params["progression_cost"])
    impact.cost_flow.add("PFS", "PPS", cost)

    return impact

progression_cost_event = EventSpec(
    event_name="Treatment cost",
    tags={"cost"},
    calculation_function=progression_cost_event,
)

# --- Accrual event 2: baseline utility (occupancy-based) ---
def baseline_utility_event(ctx: EventContext) -> EventImpact:
    impact = initialise_impact(ctx.health_states)
    cycle_length = float(ctx.params["cycle_length"])

    impact.qaly_occupation.add("PFS", float(ctx.params["pfs_utility"]) * cycle_length)
    impact.qaly_occupation.add("PPS", float(ctx.params["pps_utility"]) * cycle_length)

    # Death stays 0
    return impact

baseline_utility_event = EventSpec(
    event_name="Health state utility",
    tags={"utility"},
    calculation_function=baseline_utility_event,
)

# -------------------------
# Runner v2: uses P + (occupancy vectors + flow matrices)
# Keeps your discounted/undiscounted totals + per-cycle state-event cubes
# -------------------------

def run_markov_model(
    *,
    build_transition_matrix_fn: Callable[[TransitionMatrixContext], np.ndarray],
    event_specs: List[EventSpec],
    parameters: Dict[str, Any],
    health_states: List[str],
    treatments: List[str],
    n_cycles: int,
    discount_timing: str = "mid",

) -> Dict[str, Any]:

    idx = {s: i for i, s in enumerate(health_states)}

    cycle_length = float(parameters["cycle_length"])
    time_horizon = float(parameters["time_horizon"])
    disc_cost_annual = float(parameters["disc_rate_cost_annual"])
    disc_qaly_annual = float(parameters["discount_rate_QALY"])

    event_names = [e.event_name for e in event_specs if e.enabled]

    # -------------------------
    # Helpers
    # -------------------------

    def time_at_cycle_years(cycle: int) -> float:
        if discount_timing == "start":
            return cycle * cycle_length
        if discount_timing == "mid":
            return (cycle + 0.5) * cycle_length
        if discount_timing == "end":
            return (cycle + 1.0) * cycle_length
        raise ValueError("discount_timing must be 'start', 'mid', or 'end'")

    def df(rate_annual: float, t_years: float) -> float:
        return 1.0 / ((1.0 + rate_annual) ** t_years)

    def zeros_event_dict() -> Dict[str, float]:
        return {ename: 0.0 for ename in event_names}

    def zeros_state_dict() -> Dict[str, float]:
        return {s: 0.0 for s in health_states}

    # -------------------------
    # Results container
    # -------------------------

    results = {
        "settings": {
            "health_states": health_states,
            "cycle_length_years": cycle_length,
            "time_horizon_years": time_horizon,
            "n_cycles": n_cycles,
            "discount_timing": discount_timing,
            "disc_rate_cost_annual": disc_cost_annual,
            "discount_rate_qaly_annual": disc_qaly_annual,
        },
        "event_names": event_names,
        "treatments": treatments,
        "per_treatment": {},
        "icer": None,
    }

    totals_for_icer = {}

    # =========================
    # MAIN LOOP (by treatment)
    # =========================

    for trt in treatments:

        # ---- occupancy vectors ----
        s_by_cycle: List[np.ndarray] = []
        s0 = np.array(
            [float(parameters["initial_occupancy"].get(s, 0.0)) for s in health_states],
            dtype=float,
        )
        s_by_cycle.append(s0)

        # ---- cubes ----
        cost_cse_u, qaly_cse_u = [], []
        cost_cse_d, qaly_cse_d = [], []
        ts_cs_u, ts_cs_d = [], []

        totals = {
            "undiscounted": {
                "cost_total": 0.0,
                "qaly_total": 0.0,
                "cost_by_event": zeros_event_dict(),
                "qaly_by_event": zeros_event_dict(),
                "cost_by_state": zeros_state_dict(),
                "qaly_by_state": zeros_state_dict(),
                "cost_by_state_event": {s: zeros_event_dict() for s in health_states},
                "qaly_by_state_event": {s: zeros_event_dict() for s in health_states},
            },
            "discounted": {
                "cost_total": 0.0,
                "qaly_total": 0.0,
                "cost_by_event": zeros_event_dict(),
                "qaly_by_event": zeros_event_dict(),
                "cost_by_state": zeros_state_dict(),
                "qaly_by_state": zeros_state_dict(),
                "cost_by_state_event": {s: zeros_event_dict() for s in health_states},
                "qaly_by_state_event": {s: zeros_event_dict() for s in health_states},
            },
        }

        ts_totals = {
            "undiscounted": {"time_spent_total": 0.0, "time_spent_by_state": zeros_state_dict()},
            "discounted": {"time_spent_total": 0.0, "time_spent_by_state": zeros_state_dict()},
        }

        # =========================
        # CYCLE LOOP
        # =========================

        for cycle in range(n_cycles):

            s_t = s_by_cycle[cycle]
            t_years = time_at_cycle_years(cycle)
            df_cost = df(disc_cost_annual, t_years)
            df_qaly = df(disc_qaly_annual, t_years)

            # ---- time spent ----
            ts_u, ts_d = {}, {}
            for i, st in enumerate(health_states):
                ly = float(s_t[i]) * cycle_length
                ts_u[st] = ly
                ts_d[st] = ly

                ts_totals["undiscounted"]["time_spent_by_state"][st] += ly
                ts_totals["undiscounted"]["time_spent_total"] += ly
                ts_totals["discounted"]["time_spent_by_state"][st] += ly
                ts_totals["discounted"]["time_spent_total"] += ly

            ts_cs_u.append(ts_u)
            ts_cs_d.append(ts_d)

            # ---- transition matrix ----
            tm_ctx = TransitionMatrixContext(
                cycle=cycle,
                treatment=trt,
                params=parameters,
                health_states=health_states,
            )

            P_t = validate_transition_matrix(
                build_transition_matrix_fn(tm_ctx)
            )

            F_t = np.diag(s_t) @ P_t

            # ---- accruals ----
            impacts = compile_impacts(
                health_states=health_states,
                treatment=trt,
                cycle=cycle,
                params=parameters,
                event_specs=event_specs,
            )

            per_event = impacts["per_event_impacts"]

            cost_state_event_u = {s: zeros_event_dict() for s in health_states}
            qaly_state_event_u = {s: zeros_event_dict() for s in health_states}
            cost_state_event_d = {s: zeros_event_dict() for s in health_states}
            qaly_state_event_d = {s: zeros_event_dict() for s in health_states}

            for ename, contrib in per_event.items():

                c_occ = contrib.cost_occupation.as_array()
                u_occ = contrib.qaly_occupation.as_array()
                C_flow = contrib.cost_flow.as_array()
                U_flow = contrib.qaly_flow.as_array()

                # ---- occupancy effects ----
                for i, st in enumerate(health_states):
                    c_u = s_t[i] * c_occ[i]
                    q_u = s_t[i] * u_occ[i]

                    cost_state_event_u[st][ename] += c_u
                    qaly_state_event_u[st][ename] += q_u
                    cost_state_event_d[st][ename] += c_u * df_cost
                    qaly_state_event_d[st][ename] += q_u * df_qaly

                    totals["undiscounted"]["cost_total"] += c_u
                    totals["undiscounted"]["qaly_total"] += q_u
                    totals["undiscounted"]["cost_by_event"][ename] += c_u
                    totals["undiscounted"]["qaly_by_event"][ename] += q_u
                    totals["undiscounted"]["cost_by_state"][st] += c_u
                    totals["undiscounted"]["qaly_by_state"][st] += q_u
                    totals["undiscounted"]["cost_by_state_event"][st][ename] += c_u
                    totals["undiscounted"]["qaly_by_state_event"][st][ename] += q_u

                    totals["discounted"]["cost_total"] += c_u * df_cost
                    totals["discounted"]["qaly_total"] += q_u * df_qaly
                    totals["discounted"]["cost_by_event"][ename] += c_u * df_cost
                    totals["discounted"]["qaly_by_event"][ename] += q_u * df_qaly
                    totals["discounted"]["cost_by_state"][st] += c_u * df_cost
                    totals["discounted"]["qaly_by_state"][st] += q_u * df_qaly
                    totals["discounted"]["cost_by_state_event"][st][ename] += c_u * df_cost
                    totals["discounted"]["qaly_by_state_event"][st][ename] += q_u * df_qaly

                # ---- flow effects (attributed to origin) ----
                for i, origin in enumerate(health_states):
                    c_flow_u = float(np.sum(F_t[i, :] * C_flow[i, :]))
                    q_flow_u = float(np.sum(F_t[i, :] * U_flow[i, :]))

                    cost_state_event_u[origin][ename] += c_flow_u
                    qaly_state_event_u[origin][ename] += q_flow_u
                    cost_state_event_d[origin][ename] += c_flow_u * df_cost
                    qaly_state_event_d[origin][ename] += q_flow_u * df_qaly

                    totals["undiscounted"]["cost_total"] += c_flow_u
                    totals["undiscounted"]["qaly_total"] += q_flow_u
                    totals["undiscounted"]["cost_by_event"][ename] += c_flow_u
                    totals["undiscounted"]["qaly_by_event"][ename] += q_flow_u
                    totals["undiscounted"]["cost_by_state"][origin] += c_flow_u
                    totals["undiscounted"]["qaly_by_state"][origin] += q_flow_u
                    totals["undiscounted"]["cost_by_state_event"][origin][ename] += c_flow_u
                    totals["undiscounted"]["qaly_by_state_event"][origin][ename] += q_flow_u

                    totals["discounted"]["cost_total"] += c_flow_u * df_cost
                    totals["discounted"]["qaly_total"] += q_flow_u * df_qaly
                    totals["discounted"]["cost_by_event"][ename] += c_flow_u * df_cost
                    totals["discounted"]["qaly_by_event"][ename] += q_flow_u * df_qaly
                    totals["discounted"]["cost_by_state"][origin] += c_flow_u * df_cost
                    totals["discounted"]["qaly_by_state"][origin] += q_flow_u * df_qaly
                    totals["discounted"]["cost_by_state_event"][origin][ename] += c_flow_u * df_cost
                    totals["discounted"]["qaly_by_state_event"][origin][ename] += q_flow_u * df_qaly

            cost_cse_u.append(cost_state_event_u)
            qaly_cse_u.append(qaly_state_event_u)
            cost_cse_d.append(cost_state_event_d)
            qaly_cse_d.append(qaly_state_event_d)

            # ---- next occupancy ----
            s_by_cycle.append(s_t @ P_t)

        # ---- save treatment results ----
        occupancy_by_cycle = [
            {st: float(svec[idx[st]]) for st in health_states}
            for svec in s_by_cycle
        ]

        results["per_treatment"][trt] = {
            "outcomes": {
                "undiscounted": {
                    "costs_per_cycle_state_event": cost_cse_u,
                    "qalys_per_cycle_state_event": qaly_cse_u,
                    "totals": totals["undiscounted"],
                },
                "discounted": {
                    "costs_per_cycle_state_event": cost_cse_d,
                    "qalys_per_cycle_state_event": qaly_cse_d,
                    "totals": totals["discounted"],
                },
            },
            "occupancy": {
                "occupancy_by_cycle": occupancy_by_cycle,
                "undiscounted": {"time_spent_per_cycle_state": ts_cs_u, "totals": ts_totals["undiscounted"]},
                "discounted": {"time_spent_per_cycle_state": ts_cs_d, "totals": ts_totals["discounted"]},
            },
        }

        totals_for_icer[trt] = {
            "cost_discounted": totals["discounted"]["cost_total"],
            "qaly_discounted": totals["discounted"]["qaly_total"],
            "cost_undiscounted": totals["undiscounted"]["cost_total"],
            "qaly_undiscounted": totals["undiscounted"]["qaly_total"],
        }

    # -------------------------
    # ICERs
    # -------------------------

    ref = treatments[0]

    def compute_icers(kind: str):
        ref_cost = totals_for_icer[ref][f"cost_{kind}"]
        ref_qaly = totals_for_icer[ref][f"qaly_{kind}"]
        comps = []
        for comp in treatments[1:]:
            d_cost = totals_for_icer[comp][f"cost_{kind}"] - ref_cost
            d_qaly = totals_for_icer[comp][f"qaly_{kind}"] - ref_qaly
            icer = None if abs(d_qaly) < 1e-12 else d_cost / d_qaly
            comps.append({
                "comparator": comp,
                "delta_cost": d_cost,
                "delta_qaly": d_qaly,
                "icer": icer,
            })
        return {"reference_treatment": ref, "comparisons": comps}

    results["icer"] = {
        "discounted": compute_icers("discounted"),
        "undiscounted": compute_icers("undiscounted"),
        "note": "ICERs computed for both discounted and undiscounted totals",
    }

    return results


def prune_zero_by_metric(results: Dict[str, Any], *, tol: float = 1e-12) -> Dict[str, Any]:
    """
    Prune EVENTS with ~0 contribution, separately for costs and QALYs.
    Does NOT remove states (state keys are preserved for every cycle).
    """
    out = deepcopy(results)

    health_states = out.get("settings", {}).get("health_states")
    if health_states is None:
        # fallback to whatever the model stored
        # (best is to include health_states in settings)
        health_states = []
        # try infer from first treatment cube if needed
        try:
            any_trt = next(iter(out["per_treatment"].values()))
            first_cycle = any_trt["outcomes"]["undiscounted"]["costs_per_cycle_state_event"][0]
            health_states = list(first_cycle.keys())
        except Exception:
            pass

    def prune_cube(
        cube: List[Dict[str, Dict[str, float]]],
        keep: Set[str],
        health_states: List[str],
    ) -> List[Dict[str, Dict[str, float]]]:
        new_cube = []
        for cyc in cube:
            new_cyc = {}
            # preserve ALL states for this cycle
            for state in (health_states or list(cyc.keys())):
                evmap = cyc.get(state, {})  # if missing, keep empty
                new_cyc[state] = {e: v for e, v in evmap.items() if e in keep}
            new_cube.append(new_cyc)
        return new_cube

    def prune_totals_cost(totals_block: Dict[str, Any], keep_cost: Set[str]) -> None:
        totals_block["cost_by_event"] = {e: v for e, v in totals_block["cost_by_event"].items() if e in keep_cost}
        # preserve states; just prune event keys within each state
        for s, evmap in totals_block.get("cost_by_state_event", {}).items():
            totals_block["cost_by_state_event"][s] = {e: v for e, v in evmap.items() if e in keep_cost}

    def prune_totals_qaly(totals_block: Dict[str, Any], keep_qaly: Set[str]) -> None:
        totals_block["qaly_by_event"] = {e: v for e, v in totals_block["qaly_by_event"].items() if e in keep_qaly}
        for s, evmap in totals_block.get("qaly_by_state_event", {}).items():
            totals_block["qaly_by_state_event"][s] = {e: v for e, v in evmap.items() if e in keep_qaly}

    global_event_names = list(out.get("event_names", []))

    for trt, trt_res in out["per_treatment"].items():
        und_tot = trt_res["outcomes"]["undiscounted"]["totals"]
        dis_tot = trt_res["outcomes"]["discounted"]["totals"]

        keep_cost: Set[str] = set()
        keep_qaly: Set[str] = set()

        for e in global_event_names:
            u_cost = float(und_tot.get("cost_by_event", {}).get(e, 0.0))
            d_cost = float(dis_tot.get("cost_by_event", {}).get(e, 0.0))
            if (abs(u_cost) > tol) or (abs(d_cost) > tol):
                keep_cost.add(e)

            u_qaly = float(und_tot.get("qaly_by_event", {}).get(e, 0.0))
            d_qaly = float(dis_tot.get("qaly_by_event", {}).get(e, 0.0))
            if (abs(u_qaly) > tol) or (abs(d_qaly) > tol):
                keep_qaly.add(e)

        # Prune COST structures (events only)
        trt_res["outcomes"]["undiscounted"]["costs_per_cycle_state_event"] = prune_cube(
            trt_res["outcomes"]["undiscounted"]["costs_per_cycle_state_event"],
            keep_cost,
            health_states,
        )
        trt_res["outcomes"]["discounted"]["costs_per_cycle_state_event"] = prune_cube(
            trt_res["outcomes"]["discounted"]["costs_per_cycle_state_event"],
            keep_cost,
            health_states,
        )
        prune_totals_cost(und_tot, keep_cost)
        prune_totals_cost(dis_tot, keep_cost)

        # Prune QALY structures (events only)
        trt_res["outcomes"]["undiscounted"]["qalys_per_cycle_state_event"] = prune_cube(
            trt_res["outcomes"]["undiscounted"]["qalys_per_cycle_state_event"],
            keep_qaly,
            health_states,
        )
        trt_res["outcomes"]["discounted"]["qalys_per_cycle_state_event"] = prune_cube(
            trt_res["outcomes"]["discounted"]["qalys_per_cycle_state_event"],
            keep_qaly,
            health_states,
        )
        prune_totals_qaly(und_tot, keep_qaly)
        prune_totals_qaly(dis_tot, keep_qaly)

        trt_res["outcomes"]["cost_event_names"] = [e for e in global_event_names if e in keep_cost]
        trt_res["outcomes"]["qaly_event_names"] = [e for e in global_event_names if e in keep_qaly]

    return out


# -------------------------
# How you call it (your model)
# -------------------------

if __name__ == "__main__":

    start = time.time()

    event_specs = [treatment_cost_event, baseline_utility_event, progression_cost_event]

    results = run_markov_model(build_transition_matrix_fn=build_transition_matrix, event_specs=event_specs,
                               parameters=parameters)

    filtered_results = prune_zero_by_metric(results)

    print(f"ran model in {round(time.time()-start, 4)} seconds")

    import json

    with open("../frontend/src/data/dummy_results.json", "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=2)

    pass



