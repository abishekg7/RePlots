#!/usr/bin/env python2
"""
This module provides utility functions for the diagnostics wrapper python scripts.
__________________________
Created on Apr 01, 2015

@author: NCAR - CSEG
"""

import errno
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import datetime
from utils import cesmEnvLib

#=======================================================================
# check_ncl_nco - check if NCL and NCO/ncks are installed and accessible
#=======================================================================
def check_ncl_nco(envDict):
    """ check that NCL and NCO/ncks are installed and accessible

    Arguments:
    envDict (dictionary) - environment dictionary
    """
    #TODO: convert this to check xarray/dask?
    cmd = ['ncl', '-V']
    try:
        pipe = subprocess.Popen(cmd, env=envDict)
        pipe.wait()
    except OSError as e:
        print('NCL is required to run the ocean diagnostics package')
        print('ERROR: {0} call to "{1}" failed with error:'.format('check_ncl_nco', ' '.join(cmd)))
        print('    {0} - {1}'.format(e.errno, e.strerror))
        sys.exit(1)

    cmd = ['ncks', '--version']
    try:
        pipe = subprocess.Popen(cmd , env=envDict)
        pipe.wait()
    except OSError as e:
        print('NCO ncks is required to run the ocean diagnostics package')
        print('ERROR: {0} call to "{1}" failed with error:'.format('check_ncl_nco', ' '.join(cmd)))
        print('    {0} - {1}'.format(e.errno, e.strerror))
        sys.exit(1)


#============================================
# strip_prefix - strip the prefix from the id
#============================================
def strip_prefix(indict, prefix):
    """strip_prefix - Read the indict and strip off the leading prefix from the id element (key).
    
    Arguments:
    indict (dictionary) - input with OCNDIAG_ from the id element
    prefix (string) - prefix string to be stripped

    Return:
    outdict (dictionary) with prefix stripped from the id element
    """
    outdict = dict()
#    i = len(prefix) + 1;
    i = len(prefix);

    for k,v in indict.iteritems():
        if k.startswith(prefix):
            outdict[k[i:]] = v
#            outdict[k[8:]] = v
        else:
            outdict[k] = v

    return outdict


#=============================================================
# filter_pick - return filenames that match a pattern in a list
#=============================================================
def filter_pick(files, regex):
    return [m.group(0) for f in files for m in [regex.search(f)] if m]


#=============================================================
# filter_pick - return filenames that match a pattern in a list
#=============================================================
def filter_dates(files, si, ei, sdate, edate, date_pattern):
    date_regex = "%Y-%m-%d"
    default_regex = "%Y-%m-%d"
    start_date = datetime.datetime.strptime(sdate, date_pattern)
    end_date = datetime.datetime.strptime(edate, date_pattern)


    list = []

    for file in files:
        split_str = file[si:ei]
        date = datetime.datetime.strptime(split_str, date_regex)

        if date >= start_date and date <= end_date:
            list.append(file)

    return list

#======================================
# check_series_years - checks to see if the number of time slices in the file
#                      match the date string
#======================================
def check_series_years(hfstart_year, hfstart_month, hfstop_year, hfstop_month, hfile):

    """ check_series_years - checks to see if the number of time slices in the file match the date string
    """

    # TODO: Replace with an equivalent xarray function

    #import Nio

    # Get the count for how many slices the filename says there should be
    fname_slice_count = ((12 - int(hfstart_month))+1)+((int(hfstop_year) - int(hfstart_year)) * 12) - (12 - int(hfstop_month))

    # Get the actually count within the file
    #f = Nio.open_file(hfile)
    #file_slice_count = f.dimensions['time']
    #f.close()

    # Return True if they counts match, False if they do not match
    #return  file_slice_count == fname_slice_count

#======================================
# checkXMLyears - check run year bounds
#======================================
def checkXMLyears(hfstart_year, hfstop_year, rstart_year, rstop_year):
    """checkXMLyears - check that the years requested in the XML fall within the
    bounds of the actual history files available

    Arguments:
    hfstart_year (string) - model job start year
    hfstop_year (string) -  model job end year
    rstart_year (string) - requested start year for diagnostics
    rstop_year (string) - requested stop year for diagnostics

    Return:
    start_year (string) - for average calculations
    stop_year (string) - for average calculations
    """
    # make sure the requested years from the XML are in range with the actual history files
    #if not int(hfstart_year) <= int(rstart_year) <= int(hfstop_year):
    #    err_msg = 'ERROR: diagUtilsLib.checkXMLyears requested XML YEAR0 = {0} does not fall within range of actual available model history file years: {1}-{2}'.format(rstart_year, hfstart_year, hfstop_year)
    #    raise OSError(err_msg)
