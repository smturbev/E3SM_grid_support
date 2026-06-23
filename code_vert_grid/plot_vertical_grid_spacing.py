#!/ascldap/users/smturbe/.conda/envs/smt_met/bin/python

import os, numpy as np, xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


#-------------------------------------------------------------------------------
# Grid registration
#-------------------------------------------------------------------------------
opt_list = []
def add_grid(file_path, **kwargs):
    case_opts = {'file': file_path}
    for k, val in kwargs.items():
        case_opts[k] = val
    opt_list.append(case_opts)
#-------------------------------------------------------------------------------

grid_root = '/projects/ccsm/inputdata/atm/scream/init'
add_grid(f'{grid_root}/vertical_coordinates_L128_20220927.nc', n='L128', c='gray', sponge="14")
add_grid(f'{grid_root}/vertical_coordinates_L72_20220927.nc', n='L72',  c='black')

grid_root = '/tscratch/smturbe/strat_scratch/vert_grid_files'
# add_grid(f'{grid_root}/SCREAM_L236_c20250512_alpha_1.0_pm_300.nc',  n='L236', c='gray')
# add_grid(f'{grid_root}/SCREAM_vertical_levels_L184.nc',   n='L184 alpha=1.0 pm=300', c='red')
# add_grid(f'{grid_root}/vertical_coordinates_L177_20260507.nc',  n='L177', c='pink')
# add_grid(f'{grid_root}/SCREAM_L232_c20250512_alpha_1.0_pm_300.nc', n='L232', c='gray')
# add_grid(f'{grid_root}/SCREAM_L182_c20250512_alpha_1.0_pm_300.nc', n='L184', c='purple')

# 10 vlevs with different slopes
# slope = 0
# add_grid(f"{grid_root}/SCREAM_L234_c20250512_alpha_1.0_pm_300.nc", n="L234", c="red")
# slope =  2 m / level
# add_grid(f"{grid_root}/SCREAM_L208_c20250512_alpha_1.0_pm_300.nc", n="L208", c="red")
# # slope =  5 m / level
add_grid(f"{grid_root}/SCREAM_L192_c20250512_alpha_1.0_pm_300.nc",n="L192", c="orange", sponge="19")
# add_grid(f"{grid_root}/SCREAM_L171_c20250512_alpha_1.0_pm_300.nc", n="L171", c="yellow")
# # slope = 10 m / level
# add_grid(f"{grid_root}/SCREAM_L155_c20250512_alpha_1.0_pm_300.nc", n="L155", c="yellowgreen")
# # slope = 20 m / level
# add_grid(f"{grid_root}/SCREAM_L160_c20250512_alpha_1.0_pm_300.nc",n="L160", c="green")
# # slope = 30 m / level
# add_grid(f"{grid_root}/SCREAM_L152_c20250512_alpha_1.0_pm_300.nc", n="L152", c="C0")
# # slope = 50 m / level
# add_grid(f"{grid_root}/SCREAM_L126_c20250512_alpha_1.0_pm_300.nc", n="L126", c="purple")

#-------------------------------------------------------------------------------
# Settings
#-------------------------------------------------------------------------------
print_table     = False
use_height      = True   # use height (km) for Y-axis; else use pressure (hPa)
add_zoomed_plot = False
add_sponge_layer = True
zoom_top_idx    = -30     # index cutoff for zoomed panel
if use_height:
    fig_file    = os.path.join('figs_vert_grid/vertical_grid_spacing_km.png')
else:
    fig_file    = os.path.join('figs_vert_grid/vertical_grid_spacing_mb.png')

#-------------------------------------------------------------------------------
# Assign unique colors to any grid that didn't specify one
#-------------------------------------------------------------------------------
def _gen_unique_colors(n_colors):
    """Return n visually distinct colors using HSV spacing."""
    return [mcolors.hsv_to_rgb((i / n_colors, 0.85, 0.80)) for i in range(n_colors)]

_uncolored = [i for i, o in enumerate(opt_list) if 'c' not in o]
_palette   = _gen_unique_colors(len(_uncolored))
for idx, palette_color in zip(_uncolored, _palette):
    opt_list[idx]['c'] = palette_color

