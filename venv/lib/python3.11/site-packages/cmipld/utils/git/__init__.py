from . import actions
from . import release
from . import tree
# Delay repo_info import to avoid circular dependency with jsontools
# from . import repo_info
from . import coauthors

from .git_core import *
from .git_branch_management import *
from .git_commit_management import *
from .git_issues import *
from .git_actions_management import *
from .git_pull_request import *
from .git_repo_metadata import *
from .git_api import *
from .gh_utils import *
from .coauthors import *

# Lazy import repo_info to avoid circular dependency
_repo_info = None

def __getattr__(name):
    global _repo_info
    if name == 'repo_info':
        if _repo_info is None:
            from . import repo_info as _ri
            _repo_info = _ri
        return _repo_info
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
