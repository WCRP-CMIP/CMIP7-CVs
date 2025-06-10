import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(io,whoami,path,name,**kwargs):

    url = f'{io}/experiment/graph.jsonld'
    ctx = f'{io}/experiment/_context_'
    
    # frame = {"@context": ctx, "@type": "wcrp:experiment"}
    
    data = cmipld.get(url,depth=2)["@graph"]
    
    # framed = cmipld.jsonld.frame(data,frame)["@graph"]
    
    
    location = f'{path}/{name}_experiment_list.csv'
    
    write = ' Name (Validation-Key),UI-Label,Description,Activity,Tier,MinYears\n'
    
    for i in data:
        try:
            name = i['label']
            long_name = i.get('long-label', 'missing')
            description = i['description']
            activity = i['activity']['label']
            tier = i['tier']
            minyears = i.get('min-number-yrs-per-sim', 'unknown')
            
            write += f'"{name}"∂"{long_name}"∂"{description}"∂"{activity}"∂"{tier}"∂"{minyears}"\n'.replace('∂',',')
        except Exception as e:
            print(f"Error processing item {i}: {e}")
            continue
    
    # do not use main writing routine
    print(f'Writing to {location}')
    with open(location,'w') as f:
        f.write(write)
    
    # return location,me,write