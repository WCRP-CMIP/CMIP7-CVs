# Source Type Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Source Type',
    'description': 'Add source type to CMIP7 CVs',
    'title': 'Add/Modify: Source Type: <Type source type here>',
    'labels': ['delta', 'source-type', 'Review'],
    'issue_category': 'source_type'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'source_type': name_extract(cmipld.get('universal:source_type/graph.jsonld', depth=0)['@graph'])
}
