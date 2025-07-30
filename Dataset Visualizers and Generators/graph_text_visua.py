import networkx as nx
import random
import string
import matplotlib.pyplot as plt
import pickle  # Use standard pickle instead of gpickle
with open("random_power_graph_50.pkl", "rb") as f:
    G_loaded = pickle.load(f)

sumpow = 0
print("Node Data:")
for node_id, attributes in G_loaded.nodes(data=True):
    print(f"Node {node_id}: {attributes}")
    sumpow += attributes.get('power_output', 0)  # Use get in case the key is missing


# Example: print edges with weights
i = 0
for u, v, data in G_loaded.edges(data=True):
    i = i + 1
    print(f"Edge No: {i} Edge from {u} to {v} with weight {data['weight']}")


print(f"\nTotal Power Output: {sumpow}")


# # Optional: Draw the graph
# plt.figure(figsize=(12, 8))
# pos = nx.spring_layout(G, seed=42)
# nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue")
# nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
# plt.title("Random Power Graph")
# plt.show()
