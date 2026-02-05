# Scientific Domain Template Data
# Configuration is in realm.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'realm': name_extract(cmipld.get('constants:scientific_domain/graph.jsonld', depth=0))
}
