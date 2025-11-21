import cmipld
from cmipld.utils.ldparse import name_entry
me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f'cmip7:project/{me}.json', depth=2)[me]
    summary = name_entry(data)
    
    
    # update the name to use the id field
    return f"{path}/{whoami}_{me}.json", me, summary
