# CSV Template System for GitHub Issue Forms

A simple system for generating GitHub issue templates from CSV field definitions and Python data files. Creates CMIP7-compliant Essential Model Documentation (EMD) forms.

## How It Works

Each template consists of two files:

```
templates/
├── template_name.csv    # Field definitions
├── template_name.py     # Configuration and CV data
└── ...
```



## CSV Field Structure

Each CSV defines form fields with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `field_order` | Order of fields (1, 2, 3...) | `5` |
| `field_type` | Type of form field | `dropdown`, `input`, `textarea`, `multi-select`, `markdown` |
| `field_id` | Unique identifier | `component_name` |
| `label` | Display label | `Component Name` |
| `description` | Help text (supports `\n` for line breaks) | `Enter the name\nRequired for CMIP7` |
| `data_source` | Data source from Python file | `realms`, `licenses`, `none` |
| `required` | Required field | `true`, `false` |
| `placeholder` | Placeholder text | `e.g., ECHAM6.3` |
| `options_type` | How to format options | `dict_keys`, `list`, `dict_multiple` |
| `default_value` | Default selection | `0` |

## Field Types

### `input` - Text Input
Single-line text entry.

```csv
3,input,name,Name,The name of your model,none,true,"e.g., CESM2",,
```

### `textarea` - Multi-line Text
Large text area for descriptions.

```csv
5,textarea,description,Description,Scientific model overview,none,true,"Describe scientific basis",,
```

### `dropdown` - Single Select
Choose one option from a list.

```csv
4,dropdown,license,License,Select the model license,licenses,true,,dict_keys,
```

### `multi-select` - Multiple Select
Choose multiple options from a list.

```csv
6,multi-select,components,Components,Select all model components,realms,true,,dict_multiple,
```

### `markdown` - Instructions
Formatted text (no user input).

```csv
1,markdown,header,Header,"# Instructions\n\nPlease complete all required fields.",none,false,,,
```

## Options Types

Controls how dropdown options are generated from Python data:

### `dict_keys` - Dictionary Keys
Uses keys from dictionary data.

```python
'licenses': {
    'MIT': {'id': 'MIT', 'validation-key': 'MIT'},
    'GPL': {'id': 'GPL', 'validation-key': 'GPL'}
}
```
→ Options: `["MIT", "GPL"]`

### `list` - Simple List
Uses list items directly.

```python
'priorities': ['High', 'Medium', 'Low']
```
→ Options: `["High", "Medium", "Low"]`

### `dict_multiple` - Multi-Select Dictionary
For multi-select fields using dictionary keys.

```python
'realms': {
    'atmosphere': {'id': 'atmosphere'},
    'ocean': {'id': 'ocean'}
}
```
→ Multi-select options: `["atmosphere", "ocean"]`

### `hardcoded` - Hardcoded Options
Uses predefined options from Python file.

```python
'status_options': ['Active', 'Inactive']
```
→ Options: `["Active", "Inactive"]`

### `list_with_na` - List with "Not applicable"
Adds "Not applicable" as first option.

→ Options: `["Not applicable", "option1", "option2"]`

### `dict_with_extra` - Dictionary + Extras
Dictionary keys plus hardcoded additional options.

→ Options: `["CV_option1", "CV_option2", "Open Source", "Proprietary"]`

## Python Configuration Files

Structure for template configuration:

```python
# Required template configuration
TEMPLATE_CONFIG = {
    'name': 'Display Name',
    'description': 'Template description', 
    'title': '[EMD] Template Title',
    'labels': ['emd-submission', 'category'],
    'issue_category': 'category'  # Usually matches last label
}

# Data for form options
DATA = {
    'cv_name': {
        'option1': {'id': 'option1', 'validation-key': 'option1'},
        'option2': {'id': 'option2', 'validation-key': 'option2'}
    },
    'simple_list': ['item1', 'item2'],
    'field_id_options': ['Choice A', 'Choice B']  # For hardcoded options
}
```

## CMIPLD Integration

For controlled vocabularies from the WCRP universe:

```python
import cmipld
from cmipld.utils.ldparse import *

DATA = {
    # Load from universal repository
    'realms': name_multikey_extract(
        cmipld.get('universal:realm/graph.jsonld')['@graph'],
        ['id','validation-key','ui-label'],'validation-key'
    ),
    
    # Add custom "none" option + loaded data
    'calendars': {
        'no-calendar': {'id': 'no-calendar', 'validation-key': 'no-calendar'},
        ** name_multikey_extract(
            cmipld.get('universal:model-calendar/graph.jsonld')['@graph'],
            ['id','validation-key','ui-label'],'validation-key'
        )
    },
    
    # Hardcoded data for CVs not in universal repo
    'grid_descriptors': ['N48', 'N96', 'ORCA1', 'T63']
}
```

## Generation Commands

```bash


# Generate all templates
python per_file_generator.py

# Custom directories
python per_file_generator.py -t ./templates -o ./github_templates

```

## Generated Output Format

Creates GitHub-compliant YAML:

```yaml
name: Model Component Submission
description: Submit metadata for a model component
title: "[EMD] Model Component Submission"
labels: ["emd-submission", "component"]
body:
  - type: input
    id: name
    attributes:
      label: Name
      description: The name of your component
      placeholder: "e.g., ECHAM6.3"
    validations:
      required: true

  - type: dropdown
    attributes:
      multiple: true
      label: Components
      description: |
        Select all model components.
        Select all that apply.
      options:
        - "atmosphere"
        - "ocean"
        - "land"
```

## Adding New Templates

1. **Create CSV file**: `.github/GEN_ISSUE_TEMPLATE/my_template.csv`
2. **Create Python file**: `.github/GEN_ISSUE_TEMPLATE/my_template.py`
3. **Run generator**: `template_generator` (as installed with cmipld)

## Automated workflow. 
The workflow `issue-templates.yml` runs when the GEN_ISSUE_TEMPLATE folder is updates. 
The workflow also has a cron trigger. 
 