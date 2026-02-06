# Source Type Template Data
# Configuration is in source_type.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available source types from WCRP-constants
    'source_type': name_extract(cmipld.get('constants:source_type/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_source_type': name_multikey_extract(
        cmipld.get('cmip7:project/source_type.json', depth=2).get('source_type', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
