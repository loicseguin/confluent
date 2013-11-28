# -*- coding: utf-8 -*-
"""
Confluent flow algorithm.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2013 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.

import networkx as nx
from networkx.utils import generate_unique_node


def _compute_support_for_max_flow(G, t, demand='demand', capacity='capacity'):
    """Add a source node to transform the problem into a single source,
    single-commodity flow problem. The source has arcs to all nodes with a
    positive demand and the capacities of these arcs is equal to the demand of
    the node it points to.

    """
    source = generate_unique_node()
    for v, d in G.nodes(data=True):
        if d.get(demand, 0) > 0:
            G.add_edge(source, v, capacity=d[demand])

    # Solve the maximum s-t flow problem.
    flow_value, flow = nx.ford_fulkerson(G, source, t, capacity=capacity)
    G.remove_node(source)

    # Create the support graph for the flow.
    H = nx.DiGraph()
    H.add_weighted_edges_from(
        [(u, v, flow[u][v]) for u, v in G.edges_iter() if flow[u][v] > 0])
    for node in H:
        H.node[node][demand] = G.node[node].get(demand, 0)
    return H


def _aggregate(H, sinks, frontier_nodes, free_nodes, sink_for_color, verbose=False):
    """If a frontier node has all its outgoing edges to a single arborescence,
    the node can be merged into this arborescence.

    """
    for node in frontier_nodes:
        colors = set(H.node[neighbor]['color'] for neighbor in H[node])
        if len(colors) == 1:
            color = colors.pop()
            H.node[node]['color'] = color
            sink = sink_for_color[color]
            sinks[sink]['tree_arcs'].append((node, next(iter(H[node].keys()))))
            frontier_nodes.remove(node)
            free_nodes.remove(node)
            for u in H.predecessors_iter(node):
                if u in free_nodes:
                    frontier_nodes.add(u)
            if verbose:
                print("Aggregated node {} to sink {}".format(node, sink))
            return True
    return False


def _break_sawtooth(H, sinks, frontier_nodes, free_nodes, verbose=False):
    """A sawtooth cycle is composed of a sequence of reverse arcs and forward
    paths.  To break the cycle, find the minimum flow on an arc and reduce the
    flow on forward arcs by this amount, increase the flow on reverse arcs by
    the same amount.

    """
    # Build auxiliary graph
    H_aux = nx.DiGraph()
    for u, v in H.edges():
        if H.node[u]['color'] == -1:
            if H.node[v]['color'] == -1:
                H_aux.add_edge(u, v, reverse=False, true_neigh=v,
                               weight=H[u][v]['weight'])
            else:
                for sink in sinks:
                    if sinks[sink]['color'] == H.node[v]['color']:
                        H_aux.add_edge(u, sink, reverse=False, true_neigh=v,
                                       weight=H[u][v]['weight'])
                        H_aux.add_edge(sink, u, reverse=True, true_neigh=v,
                                       weight=H[u][v]['weight'])
                        break

    # Find a simple cycle of length greater than 2.
    for cycle in nx.simple_cycles(H_aux):
        if len(cycle) > 2:
            break
    else:
        return False

    # Break the cycle.
    cycle_edges = list(zip(cycle, cycle[1:] + cycle[:1]))
    min_flow = min(H_aux[u][v]['weight'] for u, v in cycle_edges)
    for u, v in cycle_edges:
        neigh = H_aux[u][v]['true_neigh']
        if H_aux[u][v]['reverse']:
            H[v][neigh]['weight'] += min_flow
        else:
            H[u][neigh]['weight'] -= min_flow
            if H[u][neigh]['weight'] == 0:
                H.remove_edge(u, neigh)
    if verbose:
        print("Augmented flow by {} on cycle {}".format(min_flow, cycle))
    return True


def _pivot(H, sinks, frontier_nodes, free_nodes, sink_for_color, verbose=False):
    """Find a frontier node that has an arc to a sink tree with no other
    incoming arcs and a arc to another sink tree.  Pivot the flow from one tree
    to the other.  This increases the congestion at one of the sink trees.

    """
    # Find `sink1`, a sink tree with a single predecessor `pivot_node` such that
    # the pivot has at least one outgoing arc to another sink tree.
    for sink1 in sinks:
        tree1_color = sinks[sink1]['color']
        nb_in_neighbors = 0
        arcs_to_tree1 = []
        sink2 = None
        for v in frontier_nodes:
            initial_len = len(arcs_to_tree1)
            sink = None
            for neigh in H[v]:
                neigh_color = H.node[neigh]['color']
                if neigh_color == tree1_color:
                    arcs_to_tree1.append((v, neigh))
                elif neigh_color != -1:
                    sink = sink_for_color[neigh_color]
            if initial_len != len(arcs_to_tree1) and sink:
                nb_in_neighbors += 1
                sink2 = sink
                tree2_color = sinks[sink2]['color']
                arcs_to_tree2 = [(v, u) for u in H[v]
                                 if H.node[u]['color'] == tree2_color]
        if nb_in_neighbors == 1 and sink2:
            break

    pivot_node = arcs_to_tree1[0][0]

    # Do the pivoting between tree 1 and tree 2.
    flow = sum(H[u][v]['weight'] for u, v in arcs_to_tree2)
    if sinks[sink1]['congestion'] + flow < sinks[sink2]['congestion'] - flow:
        H[pivot_node][arcs_to_tree1[0][1]]['weight'] += flow
        for u, v in arcs_to_tree2:
            H.remove_edge(u, v)
        sinks[sink1]['congestion'] += flow
        sinks[sink2]['congestion'] -= flow
        if verbose:
            print("Pivoted {} units of flow from {} to {}".format(
                flow, sink2, sink1))
    else:
        flow = sum(H[u][v]['weight'] for u, v in arcs_to_tree1)
        H[pivot_node][arcs_to_tree2[0][1]]['weight'] += flow
        for u, v in arcs_to_tree1:
            H.remove_edge(u, v)
        sinks[sink2]['congestion'] += flow
        sinks[sink1]['congestion'] -= flow
        if verbose:
            print("Pivoted {} units of flow from {} to {}".format(
                flow, sink, sink2))
            print("Deactivated sink {}".format(sink))

    return True


def confluent_flow(G, t, demand='demand', capacity='capacity', verbose=False):
    """Compute a confluent flow on graph G where nodes have demands destined to
    the single sink `s`.

    """
    H = _compute_support_for_max_flow(G, t, demand=demand, capacity=capacity)

    # Determine the set of nodes with arcs into the sink (call these sinks)
    # and then delete the sink. Set up the data structure to hold the
    # arborescences.  Make a set of nodes that are adjacent to sink nodes, the
    # frontier nodes, and a list of nodes not in an arborescence, the free
    # nodes.  Also, assign a color to every node: -1 if the node is in no
    # arborescence, arborescence color otherwise.
    sinks = {v: {'congestion': H.node[v][demand], 'tree_arcs': []}
             for v in H if t in H[v]}
    frontier_nodes = set()
    for u, v, d in H.edges_iter(data=True):
        if v in sinks:
            sinks[v]['congestion'] += d['weight']
            frontier_nodes.add(u)
    H.remove_node(t)
    free_nodes = set(v for v in H if v not in sinks)
    # For each color, name of corresponding sink.
    sink_for_color = []
    for i, v in enumerate(sinks):
        H.node[v]['color'] = i
        sinks[v]['color'] = i
        sink_for_color.append(v)
    for v in free_nodes:
        H.node[v]['color'] = -1

    # Main loop: aggregate, break sawtooth cycles and pivot.
    while free_nodes:
        (_aggregate(H, sinks, frontier_nodes, free_nodes, sink_for_color, verbose=verbose) or
         _break_sawtooth(H, sinks, frontier_nodes, free_nodes, verbose=verbose) or
         _pivot(H, sinks, frontier_nodes, free_nodes, sink_for_color, verbose=verbose))
    return sinks
