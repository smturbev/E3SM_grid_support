# TO DO 
- [x] check_config.py
- [x] Build MOAB/MBDA on flight (Thanks, @BenHillman. Path = ```/projects/ccsm/mbda/mbda```)
- [x] check_paths.py (needs moab)
- [x] Fix grid paths/names to work in this workflow
- [x] Edit `run_workflow.py` to specify which grids and steps will be handled
- [x] Generate grid file from scratch (within this workflow)
- [x] Generate map files from scratch (within this workflow)
- [x] Generate domain files from scratch (within this workflow)
- [x] Generate topo files (within this workflow) for CA32x8
- [ ] Run `run_workflow.py` for a new grid in one streamlined step



# Quick Start Guide

1. Install the environment into conda (from this repo root directory: ```E3SM_grid_support/```). Note that tempestremap and SQuadGen were install via as submodules in this repo, [smturbev/e3sm_grids_rrm](https://github.com/smturbev/e3sm_grids_rrm).

   ```
   conda activate e3sm_unified_1.11
   pip install -e .
   python -m pip install -e .
   ```
   
2. Generate Grid Files (See [Grid Generation Guidance](#grid-generation-guidance))

3. Other pre-requisites.
      
   - [moab/MBDA](https://github.com/vijaysm/topography-tool) needs to be installed... 
   - homme_tool is optional - python-based alternatives can be used instead - will try with python as a first go

4. Update project/CA-RRM-OGW directory:
   - project.yaml

5. Check the configuration by running ```check_paths.py``` and ```check_config.py```




--------------------------------------------------------------------------------

# Grid Generation Guidance

See [generate_grid_files.sh](generate_grid_files.sh).


# Grid saving conventions for this workflow to work

Output of check_grids.py (one grid only for example)

```
./check_grids.py 
  --------------------------------------------------------------------------------
  GRID: CA32x8

  Grid files
    exodus (input)          [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/CA32x8.g
    np4 scrip               [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/CA32x8np4_scrip.nc
    np4 mbda                [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/CA32x8np4_mbda.nc
    pg2 scrip               [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/CA32x8pg2_scrip.nc
    pg2 mbda                [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/CA32x8pg2_mbda.nc
    3km exodus              [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/ne3000.g
    3km scrip               [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/ne3000pg1_scrip.nc
    3km mbda                [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_grid/ne3000pg1_mbda.nc

  Topo files
    3km remapped            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_USGS-topo_ne3000.nc
    np4 remapped            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_USGS-topo_CA32x8-np4.nc
    pg2 remapped            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_USGS-topo_CA32x8-pg2.nc
    np4 smoothed            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_USGS-topo_CA32x8-np4_smoothedx6t.nc
    3km→np4 (SGH)           [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_3km-topo_CA32x8-np4.nc
    3km smoothed            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_3km-topo_CA32x8-np4_smoothedx6t.nc
    3km→pg2 (SGH)           [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/tmp_3km-topo_CA32x8-pg2.nc
    FINAL                   [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_topo/USGS-topo_CA32x8-np4_smoothedx6t_20260622.nc

  Ocean map files  (ICOS10 ↔ CA32x8pg2)
    ocn→atm  traave             [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_traave.20260622.nc
    atm→ocn  traave             [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_traave.20260622.nc
    ocn→atm  trbilin            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trbilin.20260622.nc
    atm→ocn  trbilin            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trbilin.20260622.nc
    ocn→atm  trfv2              [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trfv2.20260622.nc
    atm→ocn  trfv2              [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trfv2.20260622.nc
    ocn→atm  trintbilin         [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trintbilin.20260622.nc
    atm→ocn  trintbilin         [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trintbilin.20260622.nc

  Land map files   (ICOS10 ↔ CA32x8pg2)
    lnd→atm  traave             [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_traave.20260622.nc
    atm→lnd  traave             [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_traave.20260622.nc
    lnd→atm  trbilin            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trbilin.20260622.nc
    atm→lnd  trbilin            [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trbilin.20260622.nc
    lnd→atm  trfv2              [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trfv2.20260622.nc
    atm→lnd  trfv2              [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trfv2.20260622.nc
    lnd→atm  trintbilin         [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_ICOS10_to_CA32x8pg2_trintbilin.20260622.nc
    atm→lnd  trintbilin         [missing]  /tscratch/smturbe/E3SM_grid_support/CA-RRM-OGW/files_map/map_CA32x8pg2_to_ICOS10_trintbilin.20260622.nc
    ```


--------------------------------------------------------------------------------

# E3SM Source Code Changes Needed to Define Grid

???

--------------------------------------------------------------------------------