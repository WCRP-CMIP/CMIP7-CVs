import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(localhost,whoami,repopath,reponame):

    url = f'{localhost}/{whoami}/experiment/graph.jsonld'
    ctx = f'{localhost}/{whoami}/experiment/_context_'
    
    frame = {"@context": ctx, "@type": "wcrp:experiment"}
    
    data = cmipld.get(url)["@graph"]
    
    
    location = f'{repopath}/{reponame}_experiment_list.csv'
    
    write = 'Name,Long_Name,Description,Activity,Tier,MinYears\n'
    
    for i in data:
        try:
            name = i['label']
            long_name = i.get('long-label', 'missing')
            description = i['description']
            activity = i['activity']
            tier = i['tier']
            minyears = i.get('min-number-yrs-per-sim', 'unknown')
            write += f'{name},{long_name},{description},{activity},{tier},{minyears}\n'
        except Exception as e:
            print(f"Error processing item {i}: {e}")
            continue
    
    # do not use main writing routine
    print(f'Writing to {location}')
    with open(location,'w') as f:
        f.write(write)
    
    # return location,me,write