# AI-Based Disaster Evacuation Route Planning Using Cost-Aware Search

A Streamlit academic prototype implementing the three project modules:

1. Input data collection and graph construction
2. Hazard assessment and cost calculation
3. Uniform-Cost Search and route visualization

## Features

- Offline sample road network based on illustrative points around Chennai
- OpenStreetMap road-network download for a selected place (default: Chennai, Tamil Nadu, India)
- Road intersections represented as graph nodes and road segments as edges
- User-editable hazard, traffic and blocked-road conditions
- Capacity-aware shelter selection
- Uniform-Cost Search using Python `heapq`
- Folium route map and route-segment cost breakdown
- SQLite persistence for shelter records

## Requirements

- Python 3.10 or newer recommended
- Internet connection only for OpenStreetMap download and map tiles

## Windows installation

Open PowerShell or Command Prompt in this folder:

```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## macOS / Linux installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## First run

1. Select **Both / compare** in the sidebar.
2. Keep the default sample network to test the application immediately, or click **Load / refresh road network** to retrieve OSM roads for Chennai.
3. Enter the evacuation start latitude/longitude and population.
4. Review shelter capacity and availability in Shelter management.
5. Select a road segment and change its hazard, traffic or blocked status.
6. Adjust cost weights if required.
7. Review the minimum-cost route, metrics and map.

## Cost model

The PPT specifies:

`C(e) = wt*T(e) + wd*D(e) + wh*H(e) + wq*Q(e)`

To make unlike units comparable, the implementation normalizes time by 10 minutes, distance by 5 km, and hazard/traffic by their 0–5 scales before applying the weights. The resulting edge costs are non-negative, which is required for UCS optimality.

## Data and safety limitations

- The sample network is illustrative and must not be treated as a verified road map.
- OpenStreetMap supplies road geometry and some road attributes; it does not guarantee live traffic, flood depth, fire boundaries, road closures or shelter capacity.
- OSM shelter defaults are demonstration locations snapped to nearby road nodes, not verified emergency shelters. Replace them with official district/municipal disaster-management data.
- A blocked edge is excluded from search. Hazard and traffic values are manual scenario inputs in this prototype.
- This application is an academic decision-support prototype, not an operational emergency dispatch system. Follow official evacuation orders and emergency services.

## Tests

```bash
python -m pytest -q
```

## Project structure

```text
disaster-evacuation-system/
├── app.py
├── requirements.txt
├── README.md
├── modules/
│   ├── data_collection.py
│   ├── sample_data.py
│   ├── graph_builder.py
│   ├── hazard_assessment.py
│   ├── cost_calculation.py
│   ├── uniform_cost_search.py
│   ├── shelter_validation.py
│   ├── route_visualization.py
│   └── storage.py
├── data/
└── tests/
    └── test_ucs.py
```
