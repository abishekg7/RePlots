import RePlots
import RePlots.ocn.ocn_clim_generator as rp
import logging
from utils import CustomLogger
from utils import diagUtilsLib

def test_call_xarray_averager():
    envDict = dict()
    log = CustomLogger(logging_level=logging.INFO, file=False, console=True)
    logger = log.logger

    dataset = RePlots.dataset(envDict, logger)
    dataset.start_daskclient()

    files = ['/datasets/GOM_9k_nature_copernicus/cmpr_GOM_9k_nature_copernicus.ocn.hi.2010-01-03_03:00:00.nc']
    dataset.open_dataset(files)
    climdir = '/home/abishekg/PycharmProjects/RePlots/tests/out'
    inVarList = ['salt', 'temp']
    avgtype = 'season'
    rp.callXarrayAverager(dataset=dataset, climdir=climdir, case_prefix='test', varlist=inVarList,
                       time_dim='ocean_time', avgtype=avgtype, diag_obs_root='',
                       netcdf_format='', logger=logger)
    assert True


def test_create_clim_files():
    envDict = dict()
    log = CustomLogger(logging_level=logging.INFO, file=False, console=True)
    logger = log.logger

    dataset = RePlots.dataset(envDict, logger)
    dataset.start_daskclient()

    dout_paths = ['/datasets/GOM_9k_nature_copernicus']
    casename = 'cmpr_GOM_9k_nature_copernicus'
    start_date = '2010-02-01'
    end_date = '2010-04-01'
    date_pattern = '%Y-%m-%d'
    comp = 'ocn'
    suffix = 'hi'
    filep = '*'
    subdir = ''
    files = diagUtilsLib.getFileGlob(dout_paths=dout_paths, casename=casename, comp=comp, suffix=suffix, filep=filep,
                                     subdir=subdir, start_date=start_date, end_date=end_date, date_pattern=date_pattern)
    dataset.open_dataset(files)

    climdir = '/home/abishekg/PycharmProjects/RePlots/tests/out'
    inVarList = ['salt', 'temp']
    avglist = ['time', 'season', 'month', 'year']
    RePlots.ocn.createClimFiles(dataset=dataset, start_year='', stop_year='', climdir=climdir, case=casename, avglist=avglist,
                    inVarList=inVarList, diag_obs_root='', netcdf_format='', logger=logger)
    assert False
