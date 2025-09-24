# CMIP6 to CMIP7 Experiment Structure Changes

## Overview

This document outlines the technical and structural changes in experiment definitions between CMIP6 and CMIP7, focusing on data format, schema structure, and metadata organization rather than content changes.

## File Format Changes

### CMIP6 Structure
- **Format**: Single consolidated JSON file containing all experiments
- **Schema**: Flat JSON structure with nested experiment objects
- **Root Structure**: 
  ```json
  {
    "experiment_id": {
      "experiment_name": { ... },
      "another_experiment": { ... }
    },
    "version_metadata": { ... }
  }
  ```

### CMIP7 Structure
- **Format**: Individual JSON-LD files per experiment
- **Schema**: JSON-LD (Linked Data) with semantic web capabilities
- **File Organization**: Separate files in `/src-data/experiment/` directory
- **Naming Convention**: Experiment ID as filename (e.g., `1pctco2.json`, `historical.json`)

## Schema Structure Changes

### Key Field Transformations

| CMIP6 Field | CMIP7 Field | Notes |
|-------------|-------------|-------|
| `experiment_id` | `id` | Now the primary identifier. Lowercase. No underscores. |
| N/A | `validation-key` | New field analogous to the CMIP-acronym used for validation purposes |
| N/A | `ui-label` | New human-readable label field for aiding clarity in print |
| `description` | `description` | Enhanced formatting with newlines |
| `activity_id` | `activity` | Changed from array of strings to array of strings |
| `additional_allowed_model_components` | `model-realms` (optional) | Restructured as objects with `is-required: false` |
| `required_model_components` | `model-realms` (required) | Restructured as objects with `is-required: true` |
| `parent_experiment_id` | `parent-experiment` | Simplified array format |
| `parent_activity_id` | Removed | No longer present in CMIP7 |
| `sub_experiment_id` | Removed | No longer present in CMIP7 |
| `start_year` | `start` | Simplified field name |
| `end_year` | `end` | Simplified field name |
| N/A | `start-date` | New field for specific start dates |
| `min_number_yrs_per_sim` | `min-number-yrs-per-sim` | Field name with hyphens |
| `tier` | `tier` | Maintained, but now numeric instead of string |

### New JSON-LD Semantic Fields

CMIP7 introduces JSON-LD semantic web capabilities:

- **`@context`**: References to semantic context definitions
- **`type`**: Semantic type definitions (`["wcrp:experiment", "cmip7"]`)
- **Linked Data**: URIs for cross-referencing other WCRP resources

### Model Realms Restructuring

#### CMIP6 Format
```json
"required_model_components": ["AOGCM"],
"additional_allowed_model_components": ["AER", "CHEM", "BGC"]
```

#### CMIP7 Format
```json
"model-realms": [
    {
        "id": "aogcm",
        "is-required": true
    },
    {
        "id": "aer", 
        "is-required": false
    }
]
```

The referenced ids will have any nested code substituted in place from the required locations. This is defined in the `_context_`.

## Removed Fields

The following CMIP6 fields are no longer present in CMIP7:

- `parent_activity_id`: Parent activity relationships removed
- `sub_experiment_id`: Sub-experiment categorization removed  
- `experiment`: Short experiment name removed (replaced by `ui-label`)

## New Fields in CMIP7

- **`validation-key`**: Used for validation against legacy CMIP6 naming (CMIP acronym)
- **`ui-label`**: Human-readable display label
- **`start-date`**: Specific calendar start date (supplements numeric `start`)
- **`alias`**: Array for alternative names/identifiers
- **`@context`**: JSON-LD context reference
- **`type`**: Semantic type definitions

## Data Type Changes

### Tier Values
- **CMIP6**: String values 
- **CMIP7**: Numeric values
### Year Fields
- **CMIP6**: String values (including `""` for unspecified)
- **CMIP7**: Numeric values with `-999` for unspecified years

### Activity References
- **CMIP6**: Mixed case arrays (`["CMIP"]`, `["ScenarioMIP"]`)
- **CMIP7**: Lowercase *references* (`["cmip"]`) with semantic linking

## File Organization Impact

### CMIP6
- Single large JSON file (`CMIP6_experiment.json`)
- Central version metadata
- Monolithic structure requiring full file parsing

### CMIP7  
- Distributed individual files per experiment
- Modular loading and validation
- Individual experiment versioning capability
- Semantic web discoverability through JSON-LD

## Context and Semantic Web Integration

CMIP7 introduces semantic web capabilities through:

- **JSON-LD Context**: Links to external vocabularies and schemas
- **URI-based References**: Semantic links between experiments, activities, and model realms
- **Type Definitions**: Formal semantic typing for automated processing
- **Cross-Project Integration**: Links to broader WCRP universe metadata

## Validation Changes

### CMIP6
- Schema validation against single large JSON structure
- Internal consistency checking within monolithic file

### CMIP7
- Individual file validation against JSON-LD schema
- Cross-reference validation between distributed files
- Semantic validation through linked data contexts
- Backward compatibility validation via `validation-key` field