#
#    if not int(hfstart_year) <= int(rstop_year) <= int(hfstop_year):
#        err_msg = 'ERROR: diagUtilsLib.checkXMLyears requested XML YEAR1 = {0} does not fall within range of actual available model history file years: {1}-{2}'.format(rstop_year, hfstart_year, hfstop_year)
#        raise OSError(err_msg)

#    if int(rstop_year) < int(rstart_year):
#        err_msg = 'ERROR: diagUtilsLib.checkXMLyears requested XML YEAR1 = {0} is less than YEAR0 = {1}'.format(rstop_year, rstart_year)
#        raise OSError(err_msg)

    start_year = rstart_year
    stop_year = rstop_year

    return (start_year, stop_year)


#========================================
# checkHistoryFiles - check history files
#========================================
def checkHistoryFiles(tseries, dout_s_root, case, rstart_year, rstop_year, comp, suffix, filep, subdir):
    """checkHistoryFiles - check if variable history time-series 
    files or history time-slice files exist
    in the DOUT_S_ROOT location. Then check the actual run files 
    to get the start and stop years to compare against
    the XML specified YEAR0 and YEAR1. The OMWG diags 
    package only works with monthly average history files
    to generate annual mean history files. 

    Arguments:
    tseries (boolean) - corresponds to XML variable GENERATE_TIMESERIES
    dout_s_root (string) - corresponds to XML variable DOUT_S_ROOT disk archive location
    case (string) - corresponds to XML variable CASE name
    rstart_year (string) - requested diagnostics model start year from XML env_diags_ocn.xml
    rstop_year (string) - requested diagnostics model stop year from XML env_diags_ocn.xml
    comp (string) - component one of atm, ice, lnd, ocn, or rof
    suffix (string) - suffix for history files
    filep (string) - file pattern to match filenames
    subdir (string) - subdir location of input history files, slice or series

    Return:
    start_year (string) - start year as defined by the history files
    stop_year (string) - last year as defined by the history files
    in_dir (string) - directory location of history files
    hType (string) - history file type (slice or series)
    """
    if tseries.upper() in ['T','TRUE'] :
        htype = 'series'
    else :
        htype = 'slice'

    # make sure subdir does not include a trailing "/"
    if subdir.endswith('/'):
        subdir = subdir[:-1]
    in_dir = '{0}/{1}/{2}'.format(dout_s_root, comp, subdir)

    # check the in_dir directory exists 
    if not os.path.isdir(in_dir):
        err_msg = 'ERROR: diagUtilsLib.checkHistoryFiles {0} directory is not available.'.format(in_dir)
        raise OSError(err_msg)

    # get the file paths and formats - TO DO may need to get this from namelist var or env_archive
    files = '{0}.{1}'.format(case, suffix)
    fformat = '{0}/{1}*'.format(in_dir, files)
   
    if htype == 'slice':
        # get the first and last years from the first and last monthly history files
        allHfiles = sorted(glob.glob(fformat))
        if len(allHfiles) > 0:
            pattern = re.compile(filep)
            hfiles = filter_pick(allHfiles, pattern)

            if hfiles:
                # the first element of the hfiles list has the start year
                tlist = hfiles[0].split('.')
                slist = tlist[-2].split('-')
                hfstart_year = slist[0]
                hfstart_month = slist[1]

                # the last element of the hfiles list has the stop year
                tlist = hfiles[-1].split('.')
                slist = tlist[-2].split('-')
                hfstop_year = slist[0]
                hfstop_month = slist[1]
            else:
                print('ERROR diagUtilsLib.checkHistoryFiles: No history time slice files found matching pattern = {0}'.format(pattern))
                sys.exit(1)
        else:
            print('ERROR diagUtilsLib.checkHistoryFiles: No history time slice files found matching format {0}'.format(fformat))
            sys.exit(1)

    elif htype == 'series':
        hfiles = sorted(glob.glob(fformat))
        # the first variable time series file has the stop and start years
        if len(hfiles) > 0:
            tlist = hfiles[0].split('.')
            slist = tlist[-2].split('-')
            hfstart_year = slist[0][:4]
            hfstart_month = slist[0][4:6]
            hfstop_year = slist[1][:4]
            hfstop_month = slist[1][4:6]

            if not check_series_years(hfstart_year, hfstart_month, hfstop_year, hfstop_month, hfiles[0]):
                print('ERROR: diagUtilsLib.checkHistoryFiles Time series filename does not match file time slice count.')
                sys.exit(1)
        else:
            print('ERROR diagUtilsLib.checkHistoryFiles: No history time series files found matching format {0}'.format(fformat))
            sys.exit(1)

    # check if the XML YEAR0 and YEAR1 are within the actual start_year and stop_year bounds 
    # defined by the actual history files
    start_year, stop_year = checkXMLyears(hfstart_year, hfstop_year, rstart_year, rstop_year)

    return (start_year, stop_year, in_dir, htype, hfiles[0])


