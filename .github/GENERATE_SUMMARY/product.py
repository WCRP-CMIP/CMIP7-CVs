import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version
import os 

me = __file__.split('/')[-1].replace('.py','')

def run(io,whoami,path,name,**kwargs):

    qurl = f'{io}/project/graph.jsonld'
    
    data = cmipld.get(qurl,depth=2)["@graph"]
  
    # Find the product-list entry in the graph
    product_entry = None
    for item in data:
        if item.get('id') == 'product-list':
            product_entry = item
            break
    
    if not product_entry:
        print('product-list not found in project data')
        return None
    
    summary = name_entry(product_entry)
    
    location = f'{path}/{name}_{me}.json'
    
    return location,me,summary
