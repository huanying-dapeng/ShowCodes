#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/22 23:38
# @Author  : zhipeng.zhao
# @File    : go_plot.py

import re
import sys
from collections import OrderedDict

import pydot

from core.go.obo_parser import GODag, GraphEngines
from core.common.get_params_data import GOPlotParams


class Color(object):
    rel2col = {
        'is_a': 'black',
        'part_of': 'blue',
        'regulates': 'gold',
        'positively_regulates': 'green',
        'negatively_regulates': 'red',
        'occurs_in': 'aquamarine4',
        'capable_of': 'dodgerblue',
        'capable_of_part_of': 'darkorange',
    }

    alpha2col = OrderedDict([
        # GOEA GO terms that are significant
        (-1, 'plum'),
        (0.005, 'mistyrose'),
        (0.010, 'moccasin'),
        (0.050, 'lemonchiffon1'),
        # GOEA GO terms that are not significant
        (1.000, 'grey95'),
    ])

    key2col = {
        'level_01': 'lightcyan',
        'go_sources': 'palegreen',
    }


def label_wrap(dag_obj, label):
    """Label text for plot."""
    names = dag_obj[label].name.replace(",", r", ").split(' ')
    temp = []
    final_list = []
    for i in names:
        if len(' '.join(temp)) >= 16:
            final_list.append(' '.join(temp))
            temp.clear()
        temp.append(i)

    wrapped_label = r"%s\n%s" % (label, '\n'.join(final_list))
    return wrapped_label


def sort_terms(dag_obj, data: iter):
    terms_list = []
    for term, p in data:

        if 0 <= p <= 0.005:
            p = 0.005
        elif p <= 0.010:
            p = 0.010
        elif p <= 0.050:
            p = 0.050
        elif p <= 1.000:
            p = 1.000
        term_ = dag_obj.get(term, None)
        assert term_ is not None
        setattr(term_, 'p_value', p)
        terms_list.append(term_)
    return terms_list


def get_terms(dag_obj, file, term):
    """
        (0.005, 'mistyrose'),
        (0.010, 'moccasin'),
        (0.050, 'lemonchiffon1'),
        # GOEA GO terms that are not significant
        (1.000, 'grey95'),
    :param dag_obj:
    :param file:
    :param term:
    :return:
    """
    terms_list = []
    if file is not None:
        pattern = re.compile(r'\s+')
        with open(file) as infile:
            for line in infile:
                try:
                    term_, p = pattern.split(line.strip())
                    p = float(p)
                    if 0 <= p <= 0.005:
                        p = 0.005
                    elif p <= 0.010:
                        p = 0.010
                    elif p <= 0.050:
                        p = 0.050
                    elif p <= 1.000:
                        p = 1.000
                except ValueError:
                    term_ = line.strip()
                    p = -1
                # print(term_)
                term_ = dag_obj.get(term_, None)
                assert term_ is not None
                # print(term_)
                setattr(term_, 'p_value', p)
                terms_list.append(term_)
    elif term is not None:
        term_ = dag_obj.get(term, 'None')
        assert isinstance(term, object)
        setattr(term_, 'p_value', -1)
        terms_list = [term_]
    return terms_list


def make_graph_pydot(dag_obj, recs, nodecolor, edgecolor, dpi, draw_parents=True, draw_children=True):
    """draw AMIGO style network, lineage containing one query record."""

    color_obj = Color()
    grph = pydot.Dot(graph_type='digraph', dpi="{}".format(dpi))  # Directed Graph
    edgeset = set()
    usr_ids = [rec.id for rec in recs]
    for rec in recs:
        if draw_parents:
            edgeset.update(rec.get_all_parent_edges())
        if draw_children:
            edgeset.update(rec.get_all_child_edges())

    rec_id_set = set([rec_id for endpts in edgeset for rec_id in endpts])
    nodes = {str(ID): pydot.Node(
        label_wrap(dag_obj, ID).replace("GO:", ""),  # Node name
        shape="box",
        style="rounded, filled",
        # Highlight query terms in plum:
        fillcolor=color_obj.alpha2col.get(dag_obj[ID].p_value if ID in usr_ids else None, 'white'),
        color=nodecolor)
        for ID in rec_id_set}

    # add nodes explicitly via add_node
    for rec_id, node in nodes.items():
        grph.add_node(node)

    for src, target in edgeset:
        # default layout in graphviz is top->bottom, so we invert
        # the direction and plot using dir="back"
        grph.add_edge(pydot.Edge(nodes[target], nodes[src],
                                 shape="normal",
                                 color=edgecolor,
                                 # label="is_a",
                                 dir="back"))

    return grph


def draw_lineage(dag_obj, recs, nodecolor="mediumseagreen",
                 edgecolor="lightslateblue", dpi=96,
                 lineage_img="GO_lineage.png", engine="pygraphviz",
                 gml=False, draw_parents=True, draw_children=True):
    """Draw GO DAG subplot."""
    assert engine in GraphEngines

    if engine == "pygraphviz":
        raise Exception('no pygraphviz soft')

    grph = make_graph_pydot(dag_obj, recs, nodecolor, edgecolor, dpi,
                            draw_parents=draw_parents, draw_children=draw_children)

    if gml:

        import networkx as nx  # use networkx to do the conversion

        gmlbase = lineage_img.rsplit(".", 1)[0]
        # obj = nx.from_agraph(grph) if engine == "pygraphviz" else nx.from_pydot(grph)
        obj = nx.nx_pydot.from_pydot(grph)
        try:
            del obj.graph['node']
        except KeyError as e:
            sys.stderr.write('Node is not in obj.graph:　%s' % e)
        except Exception as e:
            sys.stderr.write(e)

        try:
            del obj.graph['edge']
        except KeyError as e:
            sys.stderr.write('Node is not in obj.graph:　%s' % e)
        except Exception as e:
            sys.stderr.write(e)

        gmlfile = gmlbase + ".gml"
        # nx.write_gml(self.label_wrap, gmlfile)
        nx.write_gml(obj, gmlfile)
        sys.stderr.write("GML graph written to {0}\n".format(gmlfile))

    sys.stderr.write(("lineage info for terms %s written to %s\n" % ([rec.id for rec in recs], lineage_img)))

    grph.write_png(lineage_img)


def run():
    opts, obo_file = GOPlotParams().get_args()

    g = GODag(obo_file)
    if opts.desc:
        g.write_dag()

    # run a test case
    if opts.term is not None or opts.terms_file is not None:
        # rec = g.query_term(opts.term, verbose=True)
        rec_list = get_terms(g, opts.terms_file, opts.term)

        draw_lineage(g, rec_list, engine=opts.engine, gml=opts.gml,
                     draw_parents=opts.draw_parents,
                     draw_children=opts.draw_children)