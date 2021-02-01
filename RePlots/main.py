#!/usr/bin/env python3
"""Generate ocean climatology average files for a given CESM case 

This script provides an interface between:
1. the CESM case environment,
2. the ocean diagnostics environment defined in XML files,
3. the Python package for averaging operations in parallel

It is called from the run script and resides in the $CCSMROOT/postprocessing/cesm-env2
__________________________
Created on October 28, 2014

Author: CSEG <cseg@cgd.ucar.edu>
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

# import core python modules
import argparse
import getopt
import os
import re
import traceback
import logging
import RePlots as rp

# import local modules for postprocessing
from utils import CustomLogger, cesmEnvLib, diagUtilsLib


#=====================================================
# commandline_options - parse any command line options
#=====================================================
def commandline_options():
    """Process the command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='ocn_avg_generator: CESM wrapper python program for ocean climatology packages.')

    parser.add_argument('--backtrace', action='store_true',
                        help='show exception backtraces as extra debugging '
                        'output')

    parser.add_argument('--debug', nargs=1, required=False, type=bool, default=False,
                        help='debugging verbosity level output: 0 = none, 1 = minimum, 2 = maximum. 0 is default')

    parser.add_argument('--console', nargs=1, required=False, type=bool, default=False,
                        help='debugging verbosity level output: 0 = none, 1 = minimum, 2 = maximum. 0 is default')

    options = parser.parse_args()

    # check to make sure CASEROOT is a valid, readable directory
    if not os.path.isdir(options.caseroot[0]):
        err_msg = ' ERROR: ocn_avg_generator.py invalid option --caseroot {0}'.format(options.caseroot[0])
        raise OSError(err_msg)

    return options


#============================================
# initialize_envDict - initialization envDict
#============================================
def initialize_envDict(envDict,  logger):
    """initialize_main - initialize settings on rank 0 
    
    Arguments:
    envDict (dictionary) - environment dictionary
    logger.debug (object) - vprinter object for printing debugging messages
    standalone (boolean) - indicate stand-alone post processing caseroot

    Return:
    envDict (dictionary) - environment dictionary
    """

    caseroot = os.getcwd()

    # setup envDict['id'] = 'value' parsed from the CASEROOT/[env_file_list] files
    env_file_list =  ['../scripts/env_postprocess.xml']
    envDict = cesmEnvLib.readXML(caseroot, env_file_list)

    # debug print out the envDict
    logger.debug('envDict after readXML = {0}'.format(envDict), verbosity=2)

    # refer to the caseroot that was specified on the command line instead of what
    # is read in the environment as the caseroot may have changed from what is listed
    # in the env xml
    envDict['CASEROOT'] = caseroot

    # add the os.environ['PATH'] to the envDict['PATH']
    envDict['OCNDIAG_PATH'] += os.pathsep + os.environ['PATH']

    # initialize varLists
    envDict['MODEL_VARLIST'] = []
    if len(envDict['OCNDIAG_PYAVG_MODELCASE_VARLIST']) > 0:
        envDict['MODEL_VARLIST'] = envDict['OCNDIAG_PYAVG_MODELCASE_VARLIST'].split(',')

    # Initialize Dout list
    envDict['MODEL_DOUT_PATHS'] = []
    if len(envDict['DOUT_PATHS']) > 0:
        envDict['MODEL_DOUT_PATHS'] = envDict['DOUT_PATHS'].split(',')


    #envDict['CNTRL_VARLIST'] = []
    #if len(envDict['OCNDIAG_PYAVG_CNTRLCASE_VARLIST']) > 0:
    #    envDict['CNTRL_VARLIST'] = envDict['OCNDIAG_PYAVG_CNTRLCASE_VARLIST'].split(',')
    
    # strip the OCNDIAG_ prefix from the envDict entries before setting the 
    # enviroment to allow for compatibility with all the diag routine calls
    envDict = diagUtilsLib.strip_prefix(envDict, 'OCNDIAG_')

    return envDict

#======
# main
#======

