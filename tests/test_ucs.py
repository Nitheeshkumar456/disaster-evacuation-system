import networkx as nx
from modules.uniform_cost_search import uniform_cost_search, path_metrics
from modules.cost_calculation import prepare_costs
from modules.shelter_validation import eligible_shelters


def test_ucs_finds_lowest_cumulative_cost():
    graph = nx.Graph()
    graph.add_edge("A", "B", cost=2, distance_km=1, travel_time_min=2)
    graph.add_edge("B", "C", cost=2, distance_km=1, travel_time_min=2)
    graph.add_edge("A", "C", cost=9, distance_km=4, travel_time_min=9)
    result = uniform_cost_search(graph, "A", {"C"})
    assert result["path"] == ["A", "B", "C"]
    assert result["total_cost"] == 4


def test_ucs_avoids_blocked_edge():
    graph = nx.Graph()
    graph.add_edge("A", "B", cost=1, blocked=True)
    graph.add_edge("A", "C", cost=2)
    graph.add_edge("C", "B", cost=2)
    result = uniform_cost_search(graph, "A", {"B"})
    assert result["path"] == ["A", "C", "B"]


def test_cost_is_non_negative():
    graph = nx.Graph()
    graph.add_edge("A", "B", distance_km=2, travel_time_min=5, hazard=3, traffic=2)
    prepare_costs(graph)
    assert graph["A"]["B"]["cost"] >= 0


def test_shelter_capacity_filter():
    shelters = [
        {"name": "small", "capacity": 100, "available": True},
        {"name": "large", "capacity": 500, "available": True},
        {"name": "closed", "capacity": 1000, "available": False},
    ]
    assert [s["name"] for s in eligible_shelters(shelters, 300)] == ["large"]


def test_path_metrics():
    graph = nx.Graph()
    graph.add_edge("A", "B", distance_km=1.5, travel_time_min=4, hazard=2, traffic=3)
    result = path_metrics(graph, ["A", "B"])
    assert result["distance_km"] == 1.5
    assert result["travel_time_min"] == 4
