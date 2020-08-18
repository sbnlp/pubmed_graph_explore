# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Plots the number of nodes in each year for the keyword categories
# "chemical", "disease", "gene" as well as all categories taken
# together. The result is saved in a single image.
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

from general import build_graph
from config import CATEGORIES, PLOT_DIR, GRAPH_FILES

YEAR_BEGIN	= 1947
YEAR_END	= 2017
CHUNK		= 1
YEARS = np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))

COLORS = {"chemical":"red", "disease":"orange", "gene":"green", "all_keys":"grey"}

def graph_size(categories, verbose=False):
	"""
	Creates a plot depicting the number of nodes in each year for a list of keyword categories.
	"""
	fig, ax = plt.subplots()
	for cat in categories:
		# Create an empty graph
		graph		= nx.Graph()
		no_nodes	= list()
		if verbose: print("-----------" + cat + "-----------")
		for year in YEARS:
			# Add edges of current year to graph
			graph = build_graph(GRAPH_FILES.format(cat, year), graph)
			no_nodes.append(len(graph))
			if verbose: print("{}\t{}".format(year, len(graph)))
		# Plot the number of nodes
		ax.plot(YEARS,
				no_nodes,
				label=cat,
				color=COLORS[cat])
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Nodes in the keyword graph")
	plt.savefig(PLOT_DIR.format("graph_size.png"))
	print("Plot saved to " + PLOT_DIR.format("graph_size.png"))

if __name__ == "__main__":
	graph_size(CATEGORIES + ["all_keys"])
