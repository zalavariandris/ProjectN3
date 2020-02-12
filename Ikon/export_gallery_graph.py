"""
export gallery-gallery GRAPH from sql
"""

import networkx as nx
from utilities.profiler import profile
from CRUD import *

@profile
def build_galleries_graph(connection):
    def to_node_id(data_id):
        return "G{:06}".format(data_id)

    G = nx.Graph()
    all_galleries = select_galleries(connection)
    for gallery in all_galleries:
        G.add_node(to_node_id(gallery[0]), label=gallery[1])

    progress = 0
    for gallery in all_galleries:
        print("{}/{}".format(progress, len(all_galleries)))
        progress+=1
        for exhibition in select_exhibitions_at_gallery(connection, gallery):
            for artist in select_artists_of_exhibition(connection, exhibition):
                for other_exhibition in select_exhibitions_of_artist(connection, artist):
                    other_gallery = select_gallery_of_exhibition(connection, other_exhibition)
                    if gallery[0] is other_gallery[0]:
                        continue
                    if G.has_edge(to_node_id(gallery[0]), to_node_id(other_gallery[0])):
                        G.edges[to_node_id(gallery[0]), to_node_id(other_gallery[0])]['weight']+=1;
                    else:
                        G.add_edge(to_node_id(gallery[0]), to_node_id(other_gallery[0]), weight=1.0)

    return G

if __name__ == "__main__":
    """ build graph from sql """
    connection = connectToDatabase("./data/ikon_clean.db")
    G = build_galleries_graph(connection)
    
    print(""" calculate weighted eigenvector centrality """)
    for n, value in nx.eigenvector_centrality(G, weight='weight').items():
        G.nodes[n]['weighted_eigenvector_centrality'] = value
        
    print(""" calculate weighted betweennes... """)
    for n, value in nx.betweenness_centrality(G, weight='weight').items():
        G.nodes[n]['weighted_betweenness_centrality'] = value

    print(""" Write edges and nodes to csv file for gephy """)
    """ write edges """
    fout = open('./ikon_gallery-gallery_edges.csv', 'w', encoding="utf-8")
    fout.write('Source\tTarget\tWeight\tType\n')
    for e in G.edges:
        source = e[0]
        target = e[1]
        weight = G.get_edge_data(e[0], e[1])['weight']
        
        fout.write(source + '\t' + target + '\t' + str(weight) + '\t' + 'Undirected' + '\n')
    
    fout.close()
    
    """ write nodes """
    fout = open('./data/ikon_gallery-gallery_nodes.csv', 'w', encoding="utf-8")
    fout.write('Id\tLabel\tweighted_eigenvector_centrality\tweighted_betweenness_centrality\n')
    for n in G.nodes:
        label = G.nodes[n]['label']
        eigen = G.nodes[n]['weighted_eigenvector_centrality']
        between = G.nodes[n]['weighted_betweenness_centrality']
        fout.write(n + '\t' + label + '\t' + str(eigen) + '\t' + str(between) + '\n')
    fout.close()
        
        
    

