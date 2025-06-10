import cmipld 
from cmipld.utils.server_tools.offline import LD_server


ldpath = cmipld.utils.io.ldpath() 

repo_url = cmipld.utils.git.url()
io_url = cmipld.utils.git.url2io(repo_url)
whoami = cmipld.reverse_mapping()[io_url]

localserver = LD_server( copy=[[ldpath, whoami]], override='y')
localhost = localserver.start_server(8084)

from cmipld.utils.server_tools.loader import Loader
loader = Loader(tries=3)

url = 'cmip7:experiment/graph.jsonld'
url = 'https://wcrp-cmip.github.io/CMIP7-CVs/experiment/esm-scen7-h.json'
# url = 'https://wcrp-cmip.github.io/CMIP7-CVs/experiment/abrupt-127k.json'
print(cmipld.jsonld.expand(url))
cmipld.view(url)
# cmipld.utils.display_depends(url, prefix=True, relative=True)

import json,requests
# print(json.dumps(requests.get(url).json(), indent=2))

# print(cmipld.utils.depends(url, prefix=False, relative=True))



# cmipld.utils.view(url, compact=True, depth=2)
# print('done')


