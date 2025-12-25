from typing import Any, Dict, List, TypedDict
from backend.src.model_generation.transitions.build_transition_matrix import build_transition_matrix_workflow
from backend.src.model_generation.events.build_events import build_events_workflow
from backend.src.model_generation.parameters.get_parameters import get_parameters
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_datapoints import DUMMY_MODEL_DATAPOINTS_1
from backend.dummy_data.dummy_treatments import DUMMY_TREATMENTS_1
from backend.src.file_management.save_snapshot import save_model_bundle_snapshot
from backend.src.model_generation.settings.health_states import generate_health_states_and_initial_occupancy
from backend.files.file_paths import snapshot_dir
import time

class ModelBundle(TypedDict):
    model_description: str
    health_states: List[str]
    treatments: List[str]
    parameters: Dict[str, Dict[str, Any]]  # your rich parameter dict
    transition_matrix_code: str            # <final_code> output
    events: List[Dict[str, Any]]           # [{"event_name":..., "final_code":...}, ...]
    provenance: Dict[str, Any]             # optional: raw LLM responses, etc.

from typing import Any, Dict, List, Optional

def generate_model_bundle(
    *,
    model_description: str,
    initial_datapoints: List[Dict[str, Any]],
    treatments: List[str],
    time_horizon_years: Any,
    cycle_length_years: Any,
    disc_rate_qaly_annual: Any,
    disc_rate_cost_annual: Any,
    overwrite_existing_params: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrates:
      - transition matrix workflow
      - events_out workflow
    Produces a single in-memory, runnable bundle.
    """

    start = time.time()

    # 0) Parameters
    model_parameters = get_parameters(datapoints=initial_datapoints)

    # TODO slight trickiness with dealing with parameters provided by user that are meant to inform initial health state
    # occupancies. We don't want these contaminating what happens, or being redundant. They won't be used in the
    # creation of the health state occupancies, as these vectors are raw parameters themselves

    # 1)
    health_states_out = generate_health_states_and_initial_occupancy(model_description=model_description,
                                                                     treatments=treatments, available_parameters=model_parameters)

    health_states = health_states_out["health_states"]
    initial_occupancy = health_states_out["initial_state_occupancy"]

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
        "initial_occupancy": initial_occupancy,
        "cycle_length_years": cycle_length_years,
        "time_horizon_years": time_horizon_years,
        "disc_rate_cost_annual": disc_rate_cost_annual,
        "disc_rate_qaly_annual": disc_rate_qaly_annual,
        "transition_matrix_code": transition_out["final_code"],
        "events": events_out["event_codes"],  # list of {"event_name","final_code"}
        "provenance": {
            "transition_raw": transition_out["raw"],
            "events_raw": events_out["raw"],
            # optional: store histories too, but can get large
        },
    }

    print(f'Generated model in {round(time.time()-start,2)} seconds')

    return bundle

if __name__ == "__main__":

    model_bundle = generate_model_bundle(model_description=DUMMY_MODEL_SPEC_1,
                                         initial_datapoints=DUMMY_MODEL_DATAPOINTS_1,
                                         treatments=DUMMY_TREATMENTS_1,
                                         time_horizon_years=15,
                                         cycle_length_years=3,
                                         disc_rate_cost_annual=0.05,
                                         disc_rate_qaly_annual=0.05)
    # TODO validate all the inputs provided through the front end to avoid weirdness

    save_model_bundle_snapshot(snapshot_dir=snapshot_dir, bundle=model_bundle, display_name="Test Model")

    pass
