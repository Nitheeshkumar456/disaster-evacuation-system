"""Graph preparation and nearest-node helpers."""
import math


def nearest_graph_node(graph, latitude: float, longitude: float):
    if graph.number_of_nodes() == 0:
        raise ValueError("The road graph is empty.")
    return min(
        graph.nodes,
        key=lambda node: (graph.nodes[node]["y"] - latitude) ** 2
        + (graph.nodes[node]["x"] - longitude) ** 2,
    )


def node_label(graph, node):
    attrs = graph.nodes[node]
    name = attrs.get("name")
    if name and str(name) != str(node):
        return f"{name} ({node})"
    return str(node)
