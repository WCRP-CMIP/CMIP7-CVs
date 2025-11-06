# Native Nominal Resolution Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Resolution',
    'description': 'Add resolution to CMIP7 CVs',
    'title': 'Add/Modify: Resolution: <Type resolution here>',
    'labels': ['delta', 'resolution', 'Review'],
    'issue_category': 'native_nominal_resolution'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'native_nominal_resolution': name_extract(cmipld.get('universal:resolution/graph.jsonld', depth=0)['@graph'])
}
