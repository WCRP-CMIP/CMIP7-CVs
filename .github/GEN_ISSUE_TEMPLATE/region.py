# Region Template Data
# Configuration is in region.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
_cmip7_regions = name_extract(
    cmipld.get('cmip7:project/region.json', depth=2).get('region', {})
)

DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available regions from WCRP-constants
    'region': name_extract(cmipld.get('constants:region/graph.jsonld', depth=0)),
    # Currently registered in CMIP7 (pre-formatted as bullet list)
    'cmip7_region': '- ' + '\n- '.join(_cmip7_regions) if _cmip7_regions else 'None registered yet'
}
