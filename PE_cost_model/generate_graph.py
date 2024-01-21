import graph_tool.all as gt
import matplotlib.pyplot as plt

# Create a random graph
g = gt.random_graph(32, lambda: (3,3))

# Rewire the graph using the RMAT algorithm
gt.random_rewire(g, model="rmat")

# Draw the graph
gt.graph_draw(g, output="rmat_graph.png")

# Output the edge list to a file
with open("edge_list.txt", "w") as f:
    for edge in g.edges():
        f.write(f"{edge.source()} {edge.target()}\n")

# Optionally, if you want to print the edge list to the console:
for edge in g.edges():
    print(edge.source(), edge.target())
