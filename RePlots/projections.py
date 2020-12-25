import logging
import cartopy



class projection():

    def __init__(self):
        self._name = 'Base'
        self._title = 'Base'
        self.FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        self.LOG_FILE = "rcesm_diag"+datetime.now().strftime("%Y%m%d%H%M%S)")+".log"

    def get_dataset(self,test):
        # set up plotting projections stuff for maps
        pc = cartopy.crs.PlateCarree()  # to match lon/lat
        proj = cartopy.crs.LambertConformal(central_longitude=-90)  # projection for plot

        return proj
