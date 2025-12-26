from typing import Any, Dict, List, TypedDict
from backend.src.model_generation.transitions.build_transition_matrix import build_transition_matrix_workflow
from backend.src.model_generation.events.build_events import build_events_workflow
from backend.src.model_generation.parameters.get_parameters import get_parameters
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_datapoints import DUMMY_MODEL_DATAPOINTS_1
from backend.dummy_data.dummy_treatments import DUMMY_TREATMENTS_1
from backend.src.file_management.save_snapshot import save_model_bundle_snapshot
from backend.src.model_generation.settings.health_states import generate_health_states_and_initial_occupancy
import time
from backend.src.core.llm.llm_stats import llm_stats
from backend.websockets.websocket_manager import manager
import asyncio
from backend.src.file_management.save_snapshot import save_working_model_bundle

PROCESS_NAME = "generate_model"

class ModelBundle(TypedDict):
    model_description: str
    health_states: List[str]
    treatments: List[str]
    parameters: Dict[str, Dict[str, Any]]  # your rich parameter dict
    transition_matrix_code: str            # <final_code> output
    events: List[Dict[str, Any]]           # [{"event_name":..., "final_code":...}, ...]
    provenance: Dict[str, Any]             # optional: raw LLM responses, etc.

from typing import Any, Dict, List, Optional

async def generate_model_bundle(
    *,
    model_description: str,
    data_points: List[Dict[str, Any]],
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

    llm_stats.reset()

    start = time.time()

    await manager.send_message(
        message_type="process_start",
        payload={"message": "Starting model generation…"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    # 0) Parameters

    await manager.send_message(
        message_type="progress",
        payload={"message": f"Generating parameters [Step 1/4]"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    model_parameters = get_parameters(datapoints=data_points)

    # TODO slight trickiness with dealing with parameters provided by user that are meant to inform initial health state
    # occupancies. We don't want these contaminating what happens, or being redundant. They won't be used in the
    # creation of the health state occupancies, as these vectors are raw parameters themselves

    await manager.send_message(
        message_type="progress",
        payload={"message": f"Composing health states [Step 2/4]"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    # 1)
    health_states_out = generate_health_states_and_initial_occupancy(model_description=model_description,
                                                                     treatments=treatments, available_parameters=model_parameters)

    health_states = health_states_out["health_states"]
    initial_occupancy = health_states_out["initial_state_occupancy"]

    await manager.send_message(
        message_type="progress",
        payload={"message": f"Calculating transitions [Step 3/4]"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    # 2) transitions
    transition_out = build_transition_matrix_workflow(
        model_description=model_description,
        model_parameters=model_parameters,
        health_states=health_states,
        overwrite_existing_params=overwrite_existing_params,
    )
    # transition_out: { final_code, additional_parameters, model_parameters_augmented, history, raw }

    await manager.send_message(
        message_type="progress",
        payload={"message": f"Building events [Step 4/4]"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    # 3) events_out (starting from augmented params so events_out see them)
    events_out = build_events_workflow(
        model_description=model_description,
        model_parameters=transition_out["model_parameters"],
        health_states=health_states,
        overwrite_existing_params=overwrite_existing_params,
    )

    # 4) final augmented params after all event additions
    final_params = events_out["model_parameters"]

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
        "transition_matrix_data": transition_out["transition_matrix_data"],
        "event_data": events_out["event_data"],

    }

    print(f'Generated model in {round(time.time()-start,2)} seconds')

    print(llm_stats.get_stats())

    llm_stats.reset()

    save_working_model_bundle(bundle=bundle) # save to temp working directory

    await manager.send_message(
        message_type="progress",
        payload={"message": "✅ Generation complete."},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    await manager.send_message(
        message_type="model_bundle_ready",
        payload={
            "bundle": {
                "model_description": bundle["model_description"],
                "health_states": bundle["health_states"],
                "treatments": bundle["treatments"],
                "parameters": bundle["parameters"],
                "initial_occupancy": bundle["initial_occupancy"],
                "cycle_length_years": bundle["cycle_length_years"],
                "time_horizon_years": bundle["time_horizon_years"],
                "disc_rate_cost_annual": bundle["disc_rate_cost_annual"],
                "disc_rate_qaly_annual": bundle["disc_rate_qaly_annual"],
                "transition_matrix_data": bundle["transition_matrix_data"],
                "event_data": bundle["event_data"],
            }
        },
        process_name=PROCESS_NAME,
        process_complete=True,
    )


    return bundle

if __name__ == "__main__":

    model_bundle = asyncio.run(generate_model_bundle(model_description=DUMMY_MODEL_SPEC_1,
                                               data_points=DUMMY_MODEL_DATAPOINTS_1,
                                               treatments=DUMMY_TREATMENTS_1, time_horizon_years=15,
                                               cycle_length_years=3,
                                               disc_rate_qaly_annual=0.05, disc_rate_cost_annual=0.05))
    # TODO validate all the inputs provided through the front end to avoid weirdness

    save_model_bundle_snapshot(bundle=model_bundle, display_name="Test Model")

    pass


