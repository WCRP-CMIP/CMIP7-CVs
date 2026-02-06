# Scientific Domain Template Data
# Configuration is in realm.json

import cmipld
from cmipld.utils.ldparse import name_extract

# Data for this template
_cmip7_realms = name_extract(
    cmipld.get('cmip7:project/realm.json', depth=2).get('realm', {})
)

DATA = {
    'issue_kind': ['New', 'Modify'],
    # Available scientific domains from WCRP-constants
    'realm': name_extract(cmipld.get('constants:scientific_domain/graph.jsonld', depth=0)),
    # Currently registered in CMIP7 (pre-formatted as bullet list)
    'cmip7_realm': '- ' + '\n- '.join(_cmip7_realms) if _cmip7_realms else 'None registered yet'
}
