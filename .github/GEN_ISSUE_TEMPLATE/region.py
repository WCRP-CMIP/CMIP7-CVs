# Region Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Region',
    'description': 'Add region to CMIP7 CVs',
    'title': 'New Review submission : Region:',
    'labels': ['delta', 'region', 'Review'],
    'issue_category': 'region'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'region': {
        'ant': 'Antarctica',
        'glb': 'Global',
        'gre': 'Greenland',
        'nhem': 'Northern Hemisphere',
        'shem': 'Southern Hemisphere'
    }
}
