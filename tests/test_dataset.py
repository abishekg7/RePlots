import RePlots
import logging
from utils import CustomLogger


def test_dataset():
    envDict = dict()

    #files = diagUtilsLib.getFileGlob(envDict['MODEL_DOUT_PATHS'], envDict['CASENAME'],
    #                                 envDict['YEAR0'], envDict['YEAR1'], 'ocn', envDict['OCN_SUFFIX'], file_pattern,
    #                                 envDict['MODELCASE_SUBDIR'])

    #dataset = RePlots.dataset(envDict)

    assert False


def test_start_daskclient():

    envDict = dict()

    log = CustomLogger(logging_level=logging.INFO, file=False, console=True)
    logger = log.logger

    dataset = RePlots.dataset(envDict)
    dataset.start_daskclient()

    print(dataset.client)
    assert True


def test_stop_daskclient():
    assert False


def test_open_dataset():
    envDict = dict()

    log = CustomLogger(logging_level=logging.INFO, file=False, console=True)
    logger = log.logger

    dataset = RePlots.dataset(envDict, logger)
    dataset.start_daskclient()

    files=['/datasets/GOM_9k_nature_copernicus/cmpr_GOM_9k_nature_copernicus.ocn.hi.2010-01-03_03:00:00.nc']
    dataset.open_dataset(files)

    print(dataset.ds)
    assert True

