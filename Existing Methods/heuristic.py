import pickle
import networkx as nx

target_power=8000

# Load the graph
with open("random_power_graph_100.pkl", "rb") as f:
    G = pickle.load(f)

def heuristic_selection(graph, target_power, alpha=1.0, beta=1.0):
    scores = {}
    operation_count = 0  # initialize operation counter

    # Normalize factors
    max_clean = max(graph.nodes[n]['clean_score'] for n in graph.nodes())
    max_edge_sum = max(sum(d['weight'] for _, _, d in graph.edges(n, data=True)) for n in graph.nodes())
    operation_count += len(graph.nodes()) * 2  # max operations

    for n in graph.nodes():
        clean_score = graph.nodes[n]['clean_score'] / max_clean if max_clean else 0
        edge_score = sum(d['weight'] for _, _, d in graph.edges(n, data=True)) / max_edge_sum if max_edge_sum else 0
        scores[n] = alpha * clean_score + beta * edge_score
        operation_count += 1 + len(list(graph.edges(n)))  # 1 for clean, + edge count

    # Sort nodes by heuristic score ascending
    sorted_nodes = sorted(scores.items(), key=lambda x: x[1])
    operation_count += len(sorted_nodes) * int((len(sorted_nodes)).bit_length())  # estimate sorting

    selected_nodes = []
    total_power = 0

    for node_id, _ in sorted_nodes:
        selected_nodes.append(node_id)
        total_power += graph.nodes[node_id]['power_output']
        operation_count += 1
        if total_power >= target_power:
            break

    if total_power < target_power:
        print(" Not enough power available.")
        return None

    # Build MST on selected nodes
    subgraph = graph.subgraph(selected_nodes)
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))
    operation_count += len(subgraph.nodes()) + len(mst.edges()) * 2

    # Energy breakdown
    breakdown = {"Solar": 0, "Wind": 0, "Hydro": 0, "Coal": 0}
    for node in selected_nodes:
        breakdown[graph.nodes[node]['energy_source']] += 1
        operation_count += 1

    # Print results
    print("\nMST Edges (Heuristic Selection):")
    for u, v, d in mst.edges(data=True):
        name_u = graph.nodes[u]['name']
        name_v = graph.nodes[v]['name']
        print(f"{name_u} - {name_v} (cost: {d['weight']:.2f})")
        operation_count += 1

    print(f"\nTotal MST Cost: {total_cost:.2f}")
    print(f"Total Operation Count: {operation_count}")

    return {
        "Selected Nodes": selected_nodes,
        "Total Power": total_power,
        "Total Cost": total_cost,
        "Energy Breakdown": breakdown,
        "MST": mst,
        "OpCount": operation_count
    }

# Example usage
result = heuristic_selection(G, target_power, alpha=1.0, beta=0.0)

if result:
    print("\nResults for Heuristic Selection:")
    print("Total Power:", result["Total Power"])
    print("Total Cost:", result["Total Cost"])
    print("Energy Breakdown:", result["Energy Breakdown"])
    print("Operation Count:", result["OpCount"])
