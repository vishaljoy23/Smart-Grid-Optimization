import pickle
import networkx as nx

target_power = 8000
# Load the graph
with open("random_power_graph_100.pkl", "rb") as f:
    G = pickle.load(f)

def greedy_load_dispatch(graph, target_power):
    operation_count = 0  # Track operations

    # Sort nodes by descending power output
    sorted_nodes = sorted(graph.nodes(data=True), key=lambda x: x[1]['power_output'], reverse=True)
    operation_count += len(sorted_nodes) * int((len(sorted_nodes)).bit_length())  # rough estimate for sorting

    selected_nodes = []
    current_power = 0

    for node_id, attrs in sorted_nodes:
        selected_nodes.append(node_id)
        current_power += attrs['power_output']
        operation_count += 1  # node selection step
        if current_power >= target_power:
            break

    if current_power < target_power:
        print(
            " Warning: Could not meet target power with available nodes.")
        return None

    # Create subgraph with selected nodes
    subgraph = graph.subgraph(selected_nodes)
    operation_count += len(subgraph.nodes()) + len(subgraph.edges())  # subgraph overhead

    # Compute MST
    mst = nx.minimum_spanning_tree(subgraph, algorithm="kruskal", weight="weight")
    operation_count += len(mst.edges())  # MST edge processing

    # Sum MST weights
    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))
    operation_count += len(mst.edges())  # cost summation

    # Energy breakdown
    energy_breakdown = {"Solar": 0, "Wind": 0, "Hydro": 0, "Coal": 0}
    for node in selected_nodes:
        energy_type = graph.nodes[node]['energy_source']
        energy_breakdown[energy_type] += 1
        operation_count += 1  # breakdown update

    # Display MST edges
    print("\n MST Edges (Greedy Load Dispatch):")
    for u, v, d in mst.edges(data=True):
        name_u = graph.nodes[u]['name']
        name_v = graph.nodes[v]['name']
        print(f"{name_u} - {name_v} (cost: {d['weight']:.2f})")
        operation_count += 1

    print(f"\n Total MST Cost: {total_cost:.2f}")
    print(f" Total Operation Count: {operation_count}")

    return {
        "Selected Nodes": selected_nodes,
        "Total Power": current_power,
        "Total Cost": total_cost,
        "Energy Breakdown": energy_breakdown,
        "MST": mst,
        "OpCount": operation_count
    }

# Example usage
greedy_results = greedy_load_dispatch(G, target_power)

# Print the results
if greedy_results:
    print("\n Results for Greedy Load Dispatch (target = {target_power} units):")
    print("Total Cost:", greedy_results["Total Cost"])
    print("Total Power:", greedy_results["Total Power"])
    print("Energy Breakdown:", greedy_results["Energy Breakdown"])
    print("Operation Count:", greedy_results["OpCount"])
