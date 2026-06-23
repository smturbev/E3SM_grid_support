#!/ascldap/users/smturbe/.conda/envs/smt_met/bin/python

import os, numpy as np, xarray as xr
from metpy.calc import pressure_to_height_std, height_to_pressure_std
import metpy.units as mpunits


p0 = 1000e2
ps = 1000e2

print_table = True
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
def main(hy_alpha=None,hy_pm=None):
    #---------------------------------------------------------------------------
    # grid recipe using a list of height thicknesses

    # output_root = os.getenv('HOME')+f'/E3SM/vert_grid_files'
    output_root = '/tscratch/smturbe/strat_scratch/vert_grid_files'


    ofile = f'{output_root}/SCREAM_fromL128metpyto1mPa_c20260501_alpha_{hy_alpha:1.1f}_pm_{hy_pm}.nc'

    ifile = '/projects/ccsm/inputdata/atm/scream/init/vertical_coordinates_L128_20220927.nc'
    ds = xr.open_dataset(ifile)
    hyai = ds.hyai.values
    hybi = ds.hybi.values
    ilev_from_coeff = (hyai + hybi)*1000.
    ilev_from_file  = ds.ilev.values
    if (ilev_from_coeff != ilev_from_file).all():
        raise Exception(f'pressure at layer interfaces does not equal (A+B)*1000; A={hyai}; B={hybi}; (A+B)*1000={ilev_from_coeff}; ilev={ilev_from_file}')
    if p0 != ds.P0.values:
        raise Exception(f'Reference pressure is not {p0}; P0 from file = {ds.P0.values}')
    ilev = ilev_from_file
    mlev = ds.lev.values
    hyam = ds.hyam.values
    hybm = ds.hybm.values
    print(" ilev \n", ilev)
    # calculate zlev and dz from given pressure levels
    zlev = pres2height(ilev * mpunits.units("hPa"), use_metpy=True).to('m')
    print(" ------ OLD LEVELS L128 ---------\n\n", zlev)
    dz = abs(zlev[1:] - zlev[:-1]).to(mpunits.units('m'))

    num_ilev = len(ilev)
    num_mlev = num_ilev-1

    # find layer interface where dz=250m
    # should be around 14 km
    iind_newdz = np.argmin(abs(dz.magnitude - 250))
    print(iind_newdz, zlev[iind_newdz])
    # discard layer interfaces above this height
    hyai = hyai[iind_newdz-1:]
    hybi = hybi[iind_newdz-1:]
    ilev = ilev[iind_newdz-1:]
    zlev = zlev[iind_newdz-1:]
    # discard layer mid points above this height
    dz = dz[iind_newdz:]
    hyam = hyam[iind_newdz:]
    hybm = hybm[iind_newdz:]
    mlev = mlev[iind_newdz:]
    # create new layers above this height
    num_new_levs = int(((50 * mpunits.units('km') - zlev[0])/0.250 * mpunits.units('km')).magnitude)-1
    print(num_new_levs, "new levels needed to get to 60 km model top")
    zlev_new = np.array([ (zlev[0].to('m').magnitude + 250 * i) for i in range(num_new_levs) ])
    zlev_new = zlev_new[::-1]
    print(zlev_new)
    # convert new vertical levels to ilevs
    ilev_new = height2pres(zlev_new * mpunits.units("m"), use_metpy=True).to('hPa').magnitude
    iind_01hPa = np.nanargmin(abs(ilev_new - 0.1))
    print("\n", iind_01hPa, "ind for 0.1 hPa (new model top)")
    zlev_new = zlev_new[iind_01hPa:]
    ilev_new = ilev_new[iind_01hPa:]
    print(f"new levels (L{(len(ilev)+len(ilev_new)-1)})\n\n")
    hyai_new, hybi_new = compute_hybrid_coef_from_pressure(ilev_new*100, pm=hy_pm, pt=0.1)
    # combine L128 with new stratosphere levels
    ilev_all = np.zeros(len(ilev)+len(zlev_new)-1)
    zlev_all = np.zeros(len(ilev)+len(zlev_new)-1)
    hyai_all = np.zeros(len(ilev)+len(zlev_new)-1)
    hybi_all = np.zeros(len(ilev)+len(zlev_new)-1)
    ilev_all[:len(ilev_new)] = ilev_new
    ilev_all[len(ilev_new)-1:] = ilev
    zlev_all[:len(ilev_new)] = zlev_new
    zlev_all[len(ilev_new)-1:] = zlev
    dz_all = abs(zlev_all[1:]-zlev_all[:-1])
    hyai_all[:len(ilev_new)] = hyai_new
    hyai_all[len(ilev_new)-1:] = hyai
    hybi_all[:len(ilev_new)] = hybi_new
    hybi_all[len(ilev_new)-1:] = hybi

    print('\n\n-----------------------\n\n')
    # print(ilev_new)
    for i in range(len(ilev_all)):
        print(f'{i:4} {ilev_all[i]:8.2f} hPa {zlev_all[i]:8.2f} m   A/B={hyai_all[i]:4.4f}/{hybi_all[i]:4.4f}  (A+B)*1000 = {((hyai_all[i]+hybi_all[i])*1000):4.2f} hPa')
        if i == (len(ilev_all)-num_ilev):
            print('------------------------------------')
        if i<(len(ilev_all))-1:
            print(f'{dz_all[i]:30.2f}')
    # set to new levels
    zlev = zlev_all
    ilev = ilev_all
    dz = dz_all
    hyai = hyai_all
    hybi = hybi_all
    # compute hybrid coefficients for layer midpoints
    hyam = (hyai[1:]+hyai[:-1])/2
    hybm = (hybi[1:]+hybi[:-1])/2
    # compute layer midpoint pressure level from coefficients
    mlev = compute_pressure_from_hybrid_coef(hyam,hybm)

    # #---------------------------------------------------------------------------
    # # Smoothing

    # nsmooth = 20
    # fix_lowest_spacing = True
    # # dz_smoothed   = np.zeros(num_mlev)
    # zlev_smoothed = np.copy(zlev)

    # smth_k_beg,smth_k_end = (2,num_mlev) if fix_lowest_spacing else (1,num_mlev)

    # for s in range(nsmooth):
    #     zs_tmp = np.copy(zlev_smoothed)
    #     # for k in range(smth_k_beg,smth_k_end):
    #     for k in range(smth_k_beg,smth_k_end):
    #         zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
    # zlev = zlev_smoothed
    # ilev = height2pres(zlev)
    # ilev = ilev[::-1]
    
    #---------------------------------------------------------------------------
    # print mid and interface levels
    # if print_table:
    #     for k in range(num_mlev):
    #         k2 = num_mlev-k-1
    #         msg1 = f'{k:3}  ({k2:3})'
    #         msg2 = ' '*len(msg1)
    #         if k==0:
    #             ki = 0
    #             msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {hyai[ki]:8.5f}        {hybi[ki]:8.5f}'
    #             msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #             print(msg2)
    #         km = k
    #         ki = k+1
    #         msg1 = f'{k:3}  ({k2:3})'
    #         msg2 = ' '*len(msg1)
    #         msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {hyam[km]:8.5f}        {hybm[km]:8.5f}'
    #         msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {hyai[ki]:8.5f}        {hybi[ki]:8.5f}'
    #         msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #         print(msg1)
    #         print(msg2)
    #     # exit()

