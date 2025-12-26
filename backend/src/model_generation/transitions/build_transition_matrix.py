import json
from copy import deepcopy
from typing import Any, Dict, List
from backend.src.core.llm.llm_extract import extract_between_tags
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_2
from backend.dummy_data.dummy_model_parameters import DUMMY_MODEL_PARAMETERS_2
from backend.dummy_data.dummy_model_parameters import DUMMY_MODEL_PARAMETERS_1
from backend.src.model_generation.transitions.templates import transition_matrix_introduction, transition_set_build, transition_matrix_conceptualisation
from backend.src.core.llm.llm_funcs import call_llm
from backend.src.core.llm.llm_log import llm_log
from backend.dummy_data.dummy_health_states import DUMMY_HEALTH_STATES_2
from backend.dummy_data.dummy_health_states import DUMMY_HEALTH_STATES_1
from backend.src.model_generation.parameters.merge_additional_parameters import merge_additional_parameters_dict
from backend.src.model_generation.transitions.templates import transitions_meta_data
from backend.src.model_generation.events.build_events import _parse_loose_dict



def build_transition_matrix_workflow(
    *,
    model_description: str,
    model_parameters: Dict[str, Dict[str, Any]],
    health_states: List[str],
    overwrite_existing_params: bool = False,
) -> Dict[str, Any]:
    """
    Runs:
      1) transition_matrix_introduction (ack)
      2) transition_set_conceptualisation (may emit <additional_parameters>)
      3) transition_set_build (must emit <final_code>)

    Returns:
      {
        "origin_state": str,
        "final_code": str,
        "additional_parameters": list,
        "model_parameters_augmented": dict,
        "history": chat_history,
        "raw": {...}
      }
    """

    # ---------- 1) INTRODUCTION ----------
    prompt_intro = transition_matrix_introduction.format(
        model_description=model_description,
        model_parameters=json.dumps(model_parameters, indent=2),
        model_health_states=health_states,
    )

    resp_intro, history = call_llm(
        prompt=prompt_intro,
        image_titles=[],
        image_b64s=[],
        chat_history=None,
    )
    llm_log(chat_history=history, aspect=f"transition_set_intro")

    # ---------- 2) CONCEPTUALISATION ----------
    prompt_concept = transition_matrix_conceptualisation

    resp_concept, history = call_llm(
        prompt=prompt_concept,
        image_titles=[],
        image_b64s=[],
        chat_history=history,
    )
    llm_log(chat_history=history, aspect=f"transition_set_concept")

    additional_parameters: List[Dict[str, Any]] = []

    additional_block = extract_between_tags(
        resp_concept,
        "additional_parameters",
        no_match_response=None,
    )

    model_parameters_aug = model_parameters

    if additional_block:
        # tolerate ```json fences
        cleaned = additional_block.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("` \n")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        additional_parameters = json.loads(cleaned)

        if not isinstance(additional_parameters, list):
            raise ValueError("<additional_parameters> must contain a JSON array")

        model_parameters_aug = merge_additional_parameters_dict(
            model_parameters,
            additional_parameters,
            overwrite_existing=overwrite_existing_params,
        )

    # ---------- 3) BUILD ----------
    # We inject augmented parameters + origin state as context
    build_context = (
        "<available_model_parameters>\n"
        f"{json.dumps(model_parameters_aug, indent=2)}\n"
        "</available_model_parameters>\n"
    )

    prompt_build = transition_set_build + build_context

    resp_build, history = call_llm(
        prompt=prompt_build,
        image_titles=[],
        image_b64s=[],
        chat_history=history,
    )
    llm_log(chat_history=history, aspect=f"transition_matrix_build")

    final_code = extract_between_tags(
        resp_build,
        "final_code",
        no_match_response=None,
    )

    if not final_code:
        raise ValueError("No <final_code>...</final_code> block found in LLM response.")

    prompt_metadata = transitions_meta_data

    resp_metadata, history = call_llm(
        prompt=prompt_metadata,
        image_titles=[],
        image_b64s=[],
        chat_history=history,
    )
    llm_log(chat_history=history, aspect=f"transition_matrix_metadata")

    metadata = extract_between_tags(resp_metadata, "metadata", no_match_response=None)

    if not metadata:
        metadata = {"description": "None available", "assumptions": "None available"}
    else:
        metadata = _parse_loose_dict(text=metadata)

    return {
        "transition_matrix_data": {"final_code": final_code.strip(), "metadata": metadata},
        "model_parameters": model_parameters_aug,
    }

# TODO add metadata on description / assumption


if __name__ == "__main__":

    transition_matrix = build_transition_matrix_workflow(model_description=DUMMY_MODEL_SPEC_1, model_parameters=DUMMY_MODEL_PARAMETERS_1,
                                                         health_states=DUMMY_HEALTH_STATES_1)

    pass

