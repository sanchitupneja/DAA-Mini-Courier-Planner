def solve_knapsack(parcels, capacity):
    """
    0/1 Knapsack Dynamic Programming in O(n * W) time and space.
    Maximizes total priority score within vehicle weight capacity.
    Returns: max_priority, selected_parcels, dp_table
    """
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w_i = parcels[i - 1]["weight"]
        v_i = parcels[i - 1]["priority"]
        for w in range(capacity + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], v_i + dp[i - 1][w - w_i])
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find selected parcels
    selected_parcels = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_parcels.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]

    selected_parcels.reverse()
    return dp[n][capacity], selected_parcels, dp
