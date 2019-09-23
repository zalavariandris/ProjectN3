
"""
Build GRAPH
"""

import networkx as nx
import itertools
from utilities.profiler import profile

@profile
def build_graph(connection)->'nx.MultiGraph':
	"""
	build graph
	"""

	# create nodes
	artists = select_artists_with_noexhibitions(connection,5)
	galleries = select_galleries(connection)
	print(len(list(artists)), len(list(galleries)))

	G = nx.MultiGraph()
	for artist in artists:
		ID = "A{}".format(artist[0])
		G.add_node(ID, label=artist[1], color="cyan")

	for gallery in galleries:
		ID = "G{}".format(gallery[0])
		G.add_node(ID, label=gallery[1], color="orange")

	# create edges
	for artist in artists:
		source_id = "A{}".format(artist[0])
		assert source_id in G.nodes, source_id
		exhibitions = select_exhibitions_of_artist(connection, artist)
		for exhibition in exhibitions:
			gallery = select_gallery_of_exhibition(connection, exhibition)
			
			target_id = "G{}".format(gallery[0])
			assert target_id in G.nodes, target_id
			G.add_edge(source_id, target_id)

	return G

@profile
def build_graph_original(connection):
	G = nx.Graph()
	for exhibition in select_exhibitions(connection):
	    G.add_node("E{:06}".format(exhibition[0]),
	               position=[0,0,0],
	               label=exhibition[1],
	               color="orange", 
	               size=1.0
	              )
	    	

	    artists = select_artists_of_exhibition(connection, exhibition)

	    for artist in artists:
	        G.add_node("A{:06}".format(artist[0]), 
	                   position=[0,0,0],
	                   label=artist[1],
	                   color="cyan"
	                  )
	        
	        G.add_edge("E{:06}".format(exhibition[0]), "A{:06}".format(artist[0]), 
	                   weight=1.0/len(artists)
	                  )

	# Filter nodes by degree
	H = G.subgraph([n for n in G.nodes() if G.degree(n)>5])
	return H

@profile
def create_graph_json(G)->'json':
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

	print("layout nodes...")
	positions = nx.spring_layout(G, dim=3)    
	for n, position in positions.items():
		j['nodes'][n]['pos'] = [position[0], position[1], position[2]]

	return j

from CRUD import *
if __name__ == "__main__":
	connection = connectToDatabase("../resources/ikon.db")

	G = build_graph_original(connection)


	j = create_graph_json(G)
	import json
	with open("../resources/ikon_graph.js", "w", encoding='utf-8') as file:
		file.write("data = ")
		json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)


