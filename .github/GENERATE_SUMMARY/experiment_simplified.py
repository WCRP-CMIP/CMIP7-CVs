import cmipld
from cmipld.utils.ldparse import name_extract, key_extract, name_entry

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/experiment/graph.jsonld", depth=1)
    full = name_extract(data)
    # summary = {k: key_extract(v, ['ui-label', 'description']) for k, v in full.items()}
    summary = name_entry(data, 'ui-label')
    
    return f"{path}/{name}_{me}.json", me, summary
