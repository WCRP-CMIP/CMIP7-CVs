# Source Type Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Source Type',
    'description': 'Add source type to CMIP7 CVs',
    'title': 'New Review submission : Source Type:',
    'labels': ['delta', 'source-type', 'Review'],
    'issue_category': 'source_type'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'source_type': name_extract(cmipld.get('constants:source_type/graph.jsonld', depth=0))
}