# ========================================
# checkHistoryFiles - check history files
# ========================================
def getFileGlob(dout_paths, casename, comp, suffix, filep, subdir, start_date, end_date, date_pattern):
    """checkHistoryFiles - check if variable history time-series
    files or history time-slice files exist
    in the DOUT_S_ROOT location. Then check the actual run files
    to get the start and stop years to compare against
    the XML specified YEAR0 and YEAR1. The OMWG diags
    package only works with monthly average history files
    to generate annual mean history files.

    Arguments:
    dout_paths (list string) - corresponds to XML variable DOUT_S_ROOT disk archive location
    casename (string) - corresponds to XML variable CASE name
    rstart_year (string) - requested diagnostics model start year from XML env_diags_ocn.xml
    rstop_year (string) - requested diagnostics model stop year from XML env_diags_ocn.xml
    comp (string) - component one of atm, ice, lnd, ocn, or rof
    suffix (string) - suffix for history files
    filep (string) - file pattern to match filenames
    subdir (string) - subdir location of input history files, slice or series

    Return:
    start_year (string) - start year as defined by the history files
    stop_year (string) - last year as defined by the history files
    in_dir (string) - directory location of history files
    hType (string) - history file type (slice or series)
    """

    files_out = []
    # make sure subdir does not include a trailing "/"
    if subdir.endswith('/'):
        subdir = subdir[:-1]



    for dout_path in dout_paths:

        #in_dir = '{0}/{1}/{2}'.format(dout_path, comp, subdir)
        in_dir = '{0}/{1}/'.format(dout_path, subdir)
        print('in_dir:{0}'.format(in_dir))
        # check the in_dir directory exists
        if not os.path.isdir(in_dir):
            err_msg = 'ERROR: diagUtilsLib.getFileGlob {0} directory is not available.'.format(in_dir)
            raise OSError(err_msg)

        # get the file paths and formats - TO DO may need to get this from namelist var or env_archive
        files = '{0}.{1}.{2}'.format(casename, comp, suffix)
        fformat = '{0}/{1}*'.format(in_dir, files)


        #if htype == 'slice':
        # get the first and last years from the first and last monthly history files
        allHfiles = sorted(glob.glob(fformat))

        if len(allHfiles) > 0:
            #TODO: figure out pattern and regular expressions
            #pattern = re.compile(filep)
            #hfiles = filter_pick(allHfiles, pattern)
            #allHfiles = list(filter(lambda x: x[starti:endi] > '20100301', allHfiles))

            # TODO: does this need to be more generic?
            starti = len(os.path.dirname(allHfiles[0])) + 2 + len(files)
            endi = starti + 10
            allHfiles = filter_dates(allHfiles, starti, endi, start_date, end_date, date_pattern)
            files_out.extend(allHfiles)
            #if hfiles:
            #    files_out.extend(hfiles)
            #else:
            #    print(
            #        'ERROR diagUtilsLib.checkHistoryFiles: No history time slice files found matching pattern = {0}'.format(
            #            pattern))
            #    sys.exit(1)
        else:
            print('ERROR diagUtilsLib.checkHistoryFiles: No history time slice files found matching format {0}'.format(
                fformat))
            sys.exit(1)

    # check if the XML YEAR0 and YEAR1 are within the actual start_year and stop_year bounds
    # defined by the actual history files
    #start_year, stop_year = checkXMLyears(hfstart_year, hfstop_year, rstart_year, rstop_year)

    return files_out


#==============================================================================
# write_web_file - write out the final diagnostics directory
#==============================================================================
def write_web_file(out_file, comp, key, value):
    """ create a new output file, if it doesn't exist, with directory location
    for the finished diagnostics plots
    """
    # check if out_file already exists or not
    with open(out_file, 'a+') as f:
        f.write('{0}:{1}\n'.format(key, value))
    f.close()



#==========================================================
# create_plot_dat - create the plot.dat file in the workdir
#==========================================================
def create_plot_dat(workdir, xyrange, depths):
    """create plot.dot  file in the workdir

    Arguments:
    workdir (string) - work directory for plots
    xyrange (string) - env['XYRANGE']
    depths (string) - env['DEPTHS']
    """
    rc, err_msg = cesmEnvLib.checkFile('{0}/plot.dat'.format(workdir), 'read')
    if not rc:
        file = open('{0}/plot.dat'.format(workdir),'w')
        file.write( xyrange + '\n')
        numdepths = len(depths.split(','))
        file.write( str(numdepths) + '\n')
        file.write( depths + '\n')
        file.close()

    return 0


