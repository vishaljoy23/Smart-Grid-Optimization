import pulp
import networkx as nx
import pickle
import time

target_power = 8000

# Load the graph
with open("random_power_graph_100.pkl", "rb") as f:
    G = pickle.load(f)

    import re

def estimate_cbc_operations(log_text, op_per_iter=100, op_per_node=2000):
    """
    Estimates internal operations in CBC solver from log text.

    Args:
        log_text (str): The raw text output from the CBC solver.
        op_per_iter (int): Estimated operations per iteration.
        op_per_node (int): Estimated operations per BnB node.

    Returns:
        dict: Parsed metrics and total estimated operations.
    """
    # Try to find iterations and node count
    iter_match = re.search(r"Total iterations:\s+(\d+)", log_text)
    node_match = re.search(r"Total nodes:\s+(\d+)", log_text)

    iterations = int(iter_match.group(1)) if iter_match else 0
    nodes = int(node_match.group(1)) if node_match else 0

    est_ops = (iterations * op_per_iter) + (nodes * op_per_node)

    return {
        "Iterations": iterations,
        "Nodes": nodes,
        "Estimated Operations": est_ops
    }



def lp_node_selection(graph, target_power, alpha=10, beta=1, gamma=0.01):
    operation_count = 0  # Initialize op count

    prob = pulp.LpProblem("CleanPowerSelection", pulp.LpMinimize)

    # Decision variables
    node_vars = {i: pulp.LpVariable(f"x_{i}", cat='Binary') for i in graph.nodes()}
    operation_count += len(node_vars)

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
    operation_count += 1

    # Power constraint
    total_power_expr = pulp.lpSum(node_vars[i] * graph.nodes[i]['power_output'] for i in graph.nodes())
    prob += total_power_expr >= target_power, "PowerDemand"
    operation_count += len(graph.nodes())

    # Solve LP with logging and timing
    start = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=1))  # <- Solver output enabled
    end = time.time()

    if pulp.LpStatus[prob.status] != "Optimal":
        print(" No optimal solution found.")
        return None

    # Collect selected nodes
    selected_nodes = [i for i in graph.nodes() if pulp.value(node_vars[i]) == 1]
    operation_count += len(graph.nodes())

    total_power = sum(graph.nodes[i]['power_output'] for i in selected_nodes)
    operation_count += len(selected_nodes)

    # Build MST over selected subgraph
    subgraph = graph.subgraph(selected_nodes)
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))
    operation_count += len(mst.edges()) * 2

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
        #print(f"{name_u} - {name_v} (cost: {d['weight']:.2f})")
        operation_count += 1

    print(f"\n Total MST Cost: {total_cost:.2f}")
    print(f" Total Operation Count (Python-side): {operation_count}")
    print(f" LP Variables: {len(prob.variables())}")
    print(f" LP Constraints: {len(prob.constraints)}")
    print(f" LP Solver Runtime: {round(end - start, 4)} seconds")

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
lp_results = lp_node_selection(G, target_power, alpha=10, beta=1, gamma=0.01)

# Suppose this is what you copied from the solver log:
cbc_log = """
Presolve eliminated 0 rows and 0 columns
Presolve time = 0.00 sec
Total nodes: 12
Total iterations: 162
Optimal - objective value 120.00
Total time (CPU seconds): 0.01
"""

result = estimate_cbc_operations(cbc_log)
print("Parsed CBC Log Metrics:")
print(f"Iterations: {result['Iterations']}")
print(f"Nodes: {result['Nodes']}")
print(f"Estimated Total Operations: {result['Estimated Operations']}")


if lp_results:
    print("\n Results for LP-based Clean Selection:")
    print("Total Cost:", lp_results["Total Cost"])
    print("Total Power:", lp_results["Total Power"])
    print("Energy Breakdown:", lp_results["Energy Breakdown"])
    print("Operation Count:", lp_results["OpCount"])