#     #---------------------------------------------------------------------------
#     # Write to file

    mlev = xr.DataArray(mlev, coords={'lev':mlev}, attrs={'long_name':'midpoint level', 'units':'hPa', 'positive':'down'})
    ilev = xr.DataArray(ilev, coords={'ilev':ilev}, attrs={'long_name':'interface level', 'units':'hPa', 'positive':'down'})
    hyam = xr.DataArray(hyam, coords={'lev':mlev.values}, attrs={'long_name':'hybrid A coefficient at layer midpoints'})
    hybm = xr.DataArray(hybm, coords={'lev':mlev.values}, attrs={'long_name':'hybrid B coefficient at layer midpoints'})
    hyai = xr.DataArray(hyai, coords={'ilev':ilev.values}, attrs={'long_name':'hybrid A coefficient at layer interfaces'})
    hybi = xr.DataArray(hybi, coords={'ilev':ilev.values}, attrs={'long_name':'hybrid B coefficient at layer interfaces'})

    ds = xr.Dataset({'lev':mlev, 'ilev':ilev, 'hyam':hyam, 'hybm':hybm, 'hyai':hyai, 'hybi':hybi, 
                     'P0':xr.DataArray(p0, attrs={'units':'Pa','long_name':'Reference pressure'})},
                     attrs={'alpha':hy_alpha,
                            'pressure only above':hy_pm,
                            'model top':'0.1 hPa'})
    
    print(f'\n{ofile}\n')
    ds.to_netcdf(ofile)

#-------------------------------------------------------------------------------
# print some other useful info
#-------------------------------------------------------------------------------
    print()
    print(f'  zmid max: { ( (zlev[0]+zlev[1])/2 ) }')
    print(f'  pmid min: {np.min(mlev.values)}')
    print(f'  zint max: {np.max(zlev)}')
    print(f'  pint min: {np.min(ilev.values)}')
    print()
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev,pm=None,pt=None,alpha=None):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    if pm is None: 
        pm = 18230.50  # level to switch from sigma to pressure? [pa]
    else:
        pm = pm*100.   # e.g., 300 hPa = 30000 Pa
    if pt is None: 
        pt = 100.0     # top pressure? [pa]
    else:
        pt = pt*100.   # top pressure [Pa]

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
def height2pres(zlev, H=6740., use_metpy=False):
    """Uses scale height to convert height to pressure

        From WH, H=6740 m
        From typical standard atmosphere H=8500 m
    """
    if use_metpy:
        pres = height_to_pressure_std(zlev)
    else:
        pres = np.exp( -1*zlev/H ) * 1000
    return pres

def pres2height(ilev, H=6740, use_metpy=False):
    """Uses scale height to convert pressure to height

        From WH, H=6740 m
        From typical standard atmosphere H=8500 m
    """
    if use_metpy:
        height = pressure_to_height_std(ilev)
    else:
        height = (-1 * np.log(ilev/1000) * H)
    return height
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main(hy_alpha=1.0, hy_pm=300)

    # for i in range(len(hy_alpha_list)):
    #     main(hy_alpha=hy_alpha_list[i],hy_pm=hy_pm_list[i])
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------