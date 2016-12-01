import networkx as nx
import matplotlib.pyplot as pl
import os
from bokeh.models import ColumnDataSource
from math import sqrt
from bokeh.plotting import show, figure
from bokeh.io import output_notebook
from bokeh.models import HoverTool

'''
Collection of functions to recursively parse a directory and construct an interactive display of
the results using networkx and Bokeh.
'''

def ParseDirTree(tree=os.getcwd(),G=nx.Graph(),itr=0,maxItr=100,**kwds):
    colorDict = kwds.pop('colors',{'dir':'red','file':'magenta'})
    subTree,leaves=[],[]
    itr += 1
    knot = tree.pop(0)
    try:
        for x in os.listdir(knot):
            if x[0] != '.' and x[:2]!= '__':
                kx = os.path.join(knot,x)
                if os.path.isdir(kx):
                    subTree.append(kx)
                else:
                    leaves.append(kx)
    except FileNotFoundError as e:
        return G
    if subTree:
        G.add_edges_from(map(lambda b:(knot,b,{'weight':1/len(subTree)}), subTree))
        for node in subTree:
            if node[-1] == '/':
                node = node[:-1]
            G.node[node]['color'] = colorDict['dir']
            G.node[node]['lbl'] = os.path.abspath(node).split('/')[-1]
        tree.extend(subTree)
    if leaves:
        G.add_edges_from(map(lambda b:(knot, b, {'weight': 1/len(leaves)}),
                             leaves))
        for node in leaves:
            G.node[node]['color'] = colorDict['file']
            G.node[node]['lbl'] = os.path.abspath(node).split('/')[-1]
    G.node[knot]['color'] = colorDict['dir']
    G.node[knot]['lbl'] = os.path.abspath(knot).split('/')[-1]

    if tree and itr<=maxItr:
        return ParseDirTree(tree, G, itr, colors=colorDict)
    else:
        return G


def PlotCleanTree(G,figSize=(12,12),saveName=None,show=False):
    colors = [G.node[node]['color'] for node in G.nodes()]
    lbls = {node: G.node[node]['lbl'] for node in G.nodes()}
    f,ax = pl.subplots(figsize=figSize)
    pos = nx.drawing.spring_layout(G)
    nx.draw_networkx(G,pos=pos,node_color=colors,labels=lbls,ax=ax)
    if saveName:
        fmt = saveName.split('.')[-1] if '.' in saveName else '.png'
        f.savefig(saveName,dpi=300,format=fmt)
    if show:
        pl.show()


def get_edges_specs(_network, _layout):
    d = dict(xs=[], ys=[], alphas=[])
    #weights = [d['weight'] for u, v, d in _network.edges(data=True)]
    max_weight = 1 #max(weights)
    calc_alpha = lambda h: 0.1 + 0.6 * (h / max_weight)

    # example: { ..., ('user47', 'da_bjoerni', {'weight': 3}), ... }
    for u, v, data in _network.edges(data=True):
        d['xs'].append([_layout[u][0], _layout[v][0]])
        d['ys'].append([_layout[u][1], _layout[v][1]])
        d['alphas'].append(calc_alpha(data['weight']))
    return d


def BokehPlot(G, **kwds):
    width = kwds.pop('width',800)
    height = kwds.pop('height',800)
    toolTipStr = kwds.pop('toolTipStr','label')
    K = .1/sqrt(G.number_of_nodes())
    layout = nx.spring_layout(G,k=K,iterations=100)
    nodes, nodes_coordinates = zip(*sorted(layout.items()))
    nodes_xs, nodes_ys = list(zip(*nodes_coordinates))
    colors = tuple([G.node[node]['color'] for node in nodes])
    lbl = tuple([G.node[node]['lbl'] for node in nodes])
    nodes_source = ColumnDataSource(dict(x=nodes_xs, y=nodes_ys,
                                     name=nodes,color=colors,label=lbl))
    hover = HoverTool(tooltips=[(toolTipStr, '@' + toolTipStr)])
    plot = figure(plot_width=width, plot_height=height,
              tools=['tap', hover, 'box_zoom', 'reset'])
    r_circles = plot.circle('x', 'y', source=nodes_source, size=10,
                            color=colors,level='overlay')
    lines_source = ColumnDataSource(get_edges_specs(G2, layout))
    r_lines = plot.multi_line('xs', 'ys', line_width=1.5,
                              alpha='alphas', color='navy',
                              source=lines_source)


def ExportTree(G,path=os.getcwd(),format='graphml'):
    if format='graphml':
        nx.write_graphml(G,path=path)
