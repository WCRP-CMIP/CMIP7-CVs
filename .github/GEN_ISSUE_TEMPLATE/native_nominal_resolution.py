# Native Nominal Resolution Template Data
# Configuration is in native_nominal_resolution.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available resolutions from WCRP-constants
    'native_nominal_resolution': name_extract(cmipld.get('constants:resolution/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_resolution': name_multikey_extract(
        cmipld.get('cmip7:project/native_nominal_resolution.json', depth=2).get('native_nominal_resolution', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
