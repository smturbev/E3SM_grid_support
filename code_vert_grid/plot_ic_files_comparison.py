#!/ascldap/users/smturbe/.conda/envs/smt_met/bin/python

import os 
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

COLORS=['C0','C1','C2','C3']
VARS=['T_mid','horiz_winds','nc','ni','qc','qi','o3_volume_mix_ratio']

def main(icfile_dict):
    if icfile_dict=='example':
        inputdata = '/projects/ccsm/inputdata/atm/scream/init'
        icfile_dict = {'ne30np4L72':f'{inputdata}/screami_ne30np4L72_20220823.nc'}
    
    labels = icfile_dict.keys()
    print('Labels:\n', labels)
    fig= plt.figure(figsize=(30,16))
        
    # loop thru variables in file
    for j,var in enumerate(VARS):
        # print(ic[var].isel(time=0).mean(dim=['ncol']))
        print('\t', var)
        ax = fig.add_subplot(2, len(VARS)//2+1, j+1)
        # loop thru ic files
        for i,lbl in enumerate(labels):
            print(i, icfile_dict[lbl])
            ic = xr.open_dataset(icfile_dict[lbl], engine='netcdf4')
            ic[var].isel(time=0).mean(dim=['ncol']).plot(y='lev', ax=ax, color=COLORS[i], label=lbl)
        ax.set(ylim=(1000,0.1), yscale='log')
    ax.legend()
    plt.savefig('figs_vert_grid/ic_vars_comparison.png', bbox_inches='tight', pad_inches=0.1)
    plt.close()

main(
    {'ne30np4L128':'/projects/ccsm/inputdata/atm/scream/init/screami_ne30np4L128_20221004.nc',
     'ne30np4L72':'/projects/ccsm/inputdata/atm/scream/init/screami_ne30np4L72_20220823.nc',
     'ne30np4L177':'/tscratch/smturbe/strat_scratch/inputdata/scream_init/screami_ne30np4L177_20221004_c20260512.nc',
     'ne30np4L133':'/tscratch/smturbe/strat_scratch/inputdata/scream_init/screami_ne30np4L133_20221004_c20260603_new.nc',
     }
)