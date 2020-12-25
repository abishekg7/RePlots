import logging
import xroms
from glob import glob




class dataset():

    def __init__(self):
        self._name = 'Base'
        self._title = 'Base'
        self.FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        self.LOG_FILE = "rcesm_diag"+datetime.now().strftime("%Y%m%d%H%M%S)")+".log"

    def get_dataset(self,test):
        """

        :rtype: object
        :param test: 
        :return:
        """
        files = glob('/home/abishekg/Research/datasets/GOM_9k_nature_copernicus/cmpr_GOM_9k_nature_copernicus*.nc')
        files.sort()
        ds = xroms.open_mfnetcdf(files, chunks={'ocean_time': 30})
        return ds
