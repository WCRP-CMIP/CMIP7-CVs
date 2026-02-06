# Activity Template Data
# Configuration is in activity.json

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available activities from WCRP-constants
    'activity': name_extract(cmipld.get('constants:activity/graph.jsonld', depth=0)),
    # Currently registered in CMIP7
    'cmip7_activity': name_multikey_extract(
        cmipld.get('cmip7:project/activity.json', depth=2).get('activity', {}),
        ['id', 'ui-label'], 'ui-label'
    )
}
