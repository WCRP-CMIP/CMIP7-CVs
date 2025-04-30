import cmipld 
from cmipld.utils.server_tools.offline import LD_server


ldpath = cmipld.utils.io.ldpath() 

repo_url = cmipld.utils.git.url()
io_url = cmipld.utils.git.url2io(repo_url)
whoami = cmipld.reverse_mapping()[io_url]

localserver = LD_server( copy=[[ldpath, whoami]], override='y')
localhost = localserver.start_server(8084)


# we need not to get this, we just call it the same as the repo

# cmipld.jsonld.expand('cmip7:_context_',)
import requests
rq = requests.get('cmip7:_context_')
print(rq.json())
# LD server should provide the redirect paths 


ld = cmipld.jsonld.expand('universal:activity/lesfmip',)
print(ld)