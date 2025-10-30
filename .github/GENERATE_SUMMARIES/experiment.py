import cmipld
from cmipld.utils.ldparse import name_extract

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/{me}/graph.jsonld", depth=0)["@graph"]
    summary = name_extract(data)
    return f"{path}/{name}_{me}.json", me, summary
