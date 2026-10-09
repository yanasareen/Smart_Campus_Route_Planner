import time
import pandas as pd
import streamlit as st

# Import core project algorithms and campus graph
from algorithms import dijkstra, a_star
from campus import CAMPUS_GRAPH, get_available_locations, get_euclidean_heuristics

# -----------------------------------------------------------------------------
# SIMPLE STREAMLIT USER INTERFACE (UI)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Smart Campus Route Planner", page_icon="📍", layout="centered")

# Title & Description
st.title("📍 Smart Campus Route Planner")
st.write("Select a starting location and destination to compare **Dijkstra's Algorithm** and **A* Search Algorithm**.")

st.markdown("---")

# Location Selectors (Start & Destination)
locations = get_available_locations()

col1, col2 = st.columns(2)
with col1:
    start_location = st.selectbox("Select Start Location:", options=locations, index=0)

with col2:
    goal_location = st.selectbox("Select Destination Location:", options=locations, index=3)

# Calculate Button
calculate = st.button("🚀 Find Shortest Route", type="primary")

st.markdown("---")

# Execute Search & Display Results
if start_location == goal_location:
    st.warning("⚠️ Start and Destination locations are identical! Distance = 0 units.")
else:
    # 1. Run Dijkstra's Algorithm
    t0_d = time.perf_counter()
    d_path, d_dist, d_nodes = dijkstra(CAMPUS_GRAPH, start_location, goal_location)
    d_time = (time.perf_counter() - t0_d) * 1000  # Convert to milliseconds

    # 2. Run A* Search Algorithm with Dynamic Euclidean Heuristics
    heuristics = get_euclidean_heuristics(goal_location)
    t0_a = time.perf_counter()
    a_path, a_dist, a_nodes = a_star(CAMPUS_GRAPH, start_location, goal_location, heuristics)
    a_time = (time.perf_counter() - t0_a) * 1000  # Convert to milliseconds

    st.markdown("### 📊 Algorithm Comparison Table")

    # Format Path Strings
    d_route_str = " ➔ ".join(d_path) if d_path else "No path found"
    a_route_str = " ➔ ".join(a_path) if a_path else "No path found"

    # Tabular Comparison Data
    table_data = [
        {
            "Algorithm": "Dijkstra's Algorithm (Uninformed)",
            "Optimal Route": d_route_str,
            "Total Distance": f"{d_dist:.2f} units",
            "Nodes Explored": d_nodes,
            "Execution Time": f"{d_time:.3f} ms"
        },
        {
            "Algorithm": "A* Search Algorithm (Informed)",
            "Optimal Route": a_route_str,
            "Total Distance": f"{a_dist:.2f} units",
            "Nodes Explored": a_nodes,
            "Execution Time": f"{a_time:.3f} ms"
        }
    ]

    # Display Clean Streamlit Table
    df = pd.DataFrame(table_data)
    st.table(df)

    st.markdown("---")

    # Simple Summary Note
    diff = d_nodes - a_nodes
    if diff > 0:
        st.success(f"💡 **Efficiency Result:** A* Search explored **{diff} fewer node(s)** than Dijkstra because of the Euclidean straight-line heuristic!")
    elif diff == 0:
        st.info("💡 **Efficiency Result:** Both algorithms explored an equal number of nodes for this route.")
    else:
        st.info(f"💡 **Efficiency Result:** Dijkstra expanded {-diff} fewer nodes.")
