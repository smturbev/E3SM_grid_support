#!/bin/bash -e
#SBATCH --nodes=1
#SBATCH --job-name=grid_gen_ne30
#SBATCH --time=01:40:00
#SBATCH --account=fy250018
#SBATCH --license=gpfs,pscratch,tscratch
#SBATCH --reservation=flight-cldera
#SBATCH --partition=short,batch
#SBATCH --qos=normal
#SBATCH --mail-user=smturbe@sandia.gov
#SBATCH --mail-type=ALL
#SBATCH --output=z_grid_gen.o
#SBATCH --error=z_grid_gen.e

set -ev # verbose messages and crash message

uniform_grid=.true.
rrm_grid=.false.

if [ $uniform_grid ] ; then
    res=30  # base/global resolution 
    grid_name=ne${res}
    echo "---- UNIFORM GRID -----"
    echo "     ne = $res         " 
    echo "   grid = $grid_name   "
elif [ $rrm_grid ] ; then
    # Example for RRM grid using ne30 for global res
    # refined x8 in the high-res up to ne256 (13 km)
    refine_level=8
    res=32
    grid_name="CAx${refine_level}"
    echo "------ RRM GRID -------"
    echo "   grid = $grid_name   "
    echo "    res = ${res} "
    echo " refine = x${refine_level} " 
else
    echo "ERROR: Undefined grid type. Set uniform_grid or rrm_grid to True"
    exit 1
fi

output_root=/tscratch/smturbe/e3sm_grids/${grid_name}
mkdir -p ${output_root}

# activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate e3sm-unified_1.11

if [ uniform_grid ] ; then
    # generates a uniform global grid for resolution, res
    GenerateCSMesh --res ${res} --file ${output_root}/${grid_name}.g
elif [ rrm_grid ] ; then
    # generates an RRM grid using global resolution res
    # with refinement up to refine_level (hi-res = res x 2**refine_level)
    # using an image to define refinement region
    SQuadGen --resolution $res --refine_file ./CA_v1_input.png --output ${output_root}/${grid_name}.g --smooth_type SPRING --invert --refine_level ${refine_level} --lat_ref 38 --lon_ref -116 --orient_ref 20 --block_refine
fi

# format the grid from exodus to netcdf using np 2 
GenerateVolumetricMesh --in ${output_root}/${grid_name}.g     --out ${output_root}/${grid_name}pg2.g --np 2 --uniform
ConvertMeshToSCRIP     --in ${output_root}/${grid_name}pg2.g --out ${output_root}/${grid_name}pg2_scrip.nc

# check that everything is there
ls -l ${output_root}/${grid_name}*

echo "---- done ----"
