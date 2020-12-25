import unittest
import xarray as xr
import xroms
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import numpy as np
import cmocean.cm as cmo
import cf_xarray
import xcmocean
import RePlots as rp



class MyTestCase(unittest.TestCase):
    def test_something(self):

        ds = rp.get_dataset()


        EKE = ds.xroms.EKE.cf.mean('T', skipna=False)
        EKE = EKE.compute()

        # set up figure with size
        fig = plt.figure(figsize=(15, 13))
        # we will have 3 rows of plots and 3 columns of plots
        nrows, ncols = 3, 3

        titlesize = 16
        ticksize = 12

        ## EKE ##
        ax7 = plt.subplot(1, 1, 1, projection=proj)
        pargs, oargs = rp.setup_map(ax=ax7, title='Eddy kinetic energy', titlesize=titlesize,
                                    xticks=np.arange(-95, -75, 5),
                                    ticklabelsize=ticksize, subargs={'label': 'f', 'loc': 'bottom left'})
        EKE.cmo.cfplot(**pargs)
        cs = EKE.cf.plot.contour(**pargs, colors='k')
        plt.savefig('test.png')


        #self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
