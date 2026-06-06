# CMIP7 Controlled Vocabulary

The **CMIP7 controlled vocabularies (CVs)** repository defines the controlled vocabulary for the Coupled Model Intercomparison Project Phase 7. It specifies which terms from the [WCRP Universe](https://github.com/WCRP-CMIP/WCRP-universe) are used in CMIP7, adds project-specific metadata, and defines CMIP7 data specifications (DRS, NetCDF attributes, STAC catalog).

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

## Viewing the CVs and browsing terms

The CVs are currently evolving rapidly in support of CMIP7.
We hope to soon be able to "freeze" them,
i.e. forbid alterations to values in the CVs
and only allow new values to be added to the CVs.
However, this is not currently the case so when you view the CVs,
you will also need to specify which version of the CVs you are looking at to avoid confusion.
It is for exactly this reason that,
when raising an [issue with the CVs values](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=cv-value.md),
we ask you to specify how you were looking at the CVs
and also specify the underlying version of the CVs (if possible).
<!-- 
REVIEWERS: note that the link above is dead.
It will go live when this MR is merged into main
(i.e. after the esgvoc branches become the main branches)
-->

To view the CVs as they are used within CMIP, you have a few options.

### esgvoc

This is the authoritative tool for accessing the CVs.
All other ways of accessing the CVs are simply different 'views' of what comes from esgvoc.
Any view of the CVs that differs from esgvoc is either
a) wrong
or b) based on a different commit/snapshot of the CVs from the one that you are viewing via esgvoc
(e.g. your esgvoc installation is configured to use the 'latest' version of the CMIP7 CVs,
but you are looking at a view of the CVs from another tool that is based on an earlier version).
esgvoc's full documentation can be found at
[esgf.github.io/esgf-vocab/](https://esgf.github.io/esgf-vocab/).

At the time of writing
(noting that esgvoc is also being developed rapidly,
so the following text may quickly become out of date),
the docs that are most likely to be useful are:

1. [installation](https://esgf.github.io/esgf-vocab/user/introduction.html#installation)
1. [retrieving and inspecting values](https://esgf.github.io/esgf-vocab/how_to/get.html)

For example, to inspect the value of the 
`historical` and `piControl` experiments for CMIP7 on a unix-based system,
you could do something like

```sh
# create a virtual environment
$ python3 -m venv venv

# activate it
$ source venv/bin/activate

# install esgvoc's latest version
$ pip install esgvoc

# get the latest release of the CMIP7 CVs
# (note that this will not have incorporated
# any changes which are still sitting in pull requests into this repository,
# i.e. anything you see here: https://github.com/WCRP-CMIP/CMIP7-CVs/pulls)
$ esgvoc use cmip7@latest

# get the value of interest to us, e.g. historical
$ esgvoc get cmip7:experiment:historical

# Note that the `get` command requires IDs (all lowercase),
# not the experiment name as used in CMIP (e.g. in filenames).
# So this works
$ esgvoc get cmip7:experiment:picontrol

# This does not
$ esgvoc get cmip7:experiment:piControl
```

If you want to look at lots of CVs, doing it via the command line may not be your best option.
Fortunately, esgvoc offers a full Python API to support easier scripting and other uses,
see [their docs](https://esgf.github.io/esgf-vocab/).
If you want an example of working with esgvoc's Python API to create a derived product,
see [the script used to create CMOR tables](https://github.com/WCRP-CMIP/cmip7-cmor-tables/tree/main/tables-cvs/generate-cmor-cvs-table.py).

### Via the web API

To explore the terms via the web API, no installation is required — you can query directly from your browser or any HTTP client.

- **All collections in a project:**
  `https://esgvoc.ipsl.fr/api/v1/projects/{project_id}/collections`
  e.g. [all CMIP7 collections](https://esgvoc.ipsl.fr/api/v1/projects/cmip7/collections)

- **All data descriptors in the universe:** (not quite the same as collections in a project, but the closest concept in the universe)
  [https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors](https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors)

- **All terms in a collection:**
  `https://esgvoc.ipsl.fr/api/v1/projects/{project_id}/collections/{collection_id}/terms`
  e.g. [all CMIP7 institutions](https://esgvoc.ipsl.fr/api/v1/projects/cmip7/collections/institution/terms)

- **All terms in a collection in the universe:**
  `https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/{data_descriptor_id}/terms`
  e.g. [all universe organisations](https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/organisation/terms)

- **A specific term in a project collection:**
  `https://esgvoc.ipsl.fr/api/v1/projects/{project_id}/collections/{collection_id}/terms/{term_id}`
  e.g. [the historical experiment](https://esgvoc.ipsl.fr/api/v1/projects/cmip7/collections/experiment/terms/historical)

- **A specific term in the universe:**
  `https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/{data_descriptor_id}/terms/{term_id}`
  e.g. [the historical experiment in the universe](https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/experiment/terms/historical)

Full API documentation is available at [esgvoc.ipsl.fr/api/v1/docs](https://esgvoc.ipsl.fr/api/v1/docs).

### Quick lookup via the CLI (no esgvoc install required)

If you just want to quickly check whether a term exists in the CVs,
you can use [`uvx`](https://docs.astral.sh/uv/) to run esgvoc without installing it into your environment.
The current working directory doesn't matter.

**Prerequisites:**

1. Install [uv](https://docs.astral.sh/uv/) (macOS and Linux):
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Fetch the latest CMIP7 snapshot:
   ```sh
   uvx esgvoc use cmip7@latest
   ```

**Usage:**

```sh
# Check whether a term ID exists and see its DRS name
$ uvx esgvoc get cmip7:<collection>:<term_id> --select drs_name

# For example, check institution "ipsl"
$ uvx esgvoc get cmip7:institution:ipsl --select drs_name

# View all information about a term (omit --select)
$ uvx esgvoc get cmip7:institution:ipsl
```

Note: term IDs are always lowercase.

### Via the Python API

For scripting or more advanced queries,
esgvoc provides a Python API.
For example, to retrieve all institutions:

```python
import esgvoc.api as ev

cmip7_institutions = ev.get_all_terms_in_collection("cmip7", "institution_id")
# Then filter, search, or process as needed
```

See the [esgvoc Python API docs](https://esgf.github.io/esgf-vocab/) for full details.

### CMOR tables

A subset of the CVs are used with the [cmor](https://github.com/PCMDI/cmor) tool.
The subset required are formatted for CMOR in
[this repository](https://github.com/WCRP-CMIP/cmip7-cmor-tables),
specifically in [this file](https://github.com/WCRP-CMIP/cmip7-cmor-tables/tree/main/tables-cvs/cmor-cvs.json).
Updates are currently happening quite rapidly,
so please also check the
[pull requests](https://github.com/WCRP-CMIP/cmip7-cmor-tables/pulls)
if you want to see changes that are in the process of being incorporated.

<!--
### JSON-LD represenation

Add when we have a version of this we're happy with.
-->

## Altering (i.e. writing) the CVs

### Via forms

The easiest way to alter the CVs is via GitHub forms
(specifically GitHub issue forms).
At the moment we have forms available for:

<!--
    REVIEWERS: Note that these links are dead.
    They will go live when this is merged to main.
    If you want to see this idea in action,
    please see https://github.com/znichollscr/github-forms-scratch
    (I can't do a demo in this repository,
    GitHub only renders forms that are in main.)
-->
- [adding new experiments](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=register-experiment.yml)
- [adding new activities](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=register-activity.yml)

For all other changes, please use either:

- [this template](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=cv-value.md)
  for requesting changes to existing CVs
- [a blank issue](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=BLANK_ISSUE)
  for anything else (e.g. a request for a new form)

### Editing the CVs directly

It is possible to edit the CVs yourself.
This will require more effort to understand the process,
but direct editing also gives you much more control
and can lead to a much faster process if done correctly.

The values that underpin the CVs are kept in two separate repositories:

1. https://github.com/WCRP-CMIP/CMIP7-CVs
1. https://github.com/WCRP-CMIP/WCRP-universe

The full reasons for this are beyond the scope of this repository.
In very short, this split allows the CVs community to maximise (and encourage) re-use of terms
while recognising that some projects use different terms to mean the same thing
(or the same term to mean different things)
so simply enforcing consistency across all projects is not an option.
This way of working allows us to meet this need,
but it does complicate altering the CVs
(or understanding where the CVs values you see come from).
We are working on better ways to do this
and better explanations of why we have chosen the solutions that we have.

In order to alter the CVs,
you will need to understand (at least to some degree)
both the repositories listed above
as well as the interaction between them.

We go through some examples here.
If you want to understand the underlying structure a bit more,
see the 'theory' header below.

#### Examples

##### Adding a term to the CMIP7 CVs that is already in the universe CVs

Example pull request: [https://github.com/WCRP-CMIP/CMIP7-CVs/pull/371]()

This is very simple, a single file is added to the CMIP7 CVs repository.
This adds the term, which is already in the universe CVs, to the CMIP7 CVs.

This was done by simply copying an existing entry,
then updating the filename and ID so they matched the entry in the universe CVs we wanted to add
(in this case, https://github.com/WCRP-CMIP/WCRP-universe/blob/esgvoc/frequency/subhr.json).
No overrides were needed in this case, so no fields were specified beyond the ones required
to identify the universe CVs entry to use.

##### Removing a term from the CMIP7 CVs

Example pull request: [https://github.com/WCRP-CMIP/CMIP7-CVs/pull/352]()

Simply delete the file that defines the term that needs to be removed.
You do not need to (strictly speaking, must not)
remove the term from the universe CVs
(the universe CVs are intended to capture all known terms,
whether they are used in any projects or not).

##### Updating existing terms in the CMIP7 CVs

Example CMIP7 CVs pull request: [https://github.com/WCRP-CMIP/CMIP7-CVs/pull/353]()
Example universe CVs pull request: [https://github.com/WCRP-CMIP/WCRP-universe/pull/118]()

For these changes, the fields we needed to update were split across both the CMIP7 CVs and the universe CVs.
Currently, there aren't unambiguous rules for which fields go in which repository.
The general guidance is that anything which can be re-used should be in the universe CVs repository,
anything which is project specific goes in a project-specific CVs repository.
If in doubt, put the field in the project-specific CVs repository
(i.e. lean on the side of caution, if it's not obviously universal, don't guess that it is so).

The decision about where to alter the existing CMIP7 CVs entries and where to alter universe CVs entries was based on our own judgement.
If you look at the [the universe CVs pull request](https://github.com/WCRP-CMIP/WCRP-universe/pull/118),
then you will see that there are also alterations to `scripts/generate-experiments.py`.
This is because we didn't update these entries by hand.
Instead, we did this via a script.
We do this because we find it simpler to use a script
than try to ensure consistency across multiple files by hand.
You don't have to follow this pattern, but you might find that it is necessary for anything
except the most trivial edits.
Your scripts can either be added in the `scripts` folder of the relevant CVs repository
or kept separate, up to you.

##### Updating existing terms in the CMIP7 CVs and adding new terms

Example CMIP7 CVs pull request: [https://github.com/WCRP-CMIP/CMIP7-CVs/pull/381]()
Example universe CVs pull request: [https://github.com/WCRP-CMIP/WCRP-universe/pull/133]()

Like the example above, for these changes we need to make alterations in both the CMIP7 CVs and universe CVs repositories.
As above, the decision about where to alter the existing CMIP7 CVs entries and where to alter universe CVs entries was based on our own judgement.

If you look at the pull requests, you will see alterations to experiments, like in the example above.
We also add two new experiments to the CMIP7 CVs experiments, namely `hist-piaer.json` and `hist-piaq.json`,
effectively registering these as CMIP7 experiments.
You will also notice that we added these new experiments to the list of experiments registered under AerChemMIP
(see the modifications to the file `activity/aerchemmip.json`).
Here you see another reason that we make these alterations using scripts
(see the changes to `scripts/generate-experiments.py` in the [universe CVs pull request](https://github.com/WCRP-CMIP/WCRP-universe/pull/133)):
there are couplings between different parts of the CVs
and these couplings are much easier to manage using a script than trying to keep track of them all by hand.

#### Theory

Note that this is an attempt to summarise how this system works.
However, it is likely to leave you with some questions because:

1. the system is evolving rapidly so this text may quickly become out of date
1. this text is short and not exhaustive
1. the system is custom: it is close to how JSON-LD works but it isn't JSON-LD
   (it can't be, because JSON-LD is a web technology,
   but processing the CVs using web requests only is way too slow),
   so you can't easily google answers.
   To get authoritative answers, you have to look at what the esgvoc code does
   (or ask an AI coding tool to explain, they seem to able to parse the logic quite well).

In very short, for CMIP7 CVs, the CMIP7 CVs repository
(https://github.com/WCRP-CMIP/WCRP-universe/)
is the source with the highest priority.
Values set in the CMIP7 CVs repository are never overridden during the processing.
The universe CVs repository
(https://github.com/WCRP-CMIP/WCRP-universe)
is an information source which the CMIP7 CVs repository can re-use.

For example,
<!--
REVIEWERS: suggestions for checking that these links are live,
particularly as we rename `esgvoc` branches to `main`,
are welcome (do we do this manually, add CI to check links are live, something else?).
-->
the entry that describes the `1pctCO2` experiment is very thin,
see [https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/1pctco2.json]().
It is actually mostly relying on the 'universe' definition of `1pctco2`,
see [https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/experiment/1pctco2.json](),
and only augmenting/overriding the fields shown in
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/1pctco2.json]().

**Naming conventions:**

- The file name must match the `id` field (e.g. `id: "my-term"` goes in `my-term.json`)
- The `id` must match an existing term in the universe

In order to determine which universe values are used as the basis for each CMIP7 CV entry,
you must look at the `000_context.jsonld` file in the directory in which the CV is defined.
Continuing with our `1pctCO2` example, we must look at the `000_context.jsonld` file
that lives in the same directory as the `1pctco2.json` file, i.e.
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/000_context.jsonld]().
In this file, there is lots of information.
The key bit for this match is the value of `"@context"` -> `"@base"`.
This tells you which directory in the universe CVs repository
is searched to find the universe CVs entry
to combine with the CMIP7 CVs entry to create the 'full' CV entry.
At the moment, you have to replace `"https://esgvoc.ipsl.fr/resource/universe/"`
with `"https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/"`
to get the right path, but otherwise it works.
E.g. in [https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/000_context.jsonld]()
you see that `"@context"` -> `"@base"` is equal to
`"https://esgvoc.ipsl.fr/resource/universe/experiment/"`,
so we know that we need to look in 
`"https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/experiment/"`
for the 'matching' entry.

(
In our example, this match is quite straightforward
as we just use experiments from the universe too.
However, the two names don't have to match.
For example, if we look at 
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/source/000_context.jsonld](),
we see that CMIP7 CVs sources
([https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/source]())
are based on universe models
([https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/model]()),
not universe sources
([https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/source]()).
)

The 'matching' entry is then defined by the value of `"id"` in the JSON files.
Again, using our `1pctCO2` example,
we see that the value of `"id"` in
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/000_context.json]()
is `1pctco2`.
Combining this with the directory information,
we know that this file will be combined with 
[https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/experiment/1pctco2.json]()
from the universe CVs repository.

To know what values can appear in the CVs, you need a few pieces of information.
The first is that you always have to have the `"@context"` key with the value `"000_context.jsonld`.
From there, you have to look at the `"type"` key in the JSON file
(or its universe CVs counterpart if the `"type"` key is missing in the project-specific CVs file).
This tells you which pydantic model will be used with this JSON file,
and therefore which keys are valid.
(If you are not used to pydantic, the rest of this might be quite challenging.)
Again, using our `1pctCO2` example,
we see that the value of `"type"` in
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/1pctco2.json]()
is `experiment`.
(There can actually be an extra layer to this, sometimes you also need to check the `DATA_DESCRIPTOR_CLASS_MAPPING` mapping
in [https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/__init__.py]().)

The pydantic models are defined in [esgvoc](https://github.com/ESGF/esgf-vocab),
specifically [`src/esgvoc/api/data_descriptors`](https://github.com/ESGF/esgf-vocab/tree/main/src/esgvoc/api/data_descriptors).
You need to look at the data descriptor that matches your type.
Again, using our `1pctCO2` example,
we would look at [https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/experiment.py]().
From there, you can either read through the classes and their superclasses to determine the fields,
which ones are required, how they link to other classes and how the fields are validated,
or just install esgvoc and look at the class fields using pydantic's tooling.
If you're not used to this way of working, this can be a challenge,
so we would instead simply suggest looking at existing CVs entries to see which fields are used.

The last step is always opening a pull request back into the main branch.

<!--- @Laurent are we still meant to point at esgvoc_dev or do we just point straight at main now? -->
Open your PR against the **esgvoc_dev** branch (not `main`). This allows:

- Automated validation (checks that the term exists in the universe and conforms to the expected model)
- Review by CV managers before the term is merged
- Testing in a staging environment before promotion to `main`

Once approved and merged into `esgvoc_dev`, changes will be promoted to `main` after a validation cycle.

Underneath all of this, esgvoc is creating and managing a relational database of terms
(if you don't know about relational databases, but would like to learn,
we can highly recommend working through [SQLModel's intro to databases](https://sqlmodel.tiangolo.com/databases/)).
This way of working is the standard in web development and data management,
but is new to CVs management in the context of CMIP.
As a result, we expect there to be some teething issues as this way of working spreads through the community.
If you can't understand how this CMIP7 CVs repository works,
even after reading this guidance,
please raise a [blank issue](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=BLANK_ISSUE),
describe your issue and tag @ltroussellier, @znichollscr and @glevava and we will do our best to help.

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
