#!/ascldap/users/smturbe/.conda/envs/smt_met/bin/python

import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

# flags for printing debugging/tuning info/lists
print_int_debug = False
print_mid_debug = False
print_L72_comparison = False
print_table = False
discard_below_1mPa = False
date_string = "20250512"

hy_alpha_list,hy_pm_list = [],[]

for al in [1.0,1.5,2.0,2.5,3.0]:
    for pm in [100,200,300]:
        hy_alpha_list.append(al); hy_pm_list.append(pm)

# for i in range(len(hy_alpha_list)): print(f'  {hy_alpha_list[i]}  {hy_pm_list[i]}')
# exit()

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
import numpy as np

import numpy as np
from typing import Tuple

import numpy as np
from typing import Tuple

def make_vlevs_from_dz0(m: float, dz0: float, H: float = 30000.0, tol: float = 1e-12
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build interface heights and layer thicknesses with a specified minimum dz0
    and slope m (increase in dz per layer). nlev (number of interfaces) is
    determined by the function so that the arithmetic-progression baseline
    fits under H and the remaining height is added to the last layer.

    Parameters
    ----------
    m : float
        Slope per level (meters increase in dz each subsequent layer). Must be >= 0.
    dz0 : float
        Minimum (initial) layer thickness at the bottom, in meters. Must be > 0.
    H : float, optional
        Top height in meters (default 30000.0).
    tol : float, optional
        Numerical tolerance for comparisons.

    Returns
    -------
    vlevs : np.ndarray, shape (nlev_used,)
        Interface heights from 0 to H inclusive (meters).
    dz_list : np.ndarray, shape (nlev_used - 1,)
        Layer thicknesses (meters). Non-decreasing and all >= dz0.

    Raises
    ------
    ValueError
        If parameters are invalid or no feasible layering exists (e.g., dz0 > H).

    Example Usage:
        vlevs, dz = make_vlevs_from_dz0(m=5.0, dz0=50.0, H=30000.0)
        print(len(vlevs), len(dz))   # nlev_used, number of layers
        print(dz[0], dz[-1], dz.sum())  # min dz, last dz, total (should equal H)
    """
    if dz0 <= 0.0:
        raise ValueError("dz0 must be > 0 (meters).")
    if m < 0.0:
        raise ValueError("This implementation requires m >= 0 (non-decreasing dz).")
    if H <= 0.0:
        raise ValueError("H must be > 0 (meters).")

    # Sum for L layers of the progression dz0 + m*i, i=0..L-1:
    # S(L) = L*dz0 + 0.5*m*L*(L-1)
    def S_of_L(L: int) -> float:
        return L * dz0 + 0.5 * m * L * (L - 1)

    # Quick infeasible check: smallest single-layer dz0 must not exceed H
    if dz0 - tol > H:
        raise ValueError("dz0 is larger than H; no feasible layering with dz >= dz0.")

    # Solve quadratic S(L) = H for real L to get approximate maximum L
    if abs(m) < 1e-16:
        L_real = H / dz0
    else:
        # quadratic: (0.5*m) L^2 + (dz0 - 0.5*m) L - H = 0
        a = 0.5 * m
        b = dz0 - 0.5 * m
        c = -H
        disc = b * b - 4.0 * a * c
        if disc < -tol:
            # no real root (shouldn't happen with m>=0 and dz0>0), treat as infeasible
            raise ValueError("No real solution for layer count; check parameters.")
        disc = max(disc, 0.0)
        L_real_pos = (-b + np.sqrt(disc)) / (2.0 * a)
        # choose the positive root
        L_real = L_real_pos if L_real_pos > 0 else None
        if L_real is None:
            raise ValueError("Computed no positive real root for layer count.")

    # Largest integer L such that S(L) <= H is floor(L_real).
    L = max(1, int(np.floor(L_real + 1e-12)))  # ensure at least one layer

    # # Sanity check and if floor gives S(L) > H by numerical rounding, decrement
    # while L > 0 and S_of_L(L) - H > tol:
    #     L -= 1
    # if L <= 0:
    #     raise ValueError("Unable to find a positive number of layers that fits under H.")

    # Build base dzs for L layers and add remaining to the last layer
    dz_base = dz0 + m * np.arange(L+5, dtype=float)  # length L+5
    S_base = dz_base.cumsum()
    print("len to start of dz_base and S_base:", dz_base.shape, S_base.shape)
    # if dz exceeds 1500 m 
    if (dz_base > 1500).any():
        print("WARNING: dz > 1500 m")
        # dz should be less than 1500
        ind_H = np.argmin(abs(dz_base-1500))
        n_more_levs = max(0,int((H - S_base[ind_H])//1500)) # need this many more levels to get to H
        dz_base_new = np.zeros(len(dz_base)+n_more_levs)
        dz_base_new[:ind_H] = dz_base[:ind_H]
        dz_base_new[ind_H:] = 1500
        S_base_new = dz_base_new.cumsum()
        print(f"--fixed dz>1500 --> dz=1500 and added {n_more_levs} more levels")
        print(f"  to get to new S_base[-1]=",S_base[-1])
        dz_base = dz_base_new
        S_base = S_base_new
    # if the tops are mismatched
    if S_base[-1] > H:
        print(f"WARNING: top ({S_base[-1]} m) exceeds H ({H} m)")
        ind_H = np.argmin(abs(S_base-H))
        print("-- H=",H, "; S_base[ind_H]=", S_base[ind_H],"; dz=", dz_base[ind_H])
        print("-- last three dz:", dz_base[ind_H-2:ind_H+1])
        dz_base = dz_base[:ind_H]
        S_base = dz_base.cumsum()
    elif S_base[-1]==H:
        print("perfect match")
    else: # S_base < H
        print(f"WARNING: Top ({S_base[-1]} m) is below H ({H} m)")
        print(f"         Make sure dz increases monotonically and doesn't exceed 1500 m")
        ind_H = len(S_base)
        print("-- last three dz:", dz_base[-3:ind_H])
        remainder = H-S_base[-1]
        if remainder > 1500:
            remainder = H-S_base[-2]
        dz_base[ind_H] = remainder
    print("Difference between expected model top H and actual top, S_base:", H-S_base[-1])
    
    # elif dz_base[ind_H]<dz_base[ind_H-1]:
    #     # dz should be monotonically increasing
    #     ind_H = ind_H - 1
    # # remainder should be >= 0 by construction (S_base <= H)
    # if (remainder-dz_base[ind_H]) < -tol:
    #     # numeric failure
    #     raise RuntimeError("Internal numeric error: base sum exceeds H beyond tolerance.")

    dz_list = dz_base.copy()
    print("----------")
    print(dz_list)
    print("----------")

    # Final safeguards: ensure monotonic non-decreasing and dz >= dz0
    if dz_list.min() + tol < dz0:
        # numeric issue
        raise RuntimeError("Computed dz fell below dz0 unexpectedly.")
    if not np.all(np.diff(dz_list) >= -tol):
        # numeric issue
        # enforce monotonicity by small adjustments if needed
        for i in range(1, len(dz_list)):
            if dz_list[i] + tol < dz_list[i - 1]:
                dz_list[i] = dz_list[i - 1]
        # renormalize to H by adjusting last layer
        excess = dz_list.sum() - H
        dz_list[-1] -= excess
        if dz_list[-1] + tol < dz_list[-2]:
            raise RuntimeError("Unable to enforce monotonic dz while matching H.")

    # interfaces
    vlevs = np.empty(ind_H + 1, dtype=float)
    vlevs[0] = 0.0
    vlevs[1:] = np.cumsum(dz_list)

    print(f"-- dz in variable layer goes from {dz_list[0]} to {dz_list[-1]} m.")

    return vlevs, dz_list

import numpy as np
from typing import Tuple

import numpy as np
from typing import Tuple

def adjust_interfaces_to_blocks_of_8_plus_1(
    vlev: np.ndarray,
    max_spacing: float = 1500.0,
    smooth_top_n: int = 10,
) -> Tuple[np.ndarray, int]:
    """
    Adjust input interface heights vlev so the returned number of interfaces nlev_out
    satisfies nlev_out = 8*k + 1 (so number of layers L = nlev_out - 1 is a multiple of 8).
    Keeps the top interface the same, interpolates to the new count, smooths the top
    `smooth_top_n` layers (to absorb differences), enforces monotonic increase, and
    ensures no layer thickness exceeds max_spacing. If necessary, nlev is increased
    in increments of 8 until max_spacing is met.

    Parameters
    ----------
    vlev : np.ndarray
        1-D array of interface heights in meters, length nlev_in. Must be strictly increasing.
    max_spacing : float, optional
        Maximum allowed layer thickness in meters (default 1500.0).
    smooth_top_n : int, optional
        How many top layers to smooth (default 10).

    Returns
    -------
    vlev_new : np.ndarray
        Adjusted interface heights (meters), length nlev_out where nlev_out = 8*k + 1.
        Top interface equals original vlev[-1].
    nlev_out : int
        Number of interfaces in the returned array (len(vlev_new)).
    """
    vlev = np.asarray(vlev, dtype=float)
    if vlev.ndim != 1:
        raise ValueError("vlev must be 1-D.")
    nlev_in = vlev.size
    if nlev_in < 2:
        raise ValueError("vlev must contain at least two interfaces (bottom and top).")
    if not np.all(np.diff(vlev) > 0.0):
        raise ValueError("vlev must be strictly increasing.")

    H = vlev[-1] - vlev[0]
    if H <= 0.0:
        raise ValueError("Top height must be larger than bottom height.")

    # Minimal number of layers L_min required by spacing constraint
    L_min = int(np.ceil(H / float(max_spacing)))
    nlev_min = max(2, L_min + 1)  # minimal interfaces to satisfy spacing

    # Helper: given n_in, find nearest nlev = 8*k + 1 (tie -> choose lower) while respecting nlev_min
    def nearest_nlev_8k_plus_1(n_in: int, nmin: int) -> int:
        # compute k estimates
        # n = 8*k + 1  ->  k = (n - 1)/8
        k_floor = (n_in - 1) // 8
        k_ceil = ((n_in - 1) + 7) // 8
        candidates = []
        for k in (k_floor, k_ceil):
            if k >= 0:
                n_candidate = 8 * k + 1
                if n_candidate >= max(2, nmin):
                    candidates.append(n_candidate)
        # if neither candidate >= nmin, pick smallest n = 8*k + 1 >= nmin
        if not candidates:
            k_req = max(0, int(np.ceil((nmin - 1) / 8.0)))
            return 8 * k_req + 1
        # choose nearest to n_in, tie break to lower
        candidates = sorted(set(candidates))
        best = candidates[0]
        best_diff = abs(best - n_in)
        for c in candidates[1:]:
            d = abs(c - n_in)
            if d < best_diff or (d == best_diff and c < best):
                best = c
                best_diff = d
        return best

    # initial target
    target_nlev = nearest_nlev_8k_plus_1(nlev_in, nlev_min)

    # resample & smooth routine (returns vlev_interp for a candidate nlev_target)
    def resample_and_smooth(nlev_target: int) -> np.ndarray:
        idx_old = np.arange(nlev_in)
        idx_new = np.linspace(0.0, float(nlev_in - 1), nlev_target)
        vlev_interp = np.interp(idx_new, idx_old, vlev)
        vlev_interp[0] = vlev[0]
        vlev_interp[-1] = vlev[-1]

        dz = np.diff(vlev_interp)
        L_target = dz.size
        M = min(smooth_top_n, L_target)
        if M >= 2:
            dz_tail = dz[-M:].copy()
            # moving-average smoothing (window 3 if possible, else 2)
            win = 3 if M > 2 else 2
            kernel = np.ones(win) / win
            pad = win // 2
            dz_padded = np.pad(dz_tail, pad_width=pad, mode='reflect')
            dz_sm = np.convolve(dz_padded, kernel, mode='valid')
            # preserve tail sum to keep top fixed
            sum_before = dz_tail.sum()
            sum_after = dz_sm.sum()
            if sum_after > 0:
                dz_sm *= (sum_before / sum_after)
            dz_sm = np.maximum(dz_sm, 1e-6)
            dz[-M:] = dz_sm
            # recompose vlev_interp from dz, keep exact top
            vlev_interp = np.empty_like(vlev_interp)
            vlev_interp[0] = vlev[0]
            vlev_interp[1:] = vlev[0] + np.cumsum(dz)
            vlev_interp[-1] = vlev[-1]

        dz = np.diff(vlev_interp)
        if np.any(dz <= 0.0):
            dz = np.maximum(dz, 1e-6)
            vlev_interp[1:] = vlev_interp[0] + np.cumsum(dz)
            vlev_interp[-1] = vlev[-1]

        return vlev_interp

    # Try candidate; if spacing too large, increase by +8 (one block) until satisfied
    max_iter = 200
    iter_count = 0
    nlev_try = target_nlev
    while True:
        iter_count += 1
        if iter_count > max_iter:
            raise RuntimeError("Unable to find a 8*k+1 interface count satisfying spacing limit.")
        vlev_try = resample_and_smooth(nlev_try)
        dz_try = np.diff(vlev_try)
        if dz_try.max() <= max_spacing + 1e-9:
            vlev_new = vlev_try
            nlev_out = nlev_try
            break
        # increase by one 8-block (i.e., add 8 interfaces -> adds 8 layers)
        nlev_try += 8

    return vlev_new, nlev_out

def calc_levs(slope=None, discard_below_1mPa=False):
    # dk_list = [ 1, 1, 2, 2, 2, 2, 2, 2, 2,  2, 90,  6,  6,   6,   1,   1,]
    # dz_list = [20,10,30,40,50,60,70,80,90,100,250,500,750,1000,1250,1500,]
    # dk_list = [ 1, 1, 2, 2, 2, 2, 2, 2, 2,  2, 200,   6,    6,   1,   1]
    # dz_list = [20,10,30,40,50,60,70,80,90,100, 250, 500, 1000,1200,1400]
    # keep lower levels consistent (up to 18.5 km)
    dk_list = [ 1, 1, 4, 8, 8, 4, 2, 1, 1, 1, 6,   6, 60] 
    dz_list = [20,10,20,30,40,50,60,70,80,90,100,200,250] 
    dz_start = dz_list[-1]
    print("dz at 15 km:", dz_start, "m")
    # calculate the slope from current zlev to ~60 km
    zlev_lower = np.sum(np.multiply(np.array(dk_list), np.array(dz_list))) # current top give by dz from surface upward
    zlev_modeltop = 60000 - (1500*4)  # 60 km model top minus the top 6 levels have a dz=1500m
    z_leftover = zlev_modeltop - zlev_lower # how much height do we have left to account for? 
    vlevs_variable, dz_variable = make_vlevs_from_dz0(m=slope, dz0=dz_start, H=z_leftover, tol=1e-8,)
    # print(dz_variable[0], dz_variable[-1], dz_variable.sum(), (vlevs_variable[-1]-vlevs_variable[0]==dz_variable.sum()))  # initial dz, final dz, total (should equal H)
    for i in range(len(vlevs_variable)-1):
        dz_list.append(int(dz_variable[i]))
        dk_list.append(1)
    # keep top few levels to 1500 m dz
    dk_list.append(5)
    dz_list.append(1500)

    dz = []
    if 'dz_list' in locals() and 'zlev' not in locals():
        zlev = np.zeros(np.sum(dk_list)+1)
        kk = 1
        for d,dk in enumerate(dk_list):
            for k in range(dk):
                zlev[kk] = zlev[kk-1] + dz_list[d]
                dz.append(dz_list[d])
                # print(f'{kk}  {zlev[kk]:10.1}  {dz_list[d]}')
                kk += 1
    elif 'zlev' in locals():
        # calculate dz from zlev
        dz = abs(zlev[1:] - zlev[:-1])

    # Make sure number of levels is a multiple of 8
    zlev, num_ilev = adjust_interfaces_to_blocks_of_8_plus_1(zlev)
    dz = np.diff(zlev)

    print("---------------------------------------")
    print("Slope is", slope, f"m / level from {zlev_lower} m to {zlev_modeltop} m")
    #---------------------------------------------------------------------------
    # get pressure from height using curve fit from climatology
    if 'ilev' not in locals():
        ilev = height2pres(zlev)
    ind_top = np.argmin(abs(ilev-0.095))
    print("Model top is currently at: ", ilev[-1], "hPa", zlev[-1], "m")
    if abs(ilev[-1] - 0.1) > 1e-1: 
        raise Exception("Model top is not within expected tolerance of 0.1 hPa (+/- 0.1):", ilev[-1], "hPa")
    # if discard_below_1mPa:
    #     print("Discard the top", len(ilev) - ind_top, f"levels for model top at {ilev[ind_top]}")
    #     ilev = ilev[:ind_top+1]
    #     zlev = zlev[:ind_top+1]
    # print("pressure levels:", ilev)
    
    print("Number of vertical midpoint levels :", num_ilev )
    print("-- top dz: ", dz[-10:])
    print("-- top z : ", zlev[-10:]/1000, "km")
    print("---------------------------------------")
    # print(zlev/1000)
    return (dz, ilev, zlev, num_ilev)

def print_vlevs_dz(ifile=None):
    # use pressure levels from file
    if ifile is None:
        ifile = f'/projects/ccsm/inputdata/atm/scream/init/vertical_coordinates_L128_20220927.nc'
    ds = (xr.open_dataset(ifile).lev.values) # midpoints
    ds = (ds[1:]+ ds[:-1])/2 # interfaces 
    ilev = np.zeros(len(ds)+1)
    ilev[0] = (1000 + ds[-1])/2
    ilev = ds[::-1]  # bottom up
    print(f'Using ilev from input file: {ifile}')
    zlev = pres2height(ilev, H=8500)
    dz = np.diff(zlev)
    print("dz      height        pres")
    print("----------------------------------")
    for i in range(len(zlev)-1):
        print(f"{i:03} {dz[i]:4.2f} {zlev[i]:6.2f} {ilev[i]:4.2f}")
    print(f"{i:03}         {zlev[i]:6.2f} {ilev[i]:4.2f}")

def main(slope, hy_alpha=None,hy_pm=None):
    #---------------------------------------------------------------------------
    # grid recipe using a list of height thicknesses
    # slope is meters per layer

    # output_root = os.getenv('HOME')+f'/E3SM/vert_grid_files'
    output_root = '/tscratch/smturbe/strat_scratch/vert_grid_files'
    fix_lowest_spacing = True

    (dz, ilev, zlev, num_ilev) = calc_levs(slope=slope)
    num_mlev = num_ilev-1

    ofile = f'{output_root}/SCREAM_L{num_mlev}_c{date_string}_alpha_{hy_alpha:1.1f}_pm_{hy_pm}.nc'

    #---------------------------------------------------------------------------
    # Smoothing
    # dz_smoothed   = np.zeros(num_mlev)
    zlev_smoothed = np.copy(zlev)

    smth_k_beg,smth_k_end = (2,num_mlev) if fix_lowest_spacing else (1,num_mlev)
    nsmooth = 20

    for s in range(nsmooth):
        zs_tmp = np.copy(zlev_smoothed)
        # for k in range(smth_k_beg,smth_k_end):
        for k in range(smth_k_beg,smth_k_end):
            zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
    zlev = zlev_smoothed
    ilev = height2pres(zlev)
    ilev = ilev[::-1]
    # check len
    print(len(zlev), len(ilev), num_ilev, num_mlev)
    # print("-----_-_-_--------------")
    # print(ilev)
    # print("-----_-_-_--------------")

    #---------------------------------------------------------------------------
    # Generate hybrid vertical grid

    # [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)
    
    # if 't-bias' in ofile: [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, pm=  1e2, pt=1e2) # doesn't work???
    # if 't-bias' in ofile: [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, pm= 10e2, pt=1e2) # doesn't work???
    # if 'p-bias' in ofile: [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, pm=990e2, pt=1e2)

    # if 'alpha2' in ofile: [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, alpha=2)
    # if 'alpha3' in ofile: [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, alpha=3)

    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2, pm=hy_pm*1e2, pt=1e2, alpha=hy_alpha)

    # ### make sure bottom 3 levels are pure terrain following for L72
    # if (num_mlev)==72:
    #     # for a,b in ai[-3:],bi[-3:]:
    #     for k in range(0,3):
    #         k2 = num_ilev-k-1
    #         if ai[k2]>0:
    #             bi[k2] = bi[k2] + ai[k2]
    #             ai[k2] = 0

    ### calculate mid-level hybrid coefficients
    am = np.empty(num_mlev)
    bm = np.empty(num_mlev)
    for k in range(num_mlev):
        am[k] = ( ai[k+1] + ai[k] )/2.
        bm[k] = ( bi[k+1] + bi[k] )/2.

    mlev = compute_pressure_from_hybrid_coef(am,bm)
    print(len(mlev), num_mlev, len(mlev)==num_mlev)
    print("-----_-_-_--------------")
    print(mlev)
    print("-----_-_-_--------------")
    #---------------------------------------------------------------------------
    # Debug print statements

    # ### print interface levels
    # if print_int_debug:
    #     for k in range(num_ilev): 
    #         k2 = num_ilev-k-1
    #         # print(f'{k:3}  ({k2:3})    {ilev[k]:8.1f}    {ai[k]:5.3f}  {bi[k]:5.3f}')
    #         print(f'{k:02}  ({k2:02})    {ilev[k]:8.2f}    {zlev[k2]:8.1f}')


    ### print mid-level pressure and height
    # if print_mid_debug:
    #     print(f'            pressure    height')
    #     for k in range(num_mlev): 
    #         k2 = num_mlev-k-1
    #         dz = zlev[k2+1] - zlev[k2] 
    #         zmid = ( zlev[k2+1] + zlev[k2] ) / 2.
    #         # dlev = mlev72[k] - mlev[k]
    #         # print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {am[k]:5.3f}  {bm[k]:5.3f}')
    #         print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {zmid:8.1f}     {dz:5.0f}')
    #         # print(f'{k:02}  ({k2:02})    {mlev[k]:8.2f}    {zmid:8.1f}    ')
    #     print()
    
    # if print_int_debug or print_mid_debug:
    #     exit('Exiting before writing')

    #---------------------------------------------------------------------------
    # compare with E3SM's L72
    #---------------------------------------------------------------------------
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     dz = zlev[k2+1] - zlev[k2] ; dlev = mlev72[k] - mlev[k]
    #     # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {mlev[k]:8.2f}      {lev72[k]:8.2f}    {dlev:8.2f}')
    #     print(f'{k:3}  ({k2:3})     {am[k]:6.5f}  {am72[k]:6.5f}      {bm[k]:6.5f}  {bm72[k]:6.5f}')
    # print()
    if print_L72_comparison:
        for k in range(num_ilev): 
        # for k in range(20):
            k2 = num_ilev-k-1
            if k2<num_ilev-1:
                dz = zlev[k2+1] - zlev[k2] 
            else:
                dz = 0
            # dlev = ilev72[k] - ilev[k]
            # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {ilev[k]:8.2f}      {ilev72[k]:8.2f}    {dlev:8.2f}')
            if k<num_ilev-1:
                dlev1 = ilev[k+1] - ilev[k]
                dlev2 = ilev72[k+1] - ilev72[k]
            else:
                dlev1,dlev2 = 0,0
            print(f'{k:3}      {ilev[k]:6.1f}  ({dlev1:4.1f})       {ilev72[k]:6.1f}  ({dlev2:4.1f})')
            # msg = f'{k:3}  ({k2:3})'
            # msg += f'         {ilev[k]:8.2f}  {ilev72[k]:8.2f}'
            # msg += f'         {ai[k]  :6.5f}  {ai72[k]  :6.5f}'
            # msg += f'         {bi[k]  :6.5f}  {bi72[k]  :6.5f}'
            # print(msg)
        # exit()
    #---------------------------------------------------------------------------
    # print mid and interface levels
    if print_table:
        for k in range(num_mlev):
            k2 = num_mlev-k-1
            msg1 = f'{k:3}  ({k2:3})'
            msg2 = ' '*len(msg1)
            if k==0:
                ki = 0
                msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
                msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
                print(msg2)
            km = k
            ki = k+1
            msg1 = f'{k:3}  ({k2:3})'
            msg2 = ' '*len(msg1)
            msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
            msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
            msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
            print(msg1)
            print(msg2)
        # exit()

    #---------------------------------------------------------------------------
    # Write to file

    mlev = xr.DataArray(mlev, coords={'lev':mlev}, attrs={'long_name':'midpoint level', 'units':'hPa', 'positive':'down'})
    ilev = xr.DataArray(ilev, coords={'ilev':ilev}, attrs={'long_name':'interface level', 'units':'hPa', 'positive':'down'})
    hyam = xr.DataArray(am, coords={'lev':mlev.values}, attrs={'long_name':'hybrid A coefficient at layer midpoints'})
    hybm = xr.DataArray(bm, coords={'lev':mlev.values}, attrs={'long_name':'hybrid B coefficient at layer midpoints'})
    hyai = xr.DataArray(ai, coords={'ilev':ilev.values}, attrs={'long_name':'hybrid A coefficient at layer interfaces'})
    hybi = xr.DataArray(bi, coords={'ilev':ilev.values}, attrs={'long_name':'hybrid B coefficient at layer interfaces'})

    ds = xr.Dataset({'lev':mlev, 'ilev':ilev, 'hyam':hyam, 'hybm':hybm, 'hyai':hyai, 'hybi':hybi, 
                     'P0':xr.DataArray(p0, attrs={'units':'Pa','long_name':'Reference pressure'})},
                     attrs={'nsmooth':nsmooth,
                            'alpha':hy_alpha,
                            'pressure only above':hy_pm,
                            'slope':f'{slope} m / level'})
    
    print(f'\n{ofile}\n')
    ds.to_netcdf(ofile)

#-------------------------------------------------------------------------------
# print some other useful info
#-------------------------------------------------------------------------------
    print()
    print(f'  zmid max: { ( (zlev[num_ilev-1]+zlev[num_ilev-2])/2. ) }')
    print(f'  pmid min: {np.min(mlev.values)}')
    print(f'  zint max: {np.max(zlev)}')
    print(f'  pint min: {np.min(ilev.values)}')
    print()
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev,pm=None,pt=None,alpha=None):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    if pm is None: pm = 18230.50  # level to switch from sigma to pressure? [pa]
    if pt is None: pt = 100.0     # top pressure? [pa]

    psize = len(plev)
    a = np.empty(psize)
    b = np.empty(psize)

    if alpha is None: alpha = 1.0

    for i in range(psize) :
        # compute sigma
        if plev[i]<pm:
            sigma = ( plev[i] - pm ) / ( pm - pt )
        else:
            sigma = ( plev[i] - pm ) / ( ps - pm )
        # compute delta
        delta = 0.0 if sigma<0.0 else 1.0
        # compute A and B, pressure coefficients
        if sigma >= 0:
            b[i] = sigma**alpha * delta
            # compute a so that a*p0 + b*ps = plev[i]
            a[i] = ( plev[i] - b[i]*ps ) / p0
        else:
            a[i] = ( pm*(1-sigma)*delta + (1-delta)*(pm*(1+sigma)-sigma*pt) ) / p0
            b[i] = np.abs( sigma*delta )

    return [a,b]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_pressure_from_hybrid_coef(a,b):
    """
    compute pressure from hybrid coefficients
    """
    lev = ( a*p0 + b*ps ) / 100.0 
    return lev
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def height2pres(zlev, H=6740.):
    """Uses scale height to convert height to pressure

        From WH, H=6740 m
        From typical standard atmosphere H=8500 m
    """
    return np.exp( -1*zlev/H ) * 1000

def pres2height(ilev, H=6740):
    """Uses scale height to convert pressure to height

        From WH, H=6740 m
        From typical standard atmosphere H=8500 m
    """
    return (-1 * np.log(ilev/1000) * H)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main(slope=5.0, hy_alpha=1.0, hy_pm=300)
    # print_vlevs_dz()
    # (dz, ilev, zlev, num_ilev, num_mlev) = calc_levs(slope=1.0)
    # print(f"{ilev[0]} hPa to {ilev[-1]} hPa with {num_ilev} interface levels.")
    # print(dz)
    # print("--------")
    # print(ilev)
    # print("----------")
    # print(zlev)
    # vlevs_variable, dz_variable, nlevs_used = make_vlevs_with_dz0(m=5, nlev=180, dz0=250, H=30000.0, tol=1.0,)
    # print("NUM LAYER INTERFACES", nlevs_used)
    # print(dz_variable[0], dz_variable[-1], dz_variable.sum(), (vlevs_variable[-1]-vlevs_variable[0]==dz_variable.sum()))  # initial dz, final dz, total (should equal H)
    # for i in range(len(hy_alpha_list)):
    #     main(hy_alpha=hy_alpha_list[i],hy_pm=hy_pm_list[i])
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------