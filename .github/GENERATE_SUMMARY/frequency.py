import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version
import os 

me = __file__.split('/')[-1].replace('.py','')

def run(io,whoami,path,name,**kwargs):

    qurl = f'{io}/project/graph.jsonld'
    
    data = cmipld.get(qurl,depth=2)["@graph"]
  
    # Find the frequency-list entry in the graph
    frequency_entry = None
    for item in data:
        if item.get('id') == 'frequency-list':
            frequency_entry = item
            break
    
    if not frequency_entry:
        print('frequency-list not found in project data')
        return None
    
    summary = name_entry(frequency_entry)
    
    location = f'{path}/{name}_{me}.json'
    
    return location,me,summary
