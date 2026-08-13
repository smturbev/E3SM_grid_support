# New vertical grids for a stratosphere in SCREAM

This documents the process used to generate the variable resolution vertical grid for adding a stratopshere to SCREAM, varying the layer depth in the stratosphere from about 250 m to 1500 m. The model top is defined at 0.1 hPa or about 60 km. 

## 1. Creating new pressure levels

There are numerous ways you could make new vertical levels in pressure. Due to the way E3SM works, the number of vertical levels should be a multiple of 8 (midlayer levels, as the interface levels will be a multiple of 8 + 1). So, even if you make a vertical coordinate that is not a multiple of 8, E3SM will round up to the nearest multiple of 8 in its calculations and use up that much in memory so it's just better to use a multiple of 8 if you enjoy efficiency. The code for adding a stratosphere ([2026_generate_high-res-strat_pressure-vs-terrain.py](2026_generate_high-res-strat_pressure-vs-terrain.py)) makes a few automatic checks for monotonically increasing grid spacing in dz and will adjust the number of levels to the nearest multiple of 8. 

The method used for adding a stratosphere is breifly explained here (see [2026_generate_high-res-strat_pressure-vs-terrain.py](2026_generate_high-res-strat_pressure-vs-terrain.py) for generating new vertical coordinates, essentially Steps 1-3).

### A. Use dz to make height levels

Let's use L192 as an example. The troposphere remains consistent, defining the depth of each layer in height (meters) ```dz_list```. The other list ```dk_list``` gives the number of times each ```dz``` repeats. For example the first layer of the atmosphere has a depth of 20 m, the second 10m, the third 20 m, the fourth 20 m, the fifth 20 m, and so on. The lists below build the base of the vertical grid from the ground up to about 18.5 km.

```
dk_list = [ 1, 1, 4, 8, 8, 4, 2, 1, 1, 1, 6,   6, 60] 
dz_list = [20,10,20,30,40,50,60,70,80,90,100,200,250]

```

From 18.5 km, we then use a new method to calculate the depth of each layer, since we are generating several vertical grids to use as a sensitivity study to see how many levels are needed to represent gravity waves throughout the stratosphere. 

The method herein uses a ```slope``` variable to determine how to generate the vertical layers. The ```slope``` is the amount that ``dz`` increases per layer to a maximum dz of 1500 m. See ```make_vlevs_from_dz0(m=slope,dz0=18.5,H=model_top_m)```.

The top few layer should have a depth of 1500 m or larger to make the sponge layer better.

Finally, the number of levels (midpoints) should be a multiple of 8. See ```adjust_interfaces_to_blocks_of_8_plus_1(zlev_interfaces)```. A few more checks are done, then the vlevs are converted from height to pressure levels, inverted, converted to hybrid coefficients (see next step), then saved as a netcdf file. 

    \textit{Note:} We use scale height to convert height to pressure, and the vertical grid generated changes slightly based on what scale height you choose. I also tried using ```metpy.height_to_pressure_std()``` and got a slightly different vertical levels.

    $$ p = e^{-1*z/H } * 1000 $$

    where $p$  (```ilev```) is the vertical coordinate in pressure (hPa), $z$ (```zlev```) is the vertical coordinate in height (m), and $H$ is the scale height which is 8.5 km in the standard atmosphere but 
    in climatology from WH, the scale height used is 6.7 km. 

## 2. Calculate the hybrid coefficients

The hybrid coefficients, $A$ and $B$, help the transition between terrain-following and pressure following vertical coordinates. 
$B$ is associated with terrain while $A = ilev$ when purely pressure levels.

$$ p = (A p_0 + B p_s) 100 $$

where $p$ (```ilev```) is the pressure in hPa, $p_0$ is the reference pressure ($p_0=1000$ hPa), and $p_s$ is the surface pressure (in this code we assume $p_s = 1000$ hPa). 

To get from pressure to hybrid coordinates, it takes some work and a few assumptions. This calculation is done in the function ```compute_hybrid_coef_from_pressure(ilev, pm, pt, alpha)```, which we lay out here. First, we define the level to switch from sigma to pressure $p_m = 300$ hPa (the 300 at the end of the file name). Then we define the model top $p_t = 0.1$ hPa. There is also an $\alpha$ parameter, which I think dictates the speed of the change from sigma to pressure coordinates.

