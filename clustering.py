# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Create a plot comparing the average clustering coefficients of
# all graphs.
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

from config import CATEGORIES, GRAPH_FILES, PLOT_DIR
from general import build_graph

YEAR_BEGIN	= 1947
YEAR_END	= 2017
CHUNK		= 1
YEARS 		= np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))

COLORS = {"chemical":"red", "disease":"orange", "gene":"green", "all_keys":"grey"}

def clustering(categories):
	"""
	Average clustering coefficient per year.
	"""
	fig, ax = plt.subplots()
	for cat in categories:
		# Create an empty graph
		graph 		= nx.Graph()
		cl_coeff	= []
		for year in YEARS:
			# Add edges of current year to graph
			# .edgelist files contain loops to add isolated nodes to the graph.
			# These self-loops lead to density values higher than 1 with
			# networkx's density-function, therefore they are removed.
			graph, isolated = build_graph(GRAPH_FILES.format(cat, year), G=graph, count_isolated=True)
			# Average clustering coefficient:
			# For node n, how much are n's neighbors connected
			cl_coeff.append(nx.algorithms.cluster.average_clustering(graph))

		#Plot results
		ax.plot(YEARS,
		cl_coeff,
		label=cat,
		color=COLORS[cat])

	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Average clustering coefficient")
	plt.savefig(PLOT_DIR + "edges_clustering.png")
	print("Plot saved to '{}'".format(PLOT_DIR.format("edges_clustering.png")))

if __name__ == "__main__":
	clustering(CATEGORIES + ["all_keys"])