#-------------------------------------------------------------------------------
# Print table
#-------------------------------------------------------------------------------
if print_table:
    mlev_list_tbl, zlev_list_tbl = [], []
    for opts in opt_list:
        ds   = xr.open_dataset(opts['file'])
        mlev = ds['hyai'].values * 1000 + ds['hybi'].values * 1000
        zlev = np.log(mlev / 1e3) * -6740.
        mlev_list_tbl.append(mlev)
        zlev_list_tbl.append(zlev)

    max_len = max(len(m) for m in mlev_list_tbl)
    for k in range(max_len):
        k2  = max_len - k - 1
        msg = f'{k:3}  ({k2:3}) '
        for g, (mlev, zlev) in enumerate(zip(mlev_list_tbl, zlev_list_tbl)):
            if k < len(mlev):
                msg += f'     {mlev[k]:8.2f} mb   {zlev[k]:8.1f} m'
        print(msg)


#-------------------------------------------------------------------------------
# Create figure
#-------------------------------------------------------------------------------
lw        = 1.8
ms        = 4
n_panels  = 2 if add_zoomed_plot else 1
fig, axes = plt.subplots(1, n_panels, figsize=(5 * n_panels, 8), sharey=False)
if n_panels == 1:
    axes = [axes]

ax1 = axes[0]
ax2 = axes[1] if add_zoomed_plot else None

ylabel = 'Approx. Height [km]'  if use_height else 'Approx. Pressure [hPa]'
xlabel = 'Grid Spacing [m]'

for ax in axes:
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.tick_params(direction='in', which='both')

# ---- Load data -----
for opts in opt_list:
    ds    = xr.open_dataset(opts['file'])
    mlev  = ds['hyam'].values * 1000 + ds['hybm'].values * 1000
    ilev  = ds['hyai'].values * 1000 + ds['hybi'].values * 1000

    ilevz = np.log(ilev / 1e3) * -6740.         # interface heights [m]
    mlevz = np.log(mlev / 1e3) * -6740. / 1e3   # midpoint heights  [km]

    lbl = opts.get('n', opts['file'])

    dlevz = np.array([ilevz[k] - ilevz[k+1] for k in range(len(mlev))])

    color = opts['c']
    ls    = opts['ls'] if 'ls' in opts else 'solid'
    sponge_layer=int(opts['sponge']) if 'sponge' in opts else None
    ms    = 2
    if use_height:
        lev = mlevz
    else:
        lev = mlev
    ax1.plot(dlevz, lev, color=color, linestyle=ls,
                    linewidth=lw, marker='o', markersize=ms, label=lbl)
    ax1.plot(dlevz[0], lev[0], marker='_', color=color, markersize=30,   # <-- top marker
                markeredgecolor='black', markeredgewidth=0.5, zorder=5)
    if add_sponge_layer:
        if sponge_layer is not None:
            ax1.axhline(y=lev[sponge_layer], xmin=0, xmax=2500, color=color, linestyle="dashed", alpha=0.7)
    if ax2 is not None:
        ax2.plot(dlevz, mlevz, color=color, linestyle=ls,
                 linewidth=lw, marker='o', markersize=ms)

if ax2 is not None:
    x_pad2 = (dlev_max2 - dlev_min) * 0.05
    y_pad2 = (mlev_max2 - mlev_min2) * 0.05
    # ax2.set_xlim(dlev_min, dlev_max2 + x_pad2)
    # ax2.set_ylim(mlev_min2, mlev_max2)# + y_pad2)
    ax2.set_xlim(0, 200)
    ax2.set_ylim(0, 3)# + y_pad2)

# Pressure axis: invert and log scale
if not use_height:
    for ax in axes:
        ax.invert_yaxis()
    ax1.set_yscale('log')

# ---- Legend ----
ax1.legend(fontsize=8, loc=4,
           framealpha=0.85, edgecolor='gray')

# ---- Titles ----
ax1.set_title('Full Column', fontsize=11)
if ax2 is not None:
    ax2.set_title('Lower Troposphere (zoomed)', fontsize=11)

plt.tight_layout()
os.makedirs(os.path.dirname(fig_file), exist_ok=True)
plt.savefig(fig_file, dpi=150, bbox_inches='tight')
print(f'saved as\n{fig_file}\n')
plt.close()