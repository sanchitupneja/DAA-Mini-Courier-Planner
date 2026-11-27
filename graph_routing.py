import heapq


def dijkstra(graph, start):
    """
    Computes shortest distances from `start` to all nodes using a min-heap.
    Time Complexity: O((V + E) log V)
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, u = heapq.heappop(pq)
        if current_dist > distances[u]:
            continue

        for v, weight in graph[u]:
            distance = current_dist + weight
            if distance < distances[v]:
                distances[v] = distance
                heapq.heappush(pq, (distance, v))

    return distances


def plan_delivery_route(graph, depot, target_nodes):
    """
    Computes All-Pairs Shortest Paths between depot & target_nodes via Dijkstra,
    then builds a delivery tour using Nearest-Neighbor TSP approximation.
    """
    stops = sorted(list(set([depot] + target_nodes)))
    shortest_paths = {node: dijkstra(graph, node) for node in stops}

    unvisited = set(target_nodes)
    unvisited.discard(depot)

    route = [depot]
    total_distance = 0
    current = depot

    while unvisited:
        next_stop = min(unvisited, key=lambda node: shortest_paths[current][node])
        dist = shortest_paths[current][next_stop]
        total_distance += dist
        route.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop

    # Return to depot
    if current != depot:
        total_distance += shortest_paths[current][depot]
        route.append(depot)

    return route, total_distance, shortest_paths