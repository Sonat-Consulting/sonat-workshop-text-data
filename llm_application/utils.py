import re
from qdrant_client.http import models

source_map = {
    'brreg': 'BRONNOYSUND',
}

def get_source(source):
    for k in source_map:
        if k in source:
            return source_map[k]
        
def get_query_filter(options):
    filters = []

    for option in options:
        filters.append(models.FieldCondition(key="metadata.source", match=models.MatchValue(value=option)))
    return models.Filter(should=filters)

def get_url_from_filename(filename):
    name = filename
    # Extract site prefix and index from the filename
    site_prefix = re.match(r"([a-zA-Z]+)", name).group(1)
    index = int(re.search(r"(\d+)", name).group(1))

    # Construct the URLs file name
    urls_filename = f"{site_prefix}.txt"

    # Read the URLs from the URLs file
    with open(urls_filename, "r") as file:
        url_list = file.read()
        url_list = url_list.split("\n")
    # Get the URL based on the index
    if 0 <= index <= len(url_list):
        url = url_list[index]
        return url
    else:
        return None