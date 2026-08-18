#!/bin/bash -fe
#SBATCH --nodes=1
#SBATCH --job-name=submit_run_workflow
#SBATCH --time=04:00:00
#SBATCH --account=fy250018
#SBATCH --reservation=flight-cldera
#SBATCH --partition=batch
#SBATCH --qos=normal
#SBATCH --mail-user=smturbe@sandia.gov
#SBATCH --mail-type=END,FAIL
#SBATCH --output=logs_batch/zout%j.eo
#SBATCH --error=logs_batch/zerr%j.eo

source "$(conda info --base)/etc/profile.d/conda.sh"
echo "start"
conda run -n e3sm-unified_1.11 --no-capture-output python -u run_workflow.py
echo "done sh"

# Equivalently done on an interactive node:
# salloc -N1 --time=30:00 --account=fy250018 --reservation=flight-cldera --partition=batch,short
# ssh <SLURM_NODE>
# ./run_workflow.py