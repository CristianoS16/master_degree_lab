from functools import partial
import numpy as np
import networkx as nx


def get_layer_number(node_name):
    return int(node_name.split("_")[0])


# Each cell represents an activation region, in the format hiddenstate_x_y
def get_x_coord(node_name):
    return int(node_name.split("_")[1])


def get_y_coord(node_name):
    return int(node_name.split("_")[2])


def get_edge_name(source, target):
    source_layer = get_layer_number(source)
    target_layer = get_layer_number(target)

    if source_layer < target_layer:
        return f"{source_layer}>>{target_layer}"
    return f"{target_layer}>>{source_layer}"


def merge_data_from_dicts(d1, d2):
    all_keys = d1.keys() | d2.keys()

    d2_value_type = type(list(d2.values())[0])
    if d2_value_type is list:
        return {k: [*d1.get(k, []), *d2.get(k, [])] for k in all_keys}

    return {k: [*d1.get(k, []), d2.get(k, 0)] for k in all_keys}


def get_degree_per_layer(graph, return_mean=True):
    degree_per_layer = dict()
    current_graph_degree = graph.degree()
    for node, degree in current_graph_degree:
        layer = get_layer_number(node)
        if layer in degree_per_layer:
            degree_per_layer[layer].append(degree)
        else:
            degree_per_layer[layer] = [degree]
    if return_mean:
        degree_per_layer = {k: np.mean(v) for k, v in degree_per_layer.items()}
    return degree_per_layer


def get_num_nodes_per_layer(graph):
    nodes_per_layer = dict()
    for node in graph.nodes():
        layer = get_layer_number(node)
        if layer in nodes_per_layer:
            nodes_per_layer[layer] += 1
        else:
            nodes_per_layer[layer] = 1
    return nodes_per_layer


def get_num_edges_per_layer(graph):
    edges_per_layer = dict()
    for source, target in graph.edges():
        edge_name = get_edge_name(source, target)
        if edge_name in edges_per_layer:
            edges_per_layer[edge_name] += 1
        else:
            edges_per_layer[edge_name] = 1
    return edges_per_layer


def get_node_betweenness_per_layer(graph, normalized=True, return_mean=True):
    betweenness_per_layer = dict()

    general_betweenness = nx.betweenness_centrality(graph, normalized=normalized)
    for node, betweenness in general_betweenness.items():
        layer = get_layer_number(node)
        if layer in betweenness_per_layer:
            betweenness_per_layer[layer].append(betweenness)
        else:
            betweenness_per_layer[layer] = [betweenness]

    if return_mean:
        betweenness_per_layer = {
            k: np.mean(v) for k, v in betweenness_per_layer.items()
        }
    return betweenness_per_layer


def get_edge_betweenness_per_layer(graph, normalized=True, return_mean=True):
    betweenness_per_layer = dict()

    general_betweenness = nx.edge_betweenness_centrality(graph, normalized=normalized)
    for (source, target), betweenness in general_betweenness.items():
        layer = get_edge_name(source, target)
        if layer in betweenness_per_layer:
            betweenness_per_layer[layer].append(betweenness)
        else:
            betweenness_per_layer[layer] = [betweenness]

    if return_mean:
        betweenness_per_layer = {
            k: np.mean(v) for k, v in betweenness_per_layer.items()
        }
    return betweenness_per_layer


def get_node_strength_per_layer(graph, return_mean=True):
    strength_per_layer = dict()

    general_strength = graph.degree(weight="weight")
    for node, strength in general_strength:
        layer = get_layer_number(node)
        if layer in strength_per_layer:
            strength_per_layer[layer].append(strength)
        else:
            strength_per_layer[layer] = [strength]

    if return_mean:
        strength_per_layer = {k: np.mean(v) for k, v in strength_per_layer.items()}
    return strength_per_layer


def get_assortativity_per_layer(graph, return_mean=True):
    pass


def get_average_neighbor_degree_per_layer(graph, return_mean=True):
    avg_neighbor_degree_per_layer = dict()

    general_avg_neighbor_degree = nx.average_neighbor_degree(graph, weight="weight")
    for node, avg_neighbor_degree in general_avg_neighbor_degree.items():
        layer = get_layer_number(node)
        if layer in avg_neighbor_degree_per_layer:
            avg_neighbor_degree_per_layer[layer].append(avg_neighbor_degree)
        else:
            avg_neighbor_degree_per_layer[layer] = [avg_neighbor_degree]

    if return_mean:
        avg_neighbor_degree_per_layer = {
            k: np.mean(v) for k, v in avg_neighbor_degree_per_layer.items()
        }
    return avg_neighbor_degree_per_layer


# https://www.notion.so/Centro-de-Massa-por-Camada-31ab046f0c2080998336d06c6f9f4d2c?source=copy_link
def get_center_of_mass_per_layer(graph, axl):
    # Formato: {camada: {"soma_massa_posicao": 0.0, "soma_massa": 0.0}}
    layer_accumulators = dict()

    # Seleciona a função correta de coordenadas com base no eixo ('x' ou 'y')
    pos_func = {"x": get_x_coord, "y": get_y_coord}[axl]

    general_strength = graph.degree(weight="weight")
    for node, strength in general_strength:
        pos = pos_func(node)
        layer = get_layer_number(node)

        if layer not in layer_accumulators:
            layer_accumulators[layer] = {"sum_mass_pos": 0.0, "sum_mass": 0.0}
        layer_accumulators[layer]["sum_mass_pos"] += strength * pos
        layer_accumulators[layer]["sum_mass"] += strength

    center_of_mass_per_layer = dict()

    for layer, data in layer_accumulators.items():
        if data["sum_mass"] > 0:
            cm = data["sum_mass_pos"] / data["sum_mass"]
        else:
            cm = 0.0

        center_of_mass_per_layer[layer] = cm

    return center_of_mass_per_layer


def get_metric_function(metric_name=None):
    metric_name_dict = {
        "degree_per_layer": get_degree_per_layer,
        "num_nodes_per_layer": get_num_nodes_per_layer,
        "num_edges_per_layer": get_num_edges_per_layer,
        "node_betweenness_per_layer": get_node_betweenness_per_layer,
        "edge_betweenness_per_layer": get_edge_betweenness_per_layer,
        "node_strength_per_layer": get_node_strength_per_layer,
        # TODO: implementar a assortatividade de duas a duas camadas
        # "assortativity_per_layer": get_assortativity_per_layer,
        "average_neighbor_degree": get_average_neighbor_degree_per_layer,
        "center_of_mass_x": partial(get_center_of_mass_per_layer, axl="x"),
        "center_of_mass_y": partial(get_center_of_mass_per_layer, axl="y"),
    }
    if metric_name is None:
        return metric_name_dict
    return metric_name_dict.get(metric_name)
