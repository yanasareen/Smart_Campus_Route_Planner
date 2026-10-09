import math
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

# Import existing core project components - Preserving all existing code!
from algorithms import dijkstra, a_star
from campus import (
    CAMPUS_GRAPH,
    LOCATIONS,
    get_available_locations,
    get_euclidean_heuristics
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Campus Route Planner",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished cards and metrics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. MAP PLOTTING FUNCTION (MATPLOTLIB VISUALIZATION)
# -----------------------------------------------------------------------------
def plot_campus_map(start, goal, path=None, visited_nodes=None, title="Campus Map"):
    """
    Renders an interactive campus map visualization using Matplotlib.
    Displays locations as labeled nodes, walking paths with distance weights,
    and highlights the computed shortest route and explored nodes.
    """
    fig, ax = plt.subplots(figsize=(9, 6), dpi=120)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')
    
    # 1. Draw Graph Edges (Walking Paths & Weights)
    drawn_edges = set()
    for u, neighbors in CAMPUS_GRAPH.items():
        x1, y1 = LOCATIONS[u]
        for v, weight in neighbors.items():
            edge = tuple(sorted([u, v]))
            if edge not in drawn_edges:
                drawn_edges.add(edge)
                x2, y2 = LOCATIONS[v]
                
                # Draw edge line
                ax.plot([x1, x2], [y1, y2], color='#94a3b8', linestyle='--', linewidth=2, zorder=1)
                
                # Calculate midpoint for weight label placement
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                # Display distance weight
                ax.text(
                    mid_x, mid_y, str(weight),
                    fontsize=10, fontweight='bold', color='#334155',
                    ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec="#cbd5e1", lw=1),
                    zorder=2
                )

    # 2. Highlight Shortest Route (if available)
    if path and len(path) > 1:
        path_x = [LOCATIONS[node][0] for node in path]
        path_y = [LOCATIONS[node][1] for node in path]
        
        # Draw bold highlighted route
        ax.plot(path_x, path_y, color='#2563eb', linewidth=5.5, alpha=0.85, label='Shortest Route', zorder=3)
        
        # Add direction indicators along path
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            x1, y1 = LOCATIONS[u]
            x2, y2 = LOCATIONS[v]
            ax.annotate(
                '', xy=((x1 + x2)/2, (y1 + y2)/2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#1d4ed8", lw=3, mutation_scale=18),
                zorder=4
            )

    # 3. Draw Nodes (Locations)
    for node, (x, y) in LOCATIONS.items():
        # Node styling based on state
        if node == start and node == goal:
            color = '#9333ea'  # Purple if start == goal
            size = 1400
            label_prefix = "🟢🔴 "
        elif node == start:
            color = '#16a34a'  # Green for Start
            size = 1400
            label_prefix = "🟢 Start: "
        elif node == goal:
            color = '#dc2626'  # Red for Goal
            size = 1400
            label_prefix = "🔴 Goal: "
        elif visited_nodes and node in visited_nodes:
            color = '#f59e0b'  # Amber for Explored Nodes
            size = 1000
            label_prefix = "🔍 "
        else:
            color = '#475569'  # Slate for Standard Buildings
            size = 1000
            label_prefix = ""

        # Draw Node Circle
        ax.scatter(x, y, s=size, color=color, zorder=5, edgecolors='#ffffff', linewidths=2.5)
        
        # Draw Node Label
        label_text = f"{label_prefix}{node}\n({x}, {y})"
        ax.text(
            x, y + 0.55, label_text,
            fontsize=10, fontweight='bold', color='#0f172a',
            ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#e2e8f0", alpha=0.9),
            zorder=6
        )

    # Map Title & Axes Formatting
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    ax.set_xlabel("X Coordinates (meters/grid units)", fontsize=10, color='#475569')
    ax.set_ylabel("Y Coordinates (meters/grid units)", fontsize=10, color='#475569')
    ax.grid(True, linestyle=':', alpha=0.5, color='#cbd5e1')
    
    # Set comfortable axis limits around map coordinates
    all_x = [pos[0] for pos in LOCATIONS.values()]
    all_y = [pos[1] for pos in LOCATIONS.values()]
    ax.set_xlim(min(all_x) - 1.5, max(all_x) + 1.5)
    ax.set_ylim(min(all_y) - 1.2, max(all_y) + 2.0)
    
    # Map Legend
    legend_patches = [
        mpatches.Patch(color='#16a34a', label='Start Location'),
        mpatches.Patch(color='#dc2626', label='Destination Goal'),
        mpatches.Patch(color='#2563eb', label='Optimal Route Path'),
        mpatches.Patch(color='#475569', label='Campus Building')
    ]
    if visited_nodes:
        legend_patches.insert(3, mpatches.Patch(color='#f59e0b', label='Explored Node'))
        
    ax.legend(handles=legend_patches, loc='upper left', framealpha=0.9, fontsize=9)
    plt.tight_layout()
    return fig


# -----------------------------------------------------------------------------
# 3. MAIN APPLICATION INTERFACE
# -----------------------------------------------------------------------------
def main():
    # Application Title & Header
    st.markdown('<div class="main-header">📍 Smart Campus Route Planner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">An interactive AI Pathfinding Dashboard comparing <b>A* Search Algorithm</b> '
        'and <b>Dijkstra\'s Algorithm</b> on campus walking routes using dynamic Euclidean heuristics.</div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------
    # SIDEBAR CONTROLS
    # -------------------------------------------------------------------------
    st.sidebar.header("⚙️ Navigation Controls")
    locations = get_available_locations()
    
    # Start and Destination Dropdowns
    start_location = st.sidebar.selectbox(
        "Select Starting Location:",
        options=locations,
        index=0  # Default: Hostel
    )
    
    goal_location = st.sidebar.selectbox(
        "Select Destination Goal:",
        options=locations,
        index=3  # Default: Library
    )
    
    st.sidebar.markdown("---")
    
    # View Mode Selection
    view_mode = st.sidebar.radio(
        "Select Algorithm View Mode:",
        options=["Algorithm Comparison Mode", "A* Search Algorithm", "Dijkstra's Algorithm"],
        index=0
    )
    
    # Optional Animation Step Checkbox
    animate_steps = st.sidebar.checkbox(
        "Animate Node Exploration Steps",
        value=False,
        help="Check this to step through the order of explored nodes before showing the final path."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Viva Defense Tip:**\n"
        "- **Dijkstra** uses $f(n) = g(n)$ (uninformed search).\n"
        "- **A* Search** uses $f(n) = g(n) + h(n)$ with Euclidean distance (informed search)."
    )

    # -------------------------------------------------------------------------
    # ALGORITHM EXECUTION & TIMING (Reusing existing algorithms.py!)
    # -------------------------------------------------------------------------
    # Compute dynamic Euclidean heuristics for A*
    heuristics = get_euclidean_heuristics(goal_location)

    # 1. Run A* Search Algorithm
    t0_a = time.perf_counter()
    a_path, a_dist, a_nodes, a_visited = a_star(
        CAMPUS_GRAPH, start_location, goal_location, heuristics, return_visited_order=True
    )
    a_time_ms = (time.perf_counter() - t0_a) * 1000  # Convert to milliseconds

    # 2. Run Dijkstra's Algorithm
    t0_d = time.perf_counter()
    d_path, d_dist, d_nodes, d_visited = dijkstra(
        CAMPUS_GRAPH, start_location, goal_location, return_visited_order=True
    )
    d_time_ms = (time.perf_counter() - t0_d) * 1000  # Convert to milliseconds

    # -------------------------------------------------------------------------
    # DISPLAY MAIN CONTENT TABS
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Campus Map & Route Visualizer",
        "📊 Algorithm Performance Comparison",
        "🎓 Technical Viva Preparation Guide"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: CAMPUS MAP & ROUTE VISUALIZER
    # -------------------------------------------------------------------------
    with tab1:
        # Edge Case: Start == Destination
        if start_location == goal_location:
            st.warning("⚠️ **Notice:** Starting location and destination goal are identical!")
            st.info("📍 **Route:** You are already at your destination. Distance = 0.00 units.")
            fig = plot_campus_map(start_location, goal_location, path=[start_location], title=f"Route: {start_location} (Start = Destination)")
            st.pyplot(fig)
        
        # Edge Case: Path Unreachable
        elif a_path is None or d_path is None:
            st.error(f"❌ No valid walking route exists between **{start_location}** and **{goal_location}**.")
            fig = plot_campus_map(start_location, goal_location, title="No Route Available")
            st.pyplot(fig)

        # Standard Route Found
        else:
            # Determine which algorithm output to display based on view mode
            if view_mode == "A* Search Algorithm":
                active_path, active_dist, active_nodes, active_visited = a_path, a_dist, a_nodes, a_visited
                mode_title = f"A* Search Route: {start_location} ➔ {goal_location}"
            elif view_mode == "Dijkstra's Algorithm":
                active_path, active_dist, active_nodes, active_visited = d_path, d_dist, d_nodes, d_visited
                mode_title = f"Dijkstra Route: {start_location} ➔ {goal_location}"
            else:
                # Comparison Mode: Default display A* path on map
                active_path, active_dist, active_nodes, active_visited = a_path, a_dist, a_nodes, a_visited
                mode_title = f"Optimal Route: {start_location} ➔ {goal_location}"

            # Step-by-Step Animation Option (Requirement 4)
            if animate_steps and len(active_visited) > 1:
                st.subheader("🔍 Step-by-Step Node Exploration Progress")
                step = st.slider(
                    "Move slider to step through node exploration sequence:",
                    min_value=1,
                    max_value=len(active_visited),
                    value=len(active_visited)
                )
                current_explored = active_visited[:step]
                current_path = active_path if step == len(active_visited) else None
                
                fig = plot_campus_map(
                    start_location, goal_location,
                    path=current_path,
                    visited_nodes=current_explored,
                    title=f"Exploration Step {step}/{len(active_visited)}: Explored {current_explored[-1]}"
                )
                st.pyplot(fig)
            else:
                # Standard Map View
                fig = plot_campus_map(start_location, goal_location, path=active_path, title=mode_title)
                st.pyplot(fig)

            # Results Cards Section
            st.markdown("### 📌 Route Results Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Start Location", start_location)
            with col2:
                st.metric("Destination Goal", goal_location)
            with col3:
                st.metric("Shortest Distance", f"{active_dist:.2f} units")
            with col4:
                st.metric("Nodes Explored", f"{active_nodes} nodes")

            st.success(f"🛣️ **Optimal Route Sequence:** `{' ➔ '.join(active_path)}`")

    # -------------------------------------------------------------------------
    # TAB 2: ALGORITHM COMPARISON SECTION (Requirement 3)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("📊 Side-by-Side Algorithm Comparison")
        st.markdown(
            "Comparing **A* Search** and **Dijkstra's Algorithm** executing on the exact same campus graph "
            "and edge weights for the selected start and destination."
        )

        col_a, col_b = st.columns(2)

        # Dijkstra Summary Card
        with col_a:
            st.markdown("#### 1. Dijkstra's Algorithm (Uninformed Search)")
            st.markdown(f"- **Optimal Route:** `{' ➔ '.join(d_path) if d_path else 'None'}`")
            st.markdown(f"- **Total Distance:** `{d_dist:.2f}` units")
            st.markdown(f"- **Nodes Explored:** `{d_nodes}` nodes")
            st.markdown(f"- **Execution Time:** `{d_time_ms:.4f}` ms")
            st.markdown(f"- **Exploration Order:** `{', '.join(d_visited)}`")

        # A* Search Summary Card
        with col_b:
            st.markdown("#### 2. A* Search Algorithm (Informed Search)")
            st.markdown(f"- **Optimal Route:** `{' ➔ '.join(a_path) if a_path else 'None'}`")
            st.markdown(f"- **Total Distance:** `{a_dist:.2f}` units")
            st.markdown(f"- **Nodes Explored:** `{a_nodes}` nodes")
            st.markdown(f"- **Execution Time:** `{a_time_ms:.4f}` ms")
            st.markdown(f"- **Exploration Order:** `{', '.join(a_visited)}`")

        st.markdown("---")

        # Visual Comparison Bar Charts
        st.markdown("### 📈 Visual Metrics Comparison")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Bar Chart: Nodes Explored
            fig_bar1, ax_bar1 = plt.subplots(figsize=(5, 3.5), dpi=100)
            algorithms = ['Dijkstra', 'A* Search']
            nodes = [d_nodes, a_nodes]
            colors = ['#f59e0b', '#2563eb']
            
            bars = ax_bar1.bar(algorithms, nodes, color=colors, width=0.5, edgecolor='#0f172a', linewidth=1)
            ax_bar1.set_ylabel("Nodes Explored Count", fontsize=9)
            ax_bar1.set_title("Explored Nodes Comparison (Lower is Better)", fontsize=10, fontweight='bold')
            ax_bar1.grid(axis='y', linestyle=':', alpha=0.6)
            
            # Value Labels on Bars
            for bar in bars:
                height = bar.get_height()
                ax_bar1.text(bar.get_x() + bar.get_width()/2., height + 0.05, f"{int(height)}", ha='center', va='bottom', fontweight='bold')
                
            st.pyplot(fig_bar1)

        with chart_col2:
            # Bar Chart: Execution Time
            fig_bar2, ax_bar2 = plt.subplots(figsize=(5, 3.5), dpi=100)
            times = [d_time_ms, a_time_ms]
            
            bars2 = ax_bar2.bar(algorithms, times, color=['#e11d48', '#10b981'], width=0.5, edgecolor='#0f172a', linewidth=1)
            ax_bar2.set_ylabel("Execution Time (ms)", fontsize=9)
            ax_bar2.set_title("Execution Time Comparison (ms)", fontsize=10, fontweight='bold')
            ax_bar2.grid(axis='y', linestyle=':', alpha=0.6)
            
            for bar in bars2:
                height = bar.get_height()
                ax_bar2.text(bar.get_x() + bar.get_width()/2., height + 0.001, f"{height:.3f} ms", ha='center', va='bottom', fontweight='bold', fontsize=8)
                
            st.pyplot(fig_bar2)

        # Performance Analysis Explanation (Requirement 3 & 6)
        st.info(
            "🧠 **Performance Analysis Explanation:**\n\n"
            f"- **Node Exploration Gain:** A* explored **{d_nodes - a_nodes}** fewer node(s) than Dijkstra for this route because the Euclidean heuristic directed the search toward the destination goal.\n"
            "- **Execution Time Note:** Microsecond execution times reflect Python's standard `time.perf_counter()`. Minor variations occur between runs due to operating system thread scheduling and CPU load. Node exploration count is the mathematically deterministic metric for algorithm efficiency."
        )

    # -------------------------------------------------------------------------
    # TAB 3: TECHNICAL VIVA PREPARATION GUIDE
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("🎓 Technical Viva Preparation Guide & Code Architecture")
        st.markdown("""
        ### Project Architecture & Modular Design
        1. **`campus.py`**: Manages graph topology (`CAMPUS_GRAPH`), spatial coordinates (`LOCATIONS`), and dynamic Euclidean heuristic calculation (`get_euclidean_heuristics`).
        2. **`algorithms.py`**: Standard scratch implementations of Dijkstra's algorithm ($f=g$) and A* Search ($f=g+h$) using Python's min-heap (`heapq`).
        3. **`main.py`**: Terminal-based interactive CLI entry point.
        4. **`app.py`**: Streamlit & Matplotlib visual dashboard.

        ---

        ### Key Technical Questions & Answers for Viva

        #### Q1: Why use Euclidean Distance as the Heuristic $h(n)$?
        > **Answer:** Euclidean distance $\\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ calculates straight-line distance on a 2D plane. Since straight-line distance is physically the shortest distance between two points, $h(n) \\le h^*(n)$ (it never overestimates actual walking distance). This makes the heuristic **admissible**, guaranteeing that A* Search returns an optimal path.

        #### Q2: What is the Time and Space Complexity?
        > **Answer:** 
        > - **Time Complexity:** $\\mathcal{O}((V + E) \\log V)$, where $V$ is vertices (buildings) and $E$ is edges (paths). Using `heapq` allows minimum extraction in $\\mathcal{O}(\\log V)$.
        > - **Space Complexity:** $\\mathcal{O}(V + E)$ to store graph adjacency lists, distance tables, and priority queue elements.

        #### Q3: How does Edge Relaxation work in your code?
        > **Answer:** When visiting a node, we check every neighbor. If `current_distance + edge_weight < distances[neighbor]`, we update `distances[neighbor]`, set `previous[neighbor] = current_node`, and push the new distance into the min-heap.
        """)


if __name__ == "__main__":
    main()
