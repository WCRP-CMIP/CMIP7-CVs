import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version
import os 

me = __file__.split('/')[-1].replace('.py','')

def run(io,whoami,path,name,**kwargs):

    qurl = f'{io}/project/graph.jsonld'
    
    data = cmipld.get(qurl,depth=2)["@graph"]
  
    # Find the index-list entry in the graph
    index_entry = None
    for item in data:
        if item.get('id') == 'index-list':
            index_entry = item
            break
    
    if not index_entry:
        print('index-list not found in project data')
        return None
    
    summary = name_entry(index_entry)
    
    location = f'{path}/{name}_{me}.json'
    
    return location,me,summary
