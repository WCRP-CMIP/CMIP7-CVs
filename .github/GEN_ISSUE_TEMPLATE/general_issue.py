# General Issue Template Configuration

TEMPLATE_CONFIG = {
    'name': 'General Issue',
    'description': 'Report a general issue, bug, or request',
    'title': 'Issue: <Brief description here>',
    'labels': ['cmip7', 'general'],
    'issue_category': 'general'
}

# Data for this template
DATA = {
    'issue_type_options': [
        'Bug Report',
        'Feature Request',
        'Documentation Issue',
        'Data Quality Issue',
        'Process Improvement',
        'Other'
    ],
    'affected_areas_options': [
        'Controlled Vocabularies (CVs)',
        'Documentation',
        'GitHub Actions/Workflows',
        'Data Files',
        'Scripts/Tools',
        'Issue Templates',
        'General Repository Structure',
        'All/Multiple Areas'
    ],
    'priority_options': [
        'Critical - Blocking work',
        'High - Important issue',
        'Medium - Should be addressed',
        'Low - Nice to fix'
    ],
    'help_needed_options': [
        'I can work on this myself',
        'I need help implementing a solution',
        "I'm just reporting this issue"
    ]
}
