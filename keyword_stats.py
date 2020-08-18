# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Creates 4 types of plots:
# 1 'keyword_occurrence': Keyword occurrences in all papers (counting duplicates)
# 2 'active_keywords_rate': rate of keywords known until a year that occur in that year
# 3 'new_keywords': New keywords and keyword 'vocabulary' process
# 4 'new_keywords_rate': Rate keyword introductions to all keyword occurrences
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

from config import TABLE, CATEGORIES, CATEGORY_IDS, PLOT_DIR
from general import get_subset_ids, get_connection, get_kws_from_list

# This skript counts total number of keyword uses in a year
# -> number of tokens, not distinct keywords types!

COLORS = {"chemical":"red", "disease":"orange", "gene":"green", "all_keys":"grey"}

YEAR_BEGIN	= 1947
YEAR_END	= 2017
CHUNK		= 1
YEARS		= np.array(range(YEAR_BEGIN, YEAR_END+1, CHUNK))


# ----------- plot creation --------------

def keyword_mentions(categories, mentions_per_year):
	"""
	Plot 1: Count how many keyword mentions there were in total
	"""
	fig, ax = plt.subplots()
	for cat in categories:
		ax.plot(YEARS,
				[mentions_per_year[cat][y] for y in YEARS],
				label=cat,
				color=COLORS[cat])
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Total keyword occurrences")
	plt.title("Keyword occurrences in all papers (counting duplicates)")
	plt.savefig(PLOT_DIR.format("keyword_occurrence.png"))
	print("Plot 1 saved to '{}'".format(PLOT_DIR.format("keyword_occurrence.png")))

def cumulative(categories, kws_cumulative):
	"""
	Plot 2: What percentage of the keywords known until a year are used in that year
	"""
	fig, ax = plt.subplots()
	for cat in categories:
		ax.plot(YEARS,
				kws_cumulative[cat],
				label=cat,
				color=COLORS[cat])
	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("Ratio keywords used in a year to\n all keywords known until that year")
	plt.savefig(PLOT_DIR.format("active_keywords_rate.png"))
	plt.title("Rate of keywords known until a year that is actively used")
	print("Plot 2 saved to '{}'".format(PLOT_DIR.format("active_keywords_rate.png")))

def new_keywords_cat_compare(categories, kws_total_count, kws_new):
	"""
	Plot 3: New keywords and keyword 'vocabulary' process
	"""
	# Version joining three categories into one plot for each category
	
	fig, ax = plt.subplots(1,3, figsize=(12, 4), sharex=True, sharey=True)
	# create second y axis for all three subplots()
	ax2 = (ax[0].twinx(), ax[1].twinx(), ax[2].twinx())
	
	for i, cat in enumerate(categories):
		all_kws = kws_total_count[cat][-1]
		kws_total_count[cat] = [c/all_kws for c in kws_total_count[cat]]

		print("{} total keywords in category {}".format(all_kws, cat))
		ax[i].plot(YEARS,
				kws_new[cat],
				label=cat,
				color=COLORS[cat])
		ax2[i].plot(YEARS,
				kws_total_count[cat],
				color="grey")
	for a in ax.flat:
		a.set(xlabel="year", ylabel="keywords newly introduced")
		a.legend(loc="upper left")
		a.label_outer()
	for a2 in ax2:
		a2.set_ylabel("keywords discovered so far")
		a2.set_yticks(np.arange(0.0, 1.1, 0.2))
	
	plt.tight_layout()
	plt.savefig(PLOT_DIR.format("new_keywords_split.png"))
	print("Plot 3a saved to '{}'".format(PLOT_DIR.format("new_keywords_split.png")))
	
	# Create a plot for each category

	for cat in categories:
		fig, ax = plt.subplots()
		ax2 = ax.twinx()
		
		ax.plot(YEARS,
				kws_new[cat],
				label=cat,
				color=COLORS[cat])
		ax2.plot(YEARS,
				kws_total_count[cat],
				color="grey")
		ax.set_xlabel("Year")
		ax.set_ylabel("Keywords introduced")
		ax.legend(loc="upper left")
		ax2.set_ylabel("Keywords discovered so far")

		plt.savefig(PLOT_DIR.format("new_keywords_{}.png".format(cat)))
		print("Plot 3b saved to '" + PLOT_DIR.format("new_keywords_{}.png'".format(cat)) + "'")

