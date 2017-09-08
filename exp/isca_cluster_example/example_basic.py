# A basic Earth-like setup.
# - Uses nearly all standard parameter values.
# - Grey radiation scheme
# - No seasonal cycle - p2 like insolation profile

import sys
import numpy as np

import gfdl.experiment

exp = gfdl.experiment.Experiment('ref_earth_grey')

exp.log_to_file('ref_earth.log')

# compiles source code to exp.execdir
# only compile if we pass the command line argument 'compile'
exp.disable_rrtm()
if 'compile' in sys.argv:
    exp.compile()

# setup the namelist:
# - Frierson gray radiation
# - No diurnal or seasonal cycle
# - 25 vertical levels (26 half levels)
# - T171 resolution

exp.namelist['idealized_moist_phys_nml']['two_stream_gray'] = True
exp.namelist['idealized_moist_phys_nml']['do_rrtm_radiation'] = False
exp.namelist['two_stream_gray_rad_nml']['do_seasonal'] = False
exp.namelist['spectral_dynamics_nml']['num_levels'] = 25

# don't use a calendar, but do use 30 day "months"
exp.namelist['main_nml'] = {
    'dt_atmos': 300,
    'seconds': 86400.0*30,
    'calendar': 'thirty_day',
    'current_date': [2000, 1, 1, 0, 0, 0]
}

exp.update_namelist({
    'spectral_dynamics_nml': {
        'num_fourier': 170,
        'lat_max': 256,
        'num_spherical': 171,
        'lon_max': 512,
        'num_levels': 25,
}
})

# Setup a diag_table
# - Record daily and every 6 hours
# - Basic primitive equation prognostic var output
# - Radiation fluxes

diag = gfdl.experiment.DiagTable()

diag.add_file('daily', 1, 'days')

diag.add_field('dynamics', 'ps')
diag.add_field('dynamics', 'bk')
diag.add_field('dynamics', 'pk')
diag.add_field('dynamics', 'ucomp')
diag.add_field('dynamics', 'vcomp')
diag.add_field('dynamics', 'temp')
diag.add_field('dynamics', 'vor')
diag.add_field('dynamics', 'div')
diag.add_field('dynamics', 'sphum')

diag.add_field('two_stream', 'olr')
diag.add_field('two_stream', 'flux_sw')
diag.add_field('two_stream', 'flux_lw')

diag.add_field('mixed_layer', 't_surf')

# add the diag_table setup to the experiment
exp.use_diag_table(diag)

# clean up previous runs.
exp.clear_rundir()

# run month 1 from a cold start
exp.runmonth(1, use_restart=False, num_cores=64, multi_node=True)
for i in range(2, 6):
    # run subsequent months (default is to find the previous month
    # and use that as restart).
    exp.runmonth(i, num_cores=64, multi_node=True)
