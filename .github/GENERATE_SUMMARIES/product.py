import cmipld
from cmipld.utils.ldparse import name_extract

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f'cmip7:project/{me}.json', depth=2)[me]
    summary = name_extract(data)
    return f"{path}/{name}_{me}.json", me, summary
