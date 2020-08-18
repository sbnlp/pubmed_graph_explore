# ---------------------------------------------------------------- #
# Evolution of innovation in biomedical sciences
# A network-based characterization on a subset of PubMed
# ---------------------------------------------------------------- #
#
# Helper script to get papers stating a connection between two keywords.
# (Keywords co-appear in the paper's abstract)
#
# Python 3
# Author: Karla Friedrichs
# ---------------------------------------------------------------- #

import argparse

from config import CATEGORIES, CATEGORY_IDS

def parse_args():
	"""
	Parses the command line arguments.
	"""
	parser = argparse.ArgumentParser(description="Helper script to get papers stating a connection between two keywords.")

	parser.add_argument("--id1", type=str, required=True,
						help="first keyword identier")
	parser.add_argument("--cat1", type=str, default=None,
						help="category of first keyword")
	parser.add_argument("--kw1", type=str, default="",
						help="first keyword (string)")
	parser.add_argument("--id2", type=str, required=True,
						help="second keyword identier")
	parser.add_argument("--cat2", type=str, default=None,
						help="category of second keyword")
	parser.add_argument("--kw2", type=str, default="",
						help="second keyword (string)")
	parser.add_argument("--n", type=int, default=1,
						help="number of papers to return at most")
	
	return parser.parse_args()

def find_paper_making_cnx(kw1, kw2, kw1_cat, kw2_cat, max_papers=1):
	"""
	Returns one (or more) paper mentioning both keywords in its abstract.
	"""
	assert kw1_cat in CATEGORIES and kw2_cat in CATEGORIES, "Error: At least one faulty category: {}, {}. Possible categories: {}".format(kw1_cat, kw2_cat, CATEGORIES)
	# Collect all papers containing kw1
	cat1_papers = open(CATEGORY_IDS.format(kw1_cat), mode="r")
	kw1_papers = set() # Pubmed ids of papers containing first keyword
	for line in cat1_papers:
		if line.startswith("#"): continue
		line = line.strip().split("\t")
		if len(line) != 4: continue # PMID, keyword id, keyword, method
		if line[1] == kw1:
			kw1_papers.add(line[0])
	cat1_papers.close()

	# Return first paper(s) that also contains kw2
	connecting_papers = list()
	cat2_papers = open(CATEGORY_IDS.format(kw2_cat), mode="r")
	for line in cat2_papers:
		if line.startswith("#"): continue
		line = line.strip().split("\t")
		if len(line) != 4: continue # PMID, keyword id, keyword, method
		if line[0] in kw1_papers:
			if line[1] == kw2:
				connecting_papers.append(line[0])
				if len(connecting_papers) == max_papers:
					break
	cat2_papers.close()
	return connecting_papers
	
if __name__ == "__main__":
	args = parse_args()
	
	# guess categories for keywords by prefix if not given in command line
	if args.cat1 != None:
		cat1 = [args.cat1]
	elif args.id1.startswith("CHEBI"):
		cat1 = ["chemical"]
	elif args.id1.startswith("MESH"):
		cat1 = ["chemical", "disease"]
	else:
		cat1 = ["gene"]
	if args.cat2 != None:
		cat2 = [args.cat2]
	elif args.id2.startswith("CHEBI"):
		cat2 = ["chemical"]
	elif args.id2.startswith("MESH"):
		cat2 = ["chemical", "disease"]
	else:
		cat2 = ["gene"]
		
	connecting_papers = list()
	for c1 in cat1:
		for c2 in cat2:
			connecting_papers.extend(find_paper_making_cnx(args.id1, args.id2, c1, c2, max_papers=args.n))
			# stop if papers were found, other categories don't need to be checked
			if len(connecting_papers) > 0: break
		if len(connecting_papers) > 0: break
	
	if len(args.kw1) > 0: kw1 = " ({})".format(args.kw1)
	else: kw1 = ""
	if len(args.kw2) > 0: kw2 = " ({})".format(args.kw2)
	else: kw2 = ""
	
	print("First paper(s) connecting {}{} to {}{}: {}".format(args.id1, kw1, args.id2, kw2, connecting_papers))
