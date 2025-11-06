# Grid Label Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Grid Label',
    'description': 'Add grid label to CMIP7 CVs',
    'title': 'Add/Modify: Grid Label: <Type grid label here>',
    'labels': ['delta', 'grid-label', 'Review'],
    'issue_category': 'grid_label'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'grid_label': name_extract(cmipld.get('universal:grid_label/graph.jsonld', depth=0)['@graph'])
}
