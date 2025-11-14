# CMIPLD Experiment Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Add/Modify: Experiment',
    'description': 'Type: experiment',
    'title': 'Add/Modify: Experiment: <Type experiment name here>',
    'labels': ['delta', 'experiment', 'Review'],
    'issue_category': ['experiment']
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'activity': {"None Specified":{'validation-key': 'None Specified'},
                 **dict(cmipld.utils.ldparse.name_extract(cmipld.get('cmip7:project/activity.json',depth=1)['activity']))  
    },  
    'parent_experiment': {
        "Custom Parent: specify in 'Parent experiment other' field": {'id': 'custom-parent', 'validation-key': 'custom-parent'},
        'no-parent': {'id': 'no-parent', 'validation-key': 'no-parent'},
        ** name_multikey_extract(
            cmipld.get('cmip7:experiment/graph.jsonld',depth=0)['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        ),
    },
    'tier': ['Tier 1', 'Tier 2', 'Tier 3'],
    'model_components': 
        name_multikey_extract(
        cmipld.get('universal:source_type/graph.jsonld',depth=0)['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'milestone': ['Review'],
    'issue_kind': ['New', 'Modify']
}

