import json
import ast
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Optional
from backend.src.core.llm.llm_extract import extract_between_tags
from backend.src.core.llm.llm_funcs import call_llm
from backend.src.core.llm.llm_log import llm_log
from backend.src.model_generation.parameters.merge_additional_parameters import merge_additional_parameters_dict
from backend.src.model_generation.events.templates import event_build, orchestrator_introduction, event_conceptualisation, events_build_loop_introduction, event_meta_data
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_parameters import DUMMY_MODEL_PARAMETERS_1
from backend.dummy_data.dummy_health_states import DUMMY_HEALTH_STATES_1


def _parse_loose_dict(text: str) -> Dict[str, Any]:
    """
    Parse a dict that may be valid JSON or a Python-literal-like dict.
    """
    cleaned = (text)
    # Try JSON
    try:
        obj = json.loads(cleaned)
        if not isinstance(obj, dict):
            raise ValueError("Expected a dict")
        return obj
    except Exception:
        pass

    # Try Python literal (single quotes, etc.)
    try:
        obj = ast.literal_eval(cleaned)
        if not isinstance(obj, dict):
            raise ValueError("Expected a dict")
        return obj
    except Exception as e:
        raise ValueError(f"Could not parse event recommendations as JSON or Python dict. Error: {e}")


def _parse_loose_list(text: str) -> List[Any]:
    """
    Parse a list that may be valid JSON or a Python-literal-like list.
    """
    cleaned = text
    try:
        obj = json.loads(cleaned)
        if not isinstance(obj, list):
            raise ValueError("Expected a list")
        return obj
    except Exception:
        pass

    try:
        obj = ast.literal_eval(cleaned)
        if not isinstance(obj, list):
            raise ValueError("Expected a list")
        return obj
    except Exception as e:
        raise ValueError(f"Could not parse additional parameters as JSON or Python list. Error: {e}")


def build_events_workflow(
    *,
    model_description: str,
    model_parameters: Dict[str, Dict[str, Any]],
    health_states: List[str],
    overwrite_existing_params: bool = False,
) -> Dict[str, Any]:
    """
    Runs:
      1) orchestrator_introduction -> gets <event_recommendations>
      2) events_build_loop_introduction -> ack
      3) for each recommended event:
           a) event_conceptualisation (may emit <additional_parameters>)
           b) event_build (must emit <final_code>)

    Key behavior:
      - single shared chat_history across ALL calls
      - parameters augmented as we go; later events see earlier additions

    Returns:
      {
        "event_recommendations": dict[str, str],
        "event_codes": list[{"event_name": str, "final_code": str}],
        "additional_parameters_all": list[dict],
        "model_parameters_augmented": dict,
        "history": chat_history,
        "raw": {
            "intro": str,
            "build_loop_intro": str,
            "conceptualisations": dict[event_name]->str,
            "builds": dict[event_name]->str,
        }
      }
    """

    # -----------------------
    # 1) ORCHESTRATOR INTRO
    # -----------------------
    prompt_intro = orchestrator_introduction.format(
        model_description=model_description,
        available_parameters=json.dumps(model_parameters, indent=2),
    )

    resp_intro, history = call_llm(
        prompt=prompt_intro,
        image_titles=[],
        image_b64s=[],
        chat_history=None,
    )
    llm_log(chat_history=history, aspect="events_orchestrator_intro")

    rec_block = extract_between_tags(resp_intro, "event_recommendations", no_match_response=None)
    if not rec_block:
        raise ValueError("No <event_recommendations>...</event_recommendations> block found in LLM response.")

    event_recommendations = _parse_loose_dict(rec_block)

    # Coerce values to str descriptions
    event_recommendations = {str(k): str(v) for k, v in event_recommendations.items()}

    # -----------------------
    # 2) BUILD LOOP INTRO
    # -----------------------
    resp_loop_intro, history = call_llm(
        prompt=events_build_loop_introduction,
        image_titles=[],
        image_b64s=[],
        chat_history=history,
    )
    llm_log(chat_history=history, aspect="events_build_loop_intro")

    # -----------------------
    # 3) ITERATE EVENTS
    # -----------------------
    model_parameters_aug = deepcopy(model_parameters)
    additional_parameters_all: List[Dict[str, Any]] = []

    conceptualisations_raw: Dict[str, str] = {}
    builds_raw: Dict[str, str] = {}
    event_data: List[Dict[str, str]] = []
    event_metadatas: List[Dict[str, str]] = []


    # preserve insertion order from LLM output (Python 3.7+ dict keeps order)
    ordered_event_names = list(event_recommendations.keys())


    for event_name in ordered_event_names:
        event_desc = event_recommendations[event_name]

        # -------- 3a) CONCEPTUALISE --------
        prompt_concept = event_conceptualisation.format(
            current_event_name=event_name,
            current_event_description=event_desc,
            model_description=model_description,
            available_parameters=json.dumps(model_parameters_aug, indent=2),
            model_health_states=health_states,
        )

        resp_concept, history = call_llm(
            prompt=prompt_concept,
            image_titles=[],
            image_b64s=[],
            chat_history=history,
        )
        llm_log(chat_history=history, aspect=f"event_concept_{event_name}")
        conceptualisations_raw[event_name] = resp_concept

        # Extract + merge any additional parameters from conceptualisation
        add_block = extract_between_tags(resp_concept, "additional_parameters", no_match_response=None)
        if add_block:
            additional_parameters = _parse_loose_list(add_block)
            if not all(isinstance(x, dict) for x in additional_parameters):
                raise ValueError("<additional_parameters> must contain an array of objects")

            additional_parameters_all.extend(additional_parameters)

            model_parameters_aug = merge_additional_parameters_dict(
                model_parameters_aug,
                additional_parameters,
                overwrite_existing=overwrite_existing_params,
            )

        prompt_build = event_build

        resp_build, history = call_llm(
            prompt=prompt_build,
            image_titles=[],
            image_b64s=[],
            chat_history=history,
        )
        llm_log(chat_history=history, aspect=f"event_build_{event_name}")
        builds_raw[event_name] = resp_build

        final_code = extract_between_tags(resp_build, "final_code", no_match_response=None)
        if not final_code:
            raise ValueError(f"No <final_code>...</final_code> block found for event: {event_name}")

        prompt_metadata = event_meta_data

        resp_metadata, history = call_llm(
            prompt=prompt_metadata,
            image_titles=[],
            image_b64s=[],
            chat_history=history,
        )
        llm_log(chat_history=history, aspect=f"event_build_{event_name}")

        metadata = extract_between_tags(resp_metadata, "metadata", no_match_response=None)

        if not metadata:
            metadata = {"description": "None available", "assumptions": "None available"}
        else:
            metadata = _parse_loose_dict(text=metadata)

        metadata["enabled"] = True # set to enabled by default

        event_data.append(
            {
                "event_name": event_name,
                "final_code": final_code.strip(),
                "metadata": metadata
            }
        )

        event_metadatas.append(metadata)

    return {
        "event_recommendations": event_recommendations,
        "event_data": event_data,
        "model_parameters": model_parameters_aug
    }


if __name__ == "__main__":

    events = build_events_workflow(model_description=DUMMY_MODEL_SPEC_1,
                          model_parameters=DUMMY_MODEL_PARAMETERS_1, health_states=DUMMY_HEALTH_STATES_1)

    pass