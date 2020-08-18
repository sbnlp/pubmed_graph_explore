# Evolution of innovation in biomedical sciences
### A network-based characterization on a subset of PubMed

---

Skripts to perform a graph analysis and produce simple plots as given in the paper are provided in this repository.

### Prequisites
 - python modules:
    - [MySQL/Connector](https://dev.mysql.com/doc/connector-python/en/) 
    - [NetworkX](http://networkx.github.io/)
    - [Plotly graphing libraries](https://plotly.com/graphing-libraries/)

### Contents

| File | Use | Output | Remarks |
| --- | --- | --- | --- |
| config.py | --- | --- | defines globals and file locations. See *setup* |
| general.py | --- | --- | helper functions |
| clustering.py | python clustering.py | plot comparing the average clustering coefficients of all graphs | --- |
| connection_distance.py | connection_distance.py [-h] [--key_type KEY_TYPE] | plot depicting in what distance keywords are before a connection is created | --- |
| density.py | python density.py | plot comparing the density of all graphs | --- |
| find_connecting_paper.py |find_connecting_paper.py [-h] --id1 ID1 [--cat1 CAT1] [--kw1 KW1] --id2 ID2 [--cat2 CAT2] [--kw2 KW2] [--n N] | outputs some N papers co-mentioning keywords with ID1 and ID2 in their abstract | --- |
| graph_size.py | python graph_size.py | Plot comparing number of keywords in 'chemical', 'disease', 'gene' and full graph | --- | 
| keyword_stats.py | python keyword_stats.py | Creates 4 types of plots: *'keyword_occurrence'*: Keyword occurrences in all papers (counting duplicates) *'active_keywords_rate'*: rate of keywords known until a year that occur in that year, *'new_keywords'*: New keywords and keyword 'vocabulary' process, '*new_keywords_rate'*: Rate keyword introductions to all keyword occurrences | created in one script since the plots are based on the same data |
| keywords_per_paper.py | python keywords_per_paper.py | figure depicting the mean number of keywords per paper, comparing the keyword categories | --- | 
| papers_per_year.py | papers_per_year.py [-h] [--key_type KEY_TYPE] | ounts publications per year and keyword type. Joins result into a single figure. | --- | 
| shortest_paths.py | shortest_path.py [-h] [--samples SAMPLES] | estimation of the average length of the shortest path between not yet connected keywords | --- | 
| towards_connection_sankey.py | towards_connection_sankey.py [-h] [--key_type KEY_TYPE] [--year YEAR] [--samples SAMPLES] [--mode {connected,unconnected}] | plotly figure depicting evolution of the distance between a (sampled) set of keyword pairs over time | --- |

### Setup

Please contact us for access to the data these scripts were designed for. 
Before running the scripts, make sure to set the correct file paths in config.py.