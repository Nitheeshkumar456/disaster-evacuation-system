"""Uniform-Cost Search implemented with heapq."""
from __future__ import annotations
import heapq
import itertools
import math


def uniform_cost_search(graph, start, goals, weight="cost"):
    """Find the minimum cumulative-cost path from start to any goal.

    Returns a result dictionary or None if no feasible goal is reachable.
    All traversable edge weights must be non-negative.
    """
    goals = set(goals)
    if start not in graph:
        raise ValueError(f"Start node {start!r} is not in the graph.")
    goals &= set(graph.nodes)
    if not goals:
        return None

    for _, _, attrs in graph.edges(data=True):
        if attrs.get("blocked", False) or not attrs.get("available", True):
            continue
        edge_cost = float(attrs.get(weight, 1.0))
        if not math.isfinite(edge_cost) or edge_cost < 0:
            raise ValueError("Uniform-Cost Search requires finite, non-negative edge costs.")

    counter = itertools.count()
    frontier = [(0.0, next(counter), start)]
    best_cost = {start: 0.0}
    parent = {start: None}
    expanded = 0

    while frontier:
        cumulative_cost, _, current = heapq.heappop(frontier)
        if cumulative_cost > best_cost.get(current, float("inf")):
            continue
        expanded += 1
        if current in goals:
            path = []
            cursor = current
            while cursor is not None:
                path.append(cursor)
                cursor = parent[cursor]
            path.reverse()
            return {
                "path": path,
                "goal": current,
                "total_cost": cumulative_cost,
                "expanded_nodes": expanded,
            }

        for neighbour, attrs in graph[current].items():
            if attrs.get("blocked", False) or not attrs.get("available", True):
                continue
            edge_cost = float(attrs.get(weight, 1.0))
            new_cost = cumulative_cost + edge_cost
            if new_cost < best_cost.get(neighbour, float("inf")):
                best_cost[neighbour] = new_cost
                parent[neighbour] = current
                heapq.heappush(frontier, (new_cost, next(counter), neighbour))

    return None


def path_metrics(graph, path):
    distance = travel_time = 0.0
    hazards = []
    traffic = []
    for u, v in zip(path, path[1:]):
        edge = graph[u][v]
        distance += float(edge.get("distance_km", 0))
        travel_time += float(edge.get("travel_time_min", 0))
        hazards.append(int(edge.get("hazard", 0)))
        traffic.append(int(edge.get("traffic", 0)))
    return {
        "distance_km": distance,
        "travel_time_min": travel_time,
        "max_hazard": max(hazards, default=0),
        "average_hazard": sum(hazards) / len(hazards) if hazards else 0,
        "average_traffic": sum(traffic) / len(traffic) if traffic else 0,
    }


def k_shortest_feasible_paths(graph, start, goal, k=3, weight="cost"):
    """Return up to k distinct low-cost paths to one goal, excluding blocked roads.

    The primary recommended path is still produced by the project's UCS function.
    This helper uses NetworkX's Yen-style shortest-simple-path generator only to
    present alternatives for comparison.
    """
    import networkx as nx
    filtered = graph.copy()
    filtered.remove_edges_from([
        (u, v) for u, v, attrs in filtered.edges(data=True)
        if attrs.get("blocked", False) or not attrs.get("available", True)
    ])
    if start not in filtered or goal not in filtered:
        return []
    try:
        paths = []
        for path in nx.shortest_simple_paths(filtered, start, goal, weight=weight):
            cost = sum(float(filtered[u][v].get(weight, 1.0)) for u, v in zip(path, path[1:]))
            paths.append({"path": path, "total_cost": cost, **path_metrics(filtered, path)})
            if len(paths) >= max(1, int(k)):
                break
        return paths
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []
