"""Folium map rendering for road graph and selected evacuation route."""
import folium


def create_route_map(graph, path=None, hazards=True, show_roads=False):
    coords = [(float(d["y"]), float(d["x"])) for _, d in graph.nodes(data=True)]
    center = [sum(p[0] for p in coords) / len(coords), sum(p[1] for p in coords) / len(coords)]
    fmap = folium.Map(location=center, zoom_start=12, control_scale=True, tiles="OpenStreetMap")

    if show_roads:
        for u, v, attrs in graph.edges(data=True):
            a, b = graph.nodes[u], graph.nodes[v]
            color = "#888888" if not attrs.get("blocked", False) else "#d62728"
            folium.PolyLine(
                [(a["y"], a["x"]), (b["y"], b["x"])],
                color=color, weight=2, opacity=0.45,
                tooltip=f"{attrs.get('name', 'Road')} | {attrs.get('distance_km', 0):.2f} km",
            ).add_to(fmap)

    if hazards:
        for u, v, attrs in graph.edges(data=True):
            level = int(attrs.get("hazard", 0))
            if level >= 2 or attrs.get("blocked", False):
                a, b = graph.nodes[u], graph.nodes[v]
                color = "red" if attrs.get("blocked", False) or level >= 4 else "orange"
                folium.PolyLine(
                    [(a["y"], a["x"]), (b["y"], b["x"])],
                    color=color, weight=5, opacity=0.8,
                    tooltip=f"Hazard {level}/5 | {'BLOCKED' if attrs.get('blocked') else 'At risk'}",
                ).add_to(fmap)

    if path:
        route_coords = [(graph.nodes[n]["y"], graph.nodes[n]["x"]) for n in path]
        folium.PolyLine(route_coords, color="#1267e8", weight=7, opacity=0.95, tooltip="Recommended evacuation route").add_to(fmap)
        for index, node in enumerate(path):
            data = graph.nodes[node]
            if index == 0:
                label, color = "Start", "blue"
            elif index == len(path) - 1:
                label, color = "Safe shelter", "green"
            else:
                label, color = f"Intersection {index}", "cadetblue"
            folium.Marker(
                [data["y"], data["x"]],
                tooltip=label,
                popup=f"{label}: {data.get('name', node)}",
                icon=folium.Icon(color=color, icon="info-sign"),
            ).add_to(fmap)
    return fmap
