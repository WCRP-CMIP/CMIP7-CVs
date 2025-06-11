import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(whoami,path,name,io,**kwargs):

    url = f'{io}experiment/graph.jsonld'
    ctx = f'{io}experiment/_context_'
    
    frame = {"@context": ctx, "@type": "wcrp:experiment"}
    
    data = cmipld.jsonld.frame(url,frame)["@graph"]
    
    summary = name_extract(data)
    
    summary = {k:key_extract(v,['long-label','description']) for k,v in summary.items()}
    
    location = f'{path}/{name}_{me}.json'
    # summary = version(summary, me, location.split("/")[-1])
    # cmipld.utils.io.wjsn(summary,location)
    
    return location,me,summary
