# Smart Campus Route Planner 

An implementation of pathfinding algorithms (**Dijkstra's Algorithm** and **A* Search Algorithm**) from scratch in Python to find optimal walking routes across campus locations.

---

## Project Overview

The **Smart Campus Route Planner** models a university campus as a weighted graph where buildings are nodes, walking paths are edges with distance weights, and spatial coordinates $(x, y)$ are used to calculate real-world straight-line heuristics.

This project compares an **uninformed search algorithm** (Dijkstra) against an **informed search algorithm** ($A^*$) to demonstrate efficiency gains in node exploration while guaranteeing optimal route discovery.

---

##  Project Structure

```text
Smart_Campus_Route_Planner/
│
├── main.py          # Application entry point & interactive CLI interface
├── algorithms.py    # Standard implementations of Dijkstra & A* algorithms
├── campus.py        # Campus graph, 2D spatial coordinates & Euclidean heuristics
└── README.md        # Technical documentation & viva defense guide
```

---

##  Algorithms & Mathematical Formulations

### 1. Dijkstra's Algorithm (Uninformed Search)
- **Evaluation Function**: $f(n) = g(n)$
- **$g(n)$**: Exact accumulated path cost from the start node to node $n$.
- **Mechanism**: Explores nodes strictly in order of lowest accumulated cost using a min-heap priority queue.

### 2. A* Search Algorithm (Informed Search)
- **Evaluation Function**: $f(n) = g(n) + h(n)$
- **$g(n)$**: Exact path cost from start to node $n$.
- **$h(n)$**: Heuristic estimate of remaining cost from node $n$ to goal.
- **Euclidean Distance Heuristic**:
  $$h(n) = \sqrt{(x_{\text{goal}} - x_n)^2 + (y_{\text{goal}} - y_n)^2}$$
- **Admissibility**: Because straight-line distance is physically the shortest possible distance between two points on a plane, $h(n) \le h^*(n)$ (never overestimates real path cost). This guarantees $A^*$ finds the optimal path.

---

## Complexity Analysis

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | $O((V + E) \log V)$ | $V$ vertices (locations) and $E$ edges (paths). Each priority queue insert/pop takes $O(\log V)$. |
| **Space Complexity** | $O(V + E)$ | Storing adjacency list graph, distance tables, visited set, and min-heap priority queue. |

---

##  How to Run the Application

1. Open your terminal in the project directory:
   ```bash
   cd ~/Desktop/Smart_Campus_Route_Planner
   ```
2. Run the application:
   ```bash
   python3 main.py
   ```
3. Select your desired **START** and **GOAL** campus locations from the interactive menu.

---
