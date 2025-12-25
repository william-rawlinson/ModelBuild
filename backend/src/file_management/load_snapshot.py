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
        events.append({"event_name": e["event_name"], "final_code": code, "metadata": e.get("metadata", {})})

    return {
        # snapshot metadata
        "snapshot_id": snap.get("snapshot_id"),
        "display_name": snap.get("display_name"),
        "created_at": snap.get("created_at"),
        "parent_snapshot_id": snap.get("parent_snapshot_id"),
        "notes": snap.get("notes"),

        # model bundle
        "model_description": snap.get("model_description", ""),
        "health_states": snap["health_states"],
        "treatments": snap["treatments"],
        "cycle_length_years": snap["cycle_length_years"],
        "time_horizon_years": snap["time_horizon_years"],
        "disc_rate_cost_annual": snap["disc_rate_cost_annual"],
        "disc_rate_qaly_annual": snap["disc_rate_qaly_annual"],
        "initial_occupancy": snap["initial_occupancy"],
        "parameters": snap["parameters_rich"],
        "transition_matrix_code": transition_code,
        "events": events,
    }
