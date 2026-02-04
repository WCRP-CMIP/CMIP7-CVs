# Frequency Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Frequency',
    'description': 'Add frequency to CMIP7 CVs',
    'title': 'New Review submission : Frequency:',
    'labels': ['delta', 'frequency', 'Review'],
    'issue_category': 'frequency'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'frequency': name_extract(cmipld.get('constants:frequency/graph.jsonld', depth=0))
}
