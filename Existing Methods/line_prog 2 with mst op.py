import pulp
import networkx as nx
import pickle

# Load the graph
with open("random_power_graph_50.pkl", "rb") as f:
    G = pickle.load(f)

def lp_node_selection(graph, target_power, alpha=10, beta=1, gamma=0.01):
    operation_count = 0  # Initialize op count

    prob = pulp.LpProblem("CleanPowerSelection", pulp.LpMinimize)

    # Decision variables
    node_vars = {i: pulp.LpVariable(f"x_{i}", cat='Binary') for i in graph.nodes()}
    operation_count += len(node_vars)  # each variable is one operation

    # Objective components
    clean_penalty = pulp.lpSum(node_vars[i] * graph.nodes[i]['clean_score'] for i in graph.nodes())
    operation_count += len(graph.nodes())

    node_count_penalty = pulp.lpSum(node_vars[i] for i in graph.nodes())
    operation_count += len(graph.nodes())

    edge_penalty = pulp.lpSum(
        node_vars[i] * sum(d['weight'] for _, _, d in graph.edges(i, data=True))
        for i in graph.nodes()
    )
    operation_count += sum(len(list(graph.edges(i))) for i in graph.nodes())

    # Full objective
    prob += alpha * clean_penalty + beta * node_count_penalty + gamma * edge_penalty
    operation_count += 1  # full objective assembly

    # Power constraint
    total_power_expr = pulp.lpSum(node_vars[i] * graph.nodes[i]['power_output'] for i in graph.nodes())
    prob += total_power_expr >= target_power, "PowerDemand"
    operation_count += len(graph.nodes())  # power constraint terms

    # Solve LP
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != "Optimal":
        print(" No optimal solution found.")
        return None

    # Collect selected nodes
    selected_nodes = [i for i in graph.nodes() if pulp.value(node_vars[i]) == 1]
    operation_count += len(graph.nodes())  # value checks

    total_power = sum(graph.nodes[i]['power_output'] for i in selected_nodes)
    operation_count += len(selected_nodes)

    # Build MST over selected subgraph
    subgraph = graph.subgraph(selected_nodes)
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))
    operation_count += len(mst.edges()) * 2  # edges processed + weight sum

    # Energy breakdown
    breakdown = {"Solar": 0, "Wind": 0, "Hydro": 0, "Coal": 0}
    for i in selected_nodes:
        breakdown[graph.nodes[i]['energy_source']] += 1
        operation_count += 1

    # Display MST edges
    print("\n MST Edges (LP):")
    for u, v, d in mst.edges(data=True):
        name_u = graph.nodes[u]['name']
        name_v = graph.nodes[v]['name']
        print(f"{name_u} - {name_v} (cost: {d['weight']:.2f})")
        operation_count += 1

    print(f"\n Total MST Cost: {total_cost:.2f}")
    print(f"\nTotal Operation Count: {operation_count}")

    return {
        "Method": "LP Optimization",
        "Total Cost": total_cost,
        "Total Power": total_power,
        "Energy Breakdown": breakdown,
        "Selected Nodes": selected_nodes,
        "MST": mst,
        "OpCount": operation_count
    }

# Run LP optimization and display results
lp_results = lp_node_selection(G, target_power=5000, alpha=10, beta=1, gamma=0.01)

if lp_results:
    print("\n Results for LP-based Clean Selection:")
    print("Total Cost:", lp_results["Total Cost"])
    print("Total Power:", lp_results["Total Power"])
    print("Energy Breakdown:", lp_results["Energy Breakdown"])
    print("Operation Count:", lp_results["OpCount"])
