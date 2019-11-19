
"""
Build GRAPH
"""

import networkx as nx
from utilities.profiler import profile
from CRUD import *

@profile
def build_artists_exhibitions_graph(connection):
	G = nx.Graph()
	for exhibition in select_exhibitions(connection):
	    G.add_node("E{:06}".format(exhibition[0]),
	               pos=[0,0,0],
	               label=exhibition[1],
	               color="orange", 
	               size=1.0
	              )
	    	

	    artists = select_artists_of_exhibition(connection, exhibition)

	    for artist in artists:
	        G.add_node("A{:06}".format(artist[0]), 
	                   pos=[0,0,0],
	                   label=artist[1],
	                   color="cyan"
	                  )
	        
	        G.add_edge("E{:06}".format(exhibition[0]), "A{:06}".format(artist[0]), 
	                   weight=1.0/len(artists)
	                  )

	return G

@profile
def build_artists_artist_graph(connection):
	from itertools import combinations
	G = nx.Graph()
	for exhibition in select_exhibitions(connection):
		artists = list(select_artists_of_exhibition(connection, exhibition))
		if len(artists):
			weight = 1/len(artists)

			for u, v in combinations(artists, 2):
				if (u,v) in G.edges:
					G.edges[(u, v)]['weight'] +=weight
				else:
					G.add_edge("A{:06}".format(u[0]), "A{:06}".format(v[0]), weight=weight)

	# Filter nodes by degree
	H = G.subgraph([n for n in G.nodes() if G.degree(n)>5])
	return H

@profile
def write_graph_json(G, filepath)->'json':
	j = {
		'nodes': {}, 
		'edges': []
	}

	print('nodes...')
	for node in G.nodes:
		j['nodes'][node] = G.nodes[node]

	print("edges...")
	for edge in G.edges:
		u, v = edge
		w = G.edges[edge]['weight']
		j['edges'].append({'source':u, 'target': v, 'weight': w})


	# add attributes
	for node, attributes in G.nodes(True):
		for key, value in attributes.items():
			j['nodes'][key] = value

	print("graph created with {} node and {} edges".format(len(j['nodes']), len(j['edges'])))

	import json
	with open(filepath, "w", encoding='utf-8') as file:
		json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)
	return j

@profile
def layout_nodes(G):
	positions = nx.spring_layout(G, dim=3)    
	for node, position in positions.items():
		G.node[node]['pos'] = [position[0], position[1], position[2]]

@profile
def calc_degree_centrality(G):
	for node, degree_centrality in nx.pagerank(G).items():
		G.node[node]['degree_centrality'] = degree_centrality
	return G

@profile
def calc_pagerank(G):
	for node, pagerank in nx.pagerank(G).items():
		G.node[node]['pagerank'] = pagerank
	return G

@profile
def calc_eigenvector_centrality(G):
	for node, eigenvector_centrality in nx.closeness_centrality(G).items():
		G.node[node]['eigenvector_centrality'] = eigenvector_centrality
	return G

@profile
def calc_closeness_centrality(G):
	for node, closeness_centrality in nx.eigenvector_centrality(G).items():
		G.node[node]['closeness_centrality'] = closeness_centrality
	return G

@profile
def calc_betweenness_centrality(G):
	for node, betweenness_centrality in nx.betweenness_centrality(G).items():
		G.node[node]['betweenness_centrality'] = betweenness_centrality
	return G

@profile
def filter_graph_by_degree(G, degree):
	return G.subgraph([n for n in G.nodes() if G.degree(n)>degree])



if __name__ == "__main__":
	connection = connectToDatabase("../resources/ikon.db")

	# G = build_artists_exhibitions_graph(connection)
	# j = create_graph_json(G)
	# import json


	"""build graph"""
	G = build_artists_exhibitions_graph(connection)
	# G = build_artists_artist_graph(connection)

	"""filter graph"""
	G = filter_graph_by_degree(G, 5)

	"""layout graph"""
	layout_nodes(G)

	"""calc centralities"""
	calc_pagerank(G)
	calc_degree_centrality(G)

	import json
	with open("../resources/ikon_artists-exhibitions_graph_5degree.json", "w", encoding='utf-8') as file:
		data = nx.node_link_data(G)
		json.dump(data, file, ensure_ascii=False, sort_keys=True, indent=4)
	
	# calc_closeness_centrality(G)
	# calc_betweenness_centrality(G)
	# calc_eigenvector_centrality(G)


	# G.write_gexf("../resources/ikon_artists-exhibitions_graph.gexf")
	
	"""create json"""
	# j = write_graph_json(G, "../resources/ikon_artists-exhibitions_graph.json")

	# with open("../resources/ikon_artists_exhibitions_graph.json", "w", encoding='utf-8') as file:
	# 	json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)
	
	"""save json file"""


