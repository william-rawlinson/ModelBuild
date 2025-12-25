from pathlib import Path
import json
from typing import Any, Dict, List
from backend.files.file_paths import snapshot_dir as SNAPSHOT_ROOT


def list_model_snapshots() -> List[Dict[str, Any]]:
    root = Path(SNAPSHOT_ROOT)
    if not root.exists():
        return []

    out: List[Dict[str, Any]] = []
    for d in sorted(root.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        snap_path = d / "snapshot.json"
        if not snap_path.exists():
            continue
        try:
            snap = json.loads(snap_path.read_text(encoding="utf-8"))
            out.append({
                "snapshot_id": snap.get("snapshot_id"),
                "display_name": snap.get("display_name") or d.name,
                "created_at": snap.get("created_at"),
                "parent_snapshot_id": snap.get("parent_snapshot_id"),
                "model_description": (snap.get("model_description") or "")[:200],
                "snapshot_dir": str(d),
            })
        except Exception:
            # ignore broken snapshots (or you could surface with an error flag)
            continue

    return out
