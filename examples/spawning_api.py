# make sure SPAWNING_OPTS_KEY environment variable is set first

import datadiligence as dd
from pyarrow import csv

# read csv/tsv file
md = csv.read_csv("~/Downloads/cc40k.tsv", read_options=csv.ReadOptions(encoding="utf-8"), parse_options=csv.ParseOptions(delimiter='\t'))

# convert it to list
d = md.select(["url"]).to_pandas()
urls = d.iloc[:, 0].to_list()

# send through pre-process steps (only includes Spawning API currently)
verified_urls = dd.filter_allowed(urls=urls)
