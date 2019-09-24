
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
def build_artists_graph(connection):
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


if __name__ == "__main__":
	connection = connectToDatabase("../resources/ikon.db")

	# G = build_artists_exhibitions_graph(connection)
	# j = create_graph_json(G)
	# import json
	# with open("../resources/ikon_artists_exhibitions_graph.json", "w", encoding='utf-8') as file:
	# 	json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)


	G = build_artists_graph(connection)
	j = create_graph_json(G)
	import json
	with open("../resources/ikon_artists_graph.json", "w", encoding='utf-8') as file:
		json.dump(j, file, ensure_ascii=False, sort_keys=True, indent=4)


