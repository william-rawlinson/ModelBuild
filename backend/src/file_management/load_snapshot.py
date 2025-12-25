from pathlib import Path
import json
from typing import List, Dict, Any

def load_model_bundle_snapshot(snapshot_dir: str) -> Dict[str, Any]:
    base = Path(snapshot_dir)
    snap = json.loads((base / "snapshot.json").read_text(encoding="utf-8"))

    transition_code = (base / snap["code"]["transition_matrix_path"]).read_text(encoding="utf-8")

    events: List[Dict[str, Any]] = []
    for e in snap["code"]["events"]:
        code = (base / e["path"]).read_text(encoding="utf-8")
        events.append({"event_name": e["event_name"], "final_code": code})

    return {
        "model_description": snap.get("model_description", ""),
        "health_states": snap["health_states"],
        "treatments": snap["treatments"],
        "n_cycles": snap["n_cycles"],
        "parameters": snap["parameters_rich"],
        "transition_matrix_code": transition_code,
        "events": events,
    }
