# CMIP6 Global Attributes, DRS, Filenames, Directory Structure, and CV's

**9 June 2025 (v6.2.8)**  
*No substantive edits since 10 September 2018*

**Document short URL**: https://goo.gl/v1drZl

**Authors**: Karl E. Taylor, Martin Juckes, V. Balaji, Luca Cinquini, Sébastien Denvil, Paul J. Durack, Mark Elkington, Eric Guilyardi, Slava Kharin, Michael Lautenschlager, Bryan Lawrence, Denis Nadeau, and Martina Stockhause

## Executive Summary

In files containing CMIP model-simulation output, global attributes are used to describe the source of the data, the imposed experiment conditions, the contents of the file, licensing restrictions, and other information useful to those analyzing the data. Here we define the global attributes that should appear in CMIP6 files (some are required, others optional), along with the so-called CMIP6 "data reference syntax" (DRS). The subset of global attributes that defines the DRS is used in constructing the directory structure and file names found in the CMIP6 archive, and also to construct URLs leading to further information about the simulations and in populating search facets.

## Introduction

As in earlier phases of CMIP, a well-defined set of global attributes will be recorded in each CMIP6 model output file, providing information necessary for interpreting the data. Table 1 contains the list of CMIP6 global attributes and indicates which ones are required and which are optional. The values for many of the global attributes must be drawn from special CMIP6 "controlled vocabularies" (CVs). A CV, in simplest form, is a list of the permitted values that can be assigned to a given global attribute. Some of these lists of permitted values appear in this document, but they should not be relied on to be 100% correct. Rather, consult the reference CVs for CMIP6, which are available at https://github.com/WCRP-CMIP/CMIP6_CVs/

A subset of the global attributes, which comprise the data reference syntax (DRS) for CMIP6, are described following the Table 1 notes, and templates for the CMIP6 filenames and directory structures are also defined. Table 3 provides a summary of the quality assurance checks that should be performed on CMIP6 files.

[Appendix 1](appendix1_global_attributes_labeling_experiments.md) describes the rationale underlying the global attributes used to label CMIP6 experiments, and provides additional details. [Appendix 2](appendix2_algorithms_nominal_resolution.md) defines the algorithm used to define the "nominal_resolution" attribute. [Appendix 3](appendix3_document_version_information.md) contains a revision history of this document.

Documents of related interest may be found at: https://wcrp-cmip.github.io/WGCM_Infrastructure_Panel/

## Table 1: CMIP6 Global Attributes

CMIP6 global attribute description and comparison with CMIP5 (see CMIP5_output_metadata_requirements.pdf and cmip5_data_reference_syntax.pdf).

**Table key**: 
- <span style="background-color: yellow">name or form has been changed (relative to CMIP5)</span>
- <span style="background-color: lightgreen">new attribute for CMIP6</span>

