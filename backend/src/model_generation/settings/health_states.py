import json
import ast
from typing import Any, Dict, List, Optional
from backend.src.core.llm.llm_funcs import call_llm
from backend.src.core.llm.llm_extract import extract_between_tags
from backend.src.core.llm.llm_log import llm_log
from backend.dummy_data.dummy_model_spec import DUMMY_MODEL_SPEC_1
from backend.dummy_data.dummy_model_parameters import DUMMY_MODEL_PARAMETERS_1
from backend.src.model_generation.settings.templates import health_states_prompt, initial_occupancy_prompt
from backend.dummy_data.dummy_treatments import DUMMY_TREATMENTS_1



def _strip_json_fences(text: str) -> str:
    if not text:
        return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("` \n")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


def _parse_list_block(text: str, *, tag_name: str) -> List[str]:
    if text is None:
        raise ValueError(f"No <{tag_name}> block found.")

    cleaned = _strip_json_fences(text)

    try:
        obj = json.loads(cleaned)
    except Exception:
        try:
            obj = ast.literal_eval(cleaned)
        except Exception as e:
            raise ValueError(f"Could not parse <{tag_name}> as list. Error: {e}")

    if not isinstance(obj, list) or not all(isinstance(x, str) and x.strip() for x in obj):
        raise ValueError(f"<{tag_name}> must contain a list of non-empty strings")

    if len(set(obj)) != len(obj):
        raise ValueError(f"<{tag_name}> contains duplicate health state names")

    return obj


def _parse_dict_block(text: str, *, tag_name: str) -> Dict[str, Any]:
    if text is None:
        raise ValueError(f"No <{tag_name}> block found.")

    cleaned = _strip_json_fences(text)

    try:
        obj = json.loads(cleaned)
    except Exception:
        try:
            obj = ast.literal_eval(cleaned)
        except Exception as e:
            raise ValueError(f"Could not parse <{tag_name}> as dict. Error: {e}")

    if not isinstance(obj, dict):
        raise ValueError(f"<{tag_name}> must contain a dictionary/object")

    return obj


def _validate_initial_occupancy(
    occ: Dict[str, Dict[str, float]],
    *,
    treatments: List[str],
    health_states: List[str],
    tol: float = 1e-9,
) -> Dict[str, Dict[str, float]]:
    """
    Enforce:
      - one entry per treatment
      - each treatment has all states
      - probs in [0,1]
      - sums to 1
    Returns a normalised/filled version (ensures all states exist).
    """
    if not isinstance(occ, dict):
        raise ValueError("initial_state_occupancy must be a dict[treatment]->dict[state]->float")

    out: Dict[str, Dict[str, float]] = {}

    for trt in treatments:
        if trt not in occ:
            raise ValueError(f"Missing initial occupancy for treatment: {trt}")

        raw_map = occ[trt]
        if not isinstance(raw_map, dict):
            raise ValueError(f"Initial occupancy for {trt} must be a dict of state->proportion")

        filled: Dict[str, float] = {}
        for st in health_states:
            v = raw_map.get(st, 0.0)
            try:
                fv = float(v)
            except Exception:
                raise ValueError(f"Occupancy for treatment {trt}, state {st} must be numeric")
            if fv < -tol or fv > 1.0 + tol:
                raise ValueError(f"Occupancy for treatment {trt}, state {st} out of range: {fv}")
            filled[st] = max(0.0, min(1.0, fv))

        s = sum(filled.values())
        if abs(s - 1.0) > tol:
            raise ValueError(f"Initial occupancies for {trt} must sum to 1.0. Got {s}")

        out[trt] = filled

    return out


def generate_health_states_and_initial_occupancy(
    *,
    model_description: str,
    available_parameters: Dict[str, Dict[str, Any]],
    treatments: List[str],
    chat_history: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Two-step LLM flow (same chat history):
      1) Generate minimal health states -> <model_health_states>
      2) Generate per-treatment initial occupancies -> <initial_state_occupancy>

    Returns:
      {
        "health_states": List[str],
        "initial_state_occupancy": Dict[treatment][state] = float,
        "history": chat_history,
        "raw": {"health_states_response": str, "initial_occupancy_response": str}
      }
    """

    # -----------------------
    # 1) HEALTH STATES
    # -----------------------
    prompt_states = health_states_prompt.format(
        model_description=model_description,
        available_parameters=json.dumps(available_parameters, indent=2),
    )

    resp_states, history = call_llm(
        prompt=prompt_states,
        image_titles=[],
        image_b64s=[],
        chat_history=chat_history,
    )
    llm_log(chat_history=history, aspect="health_states_generation")

    states_block = extract_between_tags(resp_states, "model_health_states", no_match_response=None)
    health_states = _parse_list_block(states_block, tag_name="model_health_states")

    # -----------------------
    # 2) INITIAL OCCUPANCY (same history)
    # -----------------------
    prompt_occ = initial_occupancy_prompt.format(
        model_description=model_description,
        model_health_states=json.dumps(health_states, indent=2),
        treatments=json.dumps(treatments, indent=2),
    )

    resp_occ, history = call_llm(
        prompt=prompt_occ,
        image_titles=[],
        image_b64s=[],
        chat_history=history,
    )
    llm_log(chat_history=history, aspect="initial_state_occupancy_generation")

    occ_block = extract_between_tags(resp_occ, "initial_state_occupancy", no_match_response=None)
    occ_obj = _parse_dict_block(occ_block, tag_name="initial_state_occupancy")

    # Validate + fill missing states with 0.0 (but still require sum==1)
    initial_state_occupancy = _validate_initial_occupancy(
        occ_obj,
        treatments=treatments,
        health_states=health_states,
    )

    return {
        "health_states": health_states,
        "initial_state_occupancy": initial_state_occupancy,
        "history": history,
        "raw": {
            "health_states_response": resp_states,
            "initial_occupancy_response": resp_occ,
        },
    }



if __name__ == "__main__":

    health_states_out = generate_health_states_and_initial_occupancy(model_description=DUMMY_MODEL_SPEC_1,
                                           available_parameters=DUMMY_MODEL_PARAMETERS_1,
                                           treatments=DUMMY_TREATMENTS_1)

    pass

    # TODO rationale for health states? add to front of the prompts for transitions / events?