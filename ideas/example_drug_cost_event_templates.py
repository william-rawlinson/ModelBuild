
drug_cost_simple_spec = {
  "template": "drug_cost_simple_per_cycle",
  "event_name": "Drug acquisition cost",
  "base": {
    "type": "state",
    "states": ["PFS"]
  },
  "cost_per_cycle": {
    "treatment_a": "treatment_a_cost",
    "treatment_b": "treatment_b_cost"
  },
  "start_cycle": 0,
  "end_cycle": None   # or an int, or "until_state_exit"
}


# TODO having a global validator is by far the way to go - so we always validate specs and then if the LLM makes a mistake we explain it


def compile_drug_cost_simple(spec):
    fn_name = f"{spec['event_name'].lower().replace(' ', '_')}_event_fn"

    states = spec["base"]["states"]
    cost_map = spec["cost_per_cycle"]
    start = spec.get("start_cycle", 0)
    end = spec.get("end_cycle")

    state_list = "[" + ", ".join(repr(s) for s in states) + "]"

    if end is None:
        rate_logic = f"return 1.0 if cycle >= {start} else 0.0"
    else:
        rate_logic = f"return 1.0 if {start} <= cycle <= {end} else 0.0"

    cost_lines = []
    for trt, param in cost_map.items():
        cost_lines.append(
            f"        if treatment == {trt!r}:\n"
            f"            return parameters[{param!r}]"
        )
    cost_body = "\n".join(cost_lines) + "\n        return 0.0"

    return f'''
def {fn_name}(state, cycle, treatment, parameters):
    base = {{"type": "state", "states": {state_list}}}

    def rate_fn(state, cycle, treatment, parameters):
        {rate_logic}

    def unit_cost_fn(state, cycle, treatment, parameters):
{cost_body}

    def unit_qaly_fn(state, cycle, treatment, parameters):
        return 0.0

    return {{
        "event_name": {spec["event_name"]!r},
        "base": base,
        "rate_fn": rate_fn,
        "unit_cost_fn": unit_cost_fn,
        "unit_qaly_fn": unit_qaly_fn,
        "transitions_fn": None
    }}
'''

complex_drug_cost_spec = {
  "template": "drug_cost_per_admin",
  "event_name": "Drug acquisition cost",
  "base": {"type": "state", "states": ["PFS"]},

  "schedule": {
    "type": "fixed_interval",
    "interval_days": 21,
    "cycle_length_days_param": "cycle_length_days",
    "rounding": "none"          # "none" (fractional ok), "floor", "ceil"
  },

  "unit_cost_per_admin": {
    "treatment_a": "treatment_a_cost_per_admin",
    "treatment_b": "treatment_b_cost_per_admin"
  },

  "start_cycle": 0,
  "end_cycle": None
}

def compile_drug_cost_complex(spec):
    fn_name = f"{spec['event_name'].lower().replace(' ', '_')}_event_fn"

    states = spec["base"]["states"]
    cost_map = spec["unit_cost_per_admin"]
    start = spec.get("start_cycle", 0)
    end = spec.get("end_cycle")

    schedule = spec["schedule"]
    interval_days = schedule["interval_days"]
    cycle_length_days_param = schedule["cycle_length_days_param"]
    rounding = schedule.get("rounding", "none")

    state_list = "[" + ", ".join(repr(s) for s in states) + "]"

    # gate by cycle window
    if end is None:
        gate_logic = f"(cycle >= {start})"
    else:
        gate_logic = f"({start} <= cycle <= {end})"

    # administrations per cycle
    base_rate = f"(parameters[{cycle_length_days_param!r}] / {float(interval_days)})"

    if rounding == "none":
        rate_expr = base_rate
    elif rounding == "floor":
        rate_expr = f"float(int({base_rate}))"
    elif rounding == "ceil":
        # cheap ceil without importing: ceil(x) = int(x) if x==int(x) else int(x)+1
        rate_expr = (
            f"(lambda x: float(int(x) if x == int(x) else int(x) + 1))({base_rate})"
        )
    else:
        # no validation yet, but keep deterministic fallback
        rate_expr = base_rate

    rate_logic = f"return ({rate_expr}) if {gate_logic} else 0.0"

    # unit cost per admin mapping
    cost_lines = []
    for trt, param in cost_map.items():
        cost_lines.append(
            f"        if treatment == {trt!r}:\n"
            f"            return parameters[{param!r}]"
        )
    cost_body = "\n".join(cost_lines) + "\n        return 0.0"

    return f'''
def {fn_name}(state, cycle, treatment, parameters):
    base = {{"type": "state", "states": {state_list}}}

    def rate_fn(state, cycle, treatment, parameters):
        {rate_logic}

    def unit_cost_fn(state, cycle, treatment, parameters):
{cost_body}

    def unit_qaly_fn(state, cycle, treatment, parameters):
        return 0.0

    return {{
        "event_name": {spec["event_name"]!r},
        "base": base,
        "rate_fn": rate_fn,
        "unit_cost_fn": unit_cost_fn,
        "unit_qaly_fn": unit_qaly_fn,
        "transitions_fn": None
    }}
'''


if __name__ == "__main__":

    simple_drug_cost_event_fn = compile_drug_cost_simple(spec=drug_cost_simple_spec)

    complex_drug_cost_event_fn = compile_drug_cost_complex(spec=complex_drug_cost_spec)

    pass