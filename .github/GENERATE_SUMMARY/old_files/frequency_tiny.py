"""Simple frequency summary"""
import cmipld
from cmipld.utils.ldparse import name_entry

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/project/graph.jsonld", depth=2)["@graph"]
    entry = next((item for item in data if item.get('id') == 'frequency-list'), None)
    if not entry: return None
    
    summary = name_entry(entry)
    return f"{path}/{name}_frequency.json", "frequency", summary
