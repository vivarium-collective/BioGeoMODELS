# helpers.py
import re
from copy import deepcopy
from bigraph_viz import plot_bigraph

# ---- Store generation --------------------------------------------------------

def add_stores_to_dict(bigraph: dict) -> dict:
    """
    Add store nodes for every _inputs/_outputs port if missing.
    Produces:
      spec["inputs"][<port>]  = [<type_token>]
      spec["outputs"][<port>] = [<type_token>]
    """
    new = deepcopy(bigraph)

    for _, spec in new.items():
        spec.setdefault("inputs", {})
        spec.setdefault("outputs", {})

        # inputs
        for port_id, port_type in (spec.get("_inputs") or {}).items():
            pid = str(port_id)
            typ = port_type if isinstance(port_type, list) else [port_type]
            typ = [str(x) for x in typ]
            spec["inputs"].setdefault(pid, typ)
            spec["_inputs"][pid] = "any"  # remove type info

        # outputs
        for port_id, port_type in (spec.get("_outputs") or {}).items():
            pid = str(port_id)
            typ = port_type if isinstance(port_type, list) else [port_type]
            typ = [str(x) for x in typ]
            spec["outputs"].setdefault(pid, typ)
            spec["_outputs"][pid] = "any"  # remove type info

    return new

# ---- Plotting convenience ----------------------------------------------------

def _as_composite(obj, name=None):
    """
    Accept either:
      - composite: {"Name [Method]": {...}}
      - single spec: {...}  (must pass name or it will default)
    Return a composite dict.
    """
    if isinstance(obj, dict) and "_type" in obj:
        key = name or "process"
        return {str(key): obj}
    # already a composite (best-effort check)
    if isinstance(obj, dict) and len(obj) == 1:
        (k, v), = obj.items()
        if isinstance(v, dict) and "_type" in v:
            return {str(k): v}
    raise ValueError("plot_process needs a single process spec dict (with '_type') "
                     "or a composite {'Name': spec}. If passing a spec, also pass name=...")

def plot_process(composite, filename=None, add_stores=False, name=None,
                 plot_settings=None, **kwargs):
    """
    composite: either {'Name': spec} OR a single spec dict (then provide name=...).
    """
    graph = _as_composite(composite, name=name or filename)
    if add_stores:
        graph = add_stores_to_dict(graph)

    cfg = dict(plot_settings or {})
    cfg.update(kwargs)
    if "dpi" in cfg:
        cfg["dpi"] = str(cfg["dpi"])
    return plot_bigraph(graph, **cfg, filename=filename)