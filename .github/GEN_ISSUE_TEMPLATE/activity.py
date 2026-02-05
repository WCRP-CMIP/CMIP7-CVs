# Activity Template Data
# Configuration is in activity.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'activity': name_extract(cmipld.get('constants:activity/graph.jsonld', depth=0))
}
