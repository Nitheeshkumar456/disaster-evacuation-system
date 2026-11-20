"""Small Chennai-inspired sample network for offline demos and tests."""
import networkx as nx


def build_sample_graph():
    """Return a small, connected, weighted road graph around central Chennai.

    Coordinates are illustrative demo points, not authoritative road geometry.
    """
    graph = nx.Graph()
    nodes = {
        "T_Nagar": (13.0418, 80.2337),
        "Mambalam": (13.0382, 80.2209),
        "Nungambakkam": (13.0569, 80.2425),
        "Egmore": (13.0785, 80.2610),
        "Chepauk": (13.0644, 80.2807),
        "Marina": (13.0500, 80.2824),
        "Adyar": (13.0067, 80.2570),
        "Guindy": (13.0067, 80.2206),
        "Saidapet": (13.0213, 80.2231),
        "Velachery": (12.9815, 80.2180),
        "Anna_Nagar": (13.0878, 80.2081),
        "Koyambedu": (13.0694, 80.1948),
    }
    for name, (lat, lon) in nodes.items():
        graph.add_node(name, y=lat, x=lon, name=name.replace("_", " "))

    # distance_km, travel_time_min, hazard 0..5, traffic 0..5, blocked
    roads = [
        ("T_Nagar", "Mambalam", 1.8, 6, 0, 2, False),
        ("T_Nagar", "Nungambakkam", 2.5, 8, 0, 2, False),
        ("Nungambakkam", "Egmore", 3.0, 10, 1, 2, False),
        ("Egmore", "Chepauk", 3.1, 11, 0, 3, False),
        ("Chepauk", "Marina", 1.8, 7, 1, 2, False),
        ("Marina", "Adyar", 5.5, 16, 0, 3, False),
        ("Adyar", "Velachery", 4.0, 12, 1, 2, False),
        ("Velachery", "Guindy", 4.4, 14, 0, 3, False),
        ("Guindy", "Saidapet", 2.2, 7, 0, 2, False),
        ("Saidapet", "T_Nagar", 2.8, 9, 0, 3, False),
        ("Guindy", "Mambalam", 5.0, 15, 0, 2, False),
        ("Nungambakkam", "Anna_Nagar", 4.0, 13, 0, 2, False),
        ("Anna_Nagar", "Koyambedu", 3.0, 9, 0, 2, False),
        ("Koyambedu", "Guindy", 7.0, 20, 1, 3, False),
        ("T_Nagar", "Chepauk", 5.0, 15, 3, 4, False),
        ("Mambalam", "Guindy", 4.8, 14, 0, 2, False),
        ("Saidapet", "Adyar", 6.0, 18, 0, 3, False),
    ]
    for u, v, distance, minutes, hazard, traffic, blocked in roads:
        graph.add_edge(
            u, v,
            distance_km=distance,
            travel_time_min=minutes,
            hazard=hazard,
            traffic=traffic,
            blocked=blocked,
            name=f"{u.replace('_', ' ')} – {v.replace('_', ' ')}",
            source="sample",
        )
    return graph


SAMPLE_SHELTERS = [
    {"name": "Egmore Relief Centre", "node": "Egmore", "capacity": 1800, "available": True},
    {"name": "Adyar Community Shelter", "node": "Adyar", "capacity": 1200, "available": True},
    {"name": "Anna Nagar Relief Camp", "node": "Anna_Nagar", "capacity": 2500, "available": True},
    {"name": "Velachery Relief Centre", "node": "Velachery", "capacity": 900, "available": True},
]
