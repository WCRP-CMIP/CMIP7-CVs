# Frequency Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Frequency',
    'description': 'Add frequency to CMIP7 CVs',
    'title': 'Add/Modify: Frequency: <Type frequency name here>',
    'labels': ['delta', 'frequency', 'Review'],
    'issue_category': 'frequency'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'frequency': name_extract(cmipld.get('universal:frequency/graph.jsonld', depth=0)['@graph'])
}
