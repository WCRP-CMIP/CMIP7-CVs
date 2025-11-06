# Activity Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Activity',
    'description': 'Add activity to CMIP7 CVs',
    'title': 'Add/Modify: Activity: <Type activity name here>',
    'labels': ['delta', 'activity', 'Review'],
    'issue_category': 'activity'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'activity': name_extract(cmipld.get('universal:activity/graph.jsonld', depth=0)['@graph'])
}
