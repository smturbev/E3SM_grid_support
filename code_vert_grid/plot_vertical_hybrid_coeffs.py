#!/ascldap/users/smturbe/.conda/envs/smt_met/bin/python

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


#-------------------------------------------------------------------------------
# Grid registration
#-------------------------------------------------------------------------------
FILE_LIST = []

def add_grid(file_path, **kwargs):
    case_opts = {'file': file_path}
    for k, val in kwargs.items():
        case_opts[k] = val
    FILE_LIST.append(case_opts)
#-------------------------------------------------------------------------------

grid_root = '/projects/ccsm/inputdata/atm/scream/init'
add_grid(f'{grid_root}/vertical_coordinates_L128_20220927.nc', n='L128', c='blue')
add_grid(f'{grid_root}/vertical_coordinates_L72_20220927.nc', n='L72',  c='black')

grid_root = '/projects/scream_strat/smturbe/vert_grid'
add_grid(f'{grid_root}/vertical_coordinates_L256_20260702.nc', n='L256', c='red')
# add_grid(f'{grid_root}/vertical_coordinates_L192_20260608.nc', n='L192', c='orange')
# add_grid(f'{grid_root}/vertical_coordinates_L176_20260702.nc', n='L176', c='yellowgreen')
# add_grid(f'{grid_root}/vertical_coordinates_L160_20260702.nc',n='L160', c='green')
# add_grid(f'{grid_root}/vertical_coordinates_L152_20260702.nc', n='L152', c='C0')
# add_grid(f'{grid_root}/vertical_coordinates_L144_20260702.nc', n='L144', c='darkblue')


#-------------------------------------------------------------------------------
# Settings
#-------------------------------------------------------------------------------
fig_file    = os.path.join('figs_vert_grid/vertical_hybrid_coeffs.png')
print_table = False
print(fig_file)

#-------------------------------------------------------------------------------
# Assign unique colors to any grid that didn't specify one
#-------------------------------------------------------------------------------
# def _gen_unique_colors(n_colors):
#     """Return n visually distinct colors using HSV spacing."""
#     return [mcolors.hsv_to_rgb((i / n_colors, 0.85, 0.80)) for i in range(n_colors)]

# _uncolored = [i for i, o in enumerate(opt_list) if 'c' not in o]
# _palette   = _gen_unique_colors(len(_uncolored))
# for idx, palette_color in zip(_uncolored, _palette):
#     opt_list[idx]['c'] = palette_color

#-------------------------------------------------------------------------------
# Print table
#-------------------------------------------------------------------------------
if print_table:
    ilev_list_tbl = []
    zlev_list_tbl = []
    hyai_list = []
    hybi_list = []
    for opts in FILE_LIST:
        ds   = xr.open_dataset(opts['file'])
        hyai = ds['hyai']
        hybi = ds['hybi']
        ilev = ds['hyai'].values * 1000 + ds['hybi'].values * 1000
        zlev = np.log(ilev / 1e3) * -6740.
        # dz = np.diff(z)
        ilev_list_tbl.append(ilev)
        zlev_list_tbl.append(zlev)
        hyai_list.append(hyai)
        hybi_list.append(hybi)

    max_len = max(len(m) for m in ilev_list_tbl)
    for k in range(max_len):
        k2  = max_len - k - 1
        msg = f'{k:3}  ({k2:3}) '
        zip_list = zip(ilev_list_tbl, zlev_list_tbl, hyai_list, hybi_list)
        for g, (ilev, zlev, hyai, hybi) in enumerate(zip_list):
            if k < len(ilev):
                msg += ' '*6
                msg += f'  {ilev[k]:8.2f} mb   {zlev[k]:8.1f} m'
                msg += f'  a/b: {hyai[k]:6.4f} / {hybi[k]:6.4f}'
                msg += f'  a+b: {(hyai[k]+hybi[k]):6.4f}'
        print(msg)
# exit()

#-------------------------------------------------------------------------------
# Create figure
#-------------------------------------------------------------------------------
lw = 1.8
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))

#-------------------------------------------------------------------------------
# Load data
#-------------------------------------------------------------------------------

for opts in FILE_LIST:
    ds   = xr.open_dataset(opts['file'])
    hyai = ds['hyai'].values
    hybi = ds['hybi'].values
    lev  = (hyai*1e3 + hybi*1e3)
    lbl  = opts.get('n', opts['file'])
    color = opts['c']
    ax.plot(ds['hyai'], lev, color=color, linestyle='solid',  linewidth=lw, label=lbl)
    ax.plot(ds['hybi'], lev, color=color, linestyle='dashed', linewidth=lw)
    denom = hyai + hybi
    lev_max = np.max(lev)
    ax2.plot(ds['hyai']/denom, lev/lev_max, color=color, linestyle='solid', linewidth=lw)
    ax2.plot(ds['hybi']/denom, lev/lev_max, color=color, linestyle='dashed', linewidth=lw)
ax2.plot([0],[0], linestyle='solid', color='k', label='hyai')
ax2.plot([0],[0], linestyle='dashed', color='k', label='hybi')
# ---- Panel 1 ----
ax.set_xlabel('Hybrid Coefficient', fontsize=11)
ax.set_ylabel('Level [hPa]', fontsize=11)
ax.tick_params(direction='in', which='both')
ax.set_yscale('log')
ax.invert_yaxis()
ax.set_title('Hybrid Coefficients vs Level', fontsize=11)
ax.legend()

# ---- Panel 2 (normalized) ----
ax2.set_xlabel('Normalized Hybrid Coefficient', fontsize=11)
ax2.set_ylabel('Normalized Level', fontsize=11)
ax2.tick_params(direction='in', which='both')
ax2.invert_yaxis()
ax2.set_title('Normalized Hybrid Coefficients vs Level', fontsize=11)
ax2.legend()

os.makedirs(os.path.dirname(fig_file), exist_ok=True)
plt.savefig(fig_file, dpi=150, bbox_inches='tight')
print(f'file saved as\n{fig_file}\n')
plt.close()
