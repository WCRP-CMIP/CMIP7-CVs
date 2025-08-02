import cmipld
from cmipld.utils.ldparse import name_entry

me = __file__.split('/')[-1].replace('.py','')
print(me)

def run(io, whoami, path, name, **kwargs):
    
    
    print(cmipld.jsonld.expand(f"{io}/project/{me}-list.json"))
    
    data = cmipld.get(f"{io}/project/{me}-list.json", depth=2)[me]
    print(data)

    if not data: return None
    return f"{path}/{name}_{me}.json", me, data
# name_entry(data)
