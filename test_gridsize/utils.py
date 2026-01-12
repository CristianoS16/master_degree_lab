import networkx as nx
import numpy as np

def get_layer_number(node_name):
    return int(node_name.split("_")[0])

def get_edge_name(source, target):
    source_layer = get_layer_number(source)
    target_layer = get_layer_number(target)
    
    if source_layer < target_layer:
        return f"{source_layer}>>{target_layer}"
    return f"{target_layer}>>{source_layer}"

def get_biggest_connected_component(graph: nx.DiGraph) -> nx.DiGraph:
    if nx.is_connected(graph.to_undirected()):
        return graph
    else:
        largest_cc = max(nx.connected_components(graph.to_undirected()), key=len)
        return graph.subgraph(largest_cc).copy()

def get_more_metrics(graph: nx.DiGraph) -> dict:
    graph_cc = get_biggest_connected_component(graph.to_undirected())
    return {
        "num_nodes": graph.number_of_nodes(),
        "num_edges": graph.number_of_edges(),
        "mean_distance": nx.average_shortest_path_length(graph_cc) if graph_cc else float('inf'),
        "diameter": nx.diameter(graph_cc) if graph_cc else float('inf'),
        "density": nx.density(graph),
        "beetweenness_centrality_mean": np.mean(list(nx.betweenness_centrality(graph).values())),
    }