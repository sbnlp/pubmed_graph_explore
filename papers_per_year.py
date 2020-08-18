# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Counts publications per year and keyword type. Joins result into
# a single figure.
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #


import mysql.connector
from mysql.connector import errorcode
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np
import argparse

from config import TABLE, CATEGORIES, CATEGORY_IDS, PLOT_DIR
from general import get_subset_ids, get_connection, get_year

COLORS			= {"chemical":"red", "disease":"orange", "gene":"green"}

YEAR_BEGIN		= 1947
YEAR_END		= 2017
CHUNK			= 1
YEARS = np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))

def parse_args():
	"""
	Parses command line arguments, returns list of one or all keywords.
	"""
	parser = argparse.ArgumentParser(description="Count papers published every year.")

	parser.add_argument("--key_type", type=str, default="all_keys",
			help="The keyword types to select: [chemical, disease, gene, all_keys]. Default is all_keys.")
	return parser.parse_args()
	

def make_cat_dict(categories, paper_subset):
	"""
	For each paper id in the neurological disease subset, the categories the paper belongs
	to are collected and returned in a dictionary.
	"""
	papers = dict() # Stores categories for each paper
	for cat in categories:
		f = open(CATEGORY_IDS + cat)
		for line in f:
			if line.startswith("#"): continue
			items = line.rstrip().split("\t")
			if len(items) == 4:
				id = "PM" + items[0]
				# Make sure only subset is used
				if id in paper_subset:
					if id not in papers:
						papers[id] = set()
					papers[id].add(cat)
		f.close()
		print("Read key file for category {}".format(cat))
	return papers

def papers_per_year(cursor, categories, paper_cats):
	"""
	Counts papers published in some time span, separated into categories
	"""
	total_per_year = {cat:{y:0 for y in YEARS} for cat in categories}
	paper_counter = 0
	query = "SELECT DOC_ID, year FROM {};".format(TABLE)
	cursor.execute(query)
	for (id, year) in cursor:
		if id in paper_cats:
			# Extract int from returned year-string
			year = get_year(year)
			if year != None and year >= YEAR_BEGIN and year <= YEAR_END:
				paper_counter += 1
				# paper_cats[id] returns categories of current paper
				# Count current paper for all categories it contains keywords of
				for selected_cat in paper_cats[id]:
					total_per_year[selected_cat][year] += 1
	print("Counted {} total papers".format(paper_counter))
	return total_per_year

if __name__ == "__main__":
	args = parse_args()
	if args.key_type == "all_keys":
		categories = CATEGORIES
	elif args.key_type in CATEGORIES:
		categories = [args.key_type]
	else:
		print("Unknown keyword category. Use --h for help.")
		exit()
	
	
	cnx = get_connection()
	if cnx == None:
		print("Connection error")
		exit()
	cursor = cnx.cursor()
	
	paper_cats = make_cat_dict(categories, get_subset_ids())
	print("Created paper-category dictionary")
	
	totals = papers_per_year(cursor, categories, paper_cats)
	print("Counted papers until year {}".format(YEAR_END))

	# plot
	fig, ax = plt.subplots()
	
	for cat in categories:
		# Put results into order
		cat_count = [totals[cat][y] for y in YEARS]
		ax.plot(YEARS, cat_count, label=cat, color=COLORS[cat])
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Papers published")
	plt.savefig(PLOT_DIR.format("papers_per_year.png"))
	print("Plot saved to '{}'".format(PLOT_DIR.format("papers_per_year.png")))

	cursor.close()
	cnx.close()
