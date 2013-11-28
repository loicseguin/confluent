# -*- coding: utf-8 -*-
"""Confluent flow algorithm test suite.

Run with nose: nosetests -v test_confluent.py
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2013 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


import networkx as nx
from nose.tools import *
import confluent


class TestConfluent:
    def test_aggregate(self):
        H = nx.DiGraph()
        H.add_edges_from([(0, 3), (0, 4), (1, 4), (1, 6), (2, 6), (3, 't1'),
                          (4, 't1'), (4, 't2'), (5, 't1'), (5, 6), (6, 't3')])
        for v in H:
            H.node[v]['color'] = -1
        for i in range(3):
            H.node['t%d' % (i + 1)]['color'] = i
        sinks = {'t1': {'color': 0, 'tree_arcs': []},
                 't2': {'color': 1, 'tree_arcs': []},
                 't3': {'color': 2, 'tree_arcs': []}}
        sink_for_color = ['t1', 't2', 't3']
        frontier_nodes = set((3, 4, 5, 6))
        free_nodes = list(range(7))

        while confluent._aggregate(H, sinks, frontier_nodes, free_nodes,
                                   sink_for_color):
            pass
        assert_equal(sinks,
                     {'t1': {'color': 0, 'tree_arcs': [(3, 't1')]},
                      't2': {'color': 1, 'tree_arcs': []},
                      't3': {'color': 2, 'tree_arcs': [(6, 't3'), (2, 6)]}})
        assert_equal(frontier_nodes, set((0, 1, 4, 5)))
        assert_equal(free_nodes, [0, 1, 4, 5])
        assert_equal(H.node[3]['color'], 0)
        assert_equal(H.node[2]['color'], 2)
        assert_equal(H.node[6]['color'], 2)
        for v in free_nodes:
            assert_equal(H.node[v]['color'], -1)

    def test_break_sawtooth(self):
        H = nx.DiGraph()
        H.add_weighted_edges_from([(0, 1, 3), (0, 2, 1), (1, 3, 3), (2, 6, 2),
                                  (3, 10, 3), (3, 7, 1), (4, 8, 1), (5, 4, 1),
                                  (5, 9, 2), (6, 9, 3), (6, 10, 1), (7, 10, 2)])
        for v in H:
            H.node[v]['color'] = -1
        for v in (4, 8):
            H.node[v]['color'] = 1
        H.node[9]['color'] = 2
        for v in (1, 3, 7, 10):
            H.node[v]['color'] = 3
        sinks = {8: {'color': 1, 'tree_arcs': [(4, 8)]},
                 9: {'color': 2, 'tree_arcs': []},
                 10: {'color': 3,
                      'tree_arcs': [(1, 3), (3, 7), (3, 10), (7, 10)]}}
        frontier_nodes = set((0, 2, 5, 6))
        free_nodes = [0, 2, 5, 6]
        res = confluent._break_sawtooth(H, sinks, frontier_nodes, free_nodes)
        assert_true(res)
        assert_equal(sorted(H.edges(data=True)),
                     sorted([(0, 1, {'weight': 4}),
                             (1, 3, {'weight': 3}), (2, 6, {'weight': 1}),
                             (3, 10, {'weight': 3}), (3, 7, {'weight': 1}),
                             (4, 8, {'weight': 1}), (5, 4, {'weight': 1}),
                             (5, 9, {'weight': 2}), (6, 9, {'weight': 3}),
                             (7, 10, {'weight': 2})]))

    def test_break_two_sawtooth(self):
        H = nx.DiGraph()
        H.add_weighted_edges_from([(0, 1, 3), (0, 2, 1), (1, 3, 3), (2, 6, 3),
                                   (3, 10, 3), (3, 7, 1), (4, 8, 1), (5, 4, 1),
                                   (5, 2, 1), (5, 9, 2), (6, 9, 3), (6, 10, 2),
                                   (7, 10, 2)])
        for v in H:
            H.node[v]['color'] = -1
        for v in (4, 8):
            H.node[v]['color'] = 1
        H.node[9]['color'] = 2
        for v in (1, 3, 7, 10):
            H.node[v]['color'] = 3
        sinks = {8: {'color': 1, 'tree_arcs': [(4, 8)]},
                 9: {'color': 2, 'tree_arcs': []},
                 10: {'color': 3,
                      'tree_arcs': [(1, 3), (3, 7), (3, 10), (7, 10)]}}
        frontier_nodes = set((0, 2, 5, 6))
        free_nodes = [0, 2, 5, 6]
        while confluent._break_sawtooth(H, sinks, frontier_nodes, free_nodes):
            pass
        assert_equal(sorted(H.edges(data=True)),
                     sorted([(0, 1, {'weight': 4}),
                             (1, 3, {'weight': 3}), (2, 6, {'weight': 1}),
                             (3, 10, {'weight': 3}), (3, 7, {'weight': 1}),
                             (4, 8, {'weight': 1}), (5, 4, {'weight': 1}),
                             (5, 9, {'weight': 3}), (6, 9, {'weight': 2}),
                             (6, 10, {'weight': 1}), (7, 10, {'weight': 2})]))

    def test_pivot(self):
        H = nx.DiGraph()
        H.add_weighted_edges_from([
            (0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (0, 5, 1),
            (1, 3, 1), (2, 4, 2), (3, 5, 3), (6, 7, 1), (6, 8, 1),
            (9, 7, 1), (9, 8, 1)])
        for v in H:
            H.node[v]['color'] = -1
        H.node[2]['color'] = 0
        H.node[4]['color'] = 0
        H.node[1]['color'] = 1
        H.node[3]['color'] = 1
        H.node[5]['color'] = 1
        H.node[7]['color'] = 2
        H.node[8]['color'] = 3
        sinks = {4: {'color': 0, 'tree_arcs': [(2, 4)], 'congestion': 3},
                 5: {'color': 1,
                     'tree_arcs': [(1, 3), (3, 5)], 'congestion': 4},
                 7: {'color': 2, 'tree_arcs': [], 'congestion': 1},
                 8: {'color': 3, 'tree_arcs': [], 'congestion': 0}}
        frontier_nodes = set((0, 6, 9))
        free_nodes = [0, 6, 9]
        sink_for_color = [4, 5, 7, 8]
        res = confluent._pivot(H, sinks, frontier_nodes, free_nodes,
                               sink_for_color)
        assert_true(res)
        assert_equal(sorted(H.edges(data=True)),
                     sorted([(0, 1, {'weight': 3}), (0, 3, {'weight': 1}),
                             (0, 5, {'weight': 1}), (1, 3, {'weight': 1}),
                             (2, 4, {'weight': 2}), (3, 5, {'weight': 3}),
                             (6, 7, {'weight': 1}), (6, 8, {'weight': 1}),
                             (9, 7, {'weight': 1}), (9, 8, {'weight': 1})]))
        assert_equal(sinks,
                     {4: {'color': 0, 'tree_arcs': [(2, 4)], 'congestion': 1},
                      5: {'color': 1,
                          'tree_arcs': [(1, 3), (3, 5)], 'congestion': 6},
                      7: {'color': 2, 'tree_arcs': [], 'congestion': 1},
                      8: {'color': 3, 'tree_arcs': [], 'congestion': 0}})

    def test_pivot2(self):
        H = nx.DiGraph()
        H.add_weighted_edges_from([
            (0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (0, 5, 1),
            (1, 3, 1), (2, 4, 2), (3, 5, 3), (6, 7, 1), (6, 8, 1),
            (9, 7, 1), (9, 8, 1)])
        for v in H:
            H.node[v]['color'] = -1
        H.node[2]['color'] = 0
        H.node[4]['color'] = 0
        H.node[1]['color'] = 1
        H.node[3]['color'] = 1
        H.node[5]['color'] = 1
        H.node[7]['color'] = 2
        H.node[8]['color'] = 3
        sinks = {4: {'color': 0, 'tree_arcs': [(2, 4)], 'congestion': 3},
                 5: {'color': 1,
                     'tree_arcs': [(1, 3), (3, 5)], 'congestion': 11},
                 7: {'color': 2, 'tree_arcs': [], 'congestion': 1},
                 8: {'color': 3, 'tree_arcs': [], 'congestion': 0}}
        frontier_nodes = set((0, 6, 9))
        free_nodes = [0, 6, 9]
        sink_for_color = [4, 5, 7, 8]
        res = confluent._pivot(H, sinks, frontier_nodes, free_nodes,
                               sink_for_color)
        assert_true(res)
        assert_equal(sorted(H.edges(data=True)),
                     sorted([(0, 2, {'weight': 4}), (0, 4, {'weight': 1}),
                             (1, 3, {'weight': 1}),
                             (2, 4, {'weight': 2}), (3, 5, {'weight': 3}),
                             (6, 7, {'weight': 1}), (6, 8, {'weight': 1}),
                             (9, 7, {'weight': 1}), (9, 8, {'weight': 1})]))
        assert_equal(sinks,
                     {4: {'color': 0, 'tree_arcs': [(2, 4)], 'congestion': 6},
                      5: {'color': 1,
                          'tree_arcs': [(1, 3), (3, 5)], 'congestion': 8},
                      7: {'color': 2, 'tree_arcs': [], 'congestion': 1},
                      8: {'color': 3, 'tree_arcs': [], 'congestion': 0}})

    def test_confluent(self):
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

        sinks = confluent.confluent_flow(G, 't')
        assert_equal(sinks[8]['congestion'], 1)
        assert_equal(sorted(sinks[8]['tree_arcs']), [(4, 8)])
        assert_equal(sinks[9]['congestion'], 7)
        assert_equal(sorted(sinks[9]['tree_arcs']),
                     [(2, 6), (5, 9), (6, 9)])
        assert_equal(sinks[10]['congestion'], 8)
        assert_equal(sorted(sinks[10]['tree_arcs']),
                     [(0, 1), (1, 3), (3, 10), (7, 10)])
