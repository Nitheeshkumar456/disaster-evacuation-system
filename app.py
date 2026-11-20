from __future__ import annotations
import copy
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from modules.data_collection import load_sample_network, load_osm_network
from modules.graph_builder import nearest_graph_node, node_label
from modules.cost_calculation import prepare_costs
from modules.hazard_assessment import update_road_condition
from modules.uniform_cost_search import uniform_cost_search, path_metrics, k_shortest_feasible_paths
from modules.shelter_validation import eligible_shelters
from modules.route_visualization import create_route_map
from modules.sample_data import SAMPLE_SHELTERS
from modules.storage import initialize_database, save_shelters, load_shelters

st.set_page_config(page_title="AI Disaster Evacuation Planner", page_icon="🚨", layout="wide")

@st.cache_resource(show_spinner=False)
def cached_osm_network(place: str):
    return load_osm_network(place)


def make_shelters(graph, source):
    if source == "Sample network":
        return copy.deepcopy(SAMPLE_SHELTERS)
    # Initial demonstration shelter locations; verify and replace with official shelter data.
    candidates = [
        ("Egmore Demo Shelter", 13.0785, 80.2610, 1800),
        ("Adyar Demo Shelter", 13.0067, 80.2570, 1200),
        ("Anna Nagar Demo Shelter", 13.0878, 80.2081, 2500),
    ]
    result = []
    for name, lat, lon, capacity in candidates:
        node = nearest_graph_node(graph, lat, lon)
        result.append({"name": name, "node": node, "capacity": capacity, "available": True})
    return result


def format_node(graph, node):
    return node_label(graph, node)

initialize_database()
st.title("🚨 AI-Based Disaster Evacuation Route Planning")
st.caption("Cost-aware evacuation planning using graph construction, hazard penalties and Uniform-Cost Search")
st.info("Prototype for academic demonstration. Always follow official emergency-management instructions. Map roads and demo shelter locations must be verified before real-world use.")

with st.sidebar:
    st.header("1. Data source")
    source = st.radio("Road network", ["Sample network", "OpenStreetMap – Chennai", "Both / compare"], index=2)
    place = st.text_input("OSM area", "Chennai, Tamil Nadu, India")
    load_clicked = st.button("Load / refresh road network", type="primary", use_container_width=True)
    st.divider()
    st.header("2. Evacuation inputs")
    start_lat = st.number_input("Start latitude", value=13.0418, format="%.6f")
    start_lon = st.number_input("Start longitude", value=80.2337, format="%.6f")
    population = st.number_input("Population to evacuate", min_value=1, max_value=100000, value=500, step=50)
    st.caption("Start coordinates default to T. Nagar, Chennai. Adjust them to your scenario.")

if "active_graph" not in st.session_state:
    st.session_state.active_graph = load_sample_network()
    st.session_state.active_source = "Sample network"
    stored_shelters = load_shelters()
    node_lookup = {str(node): node for node in st.session_state.active_graph.nodes}
    restored = [dict(s, node=node_lookup[str(s["node"])]) for s in stored_shelters if str(s["node"]) in node_lookup]
    st.session_state.shelters = restored or make_shelters(st.session_state.active_graph, "Sample network")

if load_clicked:
    try:
        if source == "Sample network":
            graph = load_sample_network()
            actual_source = "Sample network"
        elif source == "OpenStreetMap – Chennai":
            with st.spinner("Downloading Chennai road network from OpenStreetMap…"):
                graph = copy.deepcopy(cached_osm_network(place))
            actual_source = "OpenStreetMap"
        else:
            # Both mode uses OSM when online; if download fails, the sample network remains usable.
            with st.spinner("Loading OpenStreetMap network; sample data remains available as fallback…"):
                graph = copy.deepcopy(cached_osm_network(place))
            actual_source = "OpenStreetMap (sample fallback available)"
        st.session_state.active_graph = graph
        st.session_state.active_source = actual_source
        st.session_state.shelters = make_shelters(graph, "OpenStreetMap" if "OpenStreetMap" in actual_source else "Sample network")
        st.success(f"Loaded {graph.number_of_nodes():,} intersections and {graph.number_of_edges():,} road segments.")
    except Exception as exc:
        if source == "Both / compare":
            st.warning(f"OSM download unavailable; using the offline sample network. Details: {exc}")
            graph = load_sample_network()
            st.session_state.active_graph = graph
            st.session_state.active_source = "Sample network (offline fallback)"
            st.session_state.shelters = make_shelters(graph, "Sample network")
        else:
            st.error(str(exc))

