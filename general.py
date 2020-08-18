# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Helper functions for mySQL connection and reading data used
# throughout the analysis scripts.
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import mysql.connector
from mysql.connector import errorcode
import re
import networkx as nx

from config import DATABASE, DB_USER, DB_PASSWORD, DB_HOST
from config import NEURO_DISEASE_IDS, CATEGORY_IDS

# ---------------------------------------------------------------- #
# Selecting/reading in paper identifiers
# ---------------------------------------------------------------- #

def get_subset_ids(id_file=NEURO_DISEASE_IDS):
	"""
	Reads in document identifiers from a file and returns them in a set.
	
	id_file should contain one file per line and end in a linebreak.
	"""
	subset = open(id_file, "rU").read().split("\n")[:-1]
	return set(["PM{}".format(id) for id in subset])

def get_papers_in_cat(cat, nd_subset):
	"""
	Collects paper ids (found in the neurological disease subset) for a given category, returns a set.
	"""
	paper_list = set()
	for line in open(CATEGORY_IDS.format(cat)):
		line = line.rstrip()
		items = line.split("\t")
		if len(items) == 4:
			id = "PM" + items[0]
			if id in nd_subset:
				paper_list.add(id)
	return paper_list

# ---------------------------------------------------------------- #
# MySQL connection
# ---------------------------------------------------------------- #

def get_connection():
	"""
	Sets up Connection to DATABASE.
	"""
	try:
		cnx = mysql.connector.connect(	user=DB_USER,
										password=DB_PASSWORD,
										host=DB_HOST,
										database=DATABASE)
	
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)
		return None
	else:
		return cnx

# ---------------------------------------------------------------- #
# Preprocessing for identifiers
# ---------------------------------------------------------------- #

def get_kws_single_id(id):
	"""
	Removes 'MESH:' or 'CHEBI:' from a single keyword identifier.
	"""
	assert len(id) > 5, "Error: Couldn't extract from {}".format(id)
	# Strip 'MESH:' or 'CHEBI:'
	return id[id.index(':')+1:]

def get_kws_from_list(kw_list):
	"""
	Extracts keywords from a list of identifiers.
	"""
	kws = re.split("\||;|,", kw_list)
	# Strip the keyword id
	final_kws = []
	for kw in kws:
		kw = kw.replace("MESH:", "")
		kw = kw.replace("CHEBI:", "")
		# Strip MESH: or CHEBI:
		final_kws.append(kw)
	return final_kws
	
def split_kw_ids(kw_term):
	"""
	Separates a keyword term into single identifiers splitting at |, ; and ,
	"""
	return re.split("\||;|,", kw_term)

# ---------------------------------------------------------------- #
# Data preprocessing
# ---------------------------------------------------------------- #

def get_year(sql_year, floor=False, ceil=False):
	"""
	Converts SQL-strings to ints, optionally rounding to upper / lower 10 year bounds.
	"""
	assert not(floor and ceil)
	# Handling '1998-1999' etc
	if len(sql_year) > 4:
		try :
			sql_year = int(sql_year[-4:])
		except:
			return None
	# cast to int
	else:
		sql_year = int(sql_year)
	# returning lower limit
	if floor:
		return sql_year - ((sql_year-2) % 5)
	# returning upper limit
	elif ceil and ((sql_year-2) % 5) > 0:
		return sql_year - ((sql_year-2) % 5) + 5
	return sql_year

# ---------------------------------------------------------------- #
# Graph construction
# ---------------------------------------------------------------- #

# .edgelist files may contain loops to add isolated nodes to the graph
def build_graph(edge_file, G=None, add_nodes=True, count_isolated=False):
	"""
	Adds edges and nodes from a file to a given graph or creates a new graph.
	
	Does not consider self-loops; instead just adds the loop's node.
	"""
	if G == None:
		G = nx.Graph()
	edges = open(edge_file, mode="r")
	isolated_count = 0
	for line in edges:
		line = line.split()
		if (len(line) >= 2):
			# Test if edge is a self-loop
			if line[0] == line[1]:
				if add_nodes:
					G.add_node(line[0])
				isolated_count += 1
			else:
				# Add regular edges to the graph
				G.add_edge(line[0], line[1])
	edges.close()
	if count_isolated:
		return G, isolated_count
	return G