| CMIP6 global attribute | description | examples | corresponding attribute in CMIP5 | form | when required? | further information and rationale |
|---|---|---|---|---|---|---|
| <span style="background-color: yellow">activity_id</span> | activity identifier(s) (part of DRS) | "CMIP", "PMIP", "LS3MIP LUMIP" (see note 3 and reference CV) | project_id | CV | always | renamed more generically, since not all activities are projects; also multiple activities may now be listed separated by single spaces. Used in faceted searches. |
| <span style="background-color: lightgreen">branch_method</span> | branching procedure | "standard", "no parent" (see note 4) | - | free form | whenever parent exists | in CMIP6 some branching methods will involve short spin-up periods or other non-standard procedures which need to be described. See note 4. If no parent, omit or set to "no parent" |
| <span style="background-color: lightgreen">branch_time_in_child</span> | branch time with respect to child's time axis | 365.0D0, 0.0D0 (see note 5) | - | double precision float | whenever parent exists | aids in interpreting branch times; units are the same as the units used for the child's time axis. If no parent, omit (preferred) or set to start time of the run. |
| <span style="background-color: yellow">branch_time_in_parent</span> | branch time with respect to parent time axis | 3650.0D0 (see note 5) | branch_time | double precision float | whenever parent exists | changed name to explicitly distinguish it from branch_time_in_child; units are specified in the attribute: parent_time_units. If no parent, omit (preferred) or set to 0.0D0. |
| comment | see note 6 | see note 6 | comment | free form | never | no change from CMIP5; CF-convention standard |
| contact | see note 6 | see note 6 | contact | free form | never | required in CMIP5, but not now because information should be available via further_info_url |
| <span style="background-color: yellow">Conventions</span> | convention version | "CF-1.7 CMIP-6.2" or "CF-1.7 CMIP-6.2 UGRID-1.0" | Conventions | CV | always | updated version from CMIP5 with a list of conventions separated by single spaces now allowed. The "examples" show the only options. Note that CMIP-6.2 reflects the version of the present document (without indicating the minor changes), and would have to be updated if the present document were incremented from 6.2.x to 6.3.0. |
| creation_date | date file was created | see note 7 | creation_date | structured form | always | no change from CMIP5 |
| <span style="background-color: lightgreen">data_specs_version</span> | version identifier | 01.00.00, 01.00.01, … 01.00.xx (see data request for latest release) | - | CV | always | records the version (or "release") number of the data request, which is relied on for certain global and variable attributes. |
| experiment | short experiment description | "pre-industrial control", "abrupt quadrupling of CO2" (see reference CV) | experiment | CV | always | no change from CMIP5 |
| experiment_id | root experiment identifier (part of DRS) | "historical", "abrupt4xCO2" (see Appendix 1 and reference CV) | experiment_id | CV | always | similar to CMIP5. Used in faceted searches. |
| <span style="background-color: lightgreen">external_variables</span> | external cell measures | "areacella", "areacello" | - | CV | whenever appropriate | list of cell measure variables (separated by single spaces) that are referenced but not included in the file. These variables will be stored independently in the CMIP data archive. |
| <span style="background-color: lightgreen">forcing_index</span> | index for variant of forcing | 1, 2, 82, 323 | - | integer >0 (see note 8) | always | distinguishes variants that differ in forcing |
| frequency | sampling frequency | "mon", "day", "6hr" (see reference CV) | frequency | CV | always | no change from CMIP5; value must be consistent with the data request. Used in faceted searches. |
| <span style="background-color: lightgreen">further_info_url</span> | location of documentation | see note 9 | - | CV | always | points to definitive documentation that can be updated (even after data files have been written) |
| <span style="background-color: lightgreen">grid</span> | grid | see note 10 | - | free form | always | briefly describes output grid characteristics |
| <span style="background-color: lightgreen">grid_label</span> | grid identifier (part of DRS) | "gn", "gr", "gr1", "gr2", "grz", "gm" (see reference CV) | - | CV (see note 11) | always | used in file name to distinguish among files when the variable is reported on more than one grid. Used in faceted searches. |
| history | see note 6 | see note 6 | history | free form | never | no change; CF-convention standard |
| <span style="background-color: yellow">initialization_index</span> | Index for variant of initialization method | 1 | initialization_method | integer >0 (see note 8) | always | name changed to increase consistency; 0 is forbidden in CMIP6 |
| institution | institution name | "Meteorological Research Institute" (see reference CV) | institution | registered content | always | no change from CMIP5 |
| <span style="background-color: yellow">institution_id</span> | institution identifier (part of DRS) | "IPSL" (see reference CV) | institute_id | registered content | always | Was "institute_id"; name changed to parallel other global attributes; this string is constructed only using the character set: a-z, A-Z, 0-9, and '-' (i.e., hyphen). Used in faceted searches. |
| <span style="background-color: lightgreen">license</span> | license restrictions | see note 12 | - | some required text | always | ensures that anyone using the files has access to the terms of use |
| <span style="background-color: lightgreen">mip_era</span> | activity's associated CMIP cycle (part of DRS) | "CMIP5", "CMIP6" (see note 3 and reference CV) | - | CV | always | added to fully define activity and to enable one to determine what cycle of CMIP dictates experiment and data specifications. This means that mip_era="CMIP6" for all CMIP6 output no matter how old the model is that produced it. Used in faceted searches. |
| <span style="background-color: lightgreen">nominal_resolution</span> | approximate horizontal resolution | "50 km", "100 km", "250 km", "1x1 degree". (See Appendix 2) | - | CV | always | Added in CMIP6 to provide an indication of approximate output grid resolution. See Appendix 2. Used in faceted searches. |
| <span style="background-color: lightgreen">parent_activity_id</span> | parent activity identifier | "CMIP", ScenarioMIP (see reference CV) | - | CV | whenever parent exists | to help identify parent run (when parent comes from a different MIP); when no parent, omit or set to "no parent" |
| parent_experiment_id | parent experiment identifier | "piControl" (see reference CV) | parent_experiment_id | CV | whenever parent exists | If the parent run is immaterial or if an experiment is initialized in some other way (e.g., from observations), then omit or set to "no parent" |
| <span style="background-color: lightgreen">parent_mip_era</span> | parent's associated MIP cycle | "CMIP5", "CMIP6" (see reference CV) | - | CV | whenever parent exists | with parent_activity_id, this fully defines parent activity; when no parent, omit or set to "no parent" |
| <span style="background-color: lightgreen">parent_source_id</span> | parent model identifier | "CanCM4" (see reference CV) | - | registered content | whenever parent exists | helps identify parent run; when no parent, omit or set to "no parent"; usually will be the same as source_id |
| <span style="background-color: lightgreen">parent_time_units</span> | time units used in parent | "days since 1850-1-1", "days since 1000-1-1 (noleap)" (see note 5) | - | structured form | whenever parent exists | without this, a user would have to read the parent file to interpret branch_time_in_parent; the "calendar" modifier is required only if the calendars used by the parent and child differ. When no parent, omit or set to "no parent". |
| <span style="background-color: yellow">parent_variant_label</span> (modified form) | parent variant label | "r1i1p1f1", "r1i2p223f3", "no parent" | parent_experiment_rip | see Appendix 1 | whenever parent exists | used to distinguish among variants of the parent; when no parent, omit or set to "no parent" |
| <span style="background-color: yellow">physics_index</span> | index for model physics variant | 3 | physics_version | integer >0 (see note 8) | always | name changed to increase consistency; 0 is forbidden |
| product | product type (part of DRS) | "model-output" | product | - | always | As in CMIP5, but "model-output" is now the only option. Used in faceted searches. |
| <span style="background-color: yellow">realization_index</span> | realization number | 5 | realization | integer >0 (see note 8) | always | name changed to increase consistency; 0 is forbidden |
| <span style="background-color: yellow">realm</span> | realm(s) where variable is defined (part of DRS) | "atmos", "ocean", "atmosChem atmos" (see reference CV) | modeling_realm | CV | always | name changed to make appropriate for observational data; multiple realms may be listed (separated by single spaces) when appropriate. Value(s) must be consistent with the data request. Used in faceted searches. |
| references | see note 6 | see note 6 | references | free form | never | no change; CF-convention standard |
| <span style="background-color: yellow">source</span> (modified form) | full model name/version | see note 13 and reference CV | source | registered content | always | somewhat different form from CMIP5. The first part (before the colon) should be an abbreviated identifier that is the basis of source_id |
| <span style="background-color: yellow">source_id</span> (modified form) | model identifier (part of DRS) | "GFDL-CM2-1" (see note 13 and reference CV) | model_id | registered content (limited in length to no more than 16 characters) | always | edited version of the first part of "source" (with forbidden characters like spaces and periods replaced with hyphens); used in constructing the file name. Used in faceted searches. |
| <span style="background-color: lightgreen">source_type</span> | model configuration | "AGCM", "OGCM", "AOGCM", "ISM", "AOGCM ISM" (see reference CV) | - | CV see note 14 | always | added partly because obs4MIPs defines this (e.g., "in-situ"); This should describe the model most directly responsible for the output (e.g., for dynamical downscaling output, it would describe the regional model, not the global model responsible for driving the regional model). Sometimes it is appropriate to list two (or more) model types here. Used in faceted searches. |
| <span style="background-color: lightgreen">sub_experiment</span> | description of sub-experiment | see Appendix 1 and reference CV | - | CV | always | needed for CMIP6 hindcast and forecast experiments. For other experiments, this should be set to "none". |
| <span style="background-color: lightgreen">sub_experiment_id</span> | sub-experiment identifier (part of DRS "member_id") | "s1960", "s1965", "none" (see reference CV) | - | CV | always | needed for CMIP6 hindcast and forecast experiments to indicate "start year". For other experiments, this should be set to "none". Used in faceted searches. |
| table_id | table identifier (part of DRS) | "Amon", "Oday" (see reference CV) | table_id | CV | always | the word "Table" is no longer included in this attribute (e.g., "Amon", not "Table Amon") and there should be no additional information (such as table date and check sum) included. Used in faceted searches. |
| title | see note 6 | see note 6 | title | free form | never | no change; CF-convention standard |
| <span style="background-color: yellow">tracking_id</span> (modified form) | unique file identifier | see note 15 | tracking_id | structured form with some CV | always | form modified to facilitate its use by ESGF. |
| <span style="background-color: lightgreen">variable_id</span> | variable identifier (part of DRS) | "tas", "pr", "ua" (see data request) | - | CV | always | added to direct users and software to the primary variable of interest in the file. Used in faceted searches. |
| <span style="background-color: lightgreen">variant_info</span> | description of run variant | "forcing: black carbon aerosol only" | - | free form | never, but recommended see note 16 | provides brief descriptions of variant differences |
| <span style="background-color: lightgreen">variant_label</span> | "variant" label (part of DRS "member_id") | "r1i1p1f1", "f1i2p223f3" | - | see Appendix 1 | always | used in faceted searches |
| - | see note 17 | - | forcing | - | not used in CMIP6 | no longer needed because this information is now recorded in variant_info |

