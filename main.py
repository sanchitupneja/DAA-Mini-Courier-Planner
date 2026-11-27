import json
import time
from sorting import merge_sort_parcels
from knapsack import solve_knapsack
from graph_routing import plan_delivery_route


def run_planner(dataset_path, show_dp_table=False):
    with open(dataset_path, "r") as f:
        data = json.load(f)

    capacity = data["vehicle_capacity"]
    depot = data["depot"]
    parcels = data["parcels"]
    # Convert string keys back to int for graph adjacency list
    graph = {int(k): v for k, v in data["graph"].items()}

    print(f"\n{'='*60}")
    print(f"MINI-COURIER PLANNER | Dataset: {dataset_path}")
    print(f"Total Parcels: {len(parcels)} | Nodes: {len(graph)} | Van Capacity: {capacity} kg")
    print(f"{'='*60}")

    # Phase 2A: Sorting
    t0 = time.perf_counter()
    sorted_parcels = merge_sort_parcels(parcels)
    t_sort = (time.perf_counter() - t0) * 1000

    print("\n[Phase 2A] Top Prioritized Parcels (Merge Sort):")
    for p in sorted_parcels[:5]:
        print(f"  ID: {p['id']} | Dest: Node {p['destination']} | Wt: {p['weight']}kg | Priority: {p['priority']} | Deadline: {p['deadline']}h")

    # Phase 2B: 0/1 Knapsack DP
    t0 = time.perf_counter()
    max_priority, selected_parcels, dp_table = solve_knapsack(sorted_parcels, capacity)
    t_dp = (time.perf_counter() - t0) * 1000

    total_weight = sum(p["weight"] for p in selected_parcels)
    print(f"\n[Phase 2B] Optimal Packing Plan (0/1 Knapsack DP):")
    print(f"  Selected Parcels ({len(selected_parcels)}): {[p['id'] for p in selected_parcels]}")
    print(f"  Total Weight: {total_weight}/{capacity} kg | Max Priority Score: {max_priority}")

    if show_dp_table:
        print("\n  DP Table Preview (First 6 rows, up to capacity 10):")
        for row in dp_table[:6]:
            print("   ", row[:11])

    # Phase 3: Dijkstra + Nearest-Neighbor TSP
    target_nodes = [p["destination"] for p in selected_parcels]
    t0 = time.perf_counter()
    route, total_distance, shortest_paths = plan_delivery_route(graph, depot, target_nodes)
    t_route = (time.perf_counter() - t0) * 1000

    print(f"\n[Phase 3] Delivery Route (Dijkstra + Nearest-Neighbor TSP):")
    print(f"  Shortest Distances from Depot (Node {depot}): {shortest_paths[depot]}")
    print(f"  Optimized Delivery Route: {' -> '.join(map(str, route))}")
    print(f"  Total Route Distance: {total_distance} km")

    print(f"\n[Phase 4] Execution Time Breakdown:")
    print(f"  Merge Sort Time : {t_sort:.4f} ms")
    print(f"  0/1 Knapsack Time: {t_dp:.4f} ms")
    print(f"  Routing Time     : {t_route:.4f} ms")
    print(f"  Total Pipeline   : {(t_sort + t_dp + t_route):.4f} ms")


if __name__ == "__main__":
    run_planner("datasets/small_dataset.json", show_dp_table=True)
    