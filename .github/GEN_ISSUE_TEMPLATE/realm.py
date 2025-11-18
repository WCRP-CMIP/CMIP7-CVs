# Realm Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Realm',
    'description': 'Add realm to CMIP7 CVs',
    'title': 'Add/Modify: Realm: <Type realm name here>',
    'labels': ['delta', 'realm', 'Review'],
    'issue_category': 'realm'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'realm': name_extract(cmipld.get('universal:realm/graph.jsonld', depth=0))
}
