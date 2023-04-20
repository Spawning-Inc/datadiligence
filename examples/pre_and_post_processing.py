# make sure SPAWNING_OPTS_KEY environment variable is set first

import datadiligence as dd
from pyarrow import csv
import requests

# read csv/tsv file
md = csv.read_csv("/path/to/urls.tsv", read_options=csv.ReadOptions(encoding="utf-8"), parse_options=csv.ParseOptions(delimiter='\t'))

# convert it to list
d = md.select(["url"]).to_pandas()
urls = d.iloc[:, 0].to_list()

# send through pre-process steps (only includes Spawning API currently)
verified_urls = dd.filter_allowed(urls=urls)  # use dd.is_allowed to get a list of booleans instead

# you'll probably be downloading these images in your pipeline, this is a placeholder for that
for url in verified_urls:
    response = requests.get(url)
    if response.status_code == 200:
        # this is the only new code you need here
        is_allowed = dd.is_allowed(response=response)
        if not is_allowed:
            continue

        # image is allowed after this point
