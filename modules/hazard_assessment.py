"""Hazard and traffic updates for road edges."""


def update_road_condition(graph, u, v, hazard=None, traffic=None, blocked=None):
    if not graph.has_edge(u, v):
        raise KeyError(f"Road edge {u!r}–{v!r} does not exist.")
    attrs = graph[u][v]
    if hazard is not None:
        if not 0 <= int(hazard) <= 5:
            raise ValueError("Hazard level must be between 0 and 5.")
        attrs["hazard"] = int(hazard)
    if traffic is not None:
        if not 0 <= int(traffic) <= 5:
            raise ValueError("Traffic level must be between 0 and 5.")
        attrs["traffic"] = int(traffic)
    if blocked is not None:
        attrs["blocked"] = bool(blocked)
    return attrs
