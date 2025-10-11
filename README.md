# CMIP7 Controlled Vocabularies

This repository is used to maintain the data that defines
the core controlled vocabularies (CVs) for use in CMIP7.
However, at present, the only recommend way to access these values
is via the [esgvoc](https://esgf.github.io/esgf-vocab/) package.
If you are looking for further details on ESGF metadata handling,
please follow [this issue](https://github.com/WCRP-CMIP/cmip7-guidance/issues/35)
as this question goes beyond the CVs alone.

## Overview

At present, this repository should not be used as your source of truth.
As stated above, the only recommend way to access the CVs
is via the [esgvoc](https://esgf.github.io/esgf-vocab/) package.
This will change in future, but for the CVs Task Team (CVs TT)
does not have the resources to maintain more than one interface to the CVs.

## Details

If you would like to understand how this works in more detail,
then here is some further information.
There are a few key concepts to be aware of.

### How esgvoc works

esgvoc works by using an `esgvoc` branch in its source data repositories
(we'll get to what those are in a minute).
Each `esgvoc` branch contains the data esgvoc needs,
in the format that esgvoc needs it.
When you query data via `esgvoc` it
(effectively, although it's smarter than this in practice)
grabs the information from the `esgvoc` branch of all the repositories it needs to query,
parses the information and serves it to you following esgvoc's defined API
(see the [esgvoc](https://esgf.github.io/esgf-vocab/) docs for the form of this API).

### Key nouns

- **Data descriptor**: a known metadata category used in CMIP
    - for example,
      "experimentDD" is the data descriptor
      which defines the experiment to which a given dataset belongs,
      "areaLabelDD" is the data descriptor
      which defines the area label given to a dataset
      and "productTypeDD" is the data descriptor
      which (loosely) describes what kind of product a given dataset is
      (e.g. model-based, observations, reanalysis).
- **Term**: an individual entry in the CVs for a given data descriptor
    - for example, the entry for the "experimentDD" data descriptor
      which defines the `historical` experiment and its associated metadata
- **Collection**: set of terms for a given data descriptor
  which are included in a given CMIP phase's CVs

Note: the naming convention for how data descriptors appear in different places,
e.e. whether they have the trailing DD, whether they are camelCase or snake_case,
are still being ironed out so expect to see a few different variants of these in the short-term,
not always with a clearly defined logic.

### Source repositories

esgvoc uses two different sources of information.
The first is the **WCRP-universe** i.e. [this repository](https://github.com/WCRP-CMIP/WCRP-universe),
(specifically the [esgvoc branch thereof](https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc)).
This is the main/baseline/canonical repository containing all known terms used in all supported phases of CMIP
(CMIP6, CMIP6-cordex, input4MIPs, CMIP7 etc.).
In the universe, terms are defined in full i.e. all metadata is supplied next to each term.
The second source of information, when it comes to CMIP7 CVs, is this repository
(specifically the [esgvoc branch](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc)).
esgvoc uses this repository to define the terms that belong to CMIP7
(not all terms in the universe are relevant to CMIP7).
In general, this definition simply means including the term in this repository too
(as above, more precisely, in the `esgvoc` branch of this repository).
Normally, this definition simply means including a link back to the universe.
There is no need to duplicate metadata using esgvoc.
However, this repository can also define, where needed, overrides of the information in the universe.
This is rare, but can allow metadata to differ from what is in the universe, specifically for CMIP7.

## Branches you may see

There are a few branches in this repository.
Given there are so many relevant ones, here is a quick guide.
In future, we hope to return to 'normal' and just have `main`,
but for now it's like this:

- `main`: just this README
    - deliberately zero content.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).
- `esgvoc`: source data for esgvoc
    - unless you are a developer, you shouldn't need to look at this.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).
- `esgvoc_dev`: if you want to make a change to the `esgvoc` branch,
  target your merge request at this branch
  (it is the development branch where all changes are added
  before being merged to `esgvoc` for releases).
    - unless you are a developer, you shouldn't need to look at this.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).
- `src-data`: A pure JSONLD version of the content.
  Can be accessed with [cmip-ld](https://github.com/WCRP-CMIP/CMIPLD).
    - as a user, for now this view should not be considered a reliable source.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).
- `docs`: An experimental docs page basd on `src-data`.
    - as a user, for now this view should not be considered a reliable source.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).
- `production`: An experimental branch that hosts compiled documentation and JSONLD files,
   as well as a static pages site.
    - as a user, for now this view should not be considered a reliable source.
      If you want to know about CVs,
      use [esgvoc](https://esgf.github.io/esgf-vocab/).

All other branches can be ignored.
They are being used by devs and are not intended to be long-lived.

## Contributors

[![Contributors](https://contrib.rocks/image?repo=WCRP-CMIP/CMIP7-CVs)](https://github.com/WCRP-CMIP/CMIP7-CVs/graphs/contributors)

Thanks to our contributors!

## Acknowledgement

<!---Horribly out of date, but I guess not worth worrying about for now-->
The repository content has been collected from many contributors representing the Coupled Model Intercomparison Project phase 7 (CMIP7),
including those from climate modeling groups and model intercomparison projects (MIPs) worldwide.
The structure of content and tools required to maintain it
was developed by climate and computer scientists from the Program for Climate Model Diagnosis and Intercomparison ([PCMDI](https://pcmdi.llnl.gov/))
at Lawrence Livermore National Laboratory ([LLNL](https://www.llnl.gov/))
with assistance from colleagues at the [UK MetOffice](https://www.metoffice.gov.uk/),
UK Centre for Environmental Data Analysis ([CEDA](https://www.ceda.ac.uk/)),
the Deutsches Klimarechenzentrum ([DKRZ](https://www.dkrz.de/en/)) in Germany
and the members of the Infrastructure for the European Network for Earth System Modelling ([IS-ENES](https://is.enes.org/)) consortium.

This work is sponsored by the Regional and Global Model Analysis ([RGMA](https://climatemodeling.science.energy.gov/program/regional-global-model-analysis))
program of the Earth and Environmental Systems Sciences Division ([EESSD](https://science.osti.gov/ber/Research/eessd))
in the Office of Biological and Environmental Research ([BER](https://science.osti.gov/ber)) within the Department of Energy's ([DOE](https://www.energy.gov/))
Office of Science ([OS](https://science.osti.gov/)).
The work at PCMDI is performed under the auspices of the U.S. Department of Energy by Lawrence Livermore National Laboratory under Contract DE-AC52-07NA27344.

<p>
    <img src="https://pcmdi.github.io/assets/PCMDI/100px-PCMDI-Logo-NoText-square-png8.png"
         width="65"
         style="margin-right: 30px"
         title="Program for Climate Model Diagnosis and Intercomparison"
         alt="Program for Climate Model Diagnosis and Intercomparison"
    >&nbsp;
    <img src="https://pcmdi.github.io/assets/DOE/480px-DOE_Seal_Color.png"
         width="65"
         style="margin-right: 30px"
         title="United States Department of Energy"
         alt="United States Department of Energy"
    >&nbsp;
    <img src="https://pcmdi.github.io/assets/LLNL/212px-LLNLiconPMS286-WHITEBACKGROUND.png"
         width="65"
         style="margin-right: 30px"
         title="Lawrence Livermore National Laboratory"
         alt="Lawrence Livermore National Laboratory"
    >&nbsp;
    <img src="https://pcmdi.github.io/assets/MetOffice/100px-Met_Office_LogoBLACK.png"
         width="65"
         style="margin-right: 30px"
         title="UK Met Office"
         alt="UK Met Office"
    >
</p>
