# Appendix 3: Document Version Information

The document version number consists of 3 integers separated by "." The first integer is "6", indicating the document applies to CMIP6. The second integer will be incremented if changes are made that likely will require modifications in existing software or output files (e.g., an addition of a new global attribute). The third digit will be incremented whenever a new release involves only minor changes (e.g., to a list of values appearing in a CV).

## Version History

### 6.0.0 (14th September 2016) - Initial release

### 6.0.1 (5 October 2016):
- Replaced source_type option "BCM" with "BGCM" (biogeochemical model).
- Eliminated source_type options: "RCM (regional climate model)", "ESD (empirical statistical downscaling model)", and "EMIC (earth-system model of intermediate complexity)". This was done
- Modified algorithm for determining grid_resolution so that the label value will now nearly always be logarithmically the closest one to d-max. This is consistent with the labels being logarithmically approximately evenly spaced.
- Corrected typos in note 13 after Table 1: "sea ice" is now "sea_ice" (for consistency with other labels in that note).
- Added text at the beginning of this Appendix about incrementing the version number.

### 6.1.0 (15 November 2016):
- Changed "grid_resolution" to "nominal_resolution", which is less definitive and more appropriate.
- Noted that the length of source_id is limited to no more than 16 characters.
- Description of grid_label now includes specifications for global mean data and data stored on regional grids centered over Greenland or Antarctica.
- Corrected model_id to read source_id and model_type to read source_type in a couple of places.
- After discussions with Pierre Friedlingstein, renamed "BGCM" to read "BGC" and eliminated distinction between ESM and "AOGCM BGC".
- Expanded description of source_type attribute to help clarify.

### 6.2.0 (2 December 2016; shortened URL is goo.gl/v1drZl):
- Reversed the order of the <source_id>_<experiment_id> segment of the filename (with "source" now first) to be consistent with subsequent examples of filename in this document and more like the ordering of the CMIP5 filename and the directory structure.
- Eliminated one of the optional sentences in the "license" attribute because it seemed unnecessary, given the more general statement made in the sentence that followed.

### 6.2.1 (21 December 2016):
- Corrected the URL in the license statement to now point to https://pcmdi.llnl.gov/home/CMIP6/CitationRequirements6-0.html where the acknowledgement guidelines will be located.

### 6.2.2 (23 March 2017):
- Corrected the Creative Commons link in the license statement to now point to https://creativecommons.org/licenses/. Also changed "should be" to "must be", and modified spaces, hyphens, and quotes in the "Attribution-ShareAlike" part of the statement. Also corrected link to terms of use document.
- Change "UGRID-0.9", which can appear in the conventions attribute to "UGRID-1.0".
- Clarified that one statement in footnote 5 referred to the decadal prediction runs only.
- Changed CMIP6 specification of "product" global attribute from "output" to "model-output". This better describes it and clearly differentiates it from "observations", which is the text assigned to this attribute in input4MIPs and obs4MIPs.
- Corrected a few entries in the CMOR Source column of Table 2 (which has now been renumbered Table 3.
- Added links in several places to the reference CV's found at https://github.com/WCRP-CMIP/CMIP6_CVs.
- Clarified that the data_specs_version attribute records the version of the data request relied on in preparing model output.
- Added specific details on defining the time labels that appear in file names, which required addition of a new table and required Table 2 to be renumbered Table 3.
- Adjusted (by less than 3%) the values used to determine nominal resolution in Appendix 2, so that models with latxlon resolution of 0.25, 0.5, 2.5 and 5.0 are now classified with nominal resolution of "25 km", "50 km", "250 km" and "500" km, respectively (instead of 50, 100, 500, and 1000 km).

### 6.2.3 (4 April 2017):
- Deleted a double entry in table 2 and added a missing entry.
- Added links to the reference controlled vocabularies in the section defining the DRS.

### 6.2.4 (14 July 2017):
- Revised note 8 for improved clarity.
- In note 13, corrected the terms used to describe each realm to be consistent with the CMIP6 CV.
- Augmented Table 2 with notes on how time-labels for file names should be constructed. Also, changed frequency "decadal" to "dec" and eliminated 3hrClim since it isn't needed for CMIP6.
- Corrected the examples of file name to make the order of the elements consistent with the template.
- Reworded a few sentences to improve clarity
- Corrected some instances of "product" to indicate for CMIP6 this should have the value "model-output".
- Corrected CMIP6 version in Conventions attribute to be "CMIP-6.2".

### 6.2.5 (14 September 2017):
- Corrected/added options for frequency appearing in Table 2.
- Expanded notes describing the directory template.
- Corrected a few typos and URL addresses.

### 6.2.6 (20 December 2017):
- Expanded description of realization_index, initialization_index, physics_index, and forcing_index in note 8 following Table 1.
- Removed "none provided" as an example of a branch_method in Table 1.
- Corrected the example of further_info_url given in note 9 following Table 1.
- Revised the description of source_type="BGC" in note 14 following Table 1.
- Expanded explanation about how the tracking_id should be generated (in note 15 following Table 1).
- Added missing items to the DRS: member_id, nominal_resolution, and source_type.
- Changed the name of institution and source appearing in the examples of file names and directory structures so that they are now consistent with names currently registered for CMIP6.
- Corrected a few typos.
- Indicated in Table 1 which global attributes are part of the DRS and which will likely be used as search facets in CoG.

### 6.2.7 (10 September 2018):
- Added to Appendix 2 an item (5) pointing to a python code that can be used to calculate nominal resolution.
- Made corrections so that when a rectangular longitude-latitude grid is described, the longitude dimension always appears first.

### 6.2.8 (9 June 2025):
- Updated some links.
- Corrected some typos.
