# Frequency Template Data
# Configuration is in frequency.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'frequency': name_extract(cmipld.get('constants:frequency/graph.jsonld', depth=0))
}