def new_rate_mentions(categories, kws_new, mentions_per_year):
	"""
	Plot 4: new keywords / all keyword occurrences
	"""
	fig, ax = plt.subplots()
	for cat in categories:
		# each keyword is introduced once - divide by all occurrences
		new_kws_rate = [(kws_new[cat][y]) / (mentions_per_year[cat][YEARS[y]]) for y in range(len(kws_new[cat]))]
		# Plot
		ax.plot(YEARS,
				new_kws_rate,
				label=cat,
				color=COLORS[cat])

	ax.legend(loc="upper left")
	ax.set_xlabel("Year")
	ax.set_ylabel("new keywords / keyword occurrences")
	plt.savefig(PLOT_DIR.format("new_keywords_rate.png"))
	print("Plot 4 saved to '{}'".format(PLOT_DIR.format("new_keywords_rate.png")))

# ----------------- other functions ------------------------

def read_cat_files(keywords, paper_subset):
	"""
	Collects paper ids for all categories.
	
	Returns a dict containing the keywords of each papers separated into categories.
	"""
	# Stores number of keywords for each paper
	papers = dict()
	for cat in keywords:
		f = open(CATEGORY_IDS.format(cat))
		for line in f:
			items = line.rstrip().split("\t")
			if len(items) == 4:
				id = "PM" + items[0]
				if id in paper_subset:
					# Add completed paper to dict
					if id not in papers:
						papers[id] = dict()
					if cat not in papers[id]:
						papers[id][cat] = list()
					papers[id][cat].extend(get_kws_from_list(items[1]))
		f.close()
		print("Read key file for category {}".format(cat))
	return papers

def count_kws(cursor, keywords, paper_kws):
	"""
	Counts keywords each year.
	"""
	# What set of keywords was used?
	kws_used = {cat:{y:set() for y in YEARS} for cat in keywords}
	# How often were keywords used?
	kw_counter = {cat:{y:0 for y in YEARS} for cat in keywords}
	# collect the keyword set known before 1947
	kws_before_1947 = {cat:set() for cat in keywords}
	query = "SELECT DOC_ID, year FROM {};".format(TABLE)
	cursor.execute(query)
	for (id, year) in cursor:
		if id in paper_kws: # contains only preselected papers
			year = get_year(year)
			if year != None and year <= YEAR_END:
				if year >= YEAR_BEGIN:
					for paper_cat in paper_kws[id]:
						kws_used[paper_cat][year].update(paper_kws[id][paper_cat])
						kw_counter[paper_cat][year] += len(paper_kws[id][paper_cat])
				else:
					for paper_cat in paper_kws[id]:
						kws_before_1947[paper_cat].update(paper_kws[id][paper_cat])
	return kws_used, kw_counter, kws_before_1947

if __name__ == "__main__":
	categories = CATEGORIES
	cnx = get_connection()
	if cnx == None:
		print("Connection error")
		exit()
	cursor = cnx.cursor()
	
	neuro_disease_papers = get_subset_ids()
	
	kws_per_paper = read_cat_files(categories, neuro_disease_papers)
	unique_kws_per_year, mentions_per_year, pre_1947 = count_kws(cursor, categories, kws_per_paper)

	# Set to collect all keywords found until current year
	kws_total = {c:pre_1947[c] for c in categories}
	# Percentage of kws already found / all keywords found until YEAR_END
	kws_cumulative = {c:[] for c in categories}
	# Number of keywords found until a year
	kws_total_count = {c:[] for c in categories}
	# Number of keyword used for the first time ever in this year
	kws_new = {c:[] for c in categories}

	for year in YEARS:
		for category in categories:
			# Add new keywords to total set
			kws_total[category].update(unique_kws_per_year[category][year])

			# Count keywords in current year
			unique_count = len(unique_kws_per_year[category][year])
			# Count keywords so far
			total_count = len(kws_total[category])
			kws_total_count[category].append(total_count)
			# Relation counted keywords this year and cumulative number until (inclusively) this year
			kws_cumulative[category].append(unique_count/total_count)
			
			# Number of new keywords
			# First entry
			if len(kws_new[category]) == 0:
				kws_new[category].append(total_count - len(pre_1947[category]))
			else: # Difference between last two entries
				kws_new[category].append(total_count - kws_total_count[category][-2])
		
		print("Completed year {}".format(year))
	
	print("________________________________________________________________________")
	
	# How many keywords are there in total per category?
	for category in categories:
		print("{} total keywords for category {}".format(len(kws_total[category]), category))
	 
	# Plot results:
	# Number of keyword identifiers used in a year (total)
	keyword_mentions(categories, mentions_per_year)
	# What percentage of the currently known keyword set was used in this year?
	cumulative(categories, kws_cumulative)
	# 3 Subplots for new keywords & progress in keyword discovery
	new_keywords_cat_compare(categories, kws_total_count, kws_new)
	# new keywords / keywords used a year
	new_rate_mentions(categories, kws_new, mentions_per_year)

	cursor.close()
	cnx.close()
