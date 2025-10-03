# CMIP6 Global Attributes - Simplified Reference

## Quick Reference Table

This is a simplified version of the CMIP6 global attributes. Attributes are grouped by category for easier reference.

### Experiment Identification

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **experiment_id** | Always | Root experiment identifier | `"historical"`, `"abrupt4xCO2"` |
| **experiment** | Always | Short experiment description | `"pre-industrial control"` |
| **activity_id** | Always | Activity identifier(s) | `"CMIP"`, `"PMIP"` |
| **sub_experiment_id** | Always | Sub-experiment identifier | `"s1960"`, `"none"` |
| **sub_experiment** | Always | Sub-experiment description | `"initialized near end of year 1960"` |

### Model & Institution

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **source_id** | Always | Model identifier (≤16 chars) | `"GFDL-CM2-1"` |
| **source** | Always | Full model name/version | See note 13 |
| **source_type** | Always | Model configuration | `"AOGCM"`, `"AGCM"` |
| **institution_id** | Always | Institution identifier | `"IPSL"` |
| **institution** | Always | Institution name | `"Meteorological Research Institute"` |

### Variant Indices (RIPF)

| Attribute | Required | Description | Range |
|-----------|----------|-------------|-------|
| **realization_index** | Always | Different initial conditions | ≥ 1 |
| **initialization_index** | Always | Different initialization methods | ≥ 1 |
| **physics_index** | Always | Different physics versions | ≥ 1 |
| **forcing_index** | Always | Different forcing variants | ≥ 1 |
| **variant_label** | Always | Combined RIPF label | `"r1i1p1f1"` |
| **variant_info** | Optional | Description of variant | `"forcing: black carbon only"` |

### Grid & Resolution

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **grid_label** | Always | Grid identifier | `"gn"`, `"gr"`, `"gr1"` |
| **grid** | Always | Grid description | `"native T63 gaussian"` |
| **nominal_resolution** | Always | Approximate resolution | `"50 km"`, `"1x1 degree"` |

### Parent Experiment (if branched)

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **parent_experiment_id** | If parent exists | Parent experiment | `"piControl"` |
| **parent_activity_id** | If parent exists | Parent activity | `"CMIP"` |
| **parent_source_id** | If parent exists | Parent model | `"CanCM4"` |
| **parent_variant_label** | If parent exists | Parent variant | `"r1i1p1f1"` |
| **branch_time_in_parent** | If parent exists | Branch time (parent units) | `3650.0D0` |
| **branch_time_in_child** | If parent exists | Branch time (child units) | `0.0D0` |
| **parent_time_units** | If parent exists | Parent time units | `"days since 1000-1-1"` |
| **branch_method** | If parent exists | Branching procedure | `"standard"` |

### Data Description

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **frequency** | Always | Sampling frequency | `"mon"`, `"day"` |
| **realm** | Always | Model realm(s) | `"atmos"`, `"ocean"` |
| **table_id** | Always | Variable table | `"Amon"`, `"Oday"` |
| **variable_id** | Always | Variable identifier | `"tas"`, `"pr"` |

### Metadata & Tracking

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| **mip_era** | Always | CMIP cycle | `"CMIP6"` |
| **Conventions** | Always | CF conventions | `"CF-1.7 CMIP-6.2"` |
| **creation_date** | Always | File creation date | `"2010-03-23T05:56:23Z"` |
| **tracking_id** | Always | Unique file ID | `"hdl:21.14100/<uuid>"` |
| **further_info_url** | Always | Documentation URL | See note 9 |
| **license** | Always | License text | See note 12 |

### Optional Metadata

| Attribute | Required | Description |
|-----------|----------|-------------|
| **title** | Never | Generated title |
| **history** | Never | Processing history |
| **comment** | Never | Additional comments |
| **references** | Never | References |
| **contact** | Never | Contact information |
| **external_variables** | When appropriate | External cell measures |

## Grid Label Reference

| Label | Description |
|-------|-------------|
| `gn` | Native grid (primary) |
| `gr` | Regridded (primary) |
| `gr1`, `gr2`, etc. | Secondary regridded grids |
| `gm` | Global mean |
| `gnz`, `grz` | Zonal means |
| `gng`, `grg` | Greenland region |
| `gna`, `gra` | Antarctica region |

## Source Type Options

```
AGCM [BGC] [AER] [CHEM] [SLAB]
AOGCM [BGC] [AER] [CHEM] [ISM]
OGCM
LAND
ISM
RAD
```

Where brackets indicate optional components depending on the experiment.
