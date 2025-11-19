import cmipld
from cmipld.utils.ldparse import name_entry

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/project/graph.jsonld", depth=2)
    entry = next((item for item in data if item.get('id') == f'{me}'), None)
    if not entry: return None
    return f"{path}/{name}_{me}.json", me, name_entry(entry)
