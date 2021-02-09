#!/usr/bin/env python3
"""Base class for ocean diagnostics plots
"""

import sys


# check the system python version and require 3.5.x or greater
if not (sys.implementation.version.major==3 and sys.implementation.version.minor >=5):
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
            ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

import traceback
import os
import subprocess

import matplotlib.pyplot as plt
import dask

# import the helper utility module
from utils import cesmEnvLib, diagUtilsLib

class OceanDiagnosticPlot(object):
    """This is the base class defining the common interface for all
    ocean diagnostic plots

    """
    def __init__(self):
        self._html = ''
        self._name = 'Base'
        self._shortname = 'Base'
        self._template_file = 'base.tmpl'
        self._files = list()


        plt.rcParams.update({
            "font.family": "serif",
            "font.serif": [],  # use latex default serif font
            "font.sans-serif": ["DejaVu Sans"],  # use a specific sans-serif font
        })

    def name(self):
        return self._name

    def shortname(self):
        return self._shortname

    def check_prerequisites(self, env):
        """This method does some generic checks for the plots prerequisites
        that are common to all plots

        """
        print('  Checking generic prerequisites for ocean diagnostics plot.')

        # set SEASAVGFILE env var to the envDict['MAVGFILE'] file
        env['SEASAVGFILE'] = env['MAVGFILE']

        # set SEASAVGTEMP env var to the envDict['MAVGFILE'] file
        env['SEASAVGTEMP'] = env['MAVGFILE']

        # set SEASAVGSALT env var to the envDict['MAVGFILE'] file
        env['SEASAVGSALT'] = env['MAVGFILE']

        cesmEnvLib.setXmlEnv(env)

    def generate_plots(self, env):
        """This is the base class for calling plots
        """
        raise RuntimeError ('Generate plots must be implimented in the sub-class')

    def get_html(self, workdir, templatePath, imgFormat):
        """This method returns the html snippet for the plot.
        """
        self._create_html(workdir, templatePath, imgFormat)
        return self._shortname, self._html

    # @dask.delayed
    # def lazy_plots(env, var, title, proj = self._):
    #     fig = plt.figure(figsize=(15, 13))
    #     nrows, ncols = 1, 1
    #     ax1 = plt.subplot(nrows, ncols, 1, projection=proj)
    #     # call the setup_map convenience function to get the basics into the map
    #     # this returns a dictionary of items to input to your subsequent plotting calls
    #     pargs, oargs = setup_map(ax=ax1, title=title, titlesize=env['fig_titlesize'], xticks=np.arange(-95, -75, 5),
    #                              ticklabelsize=env['fig_ticksize'], subargs={'label': 'a', 'loc': 'bottom left'})
    #
    #     var.cmo.cfpcolormesh(**pargs)
    #     # also plot contour lines on top. This is matplotlib wrapped by xarray with cf-xarray.
    #     cs = var.cf.plot.contour(**pargs, colors='k', linewidths=1)
    #     # also label contour lines. This is matplotlib directly.
    #     ax1.clabel(cs, inline=1, fontsize=10, fmt='%d')  # add labels to contours
    #
    #     #ds.sel(time=time)['air'].plot()
    #
    #     filename = '{0}/{1}.png'.format(self._plotdir, var)
    #
    #     fig.savefig(filename, bbox_inches='tight', pad_inches=1)
    #     plt.close()
        
# todo move these classes to another file
class RecoverableError(RuntimeError):
    pass


class UnknownPlotType(RecoverableError):
    pass

