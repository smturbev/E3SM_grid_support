#!/bin/bash -fex

# activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate smt_nco

INPUTDATA="/projects/ccsm/inputdata"
SCRATCH="/tscratch/smturbe/strat_scratch"
vert_root="${SCRATCH}/vert_grid_files"
nlevs="256"
IC_SRC="${INPUTDATA}/atm/scream/init/screami_ne30np4L72_20220823.nc"
IC_DST="${SCRATCH}/inputdata/scream_init/screami_ne30np4L${nlevs}_20221004_c20260702.nc"
VG_DST="${vert_root}/vertical_coordinates_L${nlevs}_20260702.nc"
## Step 1 - Fix the vertical coordinate file - see the README.md Step 3.
## Step 2 - ncremap
ncremap -7 --vrt_fl=${VG_DST} --ps_nm=ps --in_fl=${IC_SRC} --out_fl=${IC_DST}.tmp
# ncks: WARNING NC_DOUBLE version of "_FillValue" attribute for qv is NaN and this value fails isfinite(). Therefore valid values cannot be arithmetically compared to the _FillValue, and this can lead to unpredictable results.
# HINT: If arithmetic results (e.g., from regridding) fails or values seem weird, retry after first converting _FillValue to a normal number with, e.g., "ncatted -a _FillValue,qv,m,f,1.0e36 in.nc out.nc"
# Fix the above warning
ncatted -O -a _FillValue,,d,,1.0e36 ${IC_DST}.tmp ${IC_DST}.tmp2
ncks -O --fl_fmt=64bit_data ${IC_DST}.tmp2 ${IC_DST}
rm ${IC_DST}.tmp ${IC_DST}.tmp2

echo "done"