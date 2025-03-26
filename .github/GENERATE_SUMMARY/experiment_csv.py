import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(localhost,whoami,repopath,reponame):

    url = f'{localhost}/{whoami}/experiment/graph.jsonld'
    ctx = f'{localhost}/{whoami}/experiment/_context_'
    
    data = cmipld.jsonld.frame(url,ctx)["@graph"]
    
    location = f'{repopath}/experiment_list.csv'
    
    write = 'Name,Long_Name,Description,Activity,Tier,MinYears\n'
    
    for i in data:
        name = i['label']
        long_name = i['long_label']
        description = i['description']
        activity = i['activity']
        tier = i['tier']
        minyears = i['min-number-yrs-per-sim'],
        write += f'{name},{long_name},{description},{activity},{tier},{minyears}\n'
    
    
    print(f'Writing to {location}')
    with open(location,'w') as f:
        f.write(write)