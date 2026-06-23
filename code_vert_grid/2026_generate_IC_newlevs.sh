#!/bin/bash -fex

# activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate smt_nco

INPUTDATA="/projects/ccsm/inputdata"
SCRATCH="/tscratch/smturbe/strat_scratch"
vert_root="${SCRATCH}/vert_grid_files"
nlevs="192"
IC_SRC="${INPUTDATA}/atm/scream/init/screami_ne30np4L72_20220823.nc"
IC_DST="${SCRATCH}/inputdata/scream_init/screami_ne30np4L${nlevs}_20221004_c20260603_new.nc"
VG_DST="${vert_root}/vertical_coordinates_L${nlevs}_20260608.nc"
## Step 1 - Fix the vertical coordinate file - see the README.md Step 3.
## Step 2 - ncremap
ncremap -7 --vrt_fl=${VG_DST} --ps_nm=ps --in_fl=${IC_SRC} --out_fl=${IC_DST}.tmp
ncatted -O -a _FillValue,,d,,1.0e36 ${IC_DST}.tmp ${IC_DST}.tmp2
ncks -O --fl_fmt=64bit_data ${IC_DST}.tmp2 ${IC_DST}
rm ${IC_DST}.tmp ${IC_DST}.tmp2

echo "done"