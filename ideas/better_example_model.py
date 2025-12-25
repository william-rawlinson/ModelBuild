from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Set

State = str
Treatment = str

@dataclass(frozen=True)
class EventContext:
    state: str
    cycle: int
    treatment: str
    params: Dict[str, Any]

@dataclass(frozen=True)
class EventSpec:
    event_name: str               # human label e.g. "Treatment cost"
    applies_to_states: Optional[Set[str]] = None      # None => all states
    applies_to_treatments: Optional[Set[str]] = None  # None => all treatments
    enabled: bool = True
    tags: Set[str] = field(default_factory=set)

    # The actual implementation (pure function)
    fn: Callable[[EventContext], "EventResult"] = None

def event_applies(spec: EventSpec, ctx: EventContext) -> bool:
    if not spec.enabled:
        return False
    if spec.applies_to_states is not None and ctx.state not in spec.applies_to_states:
        return False
    if spec.applies_to_treatments is not None and ctx.treatment not in spec.applies_to_treatments:
        return False
    return True


@dataclass
class Transition:
    from_state: State
    to_state: State
    probability: float  # conditional on event happening or absolute (pick one convention)

@dataclass
class EventResult:
    event_name: str
    qaly: float
    cost: float
    transitions: Optional[List[Transition]]  # None means “no transitions”

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
        "initial_occupancy": {"PFS":1, "PPS":0, "Death":0},
        "cycle_length": 1,          # year
        "time_horizon": 30,         # years
        "discount_rate_cost": 0.05, # 5%
        "discount_rate_QALY": 0.05, # 5%
        "health_states": ["PFS", "PPS", "Death"],
        "treatments": ["treatment_a", "treatment_b"],
    }

def treatment_cost_impl(ctx: EventContext) -> EventResult:
    probability = 1.0 if ctx.cycle == 0 else 0.0

    if ctx.treatment == "treatment_a":
        unit_cost = ctx.params["treatment_a_cost"]
    elif ctx.treatment == "treatment_b":
        unit_cost = ctx.params["treatment_b_cost"]
    else:
        unit_cost = 0.0

    return EventResult(
        event_name="Treatment cost",
        qaly=0.0,
        cost=probability * unit_cost,
        transitions=None,
    )

treatment_cost_event = EventSpec(
    event_name="Treatment cost",
    applies_to_states=None,  # all states, or set(...) if you want
    applies_to_treatments=None,
    tags={"cost"},
    fn=treatment_cost_impl,
)

def baseline_utility_impl(ctx: EventContext) -> EventResult:
    p = 1.0  # always applies when called

    if ctx.state == "PFS":
        util = ctx.params["pfs_utility"]
    elif ctx.state == "PPS":
        util = ctx.params["pps_utility"]
    else:
        util = 0.0  # Death or unknown

    qaly = p * util * ctx.params["cycle_length"]

    return EventResult(
        event_name="Health state utility",
        qaly=qaly,
        cost=0.0,
        transitions=None,
    )

baseline_utility_event = EventSpec(
    event_name="Health state utility",
    applies_to_states={"PFS", "PPS"},   # utility only in living states
    applies_to_treatments=None,         # all treatments
    tags={"utility"},
    fn=baseline_utility_impl,
)


def pfs_transitions_impl(ctx: EventContext) -> EventResult:
    # This impl is only meant to be called for ctx.state == "PFS"
    # (spec applicability enforces that)
    if ctx.treatment == "treatment_a":
        rr = ctx.params["treatment_a_progression_rr"]
    elif ctx.treatment == "treatment_b":
        rr = ctx.params["treatment_b_progression_rr"]
    else:
        rr = 1.0

    p_prog = ctx.params["progression_prob_per_cycle_untreated"] * rr   # PFS -> PPS
    p_death = ctx.params["death_prob_pfs"]                              # PFS -> Death
    p_stay = 1.0 - (p_prog + p_death)                                   # PFS -> PFS

    # Safety clamp (ideally validator complains if it needed clamping)
    p_prog = max(0.0, min(1.0, p_prog))
    p_death = max(0.0, min(1.0, p_death))
    p_stay = max(0.0, min(1.0, p_stay))

    return EventResult(
        event_name="PFS transitions",
        qaly=0.0,
        cost=0.0,
        transitions=[
            Transition(from_state="PFS", to_state="PFS", probability=p_stay),
            Transition(from_state="PFS", to_state="PPS", probability=p_prog),
            Transition(from_state="PFS", to_state="Death", probability=p_death),
        ],
    )

