from utils import diagUtilsLib

def test_get_file_glob():
    dout_paths = ['/datasets/GOM_9k_nature_copernicus']
    casename = 'cmpr_GOM_9k_nature_copernicus'
    start_date = '2010-02-01'
    end_date = '2010-06-07'
    date_pattern = '%Y-%m-%d'
    comp = 'ocn'
    suffix = 'hi'
    filep = '*'
    subdir = ''

    files = diagUtilsLib.getFileGlob(dout_paths=dout_paths, casename=casename, comp=comp, suffix=suffix, filep=filep,
                                     subdir=subdir, start_date=start_date, end_date=end_date, date_pattern=date_pattern)

    for file in files:
        print(file)

    #import re

   # pattern_date_time = "([0 - 9]{4}-[0-9]{2}-[0-9]{2})"
    #for file in files:
    #    match = re.match('([0-9]{4}-[0-9]{2}-[0-9]{2})', file)
    #    if match is not None:
    #        group = match.group()
    #        date = group[0]
    #        print(date)

    #if z:
    #    print((z.groups()))


    assert True
