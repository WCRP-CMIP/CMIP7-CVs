# CMIP7 Source/Model Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Model/Source',
    'description': 'Register a climate model or data source for CMIP7',
    'title': 'Add/Modify: Source: <Type source_id here>',
    'labels': ['delta', 'source', 'Review'],
    'issue_category': ['source']
}

import cmipld
from cmipld.utils.ldparse import name_extract, name_multikey_extract

# Data for this template
DATA = {
    'activity': name_multikey_extract(
        cmipld.get('cmip7:project/activity.json', depth=1)['activity'],
        ['id', 'validation_key'], 'validation_key'
    ),
    'cohort': [
        'Published',
        'Registered', 
        'Preliminary'
    ],
    'institution': name_multikey_extract(
        cmipld.get('universal:institution/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    'license_info': name_multikey_extract(
        cmipld.get('universal:license/graph.jsonld', depth=0),
        ['id', 'validation_key'], 'validation_key'
    ),
    'issue_category': ['source'],
    'issue_kind': ['New', 'Modify']
}
