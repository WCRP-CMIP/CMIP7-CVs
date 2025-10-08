# CMIP7 Controlled Vocabularies
Core Controlled Vocabularies (CVs) for use in CMIP7

------

# CV location. 
**For information on what is in the CVs please visit the ESGVOC repository at: [insert link here]()
**

------

### THIS REPOSITORY IS CURRENTLY UNDER ACTIVE DEVELOPMENT

------

## Branch Descriptions

| Required |  |
|--------|-------------|
| [`main`](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/main) | The landing page directing users to the relevant content. |
| [`docs`](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/docs) | Contains the documentation and is version-controlled. This is the branch where documentation edits are made. Actions and automations (e.g., workflows that update docs or summaries) are also configured from this branch. |
| [`src-data`](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/src-data) | Stores the JSONLD content used to link all files. Updates here trigger automated workflows that identify changed JSON files and update documentation or summaries accordingly. |
| [`production`](https://github.com/WCRP-CMIP/CMIP7-CVs/tree/production) | Hosts the compiled documentation and JSONLD files, as well as the static pages site. Updated automatically via workflows when changes in `src-data` or `docs` are processed. |



| Optional |  |
|--------|-------------|
| `dev_*` | Other branches used for updating things. |
| `*` | All other branches are usually ones containing submissions to update the content. |






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
