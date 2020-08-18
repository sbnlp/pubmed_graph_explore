# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Create a plot comparing the density of all graphs.
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

def density(categories):
	"""
	Plots the density of a graph, defined as: (2 * #edges) / (#nodes * (#nodes -1))
	"""
	fig, ax = plt.subplots()
	for cat in categories:
	# Create an empty graph
		graph = nx.Graph()
		density   = []
		for year in YEARS:
			# Add edges of current year to graph
			graph = build_graph(GRAPH_FILES.format(cat, year), G=graph)
			# Density: (2 * #edges) / (#nodes * (#nodes -1))
			# -> Completion of a graph. Density 0 for no edges, 1 for complete graphs
			density.append(nx.density(graph))

		#Plot results
		ax.plot(YEARS,
				density,
				label=cat,
				color=COLORS[cat])

	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Density")
	plt.savefig(PLOT_DIR + "density.png")
	print("Plot saved to '{}'".format(PLOT_DIR.format("density.png")))

if __name__ == "__main__":
	density(CATEGORIES + ["all_keys"])
