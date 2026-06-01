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


def get_eigenvector_centrality_per_layer(graph, return_mean=True, max_iter=100):
    """Retorna centralidade de autovetor por camada.

    Um nó de um conjunto ganhará alta pontuação se estiver conectado a nós
    muito importantes dos outros conjuntos.
    """
    eigenvector_per_layer = dict()

    try:
        general_eigenvector = nx.eigenvector_centrality(graph, max_iter=max_iter)
    except nx.NetworkXError:
        # Se o grafo não converger, retorna zeros
        general_eigenvector = {node: 0.0 for node in graph.nodes()}

    for node, eigenvector in general_eigenvector.items():
        layer = get_layer_number(node)
        if layer in eigenvector_per_layer:
            eigenvector_per_layer[layer].append(eigenvector)
        else:
            eigenvector_per_layer[layer] = [eigenvector]

    if return_mean:
        eigenvector_per_layer = {
            k: np.mean(v) for k, v in eigenvector_per_layer.items()
        }
    return eigenvector_per_layer


def get_eccentricity_per_layer(graph, return_mean=True):
    """Retorna excentricidade (distância máxima) por camada.

    A distância máxima para alcançar qualquer outro nó, ajudando a encontrar
    nós periféricos vs. centrais.
    """
    eccentricity_per_layer = dict()

    # Apenas para grafos conexos, pega a maior componente
    if not nx.is_connected(graph):
        largest_cc = max(nx.connected_components(graph), key=len)
        subgraph = graph.subgraph(largest_cc)
    else:
        subgraph = graph

    general_eccentricity = nx.eccentricity(subgraph)

    for node, eccentricity in general_eccentricity.items():
        layer = get_layer_number(node)
        if layer in eccentricity_per_layer:
            eccentricity_per_layer[layer].append(eccentricity)
        else:
            eccentricity_per_layer[layer] = [eccentricity]

    if return_mean:
        eccentricity_per_layer = {
            k: np.mean(v) for k, v in eccentricity_per_layer.items()
        }
    return eccentricity_per_layer


def get_kcore_per_layer(graph, return_mean=True):
    """Retorna coreness (k-core decomposition) por camada.

    O processo de remoção iterativa por grau, ajudando a encontrar o núcleo
    central da rede k-partida.
    """
    kcore_per_layer = dict()

    kcore_decomposition = nx.core_number(graph)

    for node, coreness in kcore_decomposition.items():
        layer = get_layer_number(node)
        if layer in kcore_per_layer:
            kcore_per_layer[layer].append(coreness)
        else:
            kcore_per_layer[layer] = [coreness]

    if return_mean:
        kcore_per_layer = {k: np.mean(v) for k, v in kcore_per_layer.items()}
    return kcore_per_layer


# ============================================================================
# MÉTRICAS LOCAIS (POR NÓ)
# ============================================================================


def get_degree_local(graph):
    """Retorna grau de cada nó como dicionário {node: degree}"""
    return dict(graph.degree())


def get_node_betweenness_local(graph, normalized=True):
    """Retorna betweenness centrality de cada nó"""
    return nx.betweenness_centrality(graph, normalized=normalized)


def get_edge_betweenness_local(graph, normalized=True):
    """Retorna betweenness centrality de cada aresta"""
    return nx.edge_betweenness_centrality(graph, normalized=normalized)


def get_node_strength_local(graph):
    """Retorna força (grau ponderado) de cada nó"""
    strength_dict = {}
    for node, strength in graph.degree(weight="weight"):
        strength_dict[node] = strength
    return strength_dict


def get_average_neighbor_degree_local(graph):
    """Retorna grau médio dos vizinhos para cada nó"""
    return nx.average_neighbor_degree(graph, weight="weight")


def get_clustering_coefficient_local(graph):
    """Retorna coeficiente de clustering para cada nó"""
    return nx.clustering(graph, weight="weight")


def get_eigenvector_centrality_local(graph, max_iter=100):
    """Retorna centralidade de autovetor para cada nó"""
    try:
        return nx.eigenvector_centrality(graph, max_iter=max_iter)
    except nx.NetworkXError:
        # Se não convergir, retorna zeros
        return {node: 0.0 for node in graph.nodes()}


def get_eccentricity_local(graph):
    """Retorna excentricidade (distância máxima) para cada nó"""
    # Apenas para grafos conexos, pega a maior componente
    if not nx.is_connected(graph):
        largest_cc = max(nx.connected_components(graph), key=len)
        subgraph = graph.subgraph(largest_cc)
    else:
        subgraph = graph

    return nx.eccentricity(subgraph)


def get_kcore_local(graph):
    """Retorna coreness (k-core) para cada nó"""
    return nx.core_number(graph)


# ============================================================================
# FUNÇÃO DE REGISTRO DE MÉTRICAS
# ============================================================================


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
        "eigenvector_centrality_per_layer": get_eigenvector_centrality_per_layer,
        "eccentricity_per_layer": get_eccentricity_per_layer,
        "kcore_per_layer": get_kcore_per_layer,
    }
    if metric_name is None:
        return metric_name_dict
    return metric_name_dict.get(metric_name)


def get_node_metric_function(metric_name=None):
    """Retorna funções que calculam métricas locais (por nó)"""
    metric_name_dict = {
        "degree": get_degree_local,
        "node_betweenness": get_node_betweenness_local,
        "node_strength": get_node_strength_local,
        "average_neighbor_degree": get_average_neighbor_degree_local,
        # "clustering_coefficient": get_clustering_coefficient_local,
        "eigenvector_centrality": get_eigenvector_centrality_local,
        "eccentricity": get_eccentricity_local,
        "kcore": get_kcore_local,
    }
    if metric_name is None:
        return metric_name_dict
    return metric_name_dict.get(metric_name)
