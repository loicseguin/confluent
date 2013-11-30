# Confluent Flow Algorithm

This is a Python implementation of the confluent flow algorithm described in J.
Chen, R. D. Kleinberg, L. Lovász, R. Rajaraman, R. Sundaram, and A.  Vetta,
"(Almost) Tight Bounds and Existence Theorems for Single-commodity Confluent
Flows," J. ACM, vol. 54, no. 4, Jul. 2007.

## Requirements

To run the confluent flow algorithm, you need NetworkX installed
(http://networkx.github.io). If you also want to use the drawing function for
pyramid graphs, then matplotlib (http://matplotlib.org) is required.

## Example

Create a directed graph and find the confluent flow.

    $ python
    Python 3.3.2 |Anaconda 1.8.0 (x86_64)| (default, Aug  5 2013, 15:07:24) 
    [GCC 4.0.1 (Apple Inc. build 5493)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import confluent
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from([(0, 1, 3), (0, 2, 1), (1, 3, 3), 
    ...                            (2, 6, 3), (3, 10, 3), (3, 7, 1), 
    ...                            (4, 8, 1), (5, 4, 1), (5, 2, 1), 
    ...                            (5, 9, 2), (6, 9, 3), (6, 10, 2), 
    ...                            (7, 10, 2), (8, 't', 2), (9, 't', 5), 
    ...                            (10, 't', 9)], weight='capacity')
    >>> G.node[0]['demand'] = 4 
    >>> G.node[1]['demand'] = 0 
    >>> G.node[2]['demand'] = 1 
    >>> G.node[3]['demand'] = 1 
    >>> G.node[4]['demand'] = 0 
    >>> G.node[5]['demand'] = 4 
    >>> G.node[6]['demand'] = 2 
    >>> G.node[7]['demand'] = 1 
    >>> G.node[8]['demand'] = 1 
    >>> G.node[9]['demand'] = 0 
    >>> G.node[10]['demand'] = 2 
    >>> sinks = confluent.confluent_flow(G, 't')

Use the pyramid graph generator and draw the results.

    >>> import benchmark
    >>> import matplotlib.pyplot as plt
    >>> G, pos = benchmark.pyramid(6)
    >>> nx.draw(G, pos)
    >>> plt.show()
    >>> sinks = confluent.confluent_flow(G, 't')
    >>> benchmark.draw_pyramid_flow(G, pos, sinks)
    >>> plt.show()

