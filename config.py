# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Defines file locations to perform analysis on
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# General
# ---------------------------------------------------------------- #

CATEGORIES			= ["chemical","disease","gene"]

# ---------------------------------------------------------------- #
# SQL database
# ---------------------------------------------------------------- #

DATABASE			= ""
TABLE				= ""
DB_USER				= ""
DB_PASSWORD			= ""
DB_HOST				= ""

# ---------------------------------------------------------------- #
# graph files
# ---------------------------------------------------------------- #

# List describing a subset of PUBMED papers. Contains one pubmed id per line
NEURO_DISEASE_IDS	= "data/neuro_disease_ids.list"
# Lists keywords belonging to the categories chemical, disease, and gene.
# Contains 4 tab-separated values:
# Pubmed id of paper, keyword id (MESH/CHEBI), keyword names, extraction method
CATEGORY_IDS		= "data/categories/{}" # .format(category)
# Directory to save created plots
PLOT_DIR			= "plots/{}" # .format(filename)
# Files defining a graph for a specific category and year.
# Contains one edge per line represented by two keyword identifiers.
# Isolated nodes are included by giving the same node twice in a line.
GRAPH_FILES			= "data/graph/KWgraph_{}_{}.edgelist" # .format(category, year)
# Lists new connections for a specific category graph and year.
# Each line contains a keyword id following by comma-separated keyword ids the first
# one gets connected to during the year.
NEW_CNX_FILES		= "data/new_cnx/new_cnx_{}_{}.list" # .format(category, year)
# Lists the distance keywords that get connected this year.
# To be read with NEW_CNX_FILES. The distance a keyword pair had befor connection
# can be found at the same position as in NEW_CNX_FILES
DIST_FILES			= "data/dist/dist_{}_{}.list" # .format(category, year)

