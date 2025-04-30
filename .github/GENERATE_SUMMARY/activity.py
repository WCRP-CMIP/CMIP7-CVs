import cmipld
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version
import os 

me = __file__.split('/')[-1].replace('.py','')

def run(localhost,whoami,repopath,reponame):
    import requests

    url = f'{localhost}/{whoami}/project/{me}-list.json'
    print(localhost)
    print(f'url: {url}')
    
    
    # os.system(f'curl -v {url} --insecure')
    # input('press enter to continue')
    
    
    
    # print(requests.get(url,verify=False).text)
    # # # ctx = f'{localhost}/{whoami}/project/_context_'
    
    
    
    input('press enter to continue')
    
    data = cmipld.get(url,depth=2)
    
    # data = cmipld.jsonld.expand(url)
    
    import json
    # print(json.dumps(data,indent=4))
    
    # data = cmipld.processor.loader(url,{})
    print(json.dumps(data,indent=4))
    
    print('-----')
    # summary = name_extract(data)
    
    location = f'{repopath}/{reponame}_{me}.json'
    print('location',location)
    # summary = version(summary, me, location.split("/")[-1])
    
    # if os.path.exists(location):
    #     old = cmipld.utils.io.jr(location)
    #     if old['Header']['checksum'] == summary['Header']['checksum']:
    #         return 'no update - file already exists'
    
    # # cmipld.utils.io.wjsn(summary,location)
    return location,me,data
# summary