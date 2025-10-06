# Appendix 1: Global Attributes for Labeling Experiments

Global attributes that label experiments are needed to construct filenames and directories and can generally be used as search facets. Together, they should have the following characteristics:

- Uniquely label each experiment within CMIP6 and distinguish experiments with specified conditions that differ in any way
- Easily be interpreted and remembered
- Facilitate representations of groups of experiments that are closely related (e.g., same forecast conditions but different start dates, or experiment with an "offline" model driven by output from various models)

Often several simulations will be performed that satisfy the conditions specified for an experiment. For example, simulations of the historical period can branch from various points in a control run, and each of these will satisfy the conditions defining the experiment. Together, such simulations constitute a "conforming ensemble" with members all satisfying the same experiment specifications. There are also occasional cases where the experiment designers (MIP leaders) define a family of related simulations and choose to label these with a common "root" experiment name, followed by a "sub-experiment" name. An example of this is the set of decadal prediction hindcasts that are all run similarly but started from different start dates (with each simulation identified by a different sub-experiment label). Such "defined ensembles" of experiments will be labeled with a "root" experiment name, and a "sub-experiment_id" will be used to distinguish among members in the ensemble.

To accommodate the various CMIP6 experiments, we define three global attributes:

- **experiment_id**: the label identifying the "root" experiment
- **sub_experiment_id**: the label identifying a sub-experiment of a "defined ensemble"; otherwise set to "none"
- **variant_label**: a label constructed from 4 indices stored as global attributes:
  ```
  variant_label = r<k>i<l>p<m>f<n>
  ```
  where:
  - k = realization_index
  - l = initialization_index
  - m = physics_index
  - n = forcing_index

Besides the above identifiers, additional descriptive information concerning the experiment is provided by the following global attributes:

- **experiment**: brief descriptor of experiment (using CV)
- **sub_experiment**: brief descriptor of sub-experiment (using CV); if sub_experiment_id = "none", then sub_experiment = "none".
- **variant_info**: brief descriptor of what is unique about this "ripf" variant.

## Structure of Experiments in CMIP6

For the group of experiments included in CMIP6, the following structure will usually be followed:

- Each experiment_id will comprise one or more segments separated by hyphens.
- The first segment indicates that an experiment should be run with a model other than an AOGCM or a concentration-driven ESM. (This segment is omitted in experiments for AOGCMs and concentration-driven ESMs.) CMIP6 examples of the first segment (shown in parentheses) include:
  - Offline radiation code experiments ("rad")
  - Uncoupled ice-sheet models forced by AOGCM output ("ism")
  - Atmosphere (and land surface) models forced by prescribed SSTs and sea ice (e.g., "amip", "piSST", "piClim", "histSST", "ssp370SST", "aqua", "futureSST", "G6SST1", "G6SST2", "G7SST1", "G7SST2", "highresSST", "a4SST", "a4SSTice")
  - Offline land-surface model ("land")
  - Ocean and sea ice model forced by prescribed atmospheric conditions ("omip1" or "omip2")
  - Earth system model forced by emissions (rather than concentrations) of CO2 ("esm")
- The next segment is the first indication of experiment conditions
- Any additional segments indicate some relatively small variation on experiment conditions defined by the previous segment.

## Examples

We now provide two examples of the global attributes relevant to identifying a CMIP6 experiment, and the filenames and directory structures that make use of these global attributes.

### Example 1: The common case when there are no sub-experiments:

**Global attributes (relevant to experiment definition):**
```
experiment_id = "1pctCO2"
experiment = "1 percent per year increase in CO2 concentration"
sub_experiment_id = "none"
sub_experiment = "none"
realization_index = 1
initialization_index = 1
physics_index = 1
forcing_index = 1
variant_label = "r1i1p1f1"
variant_info = "realization 1"
```

**file name**: `tas_Amon_CCSM2-1_1pctCO2_r1i1p1f1_gn_202001-202912.nc`

**directory structure**: `CMIP6/CMIP/NCAR/CCSM2-1/1pctCO2/r1i1p1f1/Amon/tas/gn/v20150320/`

### Example 2: The uncommon case (in CMIP6) when there are sub-experiments defined:

**Global attributes (relevant to experiment definition):**
```
experiment_id = "dcppA-hindcast"
experiment = "year 1-5 hindcast initialized based on observations and using historical forcing"
sub_experiment_id = "s1960"
sub_experiment = "initialized near end of year 1960"
realization_index = 1
initialization_index = 2
physics_index = 1
forcing_index = 1
variant_label = "r1i2p1f1"
variant_info = "initialized using anomaly approach (method 2)"
```

**file name**: `tas_Amon_CCSM2-1_hindcast_s1960-r1i2p1f1_gn_198001-198412.nc`

**directory structure**: `CMIP6/DCPP/NCAR/CCSM2-1/dcppA-hindcast/s1960-r1i2p1f1/Amon/tas/gr/v20150320/`
