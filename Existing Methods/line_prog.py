import pulp
import networkx as nx
import pickle

# Load the graph
with open("random_power_graph_50good.pkl", "rb") as f:
    G = pickle.load(f)
import pulp

def lp_node_selection(graph, target_power, alpha=10, beta=1, gamma=0.01):
    prob = pulp.LpProblem("CleanPowerSelection", pulp.LpMinimize)

    # Decision variables for each node
    node_vars = {i: pulp.LpVariable(f"x_{i}", cat='Binary') for i in graph.nodes()}

    # A. Clean score penalty (low = clean)
    clean_penalty = pulp.lpSum(node_vars[i] * graph.nodes[i]['clean_score'] for i in graph.nodes())

    # B. Node count penalty (minimize number of selected nodes)
    node_count_penalty = pulp.lpSum(node_vars[i] for i in graph.nodes())

    # C. Edge weight approximation penalty (sum of adjacent edge weights for selected nodes)
    edge_penalty = pulp.lpSum(
        node_vars[i] * sum(d['weight'] for _, _, d in graph.edges(i, data=True))
        for i in graph.nodes()
    )

    # Full weighted objective
    prob += alpha * clean_penalty + beta * node_count_penalty + gamma * edge_penalty, "MultiObjective"

    # Constraint: Total power output must meet demand
    power_expr = pulp.lpSum(node_vars[i] * graph.nodes[i]['power_output'] for i in graph.nodes())
    prob += power_expr >= target_power, "PowerDemandConstraint"

    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != "Optimal":
        print("❌ No optimal solution found.")
        return None

    # Gather selected nodes
    selected_nodes = [i for i in graph.nodes() if pulp.value(node_vars[i]) == 1]
    total_power = sum(graph.nodes[i]['power_output'] for i in selected_nodes)

    # Build MST on selected subgraph
    subgraph = graph.subgraph(selected_nodes)
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))

    # Clean energy breakdown
    breakdown = {"Solar": 0, "Wind": 0, "Hydro": 0, "Coal": 0}
    for i in selected_nodes:
        breakdown[graph.nodes[i]['energy_source']] += 1

    return {
        "Method": "LP Optimization",
        "Total Cost": total_cost,
        "Total Power": total_power,
        "Energy Breakdown": breakdown,
        "Selected Nodes": selected_nodes,
        "MST": mst
    }

result1 = lp_node_selection(G, target_power=5000, alpha=10, beta=1, gamma=0.01)
result2 = lp_node_selection(G, target_power=5000, alpha=100, beta=1, gamma=0.01)
result3 = lp_node_selection(G, target_power=5000, alpha=1, beta=1, gamma=0.01)

'''
| Weight  | Term            | Meaning                                                     |
| ------- | --------------- | ----------------------------------------------------------- |
| `alpha` | Cleanliness     | Encourages cleaner (renewable) energy sources (low score)   |
| `beta`  | Node count      | Penalizes selecting too many nodes (compact solution)       |
| `gamma` | Edge connection | Penalizes expensive transmission links (total edge weights) |

Interpreting Your Variants
🔹 result1 = lp_node_selection(..., alpha=10, beta=1, gamma=0.01)
Emphasis: Clean energy

Interpretation: "Prioritize cleaner sources, but still keep cost and node count modest"

Result: Favors solar/wind nodes even if they are farther or more numerous.

🔹 result2 = lp_node_selection(..., alpha=100, beta=1, gamma=0.01)
Emphasis: VERY strong clean energy preference

Interpretation: "I want the cleanest solution possible, cost and compactness are secondary"

Result: Could skip dirty but cheap nodes entirely; may include more nodes to meet power.

🔹 result3 = lp_node_selection(..., alpha=1, beta=1, gamma=0.01)
Balanced

Interpretation: "I want a compromise — not too dirty, not too many nodes, not too costly"

Result: Likely most balanced result (often used as baseline or default)
'''



lp_results = lp_node_selection(G, target_power=5000, alpha=1, beta=1, gamma=0.01)
if lp_results:
    print("Results for LP-based Clean Selection:")
    print("Total Cost:", lp_results["Total Cost"])
    print("Total Power:", lp_results["Total Power"])
    print("Energy Breakdown:", lp_results["Energy Breakdown"])