### Table Notes:

1. If CMOR is used to write output files, an additional global attribute will be included: cmor_version.

2. "CV" means content must be taken from a "controlled vocabulary" defined by the WIP. "registered content" is a special controlled vocabulary defined by each modeling group and approved by the WIP. The reference CV's are hosted [here](https://github.com/WCRP-CMIP/CMIP6_CVs).

3. The project_id used in CMIP5 is being replaced in CMIP6 with two global attributes: 1) a mip_era (a label indicating the CMIP cycle responsible for the experiment and data request), which for CMIP6 must invariably be set to "CMIP6", and 2) an activity_id identifying the responsible "MIP". In a few cases multiple activities in the activity_id must be included (separated by single spaces). An example of this is "LUMIP AerChemMIP" for one of the CMIP6 land-use change experiments. For a given experiment, the activity_id must include all the associated activities in the order they are listed in the experiment_id CV.

4. branch_method examples: "perturbations to atmospheric fields were applied at the branch time, followed by a 50 year spin-up period under control conditions"; "fixed historical forcing from year 1850 was applied for a 20 year spin-up period, after which the historically-evolving forcing was imposed." For a run that had not been spawned from a parent, this attribute should be omitted or set to "no parent". If external documentation describing the branch method can be retrieved using the url recorded in the further_info_url global attribute, then branch_method may be set to "see further_info_url", but it is better to provide a brief description as in the examples above. For runs simply restarted from some point in the parent (without special procedures applied), branch_method should be set to "standard".

