#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <algorithm>

using namespace std;
int total_power = 0;

// Node structure
struct Node {
    string name;
    string energy_source; // Solar, Wind, Coal, etc.
    int clean_score;       // Lower is better (0 = solar, 5 = coal, etc.)
    int power_output;      // Available power in units
    Node(string n, string e, int c, int p) : name(n), energy_source(e), clean_score(c), power_output(p) {}
    
};

// Edge structure
struct Edge {
    int u, v;
    double weight; // cost of connecting u and v
};


// Disjoint set union aka union-find Kruskal
struct DSU {
    vector<int> parent, rank;
    
    DSU(int n) {
        parent.resize(n);
        rank.resize(n, 0);
        for (int i = 0; i < n; ++i) parent[i] = i;
    }
    
    int find(int x) {
        if (parent[x] != x) 
            parent[x] = find(parent[x]);
        return parent[x];
    }
    
    bool unite(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX == rootY) return false;
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        return true;
    }
};


// Graph class
class Graph {
public:
    vector<Node> nodes;
    vector<Edge> edges;
    
    void addEdge(int u, int v, double weight) {
        edges.push_back({u, v, weight});
    }
};

// Comparator for priority queue
struct CompareNodes {
    bool operator()(const Node& a, const Node& b) {
        if (a.clean_score == b.clean_score)
            return a.power_output < b.power_output; 
        return a.clean_score > b.clean_score; 
    }
};

// Priority queues for each energy source
unordered_map<string, priority_queue<Node, vector<Node>, CompareNodes>> stacks;

// Function to populate the stacks
void populateStacks(Graph& g) {
    for (auto& node : g.nodes) {
        stacks[node.energy_source].push(node);
    }
}

// Function to select nodes to meet power demand using priority_queue
vector<Node> selectNodes(unordered_map<string, priority_queue<Node, vector<Node>, CompareNodes>>& stacks, int power_demand) {
    vector<Node> selected;

    vector<string> priority = {"Solar", "Wind", "Hydro", "Coal"}; 

    for (auto& source : priority) {
        while (!stacks[source].empty() && total_power < power_demand) {
            Node node = stacks[source].top(); 
            stacks[source].pop();
            selected.push_back(node);
            total_power += node.power_output;
        }
        if (total_power >= power_demand) break;
    }

    return selected;
}



// display the stacks
void displayStacks() {
    for (auto& pair : stacks) {
        cout << "Energy Source: " << pair.first << endl;
        auto copy = pair.second;
        while (!copy.empty()) {
            Node n = copy.top();
            cout << "  Node: " << n.name << ", Clean Score: " << n.clean_score << ", Power Output: " << n.power_output << endl;
            copy.pop();
        }
        cout << endl;
    }
}

// Function to build MST from selected nodes
void buildMST(Graph& g, vector<Node>& selected_nodes) {
    // Map node name to its index in selected_nodes
    unordered_map<string, int> selected_index;
    for (int i = 0; i < selected_nodes.size(); ++i) {
        selected_index[selected_nodes[i].name] = i;
    }

    vector<Edge> candidate_edges;

    // Only keep edges between selected nodes
    for (auto& edge : g.edges) {
        string u_name = g.nodes[edge.u].name;
        string v_name = g.nodes[edge.v].name;
        if (selected_index.count(u_name) && selected_index.count(v_name)) {
            // Remap u and v to the index inside selected_nodes
            double effective_weight = edge.weight;
            double loss_factor = 0.02;
            effective_weight += (edge.weight * loss_factor);
            candidate_edges.push_back({selected_index[u_name], selected_index[v_name], effective_weight});
        }
    }

    // Sort edges by weight
    sort(candidate_edges.begin(), candidate_edges.end(), [](Edge& a, Edge& b) {
        return a.weight < b.weight;
    });

    // Build MST using Kruskal
    DSU dsu(selected_nodes.size());
    int total_cost = 0;
    cout << "\nMST Edges:\n";
    for (auto& edge : candidate_edges) {
        if (dsu.unite(edge.u, edge.v)) {
            cout << selected_nodes[edge.u].name << " - " << selected_nodes[edge.v].name 
                 << " with cost " << edge.weight << endl;
            total_cost += edge.weight;
        }
    }
    cout << "\nTotal MST Cost: " << total_cost << endl;
}


// Main
int main() {
    Graph g;
    
    // Add nodes 11 nodes (id, energy_source, clean_score, power_output)
    g.nodes.push_back(Node("A", "Solar", 0, 40));
    g.nodes.push_back(Node("B", "Wind", 1, 80));
    g.nodes.push_back(Node("C", "Coal", 5, 150));
    g.nodes.push_back(Node("D", "Solar", 0, 90));
    g.nodes.push_back(Node("E", "Wind", 1, 120));
    g.nodes.push_back(Node("F", "Coal", 5, 200));
    g.nodes.push_back(Node("G", "Solar", 0, 80));
    g.nodes.push_back(Node("H", "Wind", 1, 15));
    g.nodes.push_back(Node("I", "Wind", 1, 30));
    g.nodes.push_back(Node("J", "Wind", 1, 50));
    g.nodes.push_back(Node("K", "Coal", 5, 20));
    

    
    
    // Adding edges (u, v, weight)
    g.addEdge(0, 1, 10);
    g.addEdge(1, 2, 20);
    g.addEdge(0, 3, 15);
    g.addEdge(3, 2, 25);
    g.addEdge(1, 5, 25);
    g.addEdge(4, 7, 25);
    g.addEdge(2, 10, 35);
    g.addEdge(1, 4, 55);
    g.addEdge(2, 8, 25);
    g.addEdge(10, 9, 25);
    g.addEdge(2, 5, 25);

    // Build stacks
    populateStacks(g);

    // Power demand
    int required_power;
    cout << "Enter required power: ";
    cin >> required_power;

    auto selected_nodes = selectNodes(stacks, required_power);

    cout << "Selected nodes for meeting demand:\n\n";
    for (auto& node : selected_nodes) {
        cout << "Node ID: " << node.name
             << ", Source: " << node.energy_source 
             << ", Power: " << node.power_output << endl;
    }

    cout << "\nRequired Power: " << required_power << endl;
    if(required_power > total_power){
        cout << "The grid currently does not have enough power! :(" << endl;
    }

    else{ cout << "Total Power: " << total_power << endl; }

    // Build MST
    buildMST(g, selected_nodes);


    return 0;
}