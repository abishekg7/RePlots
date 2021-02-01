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
    print('hello')
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
    assert False
