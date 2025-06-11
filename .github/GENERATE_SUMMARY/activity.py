import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version
from cmipld.utils.logging.unique import UniqueLogger
log = UniqueLogger()
import os 

me = __file__.split('/')[-1].replace('.py','')

def run(whoami,path,name,url,io):


    qurl = f'{io}/project/graph.jsonld'
    # ctx = f'{localhost}/{whoami}/project/_context_'
    
    data = cmipld.get(qurl,depth=2)["@graph"]
  
    summary = name_entry(data[me])
    

    location = f'{path}/{name}_{me}.json'
    # summary = version(summary, me, location.split("/")[-1])

    
    # summary = version(summary, me, location.split("/")[-1])
    
    # if os.path.exists(location):
    #     old = cmipld.utils.io.jr(location)
    #     if old['Header']['checksum'] == summary['Header']['checksum']:
    #         return log.error('no update - file already exists')
        
    print('old',location)
    log.debug(f'Writing to {location}')
    # cmipld.utils.io.wj(summary,location)
    
    return location,me,summary
    
    # print(json.dumps(summary,indent=4))