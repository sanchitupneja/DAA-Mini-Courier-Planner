import json
import random
import time
import os
import matplotlib.pyplot as plt
from sorting import merge_sort_parcels
from knapsack import solve_knapsack
from graph_routing import plan_delivery_route


def generate_dataset(num_nodes, num_parcels, capacity, seed=42):
    random.seed(seed)
    graph = {i: [] for i in range(num_nodes)}

    # Create a connected backbone (spanning chain) so every node is reachable
    for i in range(num_nodes - 1):
        w = random.randint(1, 15)
        graph[i].append([i + 1, w])
        graph[i + 1].append([i, w])

    # Add extra random roads
    extra_edges = num_nodes * 2
    for _ in range(extra_edges):
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v and not any(neighbor == v for neighbor, _ in graph[u]):
            w = random.randint(2, 25)
            graph[u].append([v, w])
            graph[v].append([u, w])

    parcels = []
    for idx in range(1, num_parcels + 1):
        parcels.append({
            "id": f"P{idx:04d}",
            "destination": random.randint(1, num_nodes - 1),
            "weight": random.randint(1, 15),
            "priority": random.randint(10, 100),
            "deadline": random.randint(1, 12),
        })

    return {
        "vehicle_capacity": capacity,
        "depot": 0,
        "graph": {str(k): v for k, v in graph.items()},
        "parcels": parcels,
    }


def benchmark_pipeline():
    os.makedirs("Datasets", exist_ok=True)
    os.makedirs("charts", exist_ok=True)

    configs = [
        ("Small (10 parcels, 6 nodes)", "Datasets/small_dataset.json", None),
        ("Medium (100 parcels, 25 nodes)", "Datasets/medium_dataset.json", (25, 100, 60)),
        ("Large (500 parcels, 80 nodes)", "Datasets/large_dataset.json", (80, 500, 150)),
        ("XL (1000 parcels, 150 nodes)", "Datasets/xl_dataset.json", (150, 1000, 250)),
    ]

    labels = []
    sort_times = []
    dp_times = []
    route_times = []

    print(f"{'Dataset':<32} | {'Sort (ms)':<10} | {'DP (ms)':<10} | {'Route (ms)':<10} | {'Distance':<10}")
    print("-" * 82)

    for label, path, gen_params in configs:
        if gen_params is not None:
            data = generate_dataset(*gen_params)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            with open(path, "r") as f:
                data = json.load(f)

        parcels = data["parcels"]
        capacity = data["vehicle_capacity"]
        depot = data["depot"]
        graph = {int(k): v for k, v in data["graph"].items()}

        # 1. Measure Sorting
        t0 = time.perf_counter()
        sorted_parcels = merge_sort_parcels(parcels)
        t_sort = (time.perf_counter() - t0) * 1000

        # 2. Measure 0/1 Knapsack DP
        t0 = time.perf_counter()
        _, selected_parcels, _ = solve_knapsack(sorted_parcels, capacity)
        t_dp = (time.perf_counter() - t0) * 1000

        # 3. Measure Dijkstra + Nearest-Neighbor TSP
        target_nodes = [p["destination"] for p in selected_parcels]
        t0 = time.perf_counter()
        _, total_dist, _ = plan_delivery_route(graph, depot, target_nodes)
        t_route = (time.perf_counter() - t0) * 1000

        labels.append(label.split(" (")[0])
        sort_times.append(t_sort)
        dp_times.append(t_dp)
        route_times.append(t_route)

        print(f"{label:<32} | {t_sort:<10.4f} | {t_dp:<10.4f} | {t_route:<10.4f} | {total_dist:<10}")

    # Plot 1: Line Chart of Algorithmic Runtime Growth
    plt.figure(figsize=(9, 5))
    plt.plot(labels, sort_times, marker="o", linewidth=2, label="Merge Sort O(n log n)")
    plt.plot(labels, dp_times, marker="s", linewidth=2, label="0/1 Knapsack DP O(n * W)")
    plt.plot(labels, route_times, marker="^", linewidth=2, label="Dijkstra + NN TSP")
    plt.title("Mini-Courier Planner: Algorithmic Runtime Comparison")
    plt.xlabel("Dataset Scale")
    plt.ylabel("Execution Time (milliseconds)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("charts/runtime_comparison.png", dpi=300)
    plt.close()

    # Plot 2: Stacked Bar Chart of Pipeline Breakdown
    plt.figure(figsize=(9, 5))
    plt.bar(labels, sort_times, label="Merge Sort")
    plt.bar(labels, dp_times, bottom=sort_times, label="0/1 Knapsack DP")
    bottom_route = [s + d for s, d in zip(sort_times, dp_times)]
    plt.bar(labels, route_times, bottom=bottom_route, label="Dijkstra + NN TSP")
    plt.title("Total Pipeline Execution Time Breakdown")
    plt.xlabel("Dataset Scale")
    plt.ylabel("Cumulative Time (milliseconds)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("charts/pipeline_breakdown.png", dpi=300)
    plt.close()

    print("\nSaved charts to 'charts/runtime_comparison.png' and 'charts/pipeline_breakdown.png'.")


if __name__ == "__main__":
    benchmark_pipeline()