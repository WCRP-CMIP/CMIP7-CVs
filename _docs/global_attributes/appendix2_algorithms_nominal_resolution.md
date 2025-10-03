# Appendix 2: Algorithms for Defining the "nominal_resolution" Attribute

There are various ways grid resolution might be defined, but in CMIP6 this should be done in the same way by all models. If the following procedure seems inappropriate for a model, the modeling group may request an exception from the WGCM Infrastructure Panel (WIP). In general, the nominal resolution characterizes the resolution of the grid used to report model output fields, which may differ from the native grid on which the fields are calculated by the model.

## Algorithm for defining the nominal_resolution global attribute:

1. For each grid cell, calculate the distance (in km) between each pair of cell vertices and select the maximum distance ("d<sub>max</sub>"). For lonxlat grid cells, for example, d<sub>max</sub> would be the diagonal distance.

2. Calculate the mean over all cells of d<sub>max</sub>, weighting each by the grid-cell's area (A). This defines the "mean resolution" (d̄<sub>max</sub>). The formula is:

   d̄<sub>max</sub> = (Σd<sub>i</sub><sup>max</sup>A<sub>i</sub>) / (ΣA<sub>i</sub>)

   where the sums are over all grid cells except for the following cases:
   - For a global ocean grid, only sum over the ocean grid cells.
   - For a sea ice model calculated on the ocean grid, include all ocean cells, whether or not they contain sea ice.
   - For land surface models calculated on the atmospheric grid include all grid cells (not just those over land).
   - For a land surface model calculated on its own grid, include all land grid cells.
   - For data reported on a sub-domain of the globe (e.g., northern high latitudes only), include only those grid cells in the domain.
   - For data reported at individual sites, calculate as if every grid cell contained one site (i.e., include all grid cells).
   - For zonal means, global means, sector or basin means, and similar area-means, the data provider may either report the nominal resolution of the native grid or the resolution of the primary grid on which data are reported.

3. Except in the case of a CMIP6 "standard grid" (see item 4 below), define the global attribute "nominal_resolution" according to:

   ```
   if d̄ₘₐₓ < 0.72 km,     nominal_resolution = "0.5 km"
   else if d̄ₘₐₓ < 1.6 km,  nominal_resolution = "1 km"
   else if d̄ₘₐₓ < 3.6 km,  nominal_resolution = "2.5 km"
   else if d̄ₘₐₓ < 7.2 km,  nominal_resolution = "5 km"
   else if d̄ₘₐₓ < 16 km,   nominal_resolution = "10 km"
   else if d̄ₘₐₓ < 36 km,   nominal_resolution = "25 km"
   else if d̄ₘₐₓ < 72 km,   nominal_resolution = "50 km"
   else if d̄ₘₐₓ < 160 km,  nominal_resolution = "100 km"
   else if d̄ₘₐₓ < 360 km,  nominal_resolution = "250 km"
   else if d̄ₘₐₓ < 720 km,  nominal_resolution = "500 km"
   else if d̄ₘₐₓ < 1600 km, nominal_resolution = "1000 km"
   else if d̄ₘₐₓ < 3600 km, nominal_resolution = "2500 km"
   else if d̄ₘₐₓ < 7200 km, nominal_resolution = "5000 km"
   else                    nominal_resolution = "10000 km"
   ```

   The different nominal_resolution values are approximately spaced logarithmically and the bounds on each are logarithmically approximately half-way between the values.

   For a regular latxlon global grid it is possible to calculate the approximate mean resolution analytically:

   d̄<sub>max</sub> = (r<sub>earth</sub>Δφ/2) × [1 + (Δφ²+Δλ²)/(Δφ×Δλ) × tan⁻¹(Δλ/Δφ)]

   where r<sub>earth</sub> is the radius of the Earth (in km), and Δφ and Δλ are the latitude and longitude angular dimensions of each cell (measured in radians). If these dimensions are identical, then the mean resolution is:

   d̄<sub>max</sub> = (r<sub>earth</sub>Δφ/2) × [1 + π/2] ≈ 1.2854 × r<sub>earth</sub>Δφ

   For a 0.5x0.5 degree grid, the mean resolution, according to this formula is 71.5 km (given 6371 km as the Earth's radius).

4. Note that for so-called "standard CMIP6 grids," nominal_resolution will be assigned a string defined by the WGCM Infrastructure Panel (WIP), rather than applying the above algorithm. Currently the only WIP-assigned standard grid is a 1x1 degree longitude by latitude grid with 360 longitudes and 180 latitudes of equal (angular) width, and with one longitude centered at 0.5 degree east longitude (consistent with the World Ocean Atlas). For this CMIP6 standard grid, nominal_resolution = "1x1 degree", rather than "100 km" (which would be the result of the above algorithm). Defining the standard grid resolution in this way makes it easy for users to download only data that have been regridded to the standard grid, since "1x1 degree" will be selectable from the "nominal_resolution" search facet on ESGF.

5. When the above formula for a regular lonxlat global grid is inapplicable, one can rely on a python code to calculate nominal_resolution for any grid. The following links lead to the code and its documentation:
   - Code documentation: https://pcmdi.github.io/nominal_resolution/html/index.html.
   - The code can be obtained via a conda package:
     ```
     conda install -c pcmdi nominal_resolution
     ```
   - The package repository is hosted on Github at: https://github.com/pcmdi/nominal_resolution
     - The library source (api.py) is in the lib directory.
     - The test codes reside in the tests directory.
