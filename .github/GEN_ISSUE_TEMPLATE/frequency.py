# Frequency Template Data
# Configuration is in frequency.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
_cmip7_frequencies = name_extract(
    cmipld.get('cmip7:project/frequency.json', depth=2).get('frequency', {})
)

DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available frequencies from WCRP-constants
    'frequency': name_extract(cmipld.get('constants:frequency/graph.jsonld', depth=0)),
    # Currently registered in CMIP7 (pre-formatted as bullet list)
    'cmip7_frequency': '- ' + '\n- '.join(_cmip7_frequencies) if _cmip7_frequencies else 'None registered yet'
}
