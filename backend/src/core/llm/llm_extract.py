from typing import Any
from backend.src.core.llm.llm_funcs import call_llm
import re

def extract_between_tags(string: str, tag_name: str, no_match_response: Any) -> Any:

    # Escape any special regex characters in the tag name
    escaped_tag = re.escape(tag_name)
    # Pattern matches content between opening and closing tags
    # (?s) enables dot to match newlines (DOTALL mode)
    pattern = f"(?s)<{escaped_tag}>(.*?)</{escaped_tag}>"

    match = re.search(pattern, string)

    if match:
        return match.group(1).strip()

    return no_match_response



