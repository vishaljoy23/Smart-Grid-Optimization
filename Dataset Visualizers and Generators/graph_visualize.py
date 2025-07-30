import networkx as nx
import matplotlib.pyplot as plt
import pickle

# Load the graph
# with open("random_power_graph_50.pkl", "rb") as f:
#    G = pickle.load(f)

with open("selected_power_graph_500.pkl", "rb") as f:
   G = pickle.load(f)

# Use a consistent layout
pos = nx.spring_layout(G, seed=42)

# Node colors based on energy source
color_map = {
    "Solar": "gold",
    "Wind": "lightgreen",
    "Hydro": "skyblue",
    "Coal": "grey"
}
node_colors = [color_map[G.nodes[n]['energy_source']] for n in G.nodes()]

# Node sizes based on power output
node_sizes = [G.nodes[n]['power_output'] * 2 for n in G.nodes()]

# Draw nodes
nx.draw_networkx_nodes(G, pos, 
                       node_color=node_colors, 
                       node_size=node_sizes, 
                       edgecolors='black')

# Draw edges
nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)

# Draw labels (node names)
labels = {n: G.nodes[n]['name'] for n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_size=8)

# Draw edge weights
edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

# Legend
from matplotlib.patches import Patch
legend_handles = [Patch(color=color, label=src) for src, color in color_map.items()]
plt.legend(handles=legend_handles, loc='upper left', title="Energy Source")

# Final touches
plt.title("Power Network Graph")
plt.axis('off')
plt.tight_layout()
plt.show()
