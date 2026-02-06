# Frequency Template Data
# Configuration is in frequency.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available frequencies from WCRP-constants
    'frequency': name_extract(cmipld.get('constants:frequency/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_frequency': name_multikey_extract(
        cmipld.get('cmip7:project/frequency.json', depth=2).get('frequency', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
