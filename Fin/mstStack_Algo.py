import pickle
import networkx as nx
from queue import PriorityQueue

# Load the saved graph
with open("random_power_graph_50.pkl", "rb") as f:
    G = pickle.load(f)

demand = 5000

# Global trackers
total_power = 0
operation_count = 0

# Priority source order (cleanest to dirtiest)
priority_sources = ["Solar", "Wind", "Hydro", "Coal"]

# Comparator logic using tuples: (clean_score, -power_output)
def build_priority_queues(graph):
    global operation_count
    queues = {src: PriorityQueue() for src in priority_sources}
    for node_id, attr in graph.nodes(data=True):
        tup = (attr['clean_score'], -attr['power_output'], node_id)
        queues[attr['energy_source']].put(tup)
        operation_count += 1  # one operation per queue insertion
    return queues

# Select nodes to meet demand
def select_nodes(queues, demand, graph):
    global total_power, operation_count
    total_power = 0
    selected = []
    for src in priority_sources:
        q = queues[src]
        while not q.empty() and total_power < demand:
            _, _, node_id = q.get()
            selected.append(node_id)
            total_power += graph.nodes[node_id]['power_output']
            operation_count += 1  # one operation per node selected
        if total_power >= demand:
            break
    return selected

# Build MST using Kruskal's algorithm (via networkx)
def build_mst(graph, selected_nodes):
    global operation_count
    subgraph = graph.subgraph(selected_nodes).copy()
    operation_count += len(subgraph.nodes()) + len(subgraph.edges())  # copying overhead

    for u, v, d in subgraph.edges(data=True):
        d['weight'] += d['weight'] * 0.02
        operation_count += 1  # edge weight adjustment

    mst = nx.minimum_spanning_tree(subgraph, weight='weight')
    operation_count += len(mst.edges())  # edge decisions in MST

    total_cost = sum(d['weight'] for u, v, d in mst.edges(data=True))
    operation_count += len(mst.edges())  # summing costs
    return mst, total_cost

# Display selected node info
def display_selected(graph, selected):
    global operation_count
    print("\nSelected nodes for meeting demand:\n")
    for node in selected:
        attr = graph.nodes[node]
        #print(f"Node: {attr['name']}, Source: {attr['energy_source']}, Power: {attr['power_output']}")
        operation_count += 1

    print(f"\nTotal Selected Power: {total_power}\n")

    breakdown = {'Solar': 0, 'Wind': 0, 'Hydro': 0, 'Coal': 0}
    for node in selected:
        src = graph.nodes[node]['energy_source']
        if src in breakdown:
            breakdown[src] += 1
            operation_count += 1

    print(f"Energy Breakdown: {breakdown}")

# Save selected subgraph to a new pickle file
def save_selected_subgraph(graph, selected_nodes, filename="selected_power_graph_50.pkl"):
    subgraph = graph.subgraph(selected_nodes).copy()
    with open(filename, "wb") as f:
        pickle.dump(subgraph, f)
    print(f"\n Subset graph with {len(subgraph.nodes)} nodes saved to '{filename}'.")

# Main routine
def run_clean_power_selection(demand):
    global operation_count
    operation_count = 0  # Reset counter

    queues = build_priority_queues(G)
    selected = select_nodes(queues, demand, G)
    display_selected(G, selected)

    if total_power < demand:
        print("Insufficient power available to meet demand.")
        return

    save_selected_subgraph(G, selected)

    mst, cost = build_mst(G, selected)
    print("\nMST Edges:")
    for u, v, d in mst.edges(data=True):
        print(f"{G.nodes[u]['name']} - {G.nodes[v]['name']} with cost {d['weight']:.2f}")
        operation_count += 1

    print(f"\nTotal MST Cost: {cost:.2f}")
    print(f"\n Total Operation Count: {operation_count}")

# Run the method
run_clean_power_selection(demand)
