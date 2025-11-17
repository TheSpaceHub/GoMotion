import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import barri_adj_csv
import barri_manager

gdf = barri_manager.load_gdf()

if not os.path.exists("./data/barris_edges.csv"):
    # if the edges do not exist, create them
    barri_adj_csv.create_edge_csv(gdf)

adj_csv = pd.read_csv("data/barris_edges.csv")
graph = nx.Graph()

# add nodes
for barri in adj_csv["barri_a"].unique():
    graph.add_node(barri)

# add edges
for _, row in adj_csv.iterrows():
    graph.add_edge(row["barri_a"], row["barri_b"], weight=row["dist"])

#save
nx.write_gexf(graph, "data/graph.gexf")

# draw

if not os.path.exists("./data/barris_nodes.csv"):
    # if the nodes do not exist, create them
    barri_adj_csv.create_node_csv(gdf) 
    
node_df = pd.read_csv("data/barris_nodes.csv")
nx.draw(graph, pos={x["barri"]: (x["x"], x["y"]) for _, x in node_df.iterrows()})
plt.show()
