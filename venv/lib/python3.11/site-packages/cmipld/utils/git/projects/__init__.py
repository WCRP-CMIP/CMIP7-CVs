"""
GitHub Manager - A modular GitHub project management system
"""

from .issues import IssueManager
from .labels import LabelManager
from .milestones import MilestoneManager
from .projects import ProjectManager
from .teams import TeamManager
from .utils import GitHubUtils

__version__ = "1.0.0"
__all__ = [
    "IssueManager",
    "LabelManager", 
    "MilestoneManager",
    "ProjectManager",
    "TeamManager",
    "GitHubUtils"
]
