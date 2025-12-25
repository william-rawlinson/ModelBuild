from typing import List, Dict, Any
from copy import deepcopy

def merge_additional_parameters_dict(
    model_parameters: Dict[str, Dict[str, Any]],
    additional: List[Dict[str, Any]],
    *,
    overwrite_existing: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Merge additional parameters (from LLM) into model_parameters dict.

    model_parameters format:
      {
        "param_name": {
            "value": ...,
            "description": ...,
            "distribution": ...,
            "standard_error": ...
        }
      }
    """
    out = deepcopy(model_parameters)

    for p in additional or []:
        name = (p.get("parameter_name") or "").strip()
        if not name:
            continue

        if name in out and not overwrite_existing:
            continue

        out[name] = {
            "value": p.get("value"),
            "description": p.get("description") or "",
            "distribution": p.get("distribution"),
            "standard_error": p.get("standard_error"),
        }

    return out