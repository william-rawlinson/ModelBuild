import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from backend.files.file_paths import snapshot_dir


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "event"


def save_model_bundle_snapshot(
    *,
    snapshot_dir: str,
    bundle: Dict[str, Any],
) -> None:
    """
    Writes:
      snapshot.json
      code/transition_matrix.py
      code/events/*.py
    """
    base = Path(snapshot_dir)
    base.mkdir(parents=True, exist_ok=True)

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
        slug = _slugify(name)
        rel = Path(f"code/events/{i:03d}_{slug}.py")
        (base / rel).write_text(e["final_code"], encoding="utf-8")
        event_entries.append({"event_name": name, "path": str(rel)})

    snapshot = {
        "schema_version": 1,
        "model_description": bundle.get("model_description", ""),
        "health_states": bundle["health_states"],
        "treatments": bundle["treatments"],
        "n_cycles": bundle["n_cycles"],
        "parameters_rich": bundle["parameters"],  # keep your rich param structure
        "code": {
            "transition_matrix_path": str(transition_rel),
            "events": event_entries,
        },
    }

    (base / "snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")







