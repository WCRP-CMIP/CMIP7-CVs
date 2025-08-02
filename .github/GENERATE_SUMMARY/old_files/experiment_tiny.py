"""Simple experiment summary"""
import cmipld
from cmipld.utils.ldparse import name_extract

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/experiment/graph.jsonld", depth=1)["@graph"]
    summary = name_extract(data)
    return f"{path}/{name}_experiment.json", "experiment", summary