graph = copy.deepcopy(st.session_state.active_graph)
st.caption(f"Active data: **{st.session_state.active_source}** · {graph.number_of_nodes():,} nodes · {graph.number_of_edges():,} edges")

# Resolve the evacuation origin to the nearest road intersection.
start_node = nearest_graph_node(graph, start_lat, start_lon)

# Shelter editor: editable demo capacity and availability; nodes are snapped to the road graph.
with st.expander("Shelter management", expanded=True):
    shelters = copy.deepcopy(st.session_state.shelters)
    shelter_df = pd.DataFrame([
        {"Shelter": s["name"], "Road node": str(s["node"]), "Capacity": int(s["capacity"]), "Available": bool(s["available"])}
        for s in shelters
    ])
    edited = st.data_editor(shelter_df, use_container_width=True, hide_index=True, num_rows="dynamic", key="shelter_editor")
    if st.button("Save shelter changes"):
        updated = []
        for _, row in edited.iterrows():
            try:
                entered_node = row["Road node"]
                # Streamlit's editor may return numeric OSM node IDs as strings.
                node_lookup = {str(existing): existing for existing in graph.nodes}
                if str(entered_node) not in node_lookup:
                    continue
                node = node_lookup[str(entered_node)]
                updated.append({"name": str(row["Shelter"]), "node": node, "capacity": max(0, int(row["Capacity"])), "available": bool(row["Available"])})
            except Exception:
                continue
        st.session_state.shelters = updated
        save_shelters(updated)
        st.success(f"Saved {len(updated)} shelter records.")

shelters = st.session_state.shelters

# Hazard/traffic controls update one road segment in the current scenario.
with st.expander("Hazard and road-condition management", expanded=True):
    edge_pairs = list(graph.edges())
    edge_pairs.sort(key=lambda pair: str(pair))
    edge_options = edge_pairs[:5000]
    if edge_options:
        def edge_text(pair):
            attrs = graph[pair[0]][pair[1]]
            return f"{attrs.get('name', str(pair[0]) + ' – ' + str(pair[1]))} | {str(pair[0])[:18]} ↔ {str(pair[1])[:18]}"
        selected_edge = st.selectbox("Road segment to update", edge_options, format_func=edge_text)
        c1, c2, c3 = st.columns(3)
        with c1:
            hazard_level = st.slider("Hazard level (0–5)", 0, 5, int(graph[selected_edge[0]][selected_edge[1]].get("hazard", 0)))
        with c2:
            traffic_level = st.slider("Traffic level (0–5)", 0, 5, int(graph[selected_edge[0]][selected_edge[1]].get("traffic", 0)))
        with c3:
            is_blocked = st.checkbox("Confirmed blocked / impassable", value=bool(graph[selected_edge[0]][selected_edge[1]].get("blocked", False)))
        if st.button("Apply road condition"):
            update_road_condition(graph, *selected_edge, hazard=hazard_level, traffic=traffic_level, blocked=is_blocked)
            st.session_state.active_graph = graph
            st.success("Road condition updated for this planning session.")
    else:
        st.warning("No road segments are available in the current graph.")

st.subheader("3. Cost-aware route planning")
with st.expander("Path-cost weights", expanded=False):
    st.write("The four components are normalized before weighting to avoid mixing minutes, kilometres and risk scores directly.")
    w1, w2, w3, w4 = st.columns(4)
    wt = w1.slider("Travel time", 0.0, 1.0, 0.40, 0.05)
    wd = w2.slider("Distance", 0.0, 1.0, 0.20, 0.05)
    wh = w3.slider("Hazard", 0.0, 1.0, 0.30, 0.05)
    wq = w4.slider("Congestion", 0.0, 1.0, 0.10, 0.05)
    st.caption(f"Weight total: {wt + wd + wh + wq:.2f}. Weights are used as entered; they need not sum to one.")
