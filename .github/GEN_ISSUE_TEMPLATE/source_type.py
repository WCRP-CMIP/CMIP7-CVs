# Source Type Template Data
# Configuration is in source_type.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
_cmip7_source_types = name_extract(
    cmipld.get('cmip7:project/source_type.json', depth=2).get('source_type', {})
)

DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available source types from WCRP-constants
    'source_type': name_extract(cmipld.get('constants:source_type/graph.jsonld', depth=0)),
    # Currently registered in CMIP7 (pre-formatted as bullet list)
    'cmip7_source_type': '- ' + '\n- '.join(_cmip7_source_types) if _cmip7_source_types else 'None registered yet'
}
