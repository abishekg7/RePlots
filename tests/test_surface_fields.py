# import the diag baseclass module
from RePlots.ocn.ocn_diags_bc import OceanDiagnostic
import RePlots
# import the plot classes
from RePlots.ocn.plots import ocn_diags_plot_bc
from RePlots.ocn.plots import ocn_diags_plot_factory
import logging
import dask
from utils import CustomLogger
from utils import diagUtilsLib

def test_generate_plots():
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

    envDict['plot_dir'] = '/home/abishekg/PycharmProjects/RePlots/tests/out'
    envDict['fig_titlesize'] = 16
    envDict['fig_ticksize'] = 12

    plot = ocn_diags_plot_factory.oceanDiagnosticPlotFactory('model', 'PM_FLD2D')

    plot.check_prerequisites(envDict)

    tasks = plot.generate_plots(dataset, envDict)

    dask.compute(tasks, scheduler='processes', num_workers=4)

    assert False
