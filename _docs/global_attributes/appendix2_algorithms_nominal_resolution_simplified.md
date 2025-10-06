# Appendix 2: Algorithms for Defining the "nominal_resolution" Attribute

There are various ways grid resolution might be defined, but in CMIP6 this should be done in the same way by all models. If the following procedure seems inappropriate for a model, the modeling group may request an exception from the WGCM Infrastructure Panel (WIP).

## Algorithm for defining the nominal_resolution global attribute:

### Step 1: Calculate Maximum Distance
For each grid cell, calculate the distance (in km) between each pair of cell vertices and select the maximum distance ($d_{max}$). For lonxlat grid cells, for example, $d_{max}$ would be the diagonal distance.

### Step 2: Calculate Mean Resolution
Calculate the mean over all cells of $d_{max}$, weighting each by the grid-cell's area ($A$). This defines the "mean resolution" ($\bar{d}_{max}$):

$$\bar{d}_{max} = \frac{\sum d_i^{max} A_i}{\sum A_i}$$

where the sums are over all grid cells except for:
- **Global ocean grid**: only sum over ocean grid cells
- **Sea ice model**: include all ocean cells (with or without sea ice)
- **Land surface models**: 
  - On atmospheric grid: include all grid cells
  - On own grid: include all land grid cells
- **Sub-domain data**: include only grid cells in the domain
- **Site data**: calculate as if every grid cell contained one site
- **Zonal/global means**: report either native or primary grid resolution

### Step 3: Assign Nominal Resolution
Define the global attribute "nominal_resolution" according to:

| If $\bar{d}_{max}$ is: | Then nominal_resolution = |
|-------------------------|---------------------------|
| < 0.72 km | "0.5 km" |
| < 1.6 km | "1 km" |
| < 3.6 km | "2.5 km" |
| < 7.2 km | "5 km" |
| < 16 km | "10 km" |
| < 36 km | "25 km" |
| < 72 km | "50 km" |
| < 160 km | "100 km" |
| < 360 km | "250 km" |
| < 720 km | "500 km" |
| < 1600 km | "1000 km" |
| < 3600 km | "2500 km" |
| < 7200 km | "5000 km" |
| ≥ 7200 km | "10000 km" |

### Analytical Formula for Regular Lat-Lon Grids

For a regular lat×lon global grid, the approximate mean resolution can be calculated analytically:

$$\bar{d}_{max} = \frac{r_{earth}\Delta\phi}{2} \left[1 + \frac{\Delta\phi^2 + \Delta\lambda^2}{\Delta\phi \Delta\lambda} \tan^{-1}\left(\frac{\Delta\lambda}{\Delta\phi}\right)\right]$$

where:
- $r_{earth}$ = Earth's radius (in km)
- $\Delta\phi$ = latitude angular dimension (radians)
- $\Delta\lambda$ = longitude angular dimension (radians)

For square cells ($\Delta\phi = \Delta\lambda$):

$$\bar{d}_{max} = \frac{r_{earth}\Delta\phi}{2} \left[1 + \frac{\pi}{2}\right] \approx 1.2854 \cdot r_{earth} \cdot \Delta\phi$$

**Example**: For a 0.5×0.5 degree grid, the mean resolution is 71.5 km (using $r_{earth}$ = 6371 km).

### Step 4: Standard CMIP6 Grids
For "standard CMIP6 grids," nominal_resolution is assigned by the WIP rather than calculated. Currently, only one standard grid exists:
- **1×1 degree grid**: 360 longitudes × 180 latitudes
- **nominal_resolution** = "1x1 degree" (not "100 km")

### Step 5: Python Code for Complex Grids
When the analytical formula doesn't apply, use the Python code:

```bash
conda install -c pcmdi nominal_resolution
```

Resources:
- [Documentation](https://pcmdi.github.io/nominal_resolution/html/index.html)
- [GitHub Repository](https://github.com/pcmdi/nominal_resolution)
