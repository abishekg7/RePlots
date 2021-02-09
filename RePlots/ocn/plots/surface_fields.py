""" 
plot module: PM_FLD2D
plot name:   2D Surface Fields

classes:
SurfaceFields:          base class
SurfaceFields_obs:      defines specific NCL list for model vs. observations plots
SurfaceFields_control:  defines specific NCL list for model vs. control plots
"""

from __future__ import print_function

import sys

if sys.hexversion < 0x02070000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 2.7.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

import traceback
import os
import jinja2


# import the helper utility module
#from cesm_utils import cesmEnvLib
#from diag_utils import diagUtilsLib
import dask
import cartopy
import matplotlib.pyplot as plt
import numpy as np
import cmocean.cm as cmo
import cf_xarray
import xcmocean
# import the plot baseclass module
from RePlots.ocn.plots.ocn_diags_plot_bc import OceanDiagnosticPlot
import RePlots.plotting as rplt

class SurfaceFields_model(OceanDiagnosticPlot):
    """Detailed description of the plot that will show up in help documentation
    """

    def __init__(self):
        super(SurfaceFields_model, self).__init__()
        self._expectedPlots = ['sustr', 'svstr', 'zeta']
        #self._expectedPlots = [ 'SSH', 'HBLT', 'HMXL', 'DIA_DEPTH', 'TLT', 'INT_DEPTH', 'SU', 'SV', 'BSF' ]
        #self._expectedPlots_za = [ 'SSH_GLO_za', 'HBLT_GLO_za', 'HMXL_GLO_za', 'DIA_DEPTH_GLO_za', 'TLT_GLO_za', 'INT_DEPTH_GLO_za' ]

        self._name = '2D Surface Fields'
        self._shortname = 'PM_FLD2D'
        self._template_file = 'surface_fields.tmpl'
        self._ncl = list()

    def check_prerequisites(self, env):
        """list and check specific prequisites for this plot.
        """
        self._plotdir = env['plot_dir']
        self._proj = cartopy.crs.LambertConformal(central_longitude=-90)  # projection for plot

        #super(SurfaceFields_model, self).check_prerequisites(env)
        print("  Checking prerequisites for : {0}".format(self.__class__.__name__))

        # check the observation sea surface height file
        #sourceFile = '{0}/{1}'.format( env['SSHOBSDIR'], env['SSHOBSFILE'] )
        #linkFile = '{0}/{1}'.format(env['WORKDIR'],env['SSHOBSFILE'])
        #diagUtilsLib.createSymLink(sourceFile, linkFile)

    def generate_plots(self, dataset, env):
        """Put commands to generate plot here!
        """
        print('  Generating diagnostic plots for : {0}'.format(self.__class__.__name__))
        tasks = []

        for i, plot in enumerate(self._expectedPlots):
            print('plots {0} {1}'.format(i, plot))
            #SST = ds['temp'].cf.isel(Z=-1, ocean_time=0)
            var = dataset.ds[plot].isel(ocean_time=0)

            # Could use var.name for fig name
            # and vaz.attrs['long_name'] for title
            delayed_task = self.lazy_plots(env, var, name=var.name, title=var.attrs['long_name'])
            tasks.append(delayed_task)

        return tasks

    @dask.delayed
    def lazy_plots(self, env, var, name, title):

        fig = plt.figure(figsize=(15, 13))
        proj = self._proj
        nrows, ncols = 1, 1

        ax1 = plt.subplot(nrows, ncols, 1, projection=proj)
        # call the setup_map convenience function to get the basics into the map
        # this returns a dictionary of items to input to your subsequent plotting calls
        pargs, oargs = rplt.setup_map(ax=ax1, title=title, titlesize=env['fig_titlesize'], xticks=np.arange(-95, -75, 5),
                                 ticklabelsize=env['fig_ticksize'], subargs={'label': 'a', 'loc': 'bottom left'})

        var.cmo.cfpcolormesh(**pargs)
        # also plot contour lines on top. This is matplotlib wrapped by xarray with cf-xarray.
        cs = var.cf.plot.contour(**pargs, colors='k', linewidths=1)
        # also label contour lines. This is matplotlib directly.
        ax1.clabel(cs, inline=1, fontsize=10, fmt='%d')  # add labels to contours

        #ds.sel(time=time)['air'].plot()

        filename = '{0}/{1}.png'.format(self._plotdir, name)

        fig.savefig(filename, bbox_inches='tight', pad_inches=1)
        plt.close(fig=fig)



class SurfaceFields_obs(SurfaceFields_model):

    def __init__(self):
        super(SurfaceFields_obs, self).__init__()
        self._ncl = ['ssh.ncl', 'field_2d.ncl', 'field_2d_za.ncl']

class SurfaceFields_control(SurfaceFields_model):

    def __init__(self):
        super(SurfaceFields_control, self).__init__()
        self._ncl = ['field_2d_diff.ncl', 'field_2d_za_diff.ncl']
