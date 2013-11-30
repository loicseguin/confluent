# -*- coding: utf-8 -*-
"""
Benchmark and utility functions for confluent flow algorithm.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2013 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.

import networkx as nx
import matplotlib.pyplot as plt


def digraph1():
    """Create a simple instance of the confluent flow problem."""
    G = nx.DiGraph()
    G.add_weighted_edges_from([(0, 1, 3), (0, 2, 1), (1, 3, 3),
                               (2, 6, 3), (3, 10, 3), (3, 7, 1),
                               (4, 8, 1), (5, 4, 1), (5, 2, 1),
                               (5, 9, 2), (6, 9, 3), (6, 10, 2),
                               (7, 10, 2), (8, 't', 2), (9, 't', 5),
                               (10, 't', 9)], weight='capacity')
    G.node[0]['demand'] = 4
    G.node[1]['demand'] = 0
    G.node[2]['demand'] = 1
    G.node[3]['demand'] = 1
    G.node[4]['demand'] = 0
    G.node[5]['demand'] = 4
    G.node[6]['demand'] = 2
    G.node[7]['demand'] = 1
    G.node[8]['demand'] = 1
    G.node[9]['demand'] = 0
    G.node[10]['demand'] = 2

    return G


def pyramid(N):
    """Generate a pyramid graph with N layers (excluding the sink at the
    bottom).  Layer i has i nodes, each with demand 1/i. The arc capacities are
    such that the sum of each node's demand and its incoming flow is 1.

    For instance, the arcs between the third and the fourth row are as follows:

        ((2, 0), (3, 0), {'capacity': 3/4})
        ((2, 0), (3, 1), {'capacity': 1/4})
        ((2, 1), (3, 1), {'capacity': 2/4})
        ((2, 1), (3, 2), {'capacity': 2/4})
        ((2, 2), (3, 2), {'capacity': 1/4})
        ((2, 2), (3, 3), {'capacity': 3/4})

    Parameters
    ----------
    N : integer
        Number of layers in the pyramid, excluding the sink 't'.

    Returns
    -------
    G : graph
        The pyramid graph.

    pos : dictionary
        Keyed by nodes, values indicate where in the Cartesian plane the nodes
        should be positioned to obtain a nice drawing of a pyramid.

    Examples
    --------
    >>> import benchmark
    >>> G, pos = benchmark.pyramid(4)
    >>> G.nodes(data=True)[0]
    ((2, 0), {'demand': 0.3333333333333333})
    >>> G.edges(data=True)[3]
    ((0, 0), (1, 0), {'capacity': 0.5})

    To draw the pyramid graph using matplotlib:
    >>> import matplotlib.pyplot as plt
    >>> nx.draw(G, pos=pos)
    >>> plt.show()

    """
    G = nx.DiGraph()

    for i in range(N - 1):
        cap = 1.0 - 1.0 / (i + 2)
        for j in range(i + 1):
            G.add_edge((i, j), (i + 1, j), capacity=cap)
            cap = 1.0 - cap
            G.add_edge((i, j), (i + 1, j + 1), capacity=cap)
            cap = 1.0 - cap - 1.0 / (i + 2)
            G.node[(i, j)]['demand'] = 1.0/(i + 1)

    for j in range(N):
        G.add_edge((N - 1, j), 't')
        G.node[(N - 1, j)]['demand'] = 1.0/N

    pos = dict((node, (node[1] - 0.5 * node[0], -node[0]))
               for node in G if node != 't')
    pos['t'] = (0, -N)

    return G, pos


def draw_pyramid_flow(G, pos, sinks):
    """Make a nice drawing of the confluent flow `sinks` on a pyramid graph G.

    Examples
    --------
    >>> import networkx as nx
    >>> import confluent
    >>> import benchmark
    >>> import matplotlib.pyplot as plt
    >>> G, pos = benchmark.pyramid(5)
    >>> sinks = confluent.confluent_flow(G, 't')
    >>> benchmark.draw_pyramid_flow(G, pos, sinks)
    >>> plt.show()

    """
    nodes = G.nodes()
    labels = dict((node, '1/{}'.format(node[0] + 1)) for node in nodes
                  if node != 't')
    labels[(0, 0)] = '1'
    labels['t'] = 't'

    with_labels = True
    for sink in sinks:
        tree = sinks[sink]['tree_arcs']
        color = sinks[sink]['color']
        nx.draw(G, edgelist=tree, edge_color=[color] * len(tree),
                node_color="#348ABD", pos=pos, width=4, alpha=0.9,
                edge_cmap=plt.get_cmap('jet'), edge_vmin=0.0,
                edge_vmax=len(sinks), arrows=False, nodelist=nodes,
                node_size=600, font_color='w', labels=labels,
                with_labels=with_labels, linewidths=0)
        #nx.draw(G, edgelist=tree, edge_color='0.6', linewidths=0,
                #node_color="#348ABD", pos=pos, width=4, alpha=0.9,
                #arrows=False, nodelist=nodes,
                #node_size=200, font_color='w', labels=labels,
                #with_labels=False)
        nodes = []
        with_labels = False
