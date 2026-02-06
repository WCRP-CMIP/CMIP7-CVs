# Region Template Data
# Configuration is in region.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
# Note: Regions may be CMIP7-specific or from WCRP-constants
DATA = {
    'issue_kind': ['New', 'Modify'],
    'region': name_extract(cmipld.get('constants:region/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_region': name_multikey_extract(
        cmipld.get('cmip7:project/region.json', depth=2).get('region', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
