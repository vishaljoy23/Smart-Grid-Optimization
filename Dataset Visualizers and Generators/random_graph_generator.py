import networkx as nx
import random
import string
import matplotlib.pyplot as plt
import pickle  # Use standard pickle instead of gpickle

# Helper function to generate a random name
def random_name(length=3):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

# Energy sources
energy_sources = ["Solar", "Wind", "Coal", "Hydro"]

# Create an empty graph
G = nx.Graph()

node_count = 10000
# Mapping from energy source to clean score
clean_score_map = {
    "Solar": 0,
    "Wind": 1,
    "Hydro": 2,
    "Coal": 3
}

# Step 1: Add 50 nodes with attributes
for i in range(node_count):
    energy_source = random.choice(energy_sources)
    clean_score = clean_score_map[energy_source]  # Assign based on energy source
    
    G.add_node(
        i,
        name=random_name(),
        energy_source=energy_source,
        clean_score=clean_score,
        power_output=random.randint(10, 250)
    )


# Step 2: Add random edges with weights (0 to 100)
edge_prob = 0.1  # 10% chance for any pair to be connected
for i in range(node_count):
    for j in range(i + 1, node_count):
        if random.random() < edge_prob:
            weight = random.randint(0, 100)
            G.add_edge(i, j, weight=weight)

# Step 3: Print graph summary
print("Generated graph with:")
print(f"- {G.number_of_nodes()} nodes")
print(f"- {G.number_of_edges()} edges")

# Step 4: Save the graph using pickle
with open("random_power_graph_10000.pkl", "wb") as f:
    pickle.dump(G, f)