#================================================================
# createLinks - create symbolic links between tavgdir and workdir
#================================================================
def createLinks(start_year, stop_year, tavgdir, workdir, case, control):
    """createLinks - create symbolic links between tavgdir and workdir

    Arguments:
    start_year (string) - starting year
    stop_year (string) - ending year
    tavgdir (string) - output directory for averages
    workdir (string) - working directory for diagnostics
    case (string) - case name
    control (boolean) - indicates if this is a control run or not which will change the mavg and tavg filenames
    """
    padding = 4
    avgFileBaseName = '{0}/{1}.pop.h'.format(tavgdir,case)
    case_prefix = '{0}.pop.h'.format(case)

    # prepend the years with 0's for some of the plotting routines
    zstart_year = start_year.zfill(padding)
    zstop_year = stop_year.zfill(padding)

    # check if this is a control run or not
    cntrl = ''
    if control:
        cntrl = 'cntrl.'

    # link to the mavg file for the za and plotting routines
    mavgFileBase = 'mavg.{0}.{1}.{2}nc'.format(zstart_year, zstop_year, cntrl)
    avgFile = '{0}/mavg.{1}-{2}.nc'.format(tavgdir, zstart_year, zstop_year)
    rc, err_msg = cesmEnvLib.checkFile(avgFile, 'read')
    if rc:
        zmavgFile = '{0}/mavg.{1}.{2}.{3}nc'.format(workdir, zstart_year, zstop_year, cntrl)
        mavgFile = '{0}/mavg.{1}.{2}.{3}nc'.format(workdir, start_year, stop_year, cntrl)

        rc1, err_msg1 = cesmEnvLib.checkFile(zmavgFile, 'read')
        if not rc1:
            os.symlink(avgFile, zmavgFile)

        rc1, err_msg1 = cesmEnvLib.checkFile(mavgFile, 'read')
        if not rc1:
            os.symlink(avgFile, mavgFile)
    else:
        raise OSError(err_msg)

    # link to the tavg file
    tavgFileBase = 'tavg.{0}.{1}.{2}nc'.format(zstart_year, zstop_year, cntrl)
    avgFile = '{0}/tavg.{1}-{2}.nc'.format(tavgdir, zstart_year, zstop_year)
    rc, err_msg = cesmEnvLib.checkFile(avgFile, 'read')
    if rc:
        ztavgFile = '{0}/tavg.{1}.{2}.{3}nc'.format(workdir, zstart_year, zstop_year, cntrl)
        tavgFile = '{0}/tavg.{1}.{2}.{3}nc'.format(workdir, start_year, stop_year, cntrl)

        rc1, err_msg1 = cesmEnvLib.checkFile(ztavgFile, 'read')
        if not rc1:
            os.symlink(avgFile, ztavgFile)

        rc1, err_msg1 = cesmEnvLib.checkFile(tavgFile, 'read')
        if not rc1:
            os.symlink(avgFile, tavgFile)
    else:
        raise OSError(err_msg)

    # link to all the annual history files 
    year = int(start_year)
    while year <= int(stop_year):
        # check if file already exists before appending to the avgList
        syear = str(year)
        zyear = syear.zfill(padding)
        avgFile = '{0}.{1}.nc'.format(avgFileBaseName, zyear)
        rc, err_msg = cesmEnvLib.checkFile(avgFile, 'read')
        if rc:
            workAvgFile = '{0}/{1}.{2}.nc'.format(workdir, case_prefix, zyear)
            rc1, err_msg1 = cesmEnvLib.checkFile(workAvgFile, 'read')
            if not rc1:
                os.symlink(avgFile, workAvgFile)
        year += 1

    return mavgFileBase, tavgFileBase

#======================================================================
# create a single symbolic link to a given file checking the file first
#======================================================================
def createSymLink(sourceFile, linkFile):
    """ create a symbolic link between the sourceFile and the linkFile
    """
    # check if the sourceFile exists
    rc, err_msg = cesmEnvLib.checkFile(sourceFile, 'read')
    if not rc:
# these should be raise RuntimeError instead of OSError
        raise RuntimeError(err_msg)

    # check if the linkFile exists and is readable
    rc, err_msg = cesmEnvLib.checkFile(linkFile, 'read')
    if not rc:
        try:
            os.symlink(sourceFile, linkFile)
        except Exception as e:
            print('...createSymLink error = {0}'.format(e))
            raise OSError(e)
    return

#================================================================
# TODO checkAvgFiles - check that the climotology average files exist
#================================================================
def checkAvgFiles(filelist):
    """ check if the climatology files exist in the list of files passed in
    """
    rc = True
    return rc
