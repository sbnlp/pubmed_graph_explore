# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# For new connections from a specific year, the evolution of the shortest path
# (since both nodes were in the same component for the first time)
# is examined and depicted in an interative plotly figure.
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import plotly
import plotly.graph_objects as go
import numpy as np
import argparse
import networkx as nx
import random

from config import CATEGORIES, CATEGORY_IDS, GRAPH_FILES, PLOT_DIR, NEW_CNX_FILES
from general import build_graph, split_kw_ids

COLORS = {"chemical":"red", "disease":"orange", "gene":"green"}

YEAR_BEGIN	= 1947
YEAR_END	= 2017
CHUNK		= 10
YEARS = list(range(YEAR_BEGIN, YEAR_END+1, CHUNK))
THRESHOLD	= 4 # Distances >= THRESHOLD will be merged for better readability

def parse_args():
	"""
	Parses command line arguments, returns list of one or all keywords.
	"""
	parser = argparse.ArgumentParser(description="Evolution of new keyword pairs until they are linked")

	parser.add_argument("--key_type", type=str, default="all_keys",
		help="The keyword types to select: [chemical, disease, gene, all_keys]. Default is all_keys.")
	parser.add_argument("--year", type=int, default=YEAR_END-1,
		help="Year the observed new connections are sampled from. Default and max is {}".format(YEAR_END-1))
	parser.add_argument("--samples", type=int, default=None,
		help="Number of keyword pairs to observe. Per default, all new connections are used.")
	parser.add_argument("--mode", type=str, choices=["connected", "unconnected"], default="connected",
		help="Set of keyword pairs to sample from. If 'connected' is selected (default), pairs will be chosen that get connected in the respective year. If 'unconnected' is selected, pairs will be sampled that are not linked yet in the graph and won't be connected in the current year either.")
	return parser.parse_args()

def sample_connected(cat, year, num_samples=-1):
	"""
	Samples a number of connections newly made in a given year and
	returns a list of keyword pairs. If given num_samples is negative,
	collects all connections instead.
	"""
	all_new_cnx = list()
	cnx_file = open(NEW_CNX_FILES.format(cat, year), mode="r")
	for cnx in cnx_file:
		if cnx.startswith("#"): continue # skip comments
		cnx = cnx.split()
		if len(cnx) == 2:
			for target in split_kw_ids(cnx[1]):
				all_new_cnx.append((cnx[0], target))
	cnx_file.close()
	if num_samples < 0:
		return all_new_cnx
	# Select the indices of some pairs randomly
	selected_indices = np.random.choice(len(all_new_cnx), num_samples, replace=False)
	# Return the pairs at the selected indices
	return np.array(all_new_cnx)[selected_indices]

def sample_unconnected(cat, year, num_samples):
	"""
	Samples a number of keyword pairs that are not currently connected
	and don't get a connection in the current year either.
	"""
	assert year < YEAR_END
	# build graph for following year for easy checking which connections exist or are established in the current year
	graph = build_graph(GRAPH_FILES.format(cat, year+1))
	nodes = list(graph.nodes)
	samples = set()
	while len(samples) < num_samples:
		n1, n2 = random.choice(nodes), random.choice(nodes)
		if n1 == n2 or (n2, n1) in samples:
			continue
		samples.add((n1, n2))
	return np.array(list(samples))

# argument mode is only used to choose a file name of the save file
def new_cnx_convergence(kw_pairs, cat, year, mode):
	"""
	Until the year of connection the shortest path for each given
	keyword pair is observed.
	"""
	
	# Will store the number of pairs that have a specific distance in a year
	# -1 for no connection
	# -2 for at least one keyword not yet in graph
	
	# first the distances of each keyword pair are saved for each year chunk
	pair_dists = [list() for i in range(len(kw_pairs))]

	# construct list of labels
	distances = ["not in graph", "unconnected"] + [str(i) for i in range(THRESHOLD)] + [">=" + str(THRESHOLD)]
	# add years for readability
	labels = [d + " : " + str(y) for y in YEARS for d in distances]
	
	for i, y_chunk in enumerate(YEARS):
		graph = build_graph(GRAPH_FILES.format(cat, y_chunk))
		for i, pair in enumerate(kw_pairs):
			n1, n2 = pair
			# all distances for all years are consecutively numbered. -> to match a label in 'labels'
			if n1 not in graph or n2 not in graph:
				d = 0
			elif not nx.has_path(graph, n1, n2):
				d = 1
			else:
				path = nx.shortest_path_length(graph, n1, n2)
				if path < THRESHOLD:
					d = 2 + path # first two indices are taken by 'not in graph' and 'unconnected'
				else:
					d = 2 + THRESHOLD
			# Save index that matches the right label in 'labels'
			pair_dists[i].append(i * (len(distances)) + d)
	
	# convert the results for plotly sankey diagrams
	
	# source contains start distance (label); target contains goal distance (label), value contains the number of links that changed distance from source to target in a specific year
	# -> data is always saved as a triple
	dist_changes = {"source":list(), "target":list(), "value":list()}
	transfer_indices = dict() # saves position of source-target pairs in dist_changes
	for pair_dist in pair_dists:
		for dist in range(len(pair_dist) - 1):
			source_target = (pair_dist[dist], pair_dist[dist+1])
			
			if source_target not in transfer_indices:
				# get next free position
				transfer_indices[source_target] = len(transfer_indices)
				dist_changes["source"].append(source_target[0])
				dist_changes["target"].append(source_target[1])
				dist_changes["value"].append(0)
				
			dist_changes["value"][transfer_indices[source_target]] += 1
	
	# Save results
	fig = go.Figure(data=[go.Sankey(
						node = dict(
							pad = 15,
							thickness = 20,
							line = dict(color = "black", width = 0.5),
							label = labels,
							color = "blue"
						),
						link = dict(
							source = dist_changes["source"], # indices correspond to labels, eg A1, A2, A2, B1, ...
							target = dist_changes["target"],
							value = dist_changes["value"]
						))])

	fig.update_layout(title_text="Distance of {} sampled keyword pairs that get connected in {}".format(len(kw_pairs), year), font_size=10)
	plotly.io.write_html(fig, PLOT_DIR.format("pairs_before_cnx_{}_{}_{}.html".format(cat, year, mode)), include_plotlyjs="cdn")
	print("Saved as " + PLOT_DIR.format("pairs_before_cnx_{}_{}_{}.html".format(cat, year, mode)))

if __name__ == "__main__":
	args = parse_args()
	# select connection samples according to settings.
	if args.samples != None:
		if args.mode == "connected":
			print("Sampling {} edges that get a link in {}".format(args.samples, args.year))
			new_cnx = sample_connected(args.key_type, args.year, num_samples=args.samples)
		else:
			print("Sampling {} keyword pairs that stay without connection until {}".format(args.samples, args.year+1))
			new_cnx = sample_unconnected(args.key_type, args.year, args.samples)
	elif args.mode == "connected":
		print("All new connections are used. This could take a while.")
		new_cnx = sample_connected(args.key_type, args.year)
	else:
		print("Using all non-existant edges is likely to exceed capacity. Please select number of samples for this mode.")
		exit()
		
	new_cnx_convergence(new_cnx, args.key_type, args.year, args.mode)
