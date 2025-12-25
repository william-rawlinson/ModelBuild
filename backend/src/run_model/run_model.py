import numpy as np
from backend.src.run_model.globals import (TransitionMatrixContext, EventSpec,
                                           initialise_impact, NamedTransitionMatrix, EventContext, EventImpact)
import math
from typing import Dict, Any
from backend.src.run_model.compile import flatten_parameters, compile_transition_fn, compile_event_specs
from backend.src.run_model.runner import run_markov_model
from backend.src.file_management.load_snapshot import load_model_bundle_snapshot
from backend.files.file_paths import snapshot_dir

GLOBALS_FOR_CODEGEN = {
    "np": np,
    "TransitionMatrixContext": TransitionMatrixContext,
    "NamedTransitionMatrix": NamedTransitionMatrix,
    "EventContext": EventContext,
    "EventSpec": EventSpec,
    "EventImpact": EventImpact,
    "initialise_impact": initialise_impact,
    "exp": math.exp,
}


def run_model_from_bundle(
    *,
    bundle: Dict[str, Any],
    globals_ns: Dict[str, Any],
    discount_timing: str = "mid",
) -> Dict[str, Any]:
    """
    bundle must contain:
      - transition_matrix_code: str (defines get_transition_matrix)
      - events: list[{final_code: str, event_name: str}, ...]
      - parameters: rich dict
      - health_states: list[str]
      - treatments: list[str]
    """
    # 1) flatten parameters
    parameters = flatten_parameters(bundle["parameters"])
    n_cycles = bundle["n_cycles"]

    # 3) compile code to runtime objects
    build_transition_matrix_fn = compile_transition_fn(transition_code=bundle["transition_matrix_code"],
                                                       globals_ns=globals_ns)

    event_specs = compile_event_specs(events_code=[e["final_code"] for e in bundle["events"]],
        globals_ns=globals_ns,
    )

    # 4) run
    results = run_markov_model(
        build_transition_matrix_fn=build_transition_matrix_fn,
        event_specs=event_specs,
        parameters=parameters,
        health_states=bundle["health_states"],
        treatments=bundle["treatments"],
        n_cycles=n_cycles,
        discount_timing=discount_timing,
    )

    return results


if __name__ == "__main__":

    model_bundle = load_model_bundle_snapshot(snapshot_dir=snapshot_dir)

    result = run_model_from_bundle(bundle=model_bundle, globals_ns=GLOBALS_FOR_CODEGEN)

    pass