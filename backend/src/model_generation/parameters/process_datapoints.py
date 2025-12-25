import re
from typing import Any, Dict, List, Optional

def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "":
        return None
    # allow commas and percent signs
    s = s.replace(",", "")
    if s.endswith("%"):
        return float(s[:-1]) / 100.0
    return float(s)

def normalize_datapoints(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in raw or []:
        desc = (r.get("description") or "").strip()
        if not desc:
            continue
        out.append({
            "description": desc,
            "base_case_value": _to_float(r.get("base_case_value")),
            "distribution": (r.get("distribution") or "").strip() or None,
            "standard_error": _to_float(r.get("standard_error")),
        })
    return out
