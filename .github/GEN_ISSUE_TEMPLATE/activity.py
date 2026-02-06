# Activity Template Data
# Configuration is in activity.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
_cmip7_activities = name_extract(
    cmipld.get('cmip7:project/activity.json', depth=2).get('activity', {})
)

DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available activities from WCRP-constants
    'activity': name_extract(cmipld.get('constants:activity/graph.jsonld', depth=0)),
    # Currently registered in CMIP7 (pre-formatted as bullet list)
    'cmip7_activity': '- ' + '\n- '.join(_cmip7_activities) if _cmip7_activities else 'None registered yet'
}