def main(options, logger):
    """setup the environment for running the pyAverager in parallel. 

    Arguments:
    options (object) - command line options
    logger (object) - Logger object for printing debugging messages

    The env_diags_ocn.xml configuration file defines the way the diagnostics are generated. 
    See (website URL here...) for a complete desciption of the env_diags_ocn XML options.
    """

    # initialize the environment dictionary
    envDict = dict()

    logger.debug('calling initialize_envDict')
    envDict = initialize_envDict(envDict, logger, options.standalone)

    # generate the climatology files used for all plotting types

    suffix = 'pop.h.*.nc'
    file_pattern = '.*\.pop\.h\.\d{4,4}-\d{2,2}\.nc'

    # files = diagUtilsLib.getFileGlob(envDict['MODEL_DOUT_PATHS'], envDict['CASENAME'],
    #        envDict['YEAR0'], envDict['YEAR1'], 'ocn', envDict['OCN_SUFFIX'], file_pattern, envDict['MODELCASE_SUBDIR'])
    # envDict['YEAR0'] = start_year
    # envDict['YEAR1'] = stop_year
    # envDict['in_dir'] = in_dir
    # envDict['htype'] = htype

    sys.path.append(envDict['PATH'])

    dataset = rp.dataset(envDict)












    try:

        logger.debug('calling createClimFiles for model and timeseries')

        createClimFiles(dataset, envDict['YEAR0'], envDict['YEAR1'], envDict['in_dir'],
                        envDict['htype'], envDict['TAVGDIR'], envDict['CASE'], 
                        envDict['MODEL_VARLIST'], envDict['DIAGOBSROOT'],
                        envDict['netcdf_format'], int(envDict['VERTICAL']), logger)
    except Exception as error:
        print(str(error))
        traceback.print_exc()
        sys.exit(1)



    # check that the necessary control climotology files exist
    if envDict['MODEL_VS_CONTROL'].upper() == 'TRUE':

        if main_comm.is_manager():
            logger.debug('calling checkHistoryFiles for control case')
            suffix = 'pop.h.*.nc'
            file_pattern = '.*\.pop\.h\.\d{4,4}-\d{2,2}\.nc'
            start_year, stop_year, in_dir, htype, firstHistoryFile = diagUtilsLib.checkHistoryFiles(
                envDict['CNTRLCASE_INPUT_TSERIES'], envDict['CNTRLCASEDIR'], envDict['CNTRLCASE'], 
                envDict['CNTRLYEAR0'], envDict['CNTRLYEAR1'], 'ocn', suffix, file_pattern,
                envDict['CNTRLCASE_SUBDIR'])
            envDict['CNTRLYEAR0'] = start_year
            envDict['CNTRLYEAR1'] = stop_year
            envDict['cntrl_in_dir'] = in_dir
            envDict['cntrl_htype'] = htype

        main_comm.sync()
        envDict = main_comm.partition(data=envDict, func=partition.Duplicate(), involved=True)
        main_comm.sync()

        if main_comm.is_manager():
            logger.debug('before createClimFiles call for control')
            logger.debug('...CNTRLYEAR0 = {0}'.format(envDict['CNTRLYEAR0']))
            logger.debug('...CNTRLYEAR1 = {0}'.format(envDict['CNTRLYEAR1']))
            logger.debug('...cntrl_in_dir = {0}'.format(envDict['cntrl_in_dir']))
            logger.debug('...cntrl_htype = {0}'.format(envDict['cntrl_htype']))
            logger.debug('...CNTRLTAVGDIR = {0}'.format(envDict['CNTRLTAVGDIR']))
            logger.debug('...CNTRLCASE = {0}'.format(envDict['CNTRLCASE']))
            logger.debug('...CNTRLCASE_INPUT_TSERIES = {0}'.format(envDict['CNTRLCASE_INPUT_TSERIES']))
            logger.debug('...varlist = {0}'.format(envDict['CNTRL_VARLIST']))
            logger.debug('calling createClimFiles for control')
        
        # don't create timeseries averages for the control case so set to False and set the
        # tseries_start_year and tseries_stop_year to 0
        try:
            createClimFiles(envDict['CNTRLYEAR0'], envDict['CNTRLYEAR1'], envDict['cntrl_in_dir'],
                            envDict['cntrl_htype'], envDict['CNTRLTAVGDIR'], envDict['CNTRLCASE'], 
                            False, envDict['CNTRL_VARLIST'], 0, 0, envDict['DIAGOBSROOT'],
                            envDict['netcdf_format'], int(envDict['VERTICAL']), 
                            envDict['TIMESERIES_OBSPATH'], main_comm, logger.debug)
        except Exception as error:
            print(str(error))
            traceback.print_exc()
            sys.exit(1)

#===================================


if __name__ == "__main__":

    # get commandline options
    options = commandline_options()

    log_level = logging.INFO
    if options.debug:
        log_level = logging.DEBUG

    # initialize logger object
    log = CustomLogger(logging_level=log_level, file=True, console=options.console)
    logger = log.logger

    try:
        status = main(options, logger)
        log.logger.debug('Finished')
        print('*************************************************************')
        print(' Successfully completed generating ocean climatology averages')
        print('*************************************************************')
        sys.exit(status)
        
    except Exception as error:
        print(str(error))
        if options.backtrace:
            traceback.print_exc()
        sys.exit(1)

