# Native Nominal Resolution Template Data
# Configuration is in native_nominal_resolution.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'native_nominal_resolution': name_extract(cmipld.get('constants:resolution/graph.jsonld', depth=0))
}
