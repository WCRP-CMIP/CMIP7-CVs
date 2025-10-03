# CMIP7 Controlled Vocabularies
Core Controlled Vocabularies (CVs) for use in CMIP7

### THIS REPOSITORY IS CURRENTLY UNDER ACTIVE DEVELOPMENT

## Contributors

[![Contributors](https://contrib.rocks/image?repo=WCRP-CMIP/CMIP7-CVs)](https://github.com/WCRP-CMIP/CMIP7-CVs/graphs/contributors)

Thanks to our contributors!

## Acknowledgement

The repository content has been collected from many contributors representing the Coupled Model Intercomparison Project phase 7 (CMIP7), including those from climate modeling groups and model intercomparison projects (MIPs) worldwide. The structure of content and tools required to maintain it was developed by climate and computer scientists from the Program for Climate Model Diagnosis and Intercomparison ([PCMDI](https://pcmdi.llnl.gov/)) at Lawrence Livermore National Laboratory ([LLNL](https://www.llnl.gov/)) with assistance from colleagues at the [UK MetOffice](https://www.metoffice.gov.uk/), UK Centre for Environmental Data Analysis ([CEDA](https://www.ceda.ac.uk/)), the Deutsches Klimarechenzentrum ([DKRZ](https://www.dkrz.de/en/)) in Germany and the members of the Infrastructure for the European Network for Earth System Modelling ([IS-ENES](https://is.enes.org/)) consortium.

This work is sponsored by the Regional and Global Model Analysis ([RGMA](https://climatemodeling.science.energy.gov/program/regional-global-model-analysis)) program of the Earth and Environmental Systems Sciences Division ([EESSD](https://science.osti.gov/ber/Research/eessd)) in the Office of Biological and Environmental Research ([BER](https://science.osti.gov/ber)) within the Department of Energy's ([DOE](https://www.energy.gov/)) Office of Science ([OS](https://science.osti.gov/)). The work at PCMDI is performed under the auspices of the U.S. Department of Energy by Lawrence Livermore National Laboratory under Contract DE-AC52-07NA27344.

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


This repository contains the controlled vocabularies (CVs) for the CMIP7 project. It defines project-specific collections of terms used for organizing
   and documenting CMIP7 climate simulation data.

  ## Overview

  CMIP7_CVs is a project-specific CV repository that works in conjunction with the https://github.com/WCRP-CMIP/WCRP-universe repository. While the
  universe contains all possible terms with complete metadata, this repository contains collections that reference those terms by ID, selecting only the
   terms relevant to CMIP7.

  ## Key Concepts

  - **WCRP-universe**: The canonical repository containing all possible terms with full metadata (experiments, institutions, models, variables, etc.)
  - **CMIP7_CVs**: Project-specific collections that reference universe terms by ID, with optional project-specific overrides
  - **Collections**: Folders containing JSON files that list term IDs from a specific data descriptor (e.g., activity/, experiment/, institution/)
  - **Terms**: Individual JSON files representing a controlled vocabulary entry (e.g., experiment/historical.json)

## Repository Structure

  CMIP7_CVs/  
  ├── project_specs.json       # DRS (Data Reference Syntax) and global attributes  
  ├── project_specs.yaml        # Project metadata  
  ├── activity/                 # Activity IDs (CMIP, ScenarioMIP, etc.)  
  ├── experiment/               # Experiment definitions  
  ├── institution/              # Institutions  
  ├── source/                   # Climate models  
  ├── brandedVariable/          # Variable names  
  ├── reportingInterval/        # Temporal frequencies  
  └── ...                       # Other collections  

  Each collection folder contains:
  - 000_context.jsonld: JSON-LD context for semantic web compatibility
  - {term-id}.json: Individual term files that reference universe terms

  ### How Terms Link to the Universe

  Terms in CMIP7_CVs reference the universe using minimal JSON:
```json
  Example - CMIP7_CVs/activity/cmip.json:
  {
      "@context": "000_context.jsonld",
      "id": "cmip",
      "type": "activity"
  }
```
  This references the full definition in WCRP-universe/activity/cmip.json:
  ```json
  {
      "@context": "000_context.jsonld",
      "type": "activity",
      "id": "cmip",
      "name": "CMIP",
      "cmip_acronym": "CMIP",
      "long_name": "CMIP DECK: 1pctCO2, abrupt4xCO2, amip, ...",
      "url": "https://gmd.copernicus.org/articles/9/1937/2016/...",
      "drs_name": "CMIP"
  }
```
  Projects can override or add properties by including them in their term files.

### Using with esgvoc

  The https://github.com/ESGF/esgf-vocab provides a Python API and CLI to interact with these controlled vocabularies.

 Documentation can be find : https://esgf.github.io/esgf-vocab/