pfs_transitions_event = EventSpec(
    event_name="PFS transitions",
    applies_to_states={"PFS"},
    applies_to_treatments=None,
    tags={"transition"},
    fn=pfs_transitions_impl,
)


def pps_transitions_impl(ctx: EventContext) -> EventResult:
    p_death = ctx.params["death_prob_pps"]     # PPS -> Death
    p_stay = 1.0 - p_death                     # PPS -> PPS

    p_death = max(0.0, min(1.0, p_death))
    p_stay = max(0.0, min(1.0, p_stay))

    return EventResult(
        event_name="PPS transitions",
        qaly=0.0,
        cost=0.0,
        transitions=[
            Transition(from_state="PPS", to_state="PPS", probability=p_stay),
            Transition(from_state="PPS", to_state="Death", probability=p_death),
        ],
    )

pps_transitions_event = EventSpec(
    event_name="PPS transitions",
    applies_to_states={"PPS"},
    applies_to_treatments=None,
    tags={"transition"},
    fn=pps_transitions_impl,
)

def death_state_transitions_impl(ctx: EventContext) -> EventResult:
    return EventResult(
        event_name="Death transitions",
        qaly=0.0,
        cost=0.0,
        transitions=[
            Transition(from_state="Death", to_state="Death", probability=1.0),
        ],
    )

death_state_transitions_event = EventSpec(
    event_name="Death transitions",
    applies_to_states={"Death"},
    applies_to_treatments=None,
    tags={"transition"},
    fn=death_state_transitions_impl,
)


