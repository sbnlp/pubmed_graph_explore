# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Estimate the average length of the shortest path between not yet
# connected keywords
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import networkx as nx
import numpy as np
import argparse
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

from config import CATEGORIES, GRAPH_FILES, CATEGORY_IDS, PLOT_DIR
from general import build_graph

COLORS = {"chemical":"red", "disease":"orange", "gene":"green", "all_keys":"grey"}

YEAR_BEGIN	= 1947
YEAR_END	= 2017
CHUNK		= 1
YEARS		= range(YEAR_BEGIN, YEAR_END+1, CHUNK)

def parse_args():
	"""
	Parses command line arguments.
	"""
	parser = argparse.ArgumentParser(description="Estimate the average length of the shortest path between not yet connected keywords")
	parser.add_argument("--samples", type=int, default=1000, help="Number of samples to compute the average shortest path from. Default: 1000.")
	return parser.parse_args()
	
def sample_shortest_paths(graph, num_samples=1000):
	"""
	Samples a number of node pairs, computes the shortest paths and returns an average.
	
	Requires graph to be fully connected!
	"""
	samples_path_lengths = list()
	nodes = np.array(graph.nodes)
	if num_samples >= _max_edges(len(graph)): # use all keyword pairs
		for n1 in nodes:
			for n2 in nodes:
				if n1 != n2 and not graph.has_edge(n1, n2):
					pth = nx.shortest_path_length(graph, n1, n2)
					samples_path_lengths.append(pth)
	else: # sample keyword pairs
		for sample in range(num_samples):
			# sample two nodes and compute the shortest connecting path
			n1, n2 = np.random.choice(nodes, 2, replace=False)
			# only unconnected nodes
			while graph.has_edge(n1, n2):
				n1, n2 = np.random.choice(nodes, 2, replace=False)
			# This will throw an error if n1 and n2 are
			assert nx.has_path(graph, n1, n2), "Error: Did you pass a graph to sample_shortest_paths that has more than 1 component?"
			pth = nx.shortest_path_length(graph, n1, n2)
			samples_path_lengths.append(pth)
	if len(samples_path_lengths) != 0:
		sample_average = sum(samples_path_lengths) / len(samples_path_lengths)
	else: sample_average = -1
	print("{} node pairs were sampled.\nThe shortest connecting paths have an average length of {}.".format(num_samples, sample_average))
	return sample_average
	
def _largest_component(graph):
	"""
	Returns the largest component of a graph.
	"""
	components = nx.algorithms.components.connected_components(graph)
	components = [(c, len(list(c))) for c in components]
	# Find max and return only node generator
	return max(components, key=lambda x:x[1])[0]

def _max_edges(n_nodes):
	"""
	Returns the maximum number of edges a graph can have depending on it's number of nodes.
	"""
	return (n_nodes * (n_nodes-1)) / 2

if __name__ == "__main__":
	logfile = open("shortest_path.log", mode="w")
	num_samples = parse_args().samples
	fig, ax = plt.subplots()
	for cat in CATEGORIES + ["all_keys"]:
		av_sample_path	= list() # to save average shortest path between nodes
		used_years		= list() # in some years there might be too little data
		for year in YEARS:
			graph = build_graph(GRAPH_FILES.format(cat, year), add_nodes=False)
			if len(graph) > 0:
				# Build largest connected component:
				# (there are usually some isolated nodes or small clusters)
				c_sub = graph.subgraph(_largest_component(graph))
				current_av_path = sample_shortest_paths(c_sub, num_samples=num_samples)
				if current_av_path != -1:
					av_sample_path.append(current_av_path)
					used_years.append(year)
					
		ax.plot(used_years,
				av_sample_path,
				label=cat,
				color=COLORS[cat])
		print("category {} done".format(cat))
		
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Average shortest path length\nfor two random keywords")

	plt.title("Approximated average shortest path\n between unconnected nodes. Sample size {}".format(num_samples))
	plt.savefig(PLOT_DIR.format("average_shortest_paths.png"), bbox_inches="tight")
	print("Plot saved to '{}'".format(PLOT_DIR.format("average_shortest_paths.png")))
		
	logfile.close()
