#!/usr/bin/env python3
"""Generate ocean climatology average files for a given CESM case 

This script provides an interface between:
1. the CESM case environment,
2. the ocean diagnostics environment defined in XML files,
3. the Python package for averaging operations in parallel

It is called from the run script and resides in the $CCSMROOT/postprocessing/cesm-env2
__________________________
Created on October 28, 2014 by CSEG <cseg@cgd.ucar.edu>
Updated on January 31, 2021 by agopal@tamu.edu
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

# import local modules for postprocessing
from utils import CustomLogger, cesmEnvLib, diagUtilsLib


# ============================================================
# buildOcnAvgList - build the list of averages to be computed
# ============================================================
def buildOcnAvgList(start_year, stop_year, tavgdir, logger):
    """buildOcnAvgList - build the list of averages to be computed
    by the pyAverager. Checks if the file exists or not already.

    Arguments:
    start_year (string) - starting year
    stop_year (string) - ending year
    tavgdir (string) - averages directory

    Return:
    avgList (list) - list of averages to be passed to the pyaverager
    """
    avgList = []
    #TODO: polish this

    # clean out the old working plot files from the workdir
    if env['CLEANUP_FILES'].upper() in ['T', 'TRUE']:
        cesmEnvLib.purge(env['WORKDIR'], '.*\.pro')

    # check if mavg file already exists
    avgFile = '{0}/mavg.{1}-{2}.nc'.format(tavgdir, start_year, stop_year)

    logger.debug('mavgFile = {0}'.format(avgFile))
    rc, err_msg = cesmEnvLib.checkFile(avgFile, 'read')
    if not rc:
        avgList.append('mavg:{0}:{1}'.format(start_year, stop_year))

    # check if tavg file already exists
    avgFile = '{0}/tavg.{1}-{2}.nc'.format(tavgdir, start_year, stop_year)
    logger.debug('tavgFile = {0}'.format(avgFile))
    rc, err_msg = cesmEnvLib.checkFile(avgFile, 'read')
    if not rc:
        avgList.append('tavg:{0}:{1}'.format(start_year, stop_year))

    logger.debug('exit buildOcnAvgList avgList = {0}'.format(avgList))
    return avgList


# ========================================================================
# callPyAverager - create the climatology files by calling the pyAverager
# ========================================================================
def callXarrayAverager(dataset, climdir, case_prefix, varlist, time_dim,
                       avgtype, diag_obs_root, netcdf_format, logger):
    """setup the pyAverager specifier class with specifications to create
       the climatology files in parallel.

       Arguments:
       dataset (dataset) - dataset object
       climdir (string) - output directory for climatology files
       case_prefix (string) - input filename prefix
       varlist (list) - list of variables. Note: an empty list implies all variables.
       time_dim (string) - time dimension to group by
       avgtype (string) - type of averaging (season, month, year) or time for tavg
       diag_obs_root (string) - OCNDIAG_DIAGOBSROOT machine dependent path to input data root
       netcdf_format (string) - OCNDIAG_netcdf_format one of ['netcdf', 'netcdf4', 'netcdf4c', 'netcdfLarge']
       nlev (integer) - Number of ocean vertical levels
       logger (logger) - logger object

    """

    wght = False
    valid_netcdf_formats = ['netcdf', 'netcdf4', 'netcdf4c', 'netcdfLarge']
    ncfrmt = 'netcdf'
    if netcdf_format in valid_netcdf_formats:
        ncfrmt = netcdf_format
    serial = False
    clobber = True
    date_pattern = 'yyyymm-yyyymm'
    suffix = 'nc'




    logger.debug('calling specification.create_specifier with following args')
    logger.debug('... out_directory = {0}'.format(climdir))
    logger.debug('... suffix = {0}'.format(suffix))
    logger.debug('... date_pattern = {0}'.format(date_pattern))
    logger.debug('... weighted = {0}'.format(wght))
    logger.debug('... ncformat = {0}'.format(ncfrmt))
    logger.debug('... varlist = {0}'.format(varlist))
    logger.debug('... serial = {0}'.format(serial))
    logger.debug('... clobber = {0}'.format(clobber))


    try:

        if avgtype == "time":
            logger.debug("calling mean")
            if not varlist:
                ds_clim = dataset.ds.mean('{0}'.format(time_dim))
            else:
                ds_clim = dataset.ds[varlist].mean('{0}'.format(time_dim))
        else:
            if not varlist:
                ds_clim = dataset.ds.groupby('{0}.{1}'.format(time_dim, avgtype)).mean(
                    '{0}'.format(time_dim))
            else:
                ds_clim = dataset.ds[varlist].groupby('{0}.{1}'.format(time_dim, avgtype)).mean('{0}'.format(time_dim))

        for ii in ds_clim.data_vars:
            if 'grid' in ds_clim[ii].attrs: del ds_clim[ii].attrs['grid']

        path = '{0}/{1}.{2}.nc'.format(climdir, case_prefix, avgtype)
        ds_clim.to_netcdf(path=path, mode='w', format='NETCDF4', compute=True)

    except Exception as error:
        print(str(error))
        traceback.print_exc()
        sys.exit(1)


# =========================================================================
# createClimFiles - create the climatology files by calling the pyAverager
# =========================================================================
def createClimFiles(dataset, start_year, stop_year, climdir, case, avglist,
                    inVarList, diag_obs_root, netcdf_format, logger):
    """setup the pyAverager specifier class with specifications to create
       the climatology files in parallel.

       Arguments:
       start_year (integer) - starting year for diagnostics
       stop_year (integer) - ending year for diagnositcs
       in_dir (string) - input directory with either history time slice or variable time series files
       htype (string) - 'series' or 'slice' depending on input history file type
       climdir (string) - output directory for averages
       case (string) - case name
       avglist (list) -
       inVarList (list) - if empty, then create climatology files for all vars, RHO, SALT and TEMP
       diag_obs_root (string) - OCNDIAG_DIAGOBSROOT machine dependent path to input data root
       netcdf_format (string) - OCNDIAG_netcdf_format one of ['netcdf', 'netcdf4', 'netcdf4c', 'netcdfLarge']
       nlev (integer) - Number of ocean vertical levels

    """
    # create the list of averages to be computed
    avgFileBaseName = '{0}/{1}.pop.h'.format(climdir, case)
    case_prefix = '{0}.pop.h'.format(case)
    averageList = []
    avgList = []

    # create the list of averages to be computed by the pyAverager
    #averageList = buildOcnAvgList(start_year, stop_year, climdir, logger.debug)

    # if the averageList is empty, then all the climatology files exist with all variables
    for avgtype in avglist:

        logger.debug('Calling xarray Averager with averageList = {0}'.format(avgList))
        logger.debug(' and inVarList = {0}'.format(inVarList))
        callXarrayAverager(dataset=dataset, climdir=climdir, case_prefix=case_prefix, varlist=inVarList,
                           time_dim='ocean_time', avgtype=avgtype, diag_obs_root=diag_obs_root,
                           netcdf_format=netcdf_format, logger=logger)