def run_markov_model(
    *,
    events: List[EventSpec],
    parameters: Dict[str, Any],
    discount_timing: str = "mid",  # "start" | "mid" | "end"
    discount_rate_ly: Optional[float] = None,  # if None, uses discount_rate_QALY
) -> Dict[str, Any]:
    health_states: List[str] = parameters["health_states"]
    treatments: List[str] = parameters["treatments"]

    cycle_length: float = float(parameters["cycle_length"])  # in YEARS
    time_horizon: float = float(parameters["time_horizon"])  # in YEARS
    n_cycles: int = int(round(time_horizon / cycle_length))

    disc_cost_annual: float = float(parameters["discount_rate_cost"])
    disc_qaly_annual: float = float(parameters["discount_rate_QALY"])
    disc_ly_annual: float = disc_qaly_annual if discount_rate_ly is None else float(discount_rate_ly)

    transition_events = [e for e in events if e.tags and "transition" in e.tags]
    other_events = [e for e in events if not (e.tags and "transition" in e.tags)]

    event_names = [e.event_name for e in other_events if e.enabled]

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

    results = {
        "settings": {
            "cycle_length_years": cycle_length,
            "time_horizon_years": time_horizon,
            "n_cycles": n_cycles,
            "discount_timing": discount_timing,
            "discount_rate_cost_annual": disc_cost_annual,
            "discount_rate_qaly_annual": disc_qaly_annual,
            "discount_rate_ly_annual": disc_ly_annual,
        },
        "event_names": event_names,
        "treatments": treatments,
        "per_treatment": {},
        "icer": None,
    }

    # We'll fill ICER at the end using BOTH discounted and undiscounted totals
    totals_for_icer = {}  # trt -> {"cost_discounted":..., "qaly_discounted":..., "cost_undiscounted":..., "qaly_undiscounted":...}

    for trt in treatments:
        # ---------- occupancy (state membership proportions) ----------
        occupancy_by_cycle: List[Dict[str, float]] = []
        occ0 = {s: float(parameters["initial_occupancy"].get(s, 0.0)) for s in health_states}
        occupancy_by_cycle.append(occ0)

        # ---------- outcomes: cycle x state x event ----------
        # Undiscounted:
        cost_cse_u: List[Dict[str, Dict[str, float]]] = []  # cycle -> state -> event -> cost
        qaly_cse_u: List[Dict[str, Dict[str, float]]] = []  # cycle -> state -> event -> qaly
        # Discounted:
        cost_cse_d: List[Dict[str, Dict[str, float]]] = []
        qaly_cse_d: List[Dict[str, Dict[str, float]]] = []

        # ---------- life-years: cycle x state ----------
        ly_cs_u: List[Dict[str, float]] = []  # cycle -> state -> LY
        ly_cs_d: List[Dict[str, float]] = []

        # Running totals (undiscounted/discounted)
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

        # Life-year totals
        ly_totals = {
            "undiscounted": {"time_spent_total": 0.0, "time_spent_by_state": zeros_state_dict()},
            "discounted": {"time_spent_total": 0.0, "time_spent_by_state": zeros_state_dict()},
        }

        # ---------- main cycle loop ----------
        for cycle in range(n_cycles):
            occ = occupancy_by_cycle[cycle]

            t_years = time_at_cycle_years(cycle)
            df_cost = df(disc_cost_annual, t_years)
            df_qaly = df(disc_qaly_annual, t_years)
            df_ly = df(disc_ly_annual, t_years)

            # Initialize cycle slices
            cost_state_event_u = {s: zeros_event_dict() for s in health_states}
            qaly_state_event_u = {s: zeros_event_dict() for s in health_states}
            cost_state_event_d = {s: zeros_event_dict() for s in health_states}
            qaly_state_event_d = {s: zeros_event_dict() for s in health_states}

            # ---- 1) Life-years from occupancy ----
            ly_state_u = {}
            ly_state_d = {}
            for s in health_states:
                ly = float(occ.get(s, 0.0)) * cycle_length  # LY in this cycle for this state
                ly_state_u[s] = ly
                ly_state_d[s] = ly * df_ly

                ly_totals["undiscounted"]["time_spent_by_state"][s] += ly
                ly_totals["undiscounted"]["time_spent_total"] += ly
                ly_totals["discounted"]["time_spent_by_state"][s] += ly * df_ly
                ly_totals["discounted"]["time_spent_total"] += ly * df_ly

            ly_cs_u.append(ly_state_u)
            ly_cs_d.append(ly_state_d)

            # ---- 2) Cost/QALY contributions per (cycle,state,event) ----
            for state in health_states:
                weight = float(occ.get(state, 0.0))
                if weight == 0.0:
                    continue

                ctx = EventContext(state=state, cycle=cycle, treatment=trt, params=parameters)

                for spec in other_events:
                    if not spec.enabled:
                        continue
                    if not event_applies(spec, ctx):
                        continue

                    er = spec.fn(ctx)

                    c_u = weight * float(er.cost)
                    q_u = weight * float(er.qaly)

                    cost_state_event_u[state][spec.event_name] += c_u
                    qaly_state_event_u[state][spec.event_name] += q_u

                    c_d = c_u * df_cost
                    q_d = q_u * df_qaly

                    cost_state_event_d[state][spec.event_name] += c_d
                    qaly_state_event_d[state][spec.event_name] += q_d

                    # update totals (event/state/state-event/grand)
                    totals["undiscounted"]["cost_total"] += c_u
                    totals["undiscounted"]["qaly_total"] += q_u
                    totals["undiscounted"]["cost_by_event"][spec.event_name] += c_u
                    totals["undiscounted"]["qaly_by_event"][spec.event_name] += q_u
                    totals["undiscounted"]["cost_by_state"][state] += c_u
                    totals["undiscounted"]["qaly_by_state"][state] += q_u
                    totals["undiscounted"]["cost_by_state_event"][state][spec.event_name] += c_u
                    totals["undiscounted"]["qaly_by_state_event"][state][spec.event_name] += q_u

                    totals["discounted"]["cost_total"] += c_d
                    totals["discounted"]["qaly_total"] += q_d
                    totals["discounted"]["cost_by_event"][spec.event_name] += c_d
                    totals["discounted"]["qaly_by_event"][spec.event_name] += q_d
                    totals["discounted"]["cost_by_state"][state] += c_d
                    totals["discounted"]["qaly_by_state"][state] += q_d
                    totals["discounted"]["cost_by_state_event"][state][spec.event_name] += c_d
                    totals["discounted"]["qaly_by_state_event"][state][spec.event_name] += q_d

            cost_cse_u.append(cost_state_event_u)
            qaly_cse_u.append(qaly_state_event_u)
            cost_cse_d.append(cost_state_event_d)
            qaly_cse_d.append(qaly_state_event_d)

            # ---- 3) Transitions -> next occupancy ----
            next_occ = {s: 0.0 for s in health_states}

            for origin in health_states:
                origin_mass = float(occ.get(origin, 0.0))
                if origin_mass == 0.0:
                    continue

                ctx = EventContext(state=origin, cycle=cycle, treatment=trt, params=parameters)
                applicable = [spec for spec in transition_events if event_applies(spec, ctx)]

                if len(applicable) == 0:
                    next_occ[origin] += origin_mass
                    continue

                if len(applicable) > 1:
                    names = [s.event_name for s in applicable]
                    raise ValueError(
                        f"Multiple transition events apply to origin={origin}, treatment={trt}, cycle={cycle}: {names}"
                    )

                er = applicable[0].fn(ctx)
                trans = er.transitions or []

                row_sum = 0.0
                for t in trans:
                    if t.from_state != origin:
                        raise ValueError(
                            f"Transition from_state mismatch. Expected {origin}, got {t.from_state} in {er.event_name}"
                        )
                    p = float(t.probability)
                    if p < -1e-12 or p > 1.0 + 1e-12:
                        raise ValueError(f"Invalid probability {p} in {er.event_name}")
                    row_sum += p
                    if t.to_state not in next_occ:
                        raise ValueError(f"Unknown to_state {t.to_state} in {er.event_name}")
                    next_occ[t.to_state] += origin_mass * p

                if abs(row_sum - 1.0) > 1e-6:
                    raise ValueError(
                        f"Transition probabilities out of {origin} do not sum to 1. "
                        f"Sum={row_sum} in {er.event_name} (treatment={trt}, cycle={cycle})"
                    )

            occupancy_by_cycle.append(next_occ)

        # Save treatment results
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
                # occupancy itself is not discounted; we discount derived LYs
                "occupancy_by_cycle": occupancy_by_cycle,
                "undiscounted": {
                    "time_spent_per_cycle_state": ly_cs_u,
                    "totals": ly_totals["undiscounted"],
                },
                "discounted": {
                    "time_spent_per_cycle_state": ly_cs_d,
                    "totals": ly_totals["discounted"],
                },
            },
        }

        totals_for_icer[trt] = {
            "cost_discounted": totals["discounted"]["cost_total"],
            "qaly_discounted": totals["discounted"]["qaly_total"],
            "cost_undiscounted": totals["undiscounted"]["cost_total"],
            "qaly_undiscounted": totals["undiscounted"]["qaly_total"],
        }

    # ---------- ICERs (each comparator vs first treatment = intervention) ----------
    ref = treatments[0]

    def compute_icers(kind: str) -> Dict[str, Any]:
        # kind in {"discounted", "undiscounted"}
        ref_cost = totals_for_icer[ref][f"cost_{kind}"]
        ref_qaly = totals_for_icer[ref][f"qaly_{kind}"]

        comps = []
        for comp in treatments[1:]:
            c_cost = totals_for_icer[comp][f"cost_{kind}"]
            c_qaly = totals_for_icer[comp][f"qaly_{kind}"]

            d_cost = c_cost - ref_cost
            d_qaly = c_qaly - ref_qaly
            icer = None if abs(d_qaly) < 1e-12 else (d_cost / d_qaly)

            comps.append(
                {
                    "comparator": comp,
                    "delta_cost": d_cost,
                    "delta_qaly": d_qaly,
                    "icer": icer,
                }
            )

        return {
            "reference_treatment": ref,
            "comparisons": comps,
        }

    results["icer"] = {
        "discounted": compute_icers("discounted"),
        "undiscounted": compute_icers("undiscounted"),
        "note": "ICERs computed for both discounted and undiscounted totals",
    }

    return results

from copy import deepcopy
from typing import Any, Dict, List, Set

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




if __name__ == "__main__":

    results = run_markov_model(events=[pfs_transitions_event, pps_transitions_event, death_state_transitions_event,
                                       treatment_cost_event, baseline_utility_event], parameters=parameters)

    filtered_results = prune_zero_by_metric(results=results)

    import json

    with open("../frontend/src/data/dummy_results.json", "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=2)

    pass

