# Component Submission Template Configuration

TEMPLATE_CONFIG = {
    'name': 'Model Component Submission',
    'description': 'Submit metadata for a model component as specified in the EMD specification.',
    'title': '[EMD] Model Component Submission',
    'labels': ['emd-submission', 'component'],
    'issue_category': 'component'
}

import cmipld
from cmipld.utils.ldparse import *

# Data for this template - updated to match EMD property requirements
DATA = {
    'realms': name_multikey_extract(
        cmipld.get('universal:realm/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'horizontal_grid_types': {
        'no-horizontal-grid': {'id': 'no-horizontal-grid', 'validation-key': 'no-horizontal-grid'},
        ** name_multikey_extract(
            cmipld.get('universal:native-horizontal-grid-type/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    'grid_mappings': [
        'albers_conical_equal_area', 'azimuthal_equidistant', 'geostationary',
        'lambert_azimuthal_equal_area', 'lambert_conformal_conic', 'lambert_cylindrical_equal_area',
        'latitude_longitude', 'orthographic', 'polar_stereographic',
        'rotated_latitude_longitude', 'sinusoidal', 'stereographic',
        'transverse_mercator', 'vertical_perspective'
    ],
    'horizontal_regions': name_multikey_extract(
        cmipld.get('universal:native-horizontal-grid-region/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'temporal_refinements': name_multikey_extract(
        cmipld.get('universal:native-horizontal-grid-temporal-refinement/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'grid_arrangements': ['arakawa_A', 'arakawa_B', 'arakawa_C', 'arakawa_D', 'arakawa_E'],
    'truncation_methods': ['triangular', 'rhomboidal'],
    'nominal_resolutions': name_multikey_extract(
        cmipld.get('universal:resolution/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'vertical_coordinates': {
        'no-vertical-grid': {'id': 'no-vertical-grid', 'validation-key': 'no-vertical-grid'},
        ** name_multikey_extract(
            cmipld.get('universal:native-vertical-grid-coordinate/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    'vertical_units': name_multikey_extract(
        cmipld.get('universal:native-vertical-grid-units/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    'resolution_units': {
        'degrees': {'id': 'degrees', 'validation-key': 'degrees'},
        'km': {'id': 'km', 'validation-key': 'km'},
        'm': {'id': 'm', 'validation-key': 'm'}
    },
    # Issue tracking fields
    'issue_category_options': ['component'],
    'issue_kind_options': ['new', 'modify']
}
