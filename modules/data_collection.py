"""Road-network collection from sample data or OpenStreetMap via OSMnx."""
from __future__ import annotations
import networkx as nx
from modules.sample_data import build_sample_graph


def load_sample_network():
    return build_sample_graph()


def load_osm_network(place: str = "Chennai, Tamil Nadu, India", network_type: str = "drive"):
    """Download and simplify an OSM road network into an undirected NetworkX graph.

    OSM road geometry and attributes are used where available. OSM does not provide
    authoritative live flood, fire, closure or traffic conditions; those are added
    separately by the user in the hazard module.
    """
    try:
        import osmnx as ox
    except ImportError as exc:
        raise RuntimeError("OSMnx is not installed. Run: pip install -r requirements.txt") from exc

    try:
        raw = ox.graph_from_place(place, network_type=network_type, simplify=True)
    except Exception as exc:
        raise RuntimeError(
            f"Could not download OpenStreetMap roads for '{place}'. Check your internet "
            f"connection or try a smaller area. Details: {exc}"
        ) from exc

    graph = nx.Graph()
    for node_id, data in raw.nodes(data=True):
        graph.add_node(node_id, y=float(data["y"]), x=float(data["x"]), name=str(node_id))

    for u, v, data in raw.edges(data=True):
        length_m = float(data.get("length", 0.0))
        if length_m <= 0:
            continue
        speed_kph = data.get("speed_kph", 30)
        if isinstance(speed_kph, list):
            speed_kph = speed_kph[0]
        try:
            speed_kph = max(float(speed_kph), 5.0)
        except (TypeError, ValueError):
            speed_kph = 30.0
        travel_time_min = data.get("travel_time")
        if travel_time_min is None:
            travel_time_min = (length_m / 1000.0) / speed_kph * 60.0
        else:
            travel_time_min = float(travel_time_min) / 60.0

        candidate = {
            "distance_km": length_m / 1000.0,
            "travel_time_min": max(float(travel_time_min), 0.1),
            "hazard": 0,
            "traffic": 0,
            "blocked": False,
            "name": data.get("name", "Unnamed road"),
            "source": "openstreetmap",
        }
        if graph.has_edge(u, v):
            # For parallel OSM edges, retain the lower-distance connection.
            if candidate["distance_km"] < graph[u][v]["distance_km"]:
                graph[u][v].update(candidate)
        else:
            graph.add_edge(u, v, **candidate)

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        raise RuntimeError("OpenStreetMap returned an empty road graph for this area.")
    return graph