5. The three attributes related to branching time (branch_time_in_child, branch_time_in_parent, parent_time_units) must be included if branch time is needed to correctly interpret the data (e.g., in simulations spawned from a pre-industrial control run that has not reached equilibrium). Suppose a model with a "noleap" calendar carries out a control run with the time coordinate reported in units of "days since 1000-1-1". Now suppose a historical simulation branches from that control run at day 3650 (i.e., on the date: 1010-1-1), and suppose the units of the time coordinate for the historical run are "days since 1850-01-01". Then in the historical run, the following global attributes should appear:
   ```
   branch_time_in_child = 0.0D0; # double precision float
   branch_time_in_parent = 3650.0D0; # double precision float
   parent_time_units = "days since 1000-1-1"; # character string
   ```
   If the calendar used in the parent is different from the child, then the parent's calendar should be recorded in "parent_time_units". The CV for the calendar is the same as that for the CF calendar attribute. For example in the above case, if the child's calendar is "gregorian", but the parent's is "noleap", then parent_time_units="days since 1000-1-1 (noleap)".
   
   As another example, suppose a ScenarioMIP simulation "branches" from a historical run at the date 2015-1-1. Suppose a noleap calendar is used in each and both have units of "days since 1850-1-1". (Note that ScenarioMIP simulations should always adopt the same units as the historical parent.) In this case the following global attributes should appear in the ScenarioMIP output file:
   ```
   branch_time_in_child = 60225.0D0
   branch_time_in_parent = 60225.0D0
   parent_time_units = "days since 1850-1-1".
   ```
   
   As a third example, consider a decadal prediction experiment initialized from observations (e.g., from an "analysis"). In this case there is no parent so none of these attributes should be included. (Note that the initialization time of the decadal prediction experiments will be recorded as a scalar coordinate dimension, pointed to by the "coordinates" attribute, which is attached to each variable.)

