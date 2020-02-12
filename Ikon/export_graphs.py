"""
export GRAPH from sql
"""

import networkx as nx
from utilities.profiler import profile
from CRUD import *

@profile
def build_artists_exhibitions_graph(connection):
	G = nx.Graph()
	for exhibition in select_exhibitions(connection):
	    G.add_node("E{:06}".format(exhibition[0]),
	               label = exhibition[1],
	               type = "Exhibition", 
	              )
	    	

	    artists = select_artists_of_exhibition(connection, exhibition)

	    for artist in artists:
	        G.add_node("A{:06}".format(artist[0]), 
	                   label = artist[1],
	                   type = "Artist"
	                  )
	        
	        G.add_edge("E{:06}".format(exhibition[0]), "A{:06}".format(artist[0]), 
	                   weight=1.0/len(artists)
	                  )

	return G

@profile
def build_artist_exhibition_gallery_graph(connection):
	G = nx.Graph()
	for exhibition in select_exhibitions(connection):
		""" add exhibition to graph """
		exhibition_id = "E{:06}".format(exhibition[0])
		G.add_node(
			exhibition_id,
			label = exhibition[1],
			type = "Exhibition"
			)

		""" add gallery to graph """
		gallery = select_gallery_of_exhibition(connection, exhibition)
		gallery_id = "G{:06}".format(gallery[0])
		G.add_node(
			gallery_id,
			label = gallery[1],
			type = "Gallery"
			)

		G.add_edge(
			exhibition_id, gallery_id,
			weight = 1.0
			)

		""" add artists to graph """
		for artist in select_artists_of_exhibition(connection, exhibition):
			artist_id = "A{:06}".format(artist[0])
			G.add_node(
				artist_id,
				label = artist[1],
				type = "Artist"
				)

			G.add_edge(
				artist_id, exhibition_id,
				weight = 1.0/len(artist)
				)

	return G

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
		G.node[node]['x'] = position[0]
		G.node[node]['y'] = position[1]
		G.node[node]['z'] = position[2]

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
	for node, closeness_centrality in nx.closeness_centrality(G).items():
		G.node[node]['closeness_centrality'] = eigenvector_centrality
	return G

@profile
def calc_eigenvector_centrality(G):
	for node, eigenvector_centrality in nx.eigenvector_centrality(G, weight='weight').items():
		G.node[node]['eigenvector_centrality'] = closeness_centrality
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
	connection = connectToDatabase("./data/ikon.db")

	# G = build_artists_exhibitions_graph(connection)
	# j = create_graph_json(G)
	# import json


	"""build graph"""
	# G = build_artist_exhibition_gallery_graph(connection)
	# G = build_artists_artist_graph(connection)
	G = build_gallery_gallery_graph(connection)
	G = calc_eigenvector_centrality(G)

	"""filter graph"""
	# G = filter_graph_by_degree(G, 1)


	# """layout graph"""
	# layout_nodes(G)

	# """calc centralities"""
	# calc_pagerank(G)
	# calc_degree_centrality(G)
	# calc_closeness_centrality(G)
	# calc_betweenness_centrality(G)
	# calc_eigenvector_centrality(G)

	"""save to json"""
	import json
	with open("./data/ikon_gallery-gallery_graph.json", "w", encoding='utf-8') as file:
		data = nx.node_link_data(G)
		json.dump(data, file, ensure_ascii=False, sort_keys=True, indent=4)

	"""save GEXF"""
	# nx.readwrite.write_gexf("../resources/ikon_artists-exhibitions_graph.gexf")
	
	"""create json"""
	# j = write_graph_json(G, "../resources/ikon_artists-exhibitions_graph.json")

	# with open("../resources/ikon_artists_exhibitions_graph.json", "w", encoding='utf-8') as file:
	# 	json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)
	
	"""save json file"""
