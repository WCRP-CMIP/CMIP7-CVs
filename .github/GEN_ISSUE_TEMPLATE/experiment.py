# CMIPLD Experiment Template Configuration

TEMPLATE_CONFIG = {
    'name': 'New Review submission : Experiment',
    'description': 'Type: experiment',
    'title': 'New Review submission : Experiment:',
    'labels': ['delta', 'experiment', 'Review'],
    'issue_category': ['experiment']
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template
DATA = {
    'activity': {"None Specified":{'validation_key': 'None Specified'},
                 **dict(cmipld.utils.ldparse.name_extract(cmipld.get('cmip7:project/activity.json',depth=2)['activity']))  
    },  
    'parent_experiment': {
        "Custom Parent: specify in 'Parent experiment other' field": {'id': 'custom-parent', 'validation_key': 'custom-parent'},
        'no-parent': {'id': 'no-parent', 'validation_key': 'no-parent'},
        ** name_multikey_extract(
            cmipld.get('cmip7:experiment/graph.jsonld',depth=0),
            ['id','validation_key','ui-label'],'validation_key'
        ),
    },
    'tier': ['1', '2', '3'],
    'model_components': 
        name_multikey_extract(
        cmipld.get('constants:source_type/graph.jsonld',depth=0),
        ['id','validation_key','ui-label'],'validation_key'
    ),
    'milestone': ['Review'],
    'issue_kind': ['New', 'Modify']
}

