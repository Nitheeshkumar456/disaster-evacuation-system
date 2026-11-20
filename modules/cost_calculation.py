"""Non-negative, normalized edge-cost calculation."""


def calculate_edge_cost(edge, weights=None):
    """Calculate a dimensionless generalized cost for one road segment.

    Time and distance are normalized to 10 minutes and 5 km respectively;
    hazard and traffic are expected on a 0..5 scale. Default weights sum to 1.
    """
    weights = weights or {"time": 0.40, "distance": 0.20, "hazard": 0.30, "traffic": 0.10}
    time_component = max(float(edge.get("travel_time_min", 0)), 0) / 10.0
    distance_component = max(float(edge.get("distance_km", 0)), 0) / 5.0
    hazard_component = min(max(float(edge.get("hazard", 0)), 0), 5) / 5.0
    traffic_component = min(max(float(edge.get("traffic", 0)), 0), 5) / 5.0
    return (
        float(weights["time"]) * time_component
        + float(weights["distance"]) * distance_component
        + float(weights["hazard"]) * hazard_component
        + float(weights["traffic"]) * traffic_component
    )


def prepare_costs(graph, weights=None):
    """Attach cost to traversable edges and mark blocked edges as unavailable."""
    for _, _, attrs in graph.edges(data=True):
        attrs["cost"] = calculate_edge_cost(attrs, weights)
        attrs["available"] = not bool(attrs.get("blocked", False))
    return graph
