import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(localhost,whoami,repopath,reponame):

    url = f'{localhost}/{whoami}/experiment/graph.jsonld'
    ctx = f'{localhost}/{whoami}/experiment/_context_'
    
    data = cmipld.jsonld.frame(url,ctx)["@graph"]
    
    summary = name_extract(data)
    
    summary = {k:key_extract(v,['long_label','description']) for k,v in summary.items()}
    
    location = f'{repopath}/{reponame}_{me}.json'
    summary = version(summary, me, location.split("/")[-1])
    cmipld.utils.io.wjsn(summary,location)
