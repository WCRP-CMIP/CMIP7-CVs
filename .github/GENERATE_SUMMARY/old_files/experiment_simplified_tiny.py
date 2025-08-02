"""Simple experiment simplified summary"""
import cmipld
from cmipld.utils.ldparse import name_extract, key_extract

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/experiment/graph.jsonld", depth=1)["@graph"]
    full = name_extract(data)
    summary = {k: key_extract(v, ['long-label', 'description']) for k, v in full.items()}
    return f"{path}/{name}_experiment_simplified.json", "experiment_simplified", summary
