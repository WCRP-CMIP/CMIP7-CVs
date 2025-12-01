import cmipld
from cmipld.utils.ldparse import key_extract
me = __file__.split('/')[-1].replace('.py','')
def run(io, whoami, path, name, **kwargs):
    data = cmipld.get(f'cmip7:project/{me}.json', depth=2)[me]
    summary = key_extract(data,['description','regex'])
    
    
    # update the name to use the id field
    return f"{path}/{whoami}_{me}.json", me, summary