### Sigma levels ($p \geq pm$; low altitude)

$$ \sigma = \frac{p - p_m}{ps - p_m}; \delta = sgn(\sigma) $$
where $\sigma$ is always negative for low altitudes, so $\delta$ is always $-1$. 
$$B = \delta (\sigma^\alpha); A = \frac{(p - Bp_s)}{p_0} $$


### Pure pressure levels ($p < pm$; high altitude)

$$ \sigma = \frac{p - pm}{pm - pt}; \delta = sgn(\sigma) $$
where $\sigma$ is always positive for high altitudes, so $\delta$ is always $+1$. 

$$A = \frac{ \delta p_m (1-\sigma) - \delta(p_m(1+\sigma)-p_t \sigma) }{p_0}; B = \sqrt{ (\sigma \delta)^2 } $$

## 3. Save vertical coordinate to a new file

Save your dataset with variables (midpoint level, interface level, hybrid coeffcients A and B at layer midpoints and interfaces, reference pressure) and move this netcdf file to wherever you have E3SM's inputdata (```<inputdata_dir>/atm/scream/init/vertical_coordinates_Lnew.nc```). 

Something weird about the formatting means that you should follow the guidance from HICCUP on vertical grid files [here](https://github.com/E3SM-Project/HICCUP/blob/main/README.md#vertical-grid-files). Basically,

```
ncdump -v P0,hyam,hybm,hyai,hybi,lev,ilev <history_file> > vert_coord.txt
# manually delete the global file attributes
ncgen vert_coord.txt -o vert_coord.nc
```

## 4. Create initial conditions with the new vertical coordinate

The initial condition file needs the following variables: physical fields of PS, PHSI, T, Q, U, V, and vertical coordinate related variables, namely, P0,  hyam, hybm, hyai, hybi for hybrid simga-pressure coordinate and lev and ilev for constant pressure levels.

Remapping the initial condition file from L72 (which has a model top at 0.1 hPa) to your new vertical levels (just run ```./2026_generate_IC_newlevs.sh```). \textit{Note: using intial condition files from L128 will not work due to the different model top height.}

The important line uses ncremap
```bash
VG_DST=<path_to_vertical_grid/vertical_coordinate_Lnew.nc>
IC_SRC=<inputdata_path_to_L72_ic_file>
IC_DST=<scratch_output_path_for_new_ic_file>

ncremap --vrt_fl=${VG_DST} --ps_nm=ps --in_fl=${IC_SRC} --out_fl=${IC_DST}
```
The output file should be netcdf4/hdf5, which should then be moved to the inputdata directory (```<inputdata_dir>/atm/scream/init/```) or wherever you want to store the vertical grids.

If you get a bunch of warnings, see troubleshooting IC files [below](##-ic-file-generation-is-throwing-a-lot-of-warnings)

## 5. Update ```cime_config``` paths for EAMxx

\textit{Hacky way:} Update the namelist option for the vertical grid file in your run script

```
./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV ${nlevs} SCREAM_NUM_TRACERS 10"
./atmchange initial_conditions::filename=${scream_init_file}
./atmchange vertical_coordinate_filename=${scream_vertical_grid_file}
```

\textit{Better way:} We need to update the cime_config file with the list of files to use for each compset in EAMxx. For this example, we generate a new vertical grid and ic file with 192 vertical levels. We need to update two places in the namelist defaults for EAMxx (vertical coordinate filename and initial condition filename). See example below.

```<E3SM_code_dir>/components/eamxx/cime_config/namelist_defaults.xml```
```bash
<!-- Grids manager specs -->
  <grids_manager>
    <type>homme</type>
    ...
    <vertical_coordinate_filename nlev="192">${DIN_LOC_ROOT}/atm/scream/init/vertical_coordinates_L192_20260702.nc</vertical_coordinate_filename>
  </grids_manager>

<!-- List of nc files for loading inputs on specified grids -->
  <initial_conditions>
   ...
   <filename hgrid="ne30np4" nlev="192">${DIN_LOC_ROOT}/atm/scream/init/screami_ne30np4L192_20260702.nc</filename>
   ...
```

## 6. Run DP-EAMxx

Example run script is in [runscripts/run_dpxx_scream_rce.flight.csh](../../runscripts/run_dpxx_scream_rce.flight.csh). The name change to make is in SCREAM_NUM_VERTICAL_LEV. It is also important to add the namelist option for setting the sponge layer start pressure (in hPa); the default is tom_sponge_start=0 which is not configured for a model top above the stratopause, so you should set this manually. 
TODO: sensitivity study to determine the best height/depth of the sponge layer. 

```csh
./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 192 SCREAM_NUM_TRACERS 10" 
./atmchange ctl_nl::tom_sponge_start=2.0 -b
```


### Notes on run
Domain: 500 km $\times$ 500 km
Horizontal resolution: 3.3 km
Model physics time step: 100 s
Model dynamics time step: 8.3333333333333 s (should be $\frac{1}{12}$ of physics time step)
Second order viscosity near model top (nu_top): 1e4 m2/s



# Troubleshooting

First try updating your local E3SM repo and submodules

```git submodule update --init --recursive```

And make sure your fork/branch is up to date with E3SM-Project/E3SM and especially the submodules - sometimes it is good to just clone a fresh repo if you are running into problems.


## IC file generation is throwing a lot of warnings

The Warning I get during generation of the IC files is:
```
$ ncremap --vrt_fl=${vert_coord} --ps_nm=ps --in_fl=${IC_L72}.tmp --out_fl=${IC_NEW}


ncks: WARNING NC_DOUBLE version of "_FillValue" attribute for o3_volume_mix_ratio is NaN and this value fails isfinite(). Therefore valid values cannot be arithmetically compared to the _FillValue, and this can lead to unpredictable results.
HINT: If arithmetic results (e.g., from regridding) fails or values seem weird, retry after first converting _FillValue to a normal number with, e.g., "ncatted -a _FillValue,o3_volume_mix_ratio,m,f,1.0e36 in.nc out.nc"

```
Then the model throws the following error when its trying to run (builds okay bit fails when it tries to read in the IC file). See e3sm.log file output below:
```e3sm.log
PIO: WARNING: Opening file (/tscratch/smturbe/strat_scratch/vert_grid_files/SCREAM_L133_c20250512_alpha_1.0_pm_300.nc) with iotype=1 (PIO_IOTYPE_PNETCDF) failed (ierr=-128, NetCDF: Attempt to use feature that was not turned on when netCDF was built.). Retrying with iotype=PIO_IOTYPE_NETCDF
PIO: WARNING: Opening file (/tscratch/smturbe/strat_scratch/vert_grid_files/SCREAM_L133_c20250512_alpha_1.0_pm_300.nc) with iotype=1 (PIO_IOTYPE_PNETCDF) failed. But retrying with iotype PIO_IOTYPE_NETCDF was successful. Switching iotype to PIO_IOTYPE_NETCDF for this file
PIO: WARNING: Opening file (/projects/ccsm/inputdata/atm/cam/scam/iop/RCE_300K_iopfile_4scam.nc) with iotype=1 (PIO_IOTYPE_PNETCDF) failed (ierr=-128, NetCDF: Attempt to use feature that was not turned on when netCDF was built.). Retrying with iotype=PIO_IOTYPE_NETCDF
PIO: WARNING: Opening file (/projects/ccsm/inputdata/atm/cam/scam/iop/RCE_300K_iopfile_4scam.nc) with iotype=1 (PIO_IOTYPE_PNETCDF) failed. But retrying with iotype PIO_IOTYPE_NETCDF was successful. Switching iotype to PIO_IOTYPE_NETCDF for this file
Note: nsplit=-1, while nsplit must be >=1. We know SCREAM does not know nsplit until runtime, so this is fine.
      Make sure nsplit is set to a valid value before calling prim_advance_subcycle!
Error! Source field allocation is not compatible with the requested value type.

FAILED CONDITION: 'alloc_prop.template is_compatible<DstValueType>()'

BACKTRACE:
/home/smturbe/codes/e3sm/E3SM_master/components/eamxx/src/share/field/field_get_view_impl.hpp:40

Error! Source field allocation is not compatible with the requested value type.
```


-------
# Resources and Acknowledgements

- E3SM atlassian page on generating new initial conditions [here](https://e3sm.atlassian.net/wiki/spaces/DOC/pages/1002373272/Generate+atm+initial+condition+from+analysis+data)
- Much thanks to @whannah1 for the advice and [this parent repo](https://github.com/whannah1/E3SM_grid_support). 


