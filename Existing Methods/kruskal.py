import pickle
import networkx as nx

# Load the graph
with open("random_power_graph_50good.pkl", "rb") as f:
    G = pickle.load(f)

def kruskal_with_target_power(graph, target_power):
    # Sort nodes by highest power output first
    sorted_nodes = sorted(graph.nodes(data=True), key=lambda x: x[1]['power_output'], reverse=True)

    selected_nodes = []
    current_power = 0

    for node_id, attrs in sorted_nodes:
        selected_nodes.append(node_id)
        current_power += attrs['power_output']
        if current_power >= target_power:
            break

    if current_power < target_power:
        print(" Warning: Could not meet target power with available nodes.")
        return None

    # Create subgraph with selected nodes
    subgraph = graph.subgraph(selected_nodes)

    # Compute MST on the subgraph
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")

    # Calculate total MST cost
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))

    # Clean energy stats
    energy_breakdown = {"Solar": 0, "Wind": 0, "Hydro": 0, "Coal": 0}
    for node in selected_nodes:
        energy_type = graph.nodes[node]['energy_source']
        energy_breakdown[energy_type] += 1

    # Display MST edges
    print("\nMST Edges:")
    for u, v, d in mst.edges(data=True):
        name_u = graph.nodes[u]['name']
        name_v = graph.nodes[v]['name']
        print(f"{name_u} - {name_v} (cost: {d['weight']:.2f})")

    # Display summary
    print(f"\nTotal MST Cost: {total_cost:.2f}")

    return {
        "Selected Nodes": selected_nodes,
        "Total Power": current_power,
        "Total Cost": total_cost,
        "Clean Energy Breakdown": energy_breakdown,
        "MST": mst
    }

# Example: Try for 5000 unit power demand
results = kruskal_with_target_power(G, target_power=5000)

# Print summary
if results:
    print("\nResults for Standard Kruskal-Based Selection:")
    print("Total Power:", results["Total Power"])
    print("Total Cost:", results["Total Cost"])
    print("Energy Breakdown:", results["Clean Energy Breakdown"])