6. A description and examples of this global attribute may be found in the document: CMIP5_output_metadata_requirements (http://cmip-pcmCMIP5_output_metadata_requirements.pdf).

7. creation_date form: YYYY-MM-DDTHH:MM:SSZ (e.g., "2010-03-23T05:56:23Z")

8. For a given experiment, the realization_index, initialization_index, physics_index, and forcing_index are used to uniquely identify each simulation of an ensemble of runs contributed by a single model. These indices are defined as follows:
   - **realization_index** = an integer (≥1) distinguishing among members of an ensemble of simulations that differ only in their initial conditions (e.g., initialized from different points in a control run). Note that if two different simulations were started from the same initial conditions, the same realization number should be used for both simulations. For example if a historical run with "natural forcing" only and another historical run that includes anthropogenic forcing were both spawned at the same point in a control run, both should be assigned the same realization. Also, each so-called RCP (future scenario) simulation should normally be assigned the same realization integer as the historical run from which it was initiated. This will allow users to easily splice together the appropriate historical and future runs.
   - **initialization_index** = an integer (≥1), which should be assigned a value of 1 except to distinguish simulations performed under the same conditions but with different initialization procedures. In CMIP6 this index should invariably be assigned the value "1" except for some hindcast and forecast experiments called for by the DCPP activity. The initialization_index can be used either to distinguish between different algorithms used to impose initial conditions on a forecast or to distinguish between different observational datasets used to initialize a forecast.
   - **physics_index** = an integer (≥1) identifying the physics version used by the model. In the usual case of a single physics version of a model, this argument should normally be assigned the value 1, but it is essential that a consistent assignment of physics_index be used across all simulations performed by a particular model. Use of "physics_index" is reserved for closely-related model versions (e.g., as in a "perturbed physics" ensemble) or for the same model run with slightly different parameterizations (e.g., of cloud physics). Model versions that are substantially different from one another should be given a different source_id" (rather than simply assigning a different value of the physics_index).
   - **forcing_index** = an integer (≥1) used to distinguish runs conforming to the protocol of a single CMIP6 experiment, but with different variants of forcing applied. One can, for example, distinguish between two historical simulations, one forced with the CMIP6-recommended forcing data sets and another forced by a different dataset, which might yield information about how forcing uncertainty affects the simulation.
   
   Each data provider can assign whatever positive integers they like for the realization_index, intialization_index, physics_index, and forcing index. For each source/experiment pair, however, consistency (in these indices) should be maintained across each parent/child pair whenever sensible (so that, for example, both the ScenarioMIP child and its "historical" parent simulation would be assigned the same set of index values for realization, initialization, and physics); the integer 1 should normally be chosen for each of these in the case of a single variant or for the primary variant (if there is one). This is only a suggestion, however; there should be no expectation on the part of users that every model will have a value of 1 assigned to any of the r, i, p, f indices, and even if a 1 is assigned it does not imply that it is the primary variant. Note also that a child spawned by a control run will not necessarily have the same "ripf" value as the control, since, for example, multiple realizations of an experiment will branch from the same control.
   
   Note that none of the "ripf" indices can be omitted.
   
   Example of a variant_label: if realization_index=2, initialization_index=1, physics_index=3, and forcing_index=233, then variant_label = "r2i1p3f233".

9. further_info_url has the form `https://furtherinfo.es-doc.org/<mip_era>.<institution_id>.<source_id>.<experiment_id>.<sub_experiment_id>.<variant_label>` (e.g., "https://furtherinfo.es-doc.org/CMIP6.CAS_FGOALS-g3.historical.none.r3i1p1f1"). The further_info_url page will be maintained by the es-docs project and will simply be a rendering by the Viewer tool of information provided by modeling groups and recorded in so-called CIM documents.

10. The "grid" global attribute can be used to describe the horizontal grid and regridding procedure. There is no standard form used to record this information, but it is suggested that when appropriate the following be indicated: brief description of native grid and resolution, and if data have been regridded, regridding procedure and description of target grid. Here are some examples:
    ```
    grid = "native atmosphere T63 gaussian grid (128x64 lonxlat)"
    grid = "data regridded to a CMIP6 standard 1x1 degree lonxlat grid from the native T63 grid using an area-average preserving method."
    grid = "data regridded via bilinear interpolation to a 3x3 deg lonxlat grid from the native atmosphere T63 gaussian grid (128x64 lonxlat)"
    grid = "native ocean tri-polar grid with 43200 ocean cells"
    ```

11. Modeling groups may choose to report their output on the model's native grid and/or regrid it to one or more target grids. To distinguish between output reported on different grids, a "grid_label" attribute is defined.
    
    The rules for assigning grid labels should make it easy for users to select (using the ESGF search tools) CMIP output that is on a grid considered by each modeling group to best represent its model -- the so-called "primary" grid. If output is reported on the native grid, this is always deemed the "primary" grid. If output is not reported on the native grid, then modeling groups should regrid the data to some primary grid of its choosing For the "primary" grid the following labels apply:
    - grid_label = "gn" (output is reported on the native grid, usually but not invariably at grid cell centers)
    - grid_label = "gr" (output is not reported on the native grid, but instead is regridded by the modeling group to a "primary grid" of its choosing)
    - grid_label = "gm" (global mean output is reported, so data are not gridded)
    
    As noted below sometimes a "z" or "a" or "g" is appended to the labels to indicate "zonal means" or grids limited to Antarctica or Greenland.
    
    If besides the "primary" grid, output is regridded to an additional grid, then for this output:
    - grid_label = "gr[i]" (a "secondary" grid), where <i> should be replaced by a positive integer less than 10, which distinguishes this output from other regridded output.
    
    Note that:
    - If model output is reported on a native grid, then if regridded output is also reported, it must not be labeled "gr", but instead should be of the form gr[i] (e.g,, gr1, gr2, ….).
    - The grid label provides no information about the grid other than to indicate whether or not the data have been regridded (from the native grid) and whether or not the grid is considered to be a "primary" grid by the data provider.
    - Output for different variables may be reported on different grids, so "gn" and "gr" may not uniquely define a grid even within a single model.
    - If a variable is reported on more than one grid, one of these grids must be labeled "gn" or "gr" (as appropriate), and others must be labeled as secondary grids ("gr1", "gr2", etc.).
    - The grid labels ("gr1", "gr2", etc.) must be defined consistently for all variables reported from a single model on the same secondary grid. Thus, if "gr3" indicates output on a 2x2 degree grid for one variable, then the same label should be used for other variables output on this grid (unless for another variable output is considered to be primary, in which case the output would be labeled "gn" or "gr", as appropriate).
    - Output on the same grid but from different models will usually not be labeled with the same grid_label, since data providers independently assign the labels.
    - A "nominal_resolution" attribute must be defined as specified in Appendix 2, and a brief description of the grid should be recorded in the "grid" global attribute (see note 10).
    - For zonal mean output, a "z" should be appended to the grid label that would apply before performing the zonal mean (e.g., "gnz", "grz", "gr2z"). The "gnz" label would likely only be appropriate when zonally-averaging data on a native cartesian latxlon grid.
    - For "site" data the label "gn" should be used presuming data are obtained from the single native grid cell located nearest each site.
    - For "transport through a straight" (and the like), the grid label should reflect the grid relied on in calculating the transport (presumably the native grid would be best for this purpose, so "gn").
    - For output reported only over the region centered on Greenland, "g" should be appended to the grid_label (e.g., "gng", "grg", "gr1g"). Similarly for output reported only over the region centered on Antarctica, "a" should be appended to the grid_label.

12. The "license" attribute should record the following statement (with segments in square brackets optional, and with required, appropriate text entered in place of <*> ): "CMIP6 model data produced by <Your Centre Name> is licensed under a Creative Commons Attribution-[*]ShareAlike 4.0 International License (https://creativecommons.org/licenses/). Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, including citation requirements and proper acknowledgment. Further information about this data, including some limitations, can be found via the further_info_url (recorded as a global attribute in this file)[ and at <some URL maintained by modeling group>]. The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law."
    
    \* The [*] indicates that institutions may choose to use the Non-commercial version of this license by inserting the words "NonCommercial-" at this point, but this will significantly limit the use of the data in downstream climate mitigation and adaptation applications. Please do not simply copy the statement above when writing data; Some text must be entered, some text is optional and the symbols "[*]" should not appear in the licensing text.

13. The "source" is used to fully identify the model and version. The first portion of the "source" attribute is used in constructing "source_id". [The "source_id", which must not exceed 16 characters in length, is the same as the "modified source_id" (which appears as the first part of "source"-- see below) but with forbidden characters removed or replaced by a hyphen ("-"). All characters are forbidden in source_id except a-z, A-Z, 0-9 and the hyphen ("-").] Additionally, the "source" attribute must include the year (i.e., model vintage) when this model version was first used in a scientific application. It should also include information concerning the component models. The following template should be followed in constructing "source":
    
    `<modified source_id> (<year>): atmos: <model_name> (<technical_name>, <resolution_and_levels>); ocean: <model_name> (<technical_name>, <native_resolution_and_levels>); seaIce: <model_name> (<technical_name>); land: <model_name> (<technical_name>); aerosol: <model_name> (<technical_name>); atmosChem: <model_name> (<technical_name>); ocnBgchem: <model_name> (<technical_name>); landIce: <model_name> (<technical_name>)`
    
    For some models, it may not make sense to include all these components, and none of the text following "<year>" is absolutely mandatory. As an example, "source" might contain the string:
    
    CCSM2 (2002): atmos: CAM2 (cam2_0_brnchT_itea_2, T42L26); ocean: POP (pop2_0_ver_1.4.3, 3x2L15); seaIce: CSIM4; land: CLM2.0
    
    The source and source_id should not change even when some of the component models are inactive in some of the CMIP experiments. For example, if an AOGCM is named "SomeAOGCM 1.0 (2016): atmosphere: SomeAGCM; ocean: SomeOGCM; sea ice: SomeSeaIce", then source_id would be "SomeAOGCM-1-0" and this same name would be used whether or not the model were run in coupled mode or AMIP mode (with prescribed SST and sea ice).

14. The source_type will depend on which experiment is being performed. Options in the CV include:
    - AGCM (atmospheric general circulation model, including a land model),
    - OGCM (ocean general circulation model, including a sea-ice model),
    - AOGCM (atmosphere-ocean global climate model),
    - LAND (land model but only if run "offline"),
    - ISM (ice-sheet model, which may be run "offline" or coupled to an AOGCM),
    - RAD (radiation code but only if run "offline"),
    - BGC (for a model component that includes a biogeochemical treatment which at the very least can account for carbon reservoirs and fluxes in the atmosphere, terrestrial biosphere, and ocean; for some model configurations, only part of the BGC component will be active. For example, in a BGC model coupled to an AGCM, the ocean component of the BGC might be inactive, but the source_type would be "AGCM BGC". For a BGC model run coupled to an AOGCM, the source_type should include "AOGCM BGC" both when atmospheric concentrations are calculated and when they are prescribed),
    - CHEM (appears with either AOGCM or AGCM in models that calculate, rather than rely on prescribed concentrations of atmospheric oxidants including at least ozone),
    - AER (appears with AOGCM or AGCM in models that calculate tropospheric aerosols driven by emission fluxes, rather than relying on prescribed concentrations),
    - SLAB (a slab-ocean model).
    
    All types that apply to the model (i.e., are active in a given experiment) should appear in a list with each type separated by a single space.
    
    Sometimes source_type for CMIP6 simulations will be described by a single label, as in "AOGCM" or "AGCM" or "OGCM", but when additional interactive components are included, then multiple labels should be found in source_type (e..g., "AOGCM BGC", "AGCM CHEM AER", "AOGCM AER", "AOGCM ISM", "AGCM SLAB", "OGCM BGC"). Single labels will be used for "offline" models such as "ISM" and "RAD".
    
    For each of the CMIP6 experiments, the list of components that are required and the ones that are allowed but optional can be found in CMIP6 experiment_id values (or, alternatively, [here](https://github.com/WCRP-CMIP/CMIP6_CVs)). The following combinations for source_type can be found there:
    ```
    AGCM [BGC] [AER] [CHEM] [SLAB]
    AOGCM [BGC] [AER] [CHEM] [ISM]
    OGCM
    LAND
    ISM
    RAD
    ```
    where the text in brackets sometimes must appear, other times, may appear, and in still other cases should *not* appear, depending on the experiment. Apart from the first item listed, the ordering of the components is arbitrary in source_type, and all brackets should be removed (see examples in earlier paragraph above).

15. tracking_id should be of the form "hdl:21.14100/<uuid>" (e.g., "hdl:21.14100/02d9e6d5-9467-382e-8f9b-9300a64ac3cd"). The tracking_id should be unique for each file published in ESGF. The <uuid> should be generated using the OSSP utility which supports a number of different DCE 1.1 variant UUID options. For CMIP6, version 4 (random number based) is required. Download the software from http://www.ossp.org/pkg/lib/uuid/.

16. It is recommended that variant_info include information identifying major distinguishing features of a variant, but care should be taken to record correct information. Prudence dictates that this attribute include a warning along the following lines: "Information provided by this attribute may in some cases be flawed. Users can find more comprehensive and up-to-date documentation via the further_info_url global attribute."

17. The information stored in the "forcing" attribute in CMIP5 may in CMIP6 appear in the variant_info attribute.

## Data Reference Syntax (DRS) components:

The DRS identifies experiments, simulations, ensembles of experiments, and atomic datasets. Some of the DRS components are used, for example, to construct file names, directory structures, the further_info_url, and in facets of some search tools. The following components are needed for CMIP6 (along with their CMIP5 counterparts):

| DRS Component | CMIP5 Name | Reference | Notes |
|---|---|---|---|
| activity_id* | "activity" | see CMIP6_activity_id.json | |
| institution_id | "institute" | see CMIP6_institution_id.json | |
| source_id | "model" | see CMIP6_source_id.json | |
| experiment_id | "experiment" | see CMIP6_experiment_id.json | |
| variable_id | "variable name" | see data request | |
| table_id | "table_id" | see CMIP6_table_id.json | |
| variant_label | "ensemble member" | construct from realization, initialization, physics, and forcing indices | |
| version | "version number" | indicating approximate date of model output file | (This is the only DRS element that is not stored as a global attribute.) |

We need additional components in CMIP6 to accommodate the more complex structure:

| DRS Component | Notes | Reference |
|---|---|---|
| sub_experiment_id | set to "none" for most experiments | see CMIP6_sub_experiment_id.json |
| grid_label | needed to distinguish the same field stored on more than one grid | see CMIP6_grid_label.json |
| mip_era | needed to distinguish CMIP5 experiments and datasets from CMIP6 | set to "CMIP6" |
| member_id | a compound construction from sub_experiment_id and variant_label | see below for further information |

As in CMIP5, we also define additional DRS elements because they can be helpful in providing data discovery services:

| DRS Component | CMIP5 Name | Reference | Notes |
|---|---|---|---|
| frequency | "frequency" | see CMIP6_frequency.json | |
| realm* | "modeling realm" | see CMIP6_realm.json | |
| product | "product" | set to "model-output" in CMIP6 | |
| nominal_resolution | | see CMIP6_nominal_resolution.json and Appendix 2 | |
| source_type* | | see CMIP6_source_type.json | |

The DRS elements marked with an asterisk (*) are associated with global attributes that may be space-separated lists of values. Only the first item in a list is recognized by the DRS, but in faceted searches all listed items will be recognized.

## File name template:

Before constructing file names and directory structures, it is useful to define a member_id, which can be used to distinguish among different simulations belonging to a root experiment. The member_id is constructed from the sub_experiment_id and variant_label using the following algorithm:

```
if sub_experiment_id = "none"
    member_id = <variant_label>
else
    member_id = <sub_experiment_id>-<variant_label>
endif
```

With this segment defined, the file name can be constructed consistent with the following template:

```
file name = <variable_id>_<table_id>_<source_id>_<experiment_id >_<member_id>_<grid_label>[_<time_range>].nc
```

For time-invariant fields, the last segment (time_range) above is omitted.

Example when there is no sub-experiment: `tas_Amon_GFDL-CM4_historical_r1i1p1f1_gn_196001-199912.nc`
Example with a sub-experiment: `pr_day_CNRM-CM6-1_dcppA-hindcast_s1960-r2i1p1f1_gn_198001-198412.nc`

All strings appearing in the file name are constructed using only the following characters: a-z, A-Z, 0-9, and the hyphen ("-"), except the hyphen must not appear in variable_id. Underscores are prohibited throughout except as shown in the template.

Note that the last segment of the file name indicates the time-range spanned by the data in the file, and is omitted when inappropriate (e.g., if a variable is "fixed" for all time). The format for this segment is as in CMIP5 (see cmip5_data_reference_syntax.pdf):

The <time_range> is a string generated consistent with the following:
```
If frequency = "fx" then
    <time_range>=""
else
    <time_range> = N1-N2<suffix> where N1 and N2 are integers of the form 'yyyy[MM[dd[hh[mm[ss]]]]]' 
                   (expressed as a string, where 'yyyy', 'MM', 'dd', 'hh' 'mm' and 'ss' are 
                   integer year, month, day, hour, minute, and second, respectively)
endif
```

where <suffix> is defined as follows:
```
if the variable identified by variable_id has a time dimension with a "climatology" attribute then
    suffix = "-clim"
else
    suffix = ""
endif
```

and where the precision of the time_range strings is determined by the "frequency" global attribute as specified in Table 2.

## Table 2: Precision of time labels used in file names.

| Frequency | Precision of time label | Notes |
|---|---|---|
| yr, dec, yrPt | "yyyy" | Label with the years recorded in the first and last coordinate values. |
| mon, monC | "yyyyMM" | For "mon", label with the months recorded in the first and last coordinate values; for "monC" label with the first and last months contributing to the climatology. |
| day | "yyyyMMdd" | Label with the days recorded in the first and last coordinate values. |
| 6hr, 3hr, 1hr, 1hrCM, 6hrPt, 3hrPt, 1hrPt | "yyyyMMddhhmm" | Label 1hrCM files with the beginning of the first hour and the end of the last hour contributing to climatology (rounded to the nearest minute); for other frequencies in this category, label with the first and last time-coordinate values (rounded to the nearest minute). |
| subhrPt | "yyyyMMddhhmmss" | Label with the first and last time-coordinate values (rounded to the nearest second) |
| fx | Omit time label | This frequency applies to variables that are independent of time ("fixed"). |

## Directory structure template:

```
Directory structure = <mip_era>/
                     <activity_id>/
                     <institution_id>/
                     <source_id>/
                     <experiment_id>/
                     <member_id>/
                     <table_id>/
                     <variable_id>/
                     <grid_label>/
                     <version>
```

Note:
- <version> has the form "vYYYYMMDD" (e.g., "v20160314"), indicating a representative date for the version. Note that files contained in a single <version> subdirectory at the end of the directory path should represent all the available time-samples reported from the simulation; a time-series can be split across several files, but all the files must be found in the same subdirectory. This implies that <version> will not generally be the actual date that all files in the subdirectory were written or published.
- If multiple activities are listed in the global attribute, the first one is used in the directory structure.

Example when there is no sub-experiment: `CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/1pctCO2/r1i1p1f1/Amon/tas/gn/v20150322`
Example with a sub-experiment: `CMIP6/DCPP/CNRM-CERFACS/CNRM-CM6-1/dcppA-hindcast/s1960-r2i1p1f3/day/pr/gn/v20160215`

The above directory structure is not the same as CMIP5's directory structure.

## Table 3: Quality assurance checks

[Note that "CMIP6 data request" refers to information recorded in the "dreq" xml files.]

| CMIP6 global attribute | CMOR source of global attribute | Required attribute? | Check that type is | Require check against template or CV | Check also in file name? |
|---|---|---|---|---|---|
| activity_id | CMIP6_experiment_id.json | yes | string | CV (consistent with experiment_id) | no |
| branch_method | user input | conditionally | string | no | no |
| branch_time_in_child | user input | conditionally | double precision | no | no |
| branch_time_in_parent | user input | conditionally | double precision | no | no |
| comment | user input | no | string | no | no |
| contact | user input | no | string | no | no |
| Conventions | Table 1 | yes | string | CV | no |
| creation_date | CMOR-generated | yes | string | must be valid date represented as an ISO 8601 date and time string | no |
| data_specs_version | CMIP6 data request | yes | string | CV | no |
| experiment | CMIP6_experiment_id.json | yes | string | CV (consistent with experiment_id) | no |
| experiment_id | user input (drawn from CMIP6_experiment_id.json) | yes | string | CV | yes |
| external_variables | cell_measure values in CMIP6 data request | conditionally | string | CV (consistent with variable_id and table_id) | no |
| forcing_index | user input | yes | integer >0 | no | no |
| frequency | CMIP6 data request | yes | string | CV (consistent with table_id) | no |
| further_info_url | CMOR-generated, based on other global attributes | yes | string | CV (consistent with several global attributes) | no |
| grid | user input | yes | string | no | no |
| grid_label | user input (drawn from CMIP6_grid_label.json) | yes | string | CV | yes |
| history | user, supplemented by CMOR | no | string | no | no |
| initialization_index | user input | yes | integer >0 | no | no |
| institution | CMIP6_institution_id.json | yes | string | CV (consistent with institution_id) | no |
| institution_id | user input | yes | string | CV (consistent with source_id) | no |
| license | user input | yes | string | defined structure/format and partially-defined text | no |
| mip_era | Table 1 | yes | string | CV (= "CMIP6") | no |
| nominal_resolution | user input (drawn from CMIP6_nominal_resolution.json) | yes | string | CV | no |
| parent_activity_id | CMIP6_experiment_id.json | conditionally | string | CV (consistent with parent_experiment_id) | no |
| parent_mip_era | Table 1 | conditionally | string | CV (= "CMIP6") | no |
| parent_experiment_id | CMIP6_experiment_id.json | conditionally | string | CV (consistent with experiment_id) | no |
| parent_source_id | user input (drawn from CMIP6_source_id.json) | conditionally | string | CV (usually the same as source_id) | no |
| parent_time_units | user input | conditionally | string | check validity against udunits and the CF calendar CV | no |
| parent_variant_label | user input | conditionally | string | defined structure/format | no |
| physics_index | user input | yes | integer >0 | no | no |
| product | Table 1 | yes | string | CV (="model-output") | no |
| realization_index | user input | yes | integer >0 | no | no |
| realm | CMIP6 data request | yes | string | CV (consistent with table_id) | no |
| references | user input | no | string | no | no |
| source | Constructed from components recorded in CMIP6_source_id.json | yes | string | CV (consistent with source_id) | no |
| source_id | user input (drawn from CMIP6_source_id.json) | yes | string | CV | yes |
| source_type | user input (drawn from CMIP6_source_type.json) | yes | string | CV (consistent with experiment_id) | no |
| sub_experiment | CMIP6_sub_experiment_id.json | yes | string | CV (consistent with sub_experiment_id) | no |
| sub_experiment_id | user input (drawn from list in CMIP6_sub_experiment_id.json) | yes | string | CV (consistent with experiment_id) | yes |
| table_id | user input (drawn from CMIP6_table_id.json) | yes | string | CV | yes |
| title | CMOR-generated (based on, source_id, mip_era, and experiment_id) | no | string | no | no |
| tracking_id | CMOR-generated uuid with handle prefix from Table 1 | yes | string | defined structure/format | no |
| variable_id | user input (drawn from CMIP6 data request) | yes | string | CV (consistent with table_id) | yes |
| variant_info | user input | no | string | no | no |
| variant_label | CMOR-generated, based on 4 user-provided indices ("ripf") | yes | string | defined structure/format constructed from indices | yes |

## See Also

- [Appendix 1: Global Attributes for Labeling Experiments](appendix1_global_attributes_labeling_experiments.md)
- [Appendix 2: Algorithms for Defining the "nominal_resolution" Attribute](appendix2_algorithms_nominal_resolution.md)
- [Appendix 3: Document Version Information](appendix3_document_version_information.md)
