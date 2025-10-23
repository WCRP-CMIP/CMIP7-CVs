# -*- coding: utf-8 -*-
from .locations import *
# from pyld import jsonld

# from .utils.server_tools.offline import LD_server

# remap the requests links using prefixe mapping
from .utils.server_tools.monkeypatch_requests import RequestRedirector
redir = RequestRedirector({}, mapping)


from .utils.server_tools.loader import Loader
# Don't import everything from utils to avoid circular dependencies
# Import specific items as needed
from .utils.io import *
from .utils.write06 import *
from .utils.jsontools import *
from .utils import git 
from .utils.extract import *


loader = Loader(tries=3)



def reload(module=None):
    # nowork
    import sys
    if not module:
        module = sys.modules[__name__]

    import importlib
    del sys.modules[module.__name__]
    importlib.invalidate_caches()
    module = importlib.import_module(module.__name__)
    importlib.reload(module)
    print('Reloaded', module)



def expand(u):
    return jsonld.expand(resolve_url(u))


def getall(l):
    '''
    Get multiple items
    '''
    assert isinstance(l, list)
    return [expand(a) for a in l]

