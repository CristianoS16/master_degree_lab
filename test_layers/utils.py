def get_layer_number(node_name):
    return int(node_name.split("_")[0])

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


def get_degree_per_layer(graph):
    degree_per_layer = dict()
    current_graph_degree = graph.degree()
    for node, degree in current_graph_degree:
        layer = get_layer_number(node)
        if layer in degree_per_layer:
            degree_per_layer[layer].append(degree)
        else:
            degree_per_layer[layer] = [degree]
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

def get_metric_function(metric_name=None):
    metric_name_dict = {
        "degree_per_layer": get_degree_per_layer,
        "num_nodes_per_layer": get_num_nodes_per_layer,
        "num_edges_per_layer": get_num_edges_per_layer,
    }
    if metric_name is None:
        return metric_name_dict
    return metric_name_dict.get(metric_name)
    