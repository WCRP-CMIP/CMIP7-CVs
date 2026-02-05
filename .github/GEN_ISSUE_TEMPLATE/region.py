# Region Template Data
# Configuration is in region.json

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
