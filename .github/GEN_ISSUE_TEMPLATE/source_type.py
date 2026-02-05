# Source Type Template Data
# Configuration is in source_type.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'source_type': name_extract(cmipld.get('constants:source_type/graph.jsonld', depth=0))
}
