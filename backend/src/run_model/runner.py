from typing import Callable, List, Dict, Any
from backend.src.run_model.globals import TransitionMatrixContext, EventSpec, validate_transition_matrix, compile_impacts
import numpy as np

def run_markov_model(
    *,
    build_transition_matrix_fn: Callable[[TransitionMatrixContext], np.ndarray],
    event_specs: List[EventSpec],
    parameters: Dict[str, Any],
    health_states: List[str],
    treatments: List[str],
    cycle_length_years: float,
    time_horizon_years: float,
    disc_rate_cost_annual: float,
    disc_rate_qaly_annual: float,
    initial_occupancy: Dict[str, Any],
    discount_timing: str = "mid",

) -> Dict[str, Any]:

    idx = {s: i for i, s in enumerate(health_states)}

    event_names = [e.event_name for e in event_specs if e.enabled]

    n_cycles = int(time_horizon_years / cycle_length_years)

    # -------------------------
    # Helpers
    # -------------------------

    def time_at_cycle_years(cycle: int) -> float:
        if discount_timing == "start":
            return cycle * cycle_length_years
        if discount_timing == "mid":
            return (cycle + 0.5) * cycle_length_years
        if discount_timing == "end":
            return (cycle + 1.0) * cycle_length_years
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
            "cycle_length_years": cycle_length_years,
            "time_horizon_years": time_horizon_years,
            "discount_timing": discount_timing,
            "disc_rate_cost_annual": disc_rate_cost_annual,
            "discount_rate_qaly_annual": disc_rate_qaly_annual,
            "initial_occupancy": initial_occupancy,
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
            [float(initial_occupancy[trt].get(s, 0.0)) for s in health_states],
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
            df_cost = df(disc_rate_cost_annual, t_years)
            df_qaly = df(disc_rate_qaly_annual, t_years)

            # ---- time spent ----
            ts_u, ts_d = {}, {}
            for i, st in enumerate(health_states):
                ly = float(s_t[i]) * cycle_length_years
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
                cycle_length_years=cycle_length_years,
                time_horizon_years=time_horizon_years,
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
                cycle_length_years=cycle_length_years,
                time_horizon_years=time_horizon_years,
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
            d_cost = ref_cost - totals_for_icer[comp][f"cost_{kind}"]
            d_qaly =  ref_qaly - totals_for_icer[comp][f"qaly_{kind}"]
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