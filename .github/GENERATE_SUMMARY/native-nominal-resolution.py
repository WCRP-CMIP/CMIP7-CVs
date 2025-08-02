import cmipld
from cmipld.utils.ldparse import name_entry

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f"{io}/project/{me}-list.json", depth=1).get(me)

    if not data: return None
    return f"{path}/{name}_{me}.json", me, data
