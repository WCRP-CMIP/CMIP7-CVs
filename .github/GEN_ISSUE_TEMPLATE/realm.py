# Scientific Domain Template Configuration
# (Previously called "realm" - updated to use correct WCRP terminology)

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Scientific Domain',
    'description': 'Add scientific domain to CMIP7 CVs',
    'title': 'New Review submission : Scientific Domain:',
    'labels': ['delta', 'scientific_domain', 'Review'],
    'issue_category': 'scientific_domain'
}

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
DATA = {
    'issue_kind': ['New', 'Modify'],
    'realm': name_extract(cmipld.get('constants:scientific_domain/graph.jsonld', depth=0))
}
