import cmipld
import json
from pprint import pprint
process = cmipld.JsonLdProcessor()


res = process.get(
    'https://wcrp-cmip.github.io/CMIP6Plus_CVs/project/tables.json')


# pprint(res)
print(json.dumps(res, indent=2))
