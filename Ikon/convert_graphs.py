import json
import networkx as nx

import itertools
if __name__ == "__main__":
	"""read file """
	with open("../resources/ikon_gallery-gallery_graph.json", "r", encoding='utf-8') as file:
		data = json.load(file)
		G = nx.node_link_graph(data, multigraph=False, directed=False)

	""" FILTER """
	# G = G.subgraph([n for n in G.nodes() if G.degree(n)>1])

	"""save file"""
	import json
	with open("../resources/ikon_gallery-gallery_graph.cyjs", "w", encoding='utf-8') as file:
		data = nx.readwrite.json_graph.cytoscape_data(G)
		json.dump(data, file, ensure_ascii=False, sort_keys=True, indent=4)

	# """ artist-artist graph """
	# for exhibition, attributes in (e for e in G.nodes(True) if e[1]['type'] == "Exhibition" ):
	# 	print(exhibition)
	# 	neighbors = list(G.neighbors(exhibition))
	# 	weight = 1/len(neighbors)
	# 	new_edges = [(edge[0], edge[1], weight )for edge in itertools.combinations(neighbors, 2)]
	# 	G.add_weighted_edges_from(new_edges)
	# 	G.remove_node(exhibition)

	# nx.readwrite.write_graphml(G, "../resources/ikon_artists-exhibitions_graph_5degree.graphml", encoding='utf-8')
		# data = nx.node_link_graph(G)
		# json.dump(data, file, ensure_ascii=False, sort_keys=True, indent=4)