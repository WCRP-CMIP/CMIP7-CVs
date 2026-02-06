# Scientific Domain Template Data
# Configuration is in realm.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available scientific domains from WCRP-constants
    'realm': name_extract(cmipld.get('constants:scientific_domain/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_realm': name_multikey_extract(
        cmipld.get('cmip7:project/realm.json', depth=2).get('realm', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
