# CMIP7 Source/Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Model/Source',
    'description': 'Register a climate model or data source for CMIP7',
    'title': 'New Review submission : Source:',
    'labels': ['delta', 'source', 'Review'],
    'issue_category': ['source']
}

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'activity': name_multikey_extract(
        cmipld.get('cmip7:project/activity.json', depth=2)['activity'],
        ['id', 'validation_key'], 'validation_key'
    ),
    'cohort': [
        'Published',
        'Registered', 
        'Preliminary'
    ],
    'institution': name_multikey_extract(
        cmipld.get('constants:organisation/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    'license_info': name_multikey_extract(
        cmipld.get('constants:license/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    'model_documentation': {
        "un-registered": {'id': 'unregistered', 'validation_key': 'unregistered'},
        **name_multikey_extract(
            cmipld.get('emd:model/graph.jsonld', depth=0),
            ['id', 'validation_key'], 'validation_key')
    },    
        
    'issue_category': ['source'],
    'issue_kind': ['New', 'Modify']
}
