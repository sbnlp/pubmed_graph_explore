# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Creates a figure depicting in what distance keywords are before
# a connection is created. 
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import collections
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np
import argparse

from config import CATEGORIES, PLOT_DIR, DIST_FILES


YEAR_BEGIN	= 1947
YEAR_END	= 2016
CHUNK		= 1
YEARS = np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))

COLORS = {"2":"darkorange", "3":"khaki", "4":"mediumseagreen", "5":"deepskyblue", "inf":"slategrey"}

def parse_args():
	"""
	Parses the command line arguments.
	"""
	parser = argparse.ArgumentParser(description="Generate structured data")

	parser.add_argument("--key_type", type=str, default="all_keys",
						help="The keyword types to select: [chemical, disease, gene, all_keys]. Default: all_keys.")
	
	return parser.parse_args()

def get_dist_stats(current_year, category):
	"""
	Counts for one year how often keywords are connected in distance 2, 3, 4, 5 or from separate components (marked as "inf").
	"""
	# occurence of different distances. inf: keywords were in unconnected graph components.
	dist_freqs = {"2":0,"3":0,"4":0,"5":0,"inf":0}
	# total number of connections
	total = 0

	for line in open(DIST_FILES.format(category, current_year)):
		# NB: all edges are counted twice (from both sides)
		# -> doesn't matter since the total 'count' also counts them twice,
		# the result is the fraction
		line = line.split()
		if len(line) == 2:
			_, cnx_dists = line
			cnx_dists = np.array(cnx_dists.split(","))
			# count occurence of each distance tier
			for dist in dist_freqs:
				dist_freqs[dist] += (cnx_dists==dist).sum()
			total += len(cnx_dists)

	# Divide times each connection length was observed by total number of connections
	for dist in dist_freqs:
		dist_freqs[dist] /= max(total,1) # no division by zero
	return dist_freqs, total/2 # Divide by 2 to get actual number of connections


if __name__ == "__main__":
	cat = parse_args().key_type

	dist_freqs = {"2":[],"3":[],"4":[],"5":[],"inf":[]}
	total_cnx = []

	for year in YEARS:
		current_dist_freqs, current_total_cnx = get_dist_stats(year, cat)
		for dist in dist_freqs:
			dist_freqs[dist].append(current_dist_freqs[dist])
		total_cnx.append(current_total_cnx)
		print("---------- {} completed ----------".format(year))

	fig, ax = plt.subplots()
	for dist in dist_freqs:
		ax.plot(YEARS, dist_freqs[dist], label=dist, color=COLORS[dist])
	ax.legend(loc="upper left")
	ax.set_ylabel("Percentage of all new connections")
	ax.set_xlabel("Year")

	plt.title("Distances of new keyword connections ({})".format(cat))

	plt.savefig(PLOT_DIR.format("cnx_distance_{}.png".format(cat)))
