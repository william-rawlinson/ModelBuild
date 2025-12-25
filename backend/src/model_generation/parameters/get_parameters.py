from backend.src.model_generation.parameters.templates import transform_datapoints
from backend.src.core.llm.llm_funcs import call_llm
from backend.src.core.llm.llm_log import llm_log
import re
from typing import List, Any, Dict, Optional
import json
from backend.dummy_data.dummy_model_datapoints import DUMMY_MODEL_DATAPOINTS_2
from backend.dummy_data.dummy_model_datapoints import DUMMY_MODEL_DATAPOINTS_1

_IDENTIFIER_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    return [items[i:i+size] for i in range(0, len(items), size)]

def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t).strip()
    if not t.startswith("["):
        m = re.search(r"\[.*\]", t, flags=re.DOTALL)
        if not m:
            raise ValueError("LLM output did not contain a JSON array.")
        t = m.group(0)
    data = json.loads(t)
    if not isinstance(data, list):
        raise ValueError("LLM output JSON was not a list.")
    return data

def _sanitize_name(name: str) -> str:
    name = (name or "").strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "param"
    if not _IDENTIFIER_RE.match(name):
        if re.match(r"^[0-9]", name):
            name = f"p_{name}"
        if not _IDENTIFIER_RE.match(name):
            name = "param"
    return name

def _dedupe_name(name: str, used: set) -> str:
    base = name
    k = 2
    while name in used:
        name = f"{base}_{k}"
        k += 1
    used.add(name)
    return name

def _coerce_num(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None

def get_parameters(
    *,
    datapoints: List[Dict[str, Any]],
    chunk_size: int = 25,
    aspect_prefix: str = "get_parameters",
) -> Dict[str, Dict[str, Any]]:
    used_names: set = set()
    parameters: Dict[str, Dict[str, Any]] = {}

    history = None

    chunks = chunk_list(datapoints, chunk_size)

    for chunk_idx, chunk in enumerate(chunks, start=1):
        datapoints_json = json.dumps(chunk, ensure_ascii=False, indent=2)
        prompt = transform_datapoints.format(datapoints_json=datapoints_json)

        response_text, history = call_llm(
            prompt=prompt,
            image_titles=[],
            image_b64s=[],
            chat_history=history,   # <-- rolling history
        )

        llm_log(chat_history=history, aspect=f"{aspect_prefix}_chunk_{chunk_idx}")

        items = _extract_json_array(response_text)

        # Strictness: ensure 1-to-1 mapping within a chunk
        if len(items) != len(chunk):
            raise ValueError(
                f"Chunk {chunk_idx}: expected {len(chunk)} outputs, got {len(items)}."
            )

        for it in items:
            raw_name = it.get("parameter_name", "")
            name = _sanitize_name(raw_name)
            name = _dedupe_name(name, used_names)

            parameters[name] = {
                "value": _coerce_num(it.get("value")),
                "description": str(it.get("description") or "").strip(),
                "distribution": (str(it.get("distribution")).strip() if it.get("distribution") is not None else None),
                "standard_error": _coerce_num(it.get("standard_error")),
            }

    return parameters

if __name__ == "__main__":

    parameters = get_parameters(datapoints=DUMMY_MODEL_DATAPOINTS_1)

    pass

