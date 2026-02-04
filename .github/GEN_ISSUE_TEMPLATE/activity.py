# Activity Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Activity',
    'description': 'Add activity to CMIP7 CVs',
    'title': 'New Review submission : Activity:',
    'labels': ['delta', 'activity', 'Review'],
    'issue_category': 'activity'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'activity': name_extract(cmipld.get('constants:activity/graph.jsonld', depth=0))
}
