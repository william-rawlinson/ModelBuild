from typing import Callable, Dict, Any, List


def flatten_parameters(parameters_rich: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert your rich parameter dict into the flat parameters dict your runner expects.
    """
    return {k: v.get("value") for k, v in parameters_rich.items()}


def _exec_code(code: str, globals_ns: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute generated code in a controlled namespace.
    globals_ns should include any framework symbols the code references.
    """
    ns: Dict[str, Any] = dict(globals_ns)
    exec(code, ns, ns)  # noqa: S102 (you are executing trusted code from your own generator)
    return ns


def compile_transition_fn(
    *,
    transition_code: str,
    globals_ns: Dict[str, Any],
) -> Callable:
    ns = _exec_code(transition_code, globals_ns)
    fn = ns.get("get_transition_matrix")
    if fn is None or not callable(fn):
        raise ValueError("Transition code must define callable get_transition_matrix(context)")
    return fn


def compile_event_specs(
    *,
    events_code: List[str],
    globals_ns: Dict[str, Any],
) -> List[Any]:
    """
    Each event code block must define exactly one EventSpec instance.
    We locate it by type name 'EventSpec'.
    """
    specs = []
    for code in events_code:
        ns = _exec_code(code, globals_ns)

        event_spec = None
        for v in ns.values():
            if v is None:
                continue
            if v.__class__.__name__ == "EventSpec":
                event_spec = v
                break

        if event_spec is None:
            raise ValueError("Event code did not create an EventSpec instance.")

        specs.append(event_spec)
    return specs
