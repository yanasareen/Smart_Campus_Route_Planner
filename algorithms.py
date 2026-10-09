import heapq

def dijkstra(graph, start, goal):
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    priority_queue = [(0, start)]
    visited = set()

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == goal:
            break

        for neighbor, weight in graph[current_node].items():
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    if distances[goal] == float("inf"):
        return None, float("inf"), len(visited)

    path = []
    current_node = goal
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    return path, distances[goal], len(visited)


def a_star(graph, start, goal, heuristics):
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    
    # Priority queue stores tuples of (f_score, node) where f_score = g_score + h(node)
    priority_queue = [(0 + heuristics.get(start, 0), start)]
    visited = set()

    while priority_queue:
        current_f, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == goal:
            break

        for neighbor, weight in graph[current_node].items():
            new_g_distance = distances[current_node] + weight
            if new_g_distance < distances[neighbor]:
                distances[neighbor] = new_g_distance
                previous[neighbor] = current_node
                f_score = new_g_distance + heuristics.get(neighbor, 0)
                heapq.heappush(priority_queue, (f_score, neighbor))

    if distances[goal] == float("inf"):
        return None, float("inf"), len(visited)

    path = []
    current_node = goal
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    return path, distances[goal], len(visited)
