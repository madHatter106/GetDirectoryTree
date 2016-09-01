import networkx as nx

def ParseDirTree(tree=os.getcwd(),G=nx.Graph(),itr=0,maxItr=100):
    subTree,leaves=[],[]
    knot = os.path.dirname(tree.pop(0))
    #print(knot)
    for x in os.listdir(knot):
        if x[0] != '.' and x[:2]!= '__':
            kx = os.path.join(knot,x)
            if os.path.isdir(kx):
                subTree.append(kx.split('/')[-1])
            else:
                leaves.append(x+'_lf')
    shavedKnot = knot.split('/')[-1]
    if subTree:
        G.add_edges_from(map(lambda b:(shavedKnot,b), subTree))
        for node in subTree:
            G.node[node]['type'] = 'dir'
            G.node[node]['color'] = 'red'
        tree.extend(subTree)
    if leaves:
        G.add_edges_from(map(lambda b:(shavedKnot,b),leaves))
        for node in leaves:
            G.node[node]['type'] = 'file'
            G.node[node]['color'] = 'magenta'
    G.node[shavedKnot]['type'] = 'dir'
    G.node[shavedKnot]['color'] = 'red'

    return G
