"""
export artist-artist GRAPH from sql
"""

import networkx as nx
from utilities.profiler import profile
from CRUD import connectToDatabase, select_artists, select_exhibitions, select_artists_of_exhibition

@profile
def build_artists_graph(connection):
    def to_node_id(data_id):
        return "A{:06}".format(data_id)
    from itertools import combinations
    G = nx.Graph()

    all_artists = select_artists(connection)
    progress = 0
    for idx, name in all_artists:
        print("add artist {}/{}".format(progress, len(all_artists)))
        G.add_node(to_node_id(idx), label=name)
        progress+=1

    all_exhibitions = select_exhibitions(connection)
    progress = 0
    for exhibition in all_exhibitions:
        artists = list(select_artists_of_exhibition(connection, exhibition))
        print("add links through exhibitions {}/{}".format(progress, len(all_exhibitions)))
        progress+=1
        if len(artists):
            weight = 1.0/len(artists)

            for A, B in combinations(artists, 2):
                u = to_node_id(A[0])
                v = to_node_id(B[0])
                if (u,v) in G.edges:
                    G.edges[(u, v)]['weight'] +=weight
                else:
                    G.add_edge(u, v, weight=weight)

    return G

if __name__ == "__main__":
    """ build graph from sql """
    connection = connectToDatabase("./data/ikon_clean.db")
    G = build_artists_graph(connection)
    
    G = G.subgraph([n for n in G.nodes() if G.degree(n)>=3])
    
    print(""" calculate weighted eigenvector centrality... """)
    for n, value in nx.eigenvector_centrality(G, weight='weight').items():
        G.nodes[n]['weighted_eigenvector_centrality'] = value
        
    print(""" calculate weighted betweennes... """)
    for n, value in nx.betweenness_centrality(G, k=1000, weight='weight').items():
        G.nodes[n]['weighted_betweenness_centrality'] = value

    print(""" Write edges and nodes to csv file for gephy """)
    """ write edges """
    fout = open('./data/ikon_artist-artist_edges.csv', 'w', encoding="utf-8")
    fout.write('Source\tTarget\tWeight\tType\n')
    for e in G.edges:
        source = e[0]
        target = e[1]
        weight = G.get_edge_data(e[0], e[1])['weight']
        
        fout.write(source + '\t' + target + '\t' + str(weight) + '\t' + 'Undirected' + '\n')
    fout.close()
    
    """ write nodes """
    fout = open('./data/ikon_artist-artist_nodes.csv', 'w', encoding="utf-8")
    fout.write('Id\tLabel\tweighted_eigenvector_centrality\tweighted_betweennes_centrality\n')
    for n in G.nodes:
        label = G.nodes[n]['label']
        eigen = G.nodes[n]['weighted_eigenvector_centrality']
        between = G.nodes[n]['weighted_betweenness_centrality']
        fout.write(n + '\t' + label + '\t' + str(eigen) + '\t' + str(between) + '\n')
    fout.close()
