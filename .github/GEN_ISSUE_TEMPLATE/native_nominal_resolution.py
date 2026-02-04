# Native Nominal Resolution Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Resolution',
    'description': 'Add resolution to CMIP7 CVs',
    'title': 'New Review submission : Resolution:',
    'labels': ['delta', 'resolution', 'Review'],
    'issue_category': 'native_nominal_resolution'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'native_nominal_resolution': name_extract(cmipld.get('constants:resolution/graph.jsonld', depth=0))
}
