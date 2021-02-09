#!/usr/bin/env python3
"""Generate ocn diagnostics from a CESM case

This script provides an interface between:
1. the CESM case environment,
2. the ocean diagnostics environment defined in XML files,
3. the popdiag zonal average and plotting packages

It is called from the run script and resides in the $SRCROOT/postprocessing/cesm-env2.
and assumes that the ocn_avg_generator.py script has been run to generate the
ocean climatology files for the given run.
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
import datetime
import errno
import glob
import itertools
import os
import re
import shutil
import subprocess
import traceback

try:
    import lxml.etree as etree
except:
    import xml.etree.ElementTree as etree

# import modules installed by pip into virtualenv
import jinja2

# import local modules for postprocessing
import logging
from utils import CustomLogger, diagUtilsLib

from cesm_utils import cesmEnvLib, processXmlLib

# import the diagnostics classes
import ocn_diags_bc
import ocn_diags_factory

# define global debug message string variable
debugMsg = ''



def setup_html(envDict):
    # define the templatePath
    templatePath = '{0}/diagnostics/diagnostics/ocn/Templates'.format(envDict['POSTPROCESS_PATH'])

    templateLoader = jinja2.FileSystemLoader(searchpath=templatePath)
    templateEnv = jinja2.Environment(loader=templateLoader)

    template_file = 'ocean_diagnostics.tmpl'
    template = templateEnv.get_template(template_file)

    # get the current datatime string for the template
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # set the template variables
    templateVars = {'casename': envDict['CASE'],
                    'tagname': envDict['CESM_TAG'],
                    'username': envDict['USER_NAME'],
                    'diag_dict': diag_dict,
                    'control_casename': envDict['CNTRLCASE'],
                    'start_year': envDict['YEAR0'],
                    'stop_year': envDict['YEAR1'],
                    'control_start_year': envDict['CNTRLYEAR0'],
                    'control_stop_year': envDict['CNTRLYEAR1'],
                    'today': now,
                    'tseries_start_year': envDict['TSERIES_YEAR0'],
                    'tseries_stop_year': envDict['TSERIES_YEAR1']
                    }

    # write the main index.html page to the top working directory
    main_html = template.render(templateVars)
    with open('{0}/index.html'.format(envDict['WORKDIR']), 'w') as index:
        index.write(main_html)

    debugMsg('Ocean diagnostics - Copying stylesheet', header=True, verbosity=2)
    shutil.copy2('{0}/Templates/diag_style.css'.format(envDict['POSTPROCESS_PATH']),
                 '{0}/diag_style.css'.format(envDict['WORKDIR']))

    debugMsg('Ocean diagnostics - Copying logo files', header=True, verbosity=2)
    if not os.path.exists('{0}/logos'.format(envDict['WORKDIR'])):
        os.mkdir('{0}/logos'.format(envDict['WORKDIR']))

    for filename in glob.glob(os.path.join('{0}/Templates/logos'.format(envDict['POSTPROCESS_PATH']), '*.*')):
        shutil.copy(filename, '{0}/logos'.format(envDict['WORKDIR']))

    # setup the unique OCNDIAG_WEBDIR output file
    env_file = '{0}/env_diags_ocn.xml'.format(envDict['PP_CASE_PATH'])
    key = 'OCNDIAG_WEBDIR'
    value = envDict['WORKDIR']
    ##web_file = '{0}/web_dirs/{1}.{2}-{3}'.format(envDict['PP_CASE_PATH'], key, main_comm.get_size(), main_comm.get_rank() )
    web_file = '{0}/web_dirs/{1}.{2}'.format(envDict['PP_CASE_PATH'], key,
                                             datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    try:
        diagUtilsLib.write_web_file(web_file, 'ocn', key, value)
    except:
        print('WARNING ocn_diags_generator unable to write {0}={1} to {2}'.format(key, value, web_file))


# ================================================
# setup_diags - get the list of diags to generate
# ================================================
def setup_diags(envDict):
    """setup_diags - read the XML directives on which diagnostics to create
       Arguments:
       envDict (dictionary) - environment dictionary

       Return:
       requested_diags (list) - list of diagnostics classes to be generated
       diag_dict (dictionary) - dictionary with URL link if it exists
    """
    requested_diags = list()
    diag_dict = dict()
    # ocean bgc being computed by IOMB
    #avail_diags = ['MODEL_VS_OBS', 'MODEL_VS_CONTROL', 'MODEL_TIMESERIES']
    avail_diags = ['MODEL']
    for diag in avail_diags:
        diag_dict[diag] = False
        for key, value in envDict.iteritems():
            if (diag == key and value.upper() in ['T', 'TRUE']):
                requested_diags.append(key)
                diag_dict[diag] = '{0}'.format(diag)
                if 'MODEL_VS_CONTROL' in diag:
                    diag_dict[diag] = '{0}_{1}'.format(diag, envDict['CNTRLCASE'])
                elif '_VS_' in diag:
                    diag_dict[diag] = '{0}'.format(diag)
                elif 'TIMESERIES' in diag:
                    diag_dict[diag] = '{0}'.format(diag)

    return requested_diags, diag_dict



# ======
# main
# ======

def createDiagPlots(dataset, diag_dir, case, avglist,
                    diag_obs_root, logger):
    """setup the environment for running the diagnostics in parallel.

    Calls 6 different diagnostics generation types:
    model vs. observation (optional BGC - ecosystem)
    model vs. control (optional BGC - ecosystem)
    model time-series (optional BGC - ecosystem)

    Arguments:
    options (object) - command line options
    main_comm (object) - MPI simple communicator object
    debugMsg (object) - vprinter object for printing debugging messages

    The env_diags_ocn.xml configuration file defines the way the diagnostics are generated.
    See (website URL here...) for a complete desciption of the env_diags_ocn XML options.
    """

    # initialize the environment dictionary
    envDict = dict()

    logger.debug('calling initialize_main')

    logger.debug('calling check_ncl_nco')
    diagUtilsLib.check_ncl_nco(envDict)

    sys.path.append(envDict['PATH'])

    # get list of diagnostics types to be created
    diag_list = list()
    num_of_diags = 0


    diag_list, diag_dict = setup_diags(envDict)

    num_of_diags = len(diag_list)
    if num_of_diags == 0:
        print('No ocean diagnostics specified. Please check the {0}/env_diags_ocn.xml settings.'.format(
            envDict['PP_CASE_PATH']))
        sys.exit(1)

    print('User requested diagnostics:')
    for diag in diag_list:
        print('  {0}'.format(diag))

    try:
        os.makedirs(envDict['WORKDIR'])
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            err_msg = 'ERROR: ocn_diags_generator.py problem accessing the working directory {0}'.format(
                envDict['WORKDIR'])
            raise OSError(err_msg)

    logger.debug('Ocean diagnostics - Creating main index.html page')

    # loop through the local_diag_list
    for requested_diag in diag_list:
        try:

            diag = ocn_diags_factory.oceanDiagnosticsFactory(requested_diag)

            # check the prerequisites for the diagnostics types
            logger.debug('Checking prerequisites for {0}'.format(diag.__class__.__name__))

            skip_key = '{0}_SKIP'.format(requested_diag)

            try:
                envDict = diag.check_prerequisites(envDict)
            except ocn_diags_bc.PrerequisitesError:
                print("Problem with check_prerequisites for '{0}' skipping!".format(requested_diag))
                envDict[skip_key] = True
            except RuntimeError as e:
                # unrecoverable error, bail!
                print(e)
                envDict['unrecoverableErrorOnMaster'] = True

            if envDict.has_key('unrecoverableErrorOnMaster'):
                raise RuntimeError

            # run the diagnostics type on each inter_comm
            if not envDict.has_key(skip_key):
                # set the shell env using the values set in the XML and read into the envDict across all tasks
                cesmEnvLib.setXmlEnv(envDict)
                # run the diagnostics
                envDict = diag.run_diagnostics(envDict)



        except ocn_diags_bc.RecoverableError as e:
            # catch all recoverable errors, print a message and continue.
            print(e)
            print("Skipped '{0}' and continuing!".format(requested_diag))
        except RuntimeError as e:
            # unrecoverable error, bail!
            print(e)
            return 1

    # update the env_diags_ocn.xml with OCNIAG_WEBDIR settings to be used by the copy_html utility


