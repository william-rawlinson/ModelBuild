import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from backend.files.file_paths import snapshot_dir as SNAPSHOT_ROOT


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unnamed"


def _new_snapshot_id() -> str:
    # stable, filesystem-safe id
    return f"{int(time.time())}_{int(time.time_ns() % 1_000_000_000):09d}"


def save_model_bundle_snapshot(
    *,
    display_name: str,
    bundle: Dict[str, Any],
    parent_snapshot_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a new snapshot directory under SNAPSHOT_ROOT and writes:
      snapshot.json
      code/transition_matrix.py
      code/events/*.py

    Returns a small descriptor for UI: {snapshot_id, display_name, snapshot_dir, created_at, parent_snapshot_id}
    """
    snapshot_id = _new_snapshot_id()
    created_at = datetime.now(timezone.utc).isoformat()

    # directory name includes a slug for readability, but id is the real key
    dir_name = f"{snapshot_id}__{_slugify(display_name)[:60]}"
    base = Path(SNAPSHOT_ROOT) / dir_name
    base.mkdir(parents=True, exist_ok=False)  # fail if collision

    code_dir = base / "code"
    events_dir = code_dir / "events"
    events_dir.mkdir(parents=True, exist_ok=True)

    # write transition code
    transition_rel = Path("code/transition_matrix.py")
    (base / transition_rel).write_text(bundle["transition_matrix_code"], encoding="utf-8")

    # write events code
    event_entries = []
    for i, e in enumerate(bundle["events"], start=1):
        name = str(e["event_name"])
        metadata = e.get("metadata", {})
        slug = _slugify(name)
        rel = Path(f"code/events/{i:03d}_{slug}.py")
        (base / rel).write_text(e["final_code"], encoding="utf-8")
        event_entries.append({"event_name": name, "path": str(rel), "metadata": metadata})

    snapshot = {
        "schema_version": 1,
        "snapshot_id": snapshot_id,
        "display_name": display_name,
        "created_at": created_at,
        "parent_snapshot_id": parent_snapshot_id,
        "notes": notes,

        "model_description": bundle.get("model_description", ""),
        "health_states": bundle["health_states"],
        "treatments": bundle["treatments"],
        "cycle_length_years": bundle["cycle_length_years"],
        "time_horizon_years": bundle["time_horizon_years"],
        "disc_rate_cost_annual": bundle["disc_rate_cost_annual"],
        "disc_rate_qaly_annual": bundle["disc_rate_qaly_annual"],
        "initial_occupancy": bundle["initial_occupancy"],
        "parameters_rich": bundle["parameters"],

        "code": {
            "transition_matrix_path": str(transition_rel),
            "events": event_entries,
        },
    }

    (base / "snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    return {
        "snapshot_id": snapshot_id,
        "display_name": display_name,
        "created_at": created_at,
        "parent_snapshot_id": parent_snapshot_id,
        "snapshot_dir": str(base),
    }





