# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Creates a figure depicting the mean number of keywords per paper,
# comparing the keyword categories
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import mysql.connector
from mysql.connector import errorcode
import numpy as np
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

from general import get_subset_ids, get_connection, get_year, split_kw_ids
from config import TABLE, CATEGORIES, CATEGORY_IDS, PLOT_DIR

COLORS			= {"chemical":"red", "disease":"orange", "gene":"green", "all_keys":"grey"}

YEAR_BEGIN		= 1947
YEAR_END		= 2017
CHUNK			= 1
YEARS 			= np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))

def count_keywords(categories, paper_subset):
	"""
	Collects paper ids for all categories, returns a dict.
	"""
	kws_in_paper = dict() # Stores number of keywords for each paper
	for cat in categories:
		f = open(CATEGORY_IDS.format(cat))
		for line in f:
			if line.startswith("#"): continue
			items = line.rstrip().split("\t")
			id = "PM" + items[0]
			if id in paper_subset:
				if len(items) == 4:
					if id not in kws_in_paper:
						kws_in_paper[id] = {cat:0 for cat in categories}
					n_kws = len(split_kw_ids(items[1]))
					kws_in_paper[id][cat] += n_kws
					kws_in_paper[id]["all_keys"] += n_kws
		f.close()
		print("Read file for category {}".format(cat))
	return kws_in_paper

def count_year(categories, cursor, paper_counts, joined=False):
	"""
	Gets keyword count each year from y_begin to (exclusively) y_end.
	"""
	kw_counter = {cat:{y:0 for y in YEARS} for cat in categories}
	paper_counter = {cat:{y:0 for y in YEARS} for cat in categories}
	# N.B. Sometimes, years in the database are e.g. 1998-1999.
	# get_year uses the first four symbols, if possible. MySQL might apply a different policy, to not have cutoff at the borders,
	# we retrieve all documents first (majority is used anyway),
	# extract the year and then choose years between the borders
	query = "SELECT DOC_ID, year FROM {};".format(
		TABLE)
	cursor.execute(query)
	for (id, year) in cursor:
		if id in paper_counts: # contains only preselected papers
			year = get_year(year)
			if year != None and year >= YEAR_BEGIN and year <= YEAR_END:
				# Count for every category the papers belongs to
				for paper_cat in paper_counts[id]:
					# only papers with at least one keyword of the category should be
					# counted in paper_counter
					if paper_counts[id][paper_cat] > 0:
						kw_counter[paper_cat][year] += paper_counts[id][paper_cat]
						paper_counter[paper_cat][year] += 1
	return kw_counter, paper_counter

def take_mean(kw_counter, paper_counter):
	"""
	Divides the number of keywords counted in a year by the number of contributing papers.
	"""
	for cat in kw_counter:
		for year in kw_counter[cat]:
			if paper_counter[cat][year] > 0:
				kw_counter[cat][year] /= paper_counter[cat][year]
			# Else kw_counter remains 0
	return kw_counter

if __name__ == "__main__":
	categories = CATEGORIES + ["all_keys"]
	
	cnx = get_connection()
	if cnx == None:
		print("Connection error")
		exit()
	cursor = cnx.cursor()
	
	neuro_disease_papers = get_subset_ids()
	
	kws_in_paper = count_keywords(categories, neuro_disease_papers)
	print("Counted keywords for all categories")
	
	keyword_counter, paper_counter = count_year(categories, cursor, kws_in_paper)
	print("Added years")
	
	means = take_mean(keyword_counter, paper_counter)
	print("Computed means")
	
	fig, ax = plt.subplots()
	for cat in categories:
		mean = np.array([means[cat][y] for y in YEARS])
		ax.plot(YEARS, mean, label=cat, color=COLORS[cat])
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Mean number of keywords per paper")
	plt.savefig(PLOT_DIR.format("keywords_mean.png"))
	print("Plot saved to " + PLOT_DIR.format("keywords_mean.png"))

	cursor = cnx.cursor()
	cursor.close()
	cnx.close()
