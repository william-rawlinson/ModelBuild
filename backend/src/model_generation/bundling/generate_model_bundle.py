from typing import Any, Dict, List, TypedDict
from backend.src.model_generation.transitions.build_transition_matrix import build_transition_matrix_workflow
from backend.src.model_generation.events.build_events import build_events_workflow
from backend.src.model_generation.parameters.get_parameters import get_parameters
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_datapoints import DUMMY_MODEL_DATAPOINTS_1
from backend.dummy_data.dummy_health_states import DUMMY_HEALTH_STATES_1
from backend.dummy_data.dummy_treatments import DUMMY_TREATMENTS_1
from backend.src.file_management.save_snapshot import save_model_bundle_snapshot
from backend.files.file_paths import snapshot_dir
from backend.dummy_data.dummy_initial_occupancy import DUMMY_INITIAL_OCCUPANCY_1

class ModelBundle(TypedDict):
    model_description: str
    health_states: List[str]
    treatments: List[str]
    parameters: Dict[str, Dict[str, Any]]  # your rich parameter dict
    transition_matrix_code: str            # <final_code> output
    events: List[Dict[str, Any]]           # [{"event_name":..., "final_code":...}, ...]
    provenance: Dict[str, Any]             # optional: raw LLM responses, etc.

from typing import Literal, Dict

TimeUnit = Literal["days", "weeks", "months", "years"]

_UNIT_TO_YEARS: Dict[TimeUnit, float] = {
    "days": 1.0 / 365.25,
    "weeks": 7.0 / 365.25,
    "months": 1.0 / 12.0,
    "years": 1.0,
}


def calculate_n_cycles(
    *,
    time_horizon: float,
    time_horizon_unit: TimeUnit,
    cycle_length: float,
    cycle_length_unit: TimeUnit,
) -> float:
    """
    Convert time horizon and cycle length into a consistent structure
    for a cohort Markov model.

    Returns:
        {
            "time_horizon_years": float,
            "cycle_length_years": float,
            "n_cycles": int
        }
    """

    if time_horizon <= 0:
        raise ValueError("time_horizon must be > 0")

    if cycle_length <= 0:
        raise ValueError("cycle_length must be > 0")

    if time_horizon_unit not in _UNIT_TO_YEARS:
        raise ValueError(f"Invalid time_horizon_unit: {time_horizon_unit}")

    if cycle_length_unit not in _UNIT_TO_YEARS:
        raise ValueError(f"Invalid cycle_length_unit: {cycle_length_unit}")

    # Convert to years
    time_horizon_years = time_horizon * _UNIT_TO_YEARS[time_horizon_unit]
    cycle_length_years = cycle_length * _UNIT_TO_YEARS[cycle_length_unit]

    # Calculate number of cycles
    n_cycles_exact = time_horizon_years / cycle_length_years

    # We usually want an integer number of cycles
    n_cycles = int(round(n_cycles_exact))

    # Safety check: ensure rounding didn’t materially change horizon
    if abs(n_cycles_exact - n_cycles) > 1e-6:
        raise ValueError(
            f"time_horizon ({time_horizon} {time_horizon_unit}) "
            f"is not an integer multiple of cycle_length "
            f"({cycle_length} {cycle_length_unit})"
        )

    return n_cycles


from typing import Any, Dict, List, Optional

def generate_model_bundle(
    *,
    model_description: str,
    initial_datapoints: List[Dict[str, Any]],
    health_states: List[str],
    initial_occupancy: Dict[str, Any],
    treatments: List[str],
    time_horizon: Any,
    time_horizon_units: Any,
    cycle_length: Any,
    cycle_length_units: Any,
    discount_rate_qalys: Any,
    discount_rate_costs: Any,
    overwrite_existing_params: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrates:
      - transition matrix workflow
      - events_out workflow
    Produces a single in-memory, runnable bundle.
    """

    # 1) Parameters
    model_parameters = get_parameters(datapoints=initial_datapoints)

    # model parameters ignores any datapoints for the following - these always come from front-end form
    model_parameters["cycle_length"] = {'value': cycle_length, 'description': f'Model cycle length {cycle_length_units}',
                                                             'distribution': None, 'standard_error': None}
    model_parameters[f"time_horizon"] = {'value': time_horizon, 'description': f'Model time horizon {time_horizon_units}',
                                        'distribution': None, 'standard_error': None}
    model_parameters[f"discount_rate_qaly"] = {'value': discount_rate_qalys,
                                                'description': f'Yearly discount rate for QALYs',
                                                              'distribution': None, 'standard_error': None}
    model_parameters[f"discount_rate_cost"] = {'value': discount_rate_costs,
                                                'description': f'Yearly discount rate for costs',
                                                'distribution': None, 'standard_error': None}
    model_parameters["initial_occupancy"] = {'value': initial_occupancy,
                                                'description': f'List of initial state occupancies',
                                                'distribution': None, 'standard_error': None}

    n_cycles = calculate_n_cycles(time_horizon=time_horizon, time_horizon_unit=time_horizon_units,
                                  cycle_length=cycle_length, cycle_length_unit=cycle_length_units)

    # 2) transitions
    transition_out = build_transition_matrix_workflow(
        model_description=model_description,
        model_parameters=model_parameters,
        health_states=health_states,
        overwrite_existing_params=overwrite_existing_params,
    )
    # transition_out: { final_code, additional_parameters, model_parameters_augmented, history, raw }

    # 3) events_out (starting from augmented params so events_out see them)
    events_out = build_events_workflow(
        model_description=model_description,
        model_parameters=transition_out["model_parameters_augmented"],
        health_states=health_states,
        overwrite_existing_params=overwrite_existing_params,
    )

    # 4) final augmented params after all event additions
    final_params = events_out["model_parameters_augmented"]

    # 5) assemble bundle
    bundle = {
        "model_description": model_description,
        "health_states": health_states,
        "treatments": treatments,
        "parameters": final_params,
        "n_cycles": n_cycles,
        "transition_matrix_code": transition_out["final_code"],
        "events": events_out["event_codes"],  # list of {"event_name","final_code"}
        "provenance": {
            "transition_raw": transition_out["raw"],
            "events_raw": events_out["raw"],
            # optional: store histories too, but can get large
        },
    }

    return bundle

if __name__ == "__main__":

    model_bundle = generate_model_bundle(model_description=DUMMY_MODEL_SPEC_1,
                                         initial_datapoints=DUMMY_MODEL_DATAPOINTS_1,
                                         health_states=DUMMY_HEALTH_STATES_1,
                                         treatments=DUMMY_TREATMENTS_1,
                                         time_horizon=15,
                                         time_horizon_units="years",
                                         cycle_length=3,
                                         cycle_length_units="months",
                                         discount_rate_costs=0.05,
                                         discount_rate_qalys=0.05,
                                         initial_occupancy=DUMMY_INITIAL_OCCUPANCY_1)
    # TODO validate all the inputs provided through the front end to avoid weirdness

    save_model_bundle_snapshot(snapshot_dir=snapshot_dir, bundle=model_bundle)

    pass
