# CMIP7 Controlled Vocabulary

The **CMIP7 CVs** repository defines the controlled vocabulary for the Coupled Model Intercomparison Project Phase 7. It specifies which terms from the [WCRP Universe](https://github.com/WCRP-CMIP/WCRP-universe) are used in CMIP7, adds project-specific metadata, and defines CMIP7 data specifications (DRS, NetCDF attributes, STAC catalog).

## How It Works: Linking to the Universe

Terms in this repository are **not self-contained** — they are lightweight references that link back to the [WCRP Universe](https://github.com/WCRP-CMIP/WCRP-universe), the shared source of truth for all WCRP vocabulary.

Each term file contains only the project-specific fields. The full definition (description, units, standard names, etc.) lives in the universe and is resolved through the JSON-LD context.

**Example — a CMIP7 variable (`variable/abs550aer.json`):**
```json
{
    "@context": "000_context.jsonld",
    "id": "abs550aer",
    "type": "variable"
}
```

The corresponding `000_context.jsonld` maps the `id` to the universe:
```json
{
    "@context": {
        "id": "@id",
        "type": "@type",
        "@base": "https://esgvoc.ipsl.fr/resource/universe/variable/"
    }
}
```

The `@base` URI tells esgvoc to resolve the full term definition from the universe. This means:
- The universe holds the **canonical definition** (description, units, standard name, etc.)
- The CMIP7 CVs declare **which terms are used** in CMIP7 and add any project-specific fields

Some terms carry additional project-specific information. For example, experiments include CMIP7-specific fields like `min_number_yrs_per_sim` and `tier`:
```json
{
    "@context": "000_context.jsonld",
    "id": "abrupt-4xco2",
    "type": "experiment",
    "min_number_yrs_per_sim": 300.0,
    "parent_mip_era": "cmip7",
    "tier": 1
}
```

## Repository Structure

```
CMIP7_CVs/
├── activity/              # MIP activities used in CMIP7
├── experiment/            # CMIP7 experiment definitions (~72 terms)
├── variable/              # Variables requested for CMIP7 (~987 terms)
├── institution/           # Participating institutions
├── source/                # Model sources
├── frequency/             # Output frequencies
├── realm/                 # Model realms
├── region/                # Geographic regions
├── grid_label/            # Grid labels
├── ...                    # 50+ collections in total
├── project_specs.yaml     # Project identity and DRS name
├── drs_specs.yaml         # Data Reference Syntax specifications
├── attr_specs.yaml        # NetCDF global attribute specifications
├── catalog_specs.yaml     # STAC catalog specifications
├── esgvoc_manifest.yaml   # Version and release metadata
└── scripts/               # Utility scripts
```

Each collection directory contains:
- `000_context.jsonld` — JSON-LD context that links terms back to the universe
- One `.json` file per term, named by its identifier

## Browsing Terms

You can browse terms directly on GitHub by navigating into any collection directory. To see the **full definition** of a term (description, units, etc.), look up the same `id` in the [WCRP Universe](https://github.com/WCRP-CMIP/WCRP-universe) repository.

## Querying Terms with esgvoc

[**esgvoc**](https://github.com/ESGF/esgf-vocab) is the companion Python library for querying and validating CV terms. It resolves the links between CMIP7 and the universe automatically, so you always get the complete term definition.

### Installation

```bash
pip install esgvoc
```

### CLI usage

```bash
# Search for a term in CMIP7
esgvoc find "air_temperature" cmip7:variable

# Get a specific CMIP7 term (resolved with universe data)
esgvoc get cmip7:variable:tas

# List all CMIP7 experiments
esgvoc get cmip7:experiment
```

### Python API

```python
from esgvoc.api import find_terms_in_project, get_term_in_project

# Full-text search within CMIP7
results = find_terms_in_project("cmip7", "air_temperature")

# Get a specific term
term = get_term_in_project("cmip7", "variable", "tas")
```

For full documentation, see the [esgvoc documentation](https://esgf.github.io/esgf-vocab/).

## Contributing New Terms

CV managers who want to add terms to the CMIP7 CVs should follow this process:

### Prerequisites: the term must exist in the Universe

Before a term can be added to CMIP7, its **canonical definition must already exist** in the [WCRP Universe](https://github.com/WCRP-CMIP/WCRP-universe). If the term does not exist there yet, contribute it to the universe first (see the [universe contributing guide](https://github.com/WCRP-CMIP/WCRP-universe#contributing-new-terms)).

### 1. Fork the repository

Fork [WCRP-CMIP/CMIP7_CVs](https://github.com/WCRP-CMIP/CMIP7_CVs) to your GitHub account.

### 2. Add your term

Create a new JSON file in the appropriate collection directory. The term only needs to reference the universe — include only the `@context`, `id`, `type`, and any CMIP7-specific fields:

```json
{
    "@context": "000_context.jsonld",
    "id": "your-term-id",
    "type": "<collection_name>"
}
```

**Naming conventions:**
- The file name must match the `id` field (e.g. `id: "my-term"` goes in `my-term.json`)
- The `id` must match an existing term in the universe

### 3. Submit a Pull Request to `esgvoc_dev`

Open your PR against the **`esgvoc_dev`** branch (not `main`). This allows:
- Automated validation (checks that the term exists in the universe and conforms to the expected model)
- Review by CV managers before the term is merged
- Testing in a staging environment before promotion to `main`

Once approved and merged into `esgvoc_dev`, changes will be promoted to `main` after a validation cycle.

## Versioning

Version information is tracked in `esgvoc_manifest.yaml`:

```yaml
project:
  id: "cmip7"
  name: "CMIP7 Controlled Vocabulary"
cv_version: "1.1.0"
universe_version: "1.0.2"
esgvoc:
  min_version: "4.0.0"
```

The `universe_version` field indicates which version of the WCRP Universe this CV is aligned with.

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