weights = {"time": wt, "distance": wd, "hazard": wh, "traffic": wq}

# Recalculate costs after all user-edited road conditions.
prepare_costs(graph, weights)
# Keep graph changes and calculated costs in the active session.
st.session_state.active_graph = graph
valid_shelters = eligible_shelters(shelters, population)

if not valid_shelters:
    st.error("No available shelter has enough capacity for the entered population. Update shelter capacity or population before routing.")
else:
    goal_nodes = [s["node"] for s in valid_shelters if s["node"] in graph]
    result = uniform_cost_search(graph, start_node, goal_nodes)
    if result is None:
        st.error("No feasible route reaches an available shelter. Check blocked roads, start location and shelter connectivity.")
    else:
        chosen = next(s for s in valid_shelters if s["node"] == result["goal"])
        metrics = path_metrics(graph, result["path"])
        st.success(f"Minimum-cost feasible route found to **{chosen['name']}**.")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total path cost", f"{result['total_cost']:.3f}")
        k2.metric("Distance", f"{metrics['distance_km']:.2f} km")
        k3.metric("Estimated travel time", f"{metrics['travel_time_min']:.1f} min")
        k4.metric("Nodes expanded", result["expanded_nodes"])
        st.write(f"**Route:** {' → '.join(str(n) for n in result['path'])}")
        st.write(f"**Selected shelter:** {chosen['name']} · Capacity: {chosen['capacity']:,} · Population: {population:,}")
        if metrics["max_hazard"] >= 4:
            st.warning("The selected route includes a high-hazard road. Review the hazard data before using this result.")
        elif metrics["max_hazard"] >= 2:
            st.warning("The selected route includes at least one road with a moderate hazard penalty.")
        else:
            st.info("No moderate-or-higher hazard rating is recorded on the selected route. This does not guarantee real-world safety.")

        st.subheader("4. Evacuation route map")
        show_all = st.checkbox("Show surrounding road segments", value=False)
        fmap = create_route_map(graph, result["path"], hazards=True, show_roads=show_all)
        st_folium(fmap, use_container_width=True, height=560, returned_objects=[])

        route_rows = []
        for index, (u, v) in enumerate(zip(result["path"], result["path"][1:]), start=1):
            edge = graph[u][v]
            route_rows.append({
                "Segment": index,
                "From": str(u),
                "To": str(v),
                "Distance (km)": round(edge.get("distance_km", 0), 3),
                "Time (min)": round(edge.get("travel_time_min", 0), 2),
                "Hazard (0–5)": edge.get("hazard", 0),
                "Traffic (0–5)": edge.get("traffic", 0),
                "Cost": round(edge.get("cost", 0), 4),
            })
        with st.expander("Route segment breakdown"):
            st.dataframe(pd.DataFrame(route_rows), use_container_width=True, hide_index=True)

        alternatives = k_shortest_feasible_paths(graph, start_node, result["goal"], k=3)
        if len(alternatives) > 1:
            st.subheader("Alternative routes to the selected shelter")
            alternative_rows = []
            for index, alternative in enumerate(alternatives[1:], start=2):
                alternative_rows.append({
                    "Alternative": f"Route {index}",
                    "Path": " → ".join(str(node) for node in alternative["path"]),
                    "Cost": round(alternative["total_cost"], 4),
                    "Distance (km)": round(alternative["distance_km"], 2),
                    "Travel time (min)": round(alternative["travel_time_min"], 1),
                })
            st.dataframe(pd.DataFrame(alternative_rows), use_container_width=True, hide_index=True)

st.divider()
st.caption("Academic prototype · UCS optimizes the supplied edge-cost model. Live traffic, verified road closures, flood depth and official shelter status are not automatically guaranteed by OpenStreetMap.")
