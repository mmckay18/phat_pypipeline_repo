#! /usr/bin/env python

"""Ingests raw DOLPHOT output (an unzipped .phot file) and converts it
to a dataframe, which is then optionally written to an HDF5 file.
Column names are read in from the accompanying .phot.columns file.

Authors
-------
    Meredith Durbin, February 2018

Use
---
    This script is intended to be executed from the command line as
    such:
    ::
        python ingest_dolphot.py ['filebase'] ['--to_hdf'] ['--full']
    
    Parameters:
    (Required) [filebase] - Path to .phot file, with or without .phot extension.
    (Optional) [--to_hdf] - Whether to write the dataframe to an HDF5 
    file. Default is True.
    (Optional) [--full] - Whether to use the full set of columns (photometry of 
    individual exposures). Default is False.
"""

# Original script by Shellby Albrecht
# Modified and by Myles McKay
import wpipe as wp
import dask.dataframe as dd
import numpy as np
import os
import pandas as pd
import traceback
from astropy.io import fits
from astropy.wcs import WCS
from pathlib import Path



def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="dolphot_done", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("processing phot file...")
    my_config = my_job.config
    my_target = my_job.target
    this_event = my_job.firing_event
    my_job.logprint(this_event)
    my_job.logprint(this_event.options)
    my_config = my_job.config
    logpath = my_config.logpath
    procpath = my_config.procpath

# global photometry values
# first 11 columns in raw dolphot output
global_columns = ['ext','chip','x','y','chi_gl','snr_gl','sharp_gl', 
                  'round_gl','majax_gl','crowd_gl','objtype_gl']

# dictionary mapping text in .columns file to column suffix
colname_mappings = {
    'counts,'                            : 'count',
    'sky level,'                         : 'sky',
    'Normalized count rate,'             : 'rate',
    'Normalized count rate uncertainty,' : 'raterr',
    'Instrumental VEGAMAG magnitude,'    : 'vega',
    'Transformed UBVRI magnitude,'       : 'trans',
    'Magnitude uncertainty,'             : 'err',
    'Chi,'                               : 'chi',
    'Signal-to-noise,'                   : 'snr',
    'Sharpness,'                         : 'sharp',
    'Roundness,'                         : 'round',
    'Crowding,'                          : 'crowd',
    'Photometry quality flag,'           : 'flag',
}

def cull_photometry(df, filter_detectors, snrcut=4.,
                    cut_params={'irsharp'   : 0.15, 'ircrowd'   : 2.25,
                                'uvissharp' : 0.15, 'uviscrowd' : 1.30,
                                'wfcsharp'  : 0.20, 'wfccrowd'  : 2.25}):
    """Add 'ST' and 'GST' flag columns based on stellar parameters.

    TODO:
        - Allow for modification by command line
        - Generalize to more parameters?
        - Allow to interact with perl...?

    Inputs
    ------
    df : DataFrame
        table read in by read_dolphot
    filter_detectors : list of strings
        list of detectors + filters in 'detector-filter' format,
        ex. 'WFC-F814W'
    snrcut : scalar, optional
        minimum signal-to-noise ratio for a star to be flagged as 'ST'
        default: 4.0
    cut_params : dict
        dictionary of parameters to cut on, with keys in '<detector><quantity>'
        format, and scalar values.

    Returns
    -------
    df : DataFrame
        table read in by read_dolphot, with ST and GST columns added
        (name format: '<filter>_(g)st')
    """
    for filt in filter_detectors:
        d, f = filt.lower().split('-') # split into detector + filter
        try:
            print('Making ST and GST cuts for {}'.format(f))
            # make boolean arrays for each set of culling parameters
            snr_condition = df.loc[:,'{}_snr'.format(f)] > snrcut
            sharp_condition = df.loc[:,'{}_sharp'.format(f)]**2 < cut_params['{}sharp'.format(d)]
            crowd_condition = df.loc[:,'{}_crowd'.format(f)] < cut_params['{}crowd'.format(d)]
            # add st and gst columns
            df.loc[:,'{}_st'.format(f)] = (snr_condition & sharp_condition).astype(bool)
            df.loc[:,'{}_gst'.format(f)] = (df['{}_st'.format(f)] & crowd_condition).astype(bool)
            print('Found {} out of {} stars meeting ST criteria for {}'.format(
                df.loc[:,'{}_st'.format(f)].sum(), df.shape[0], f))
            print('Found {} out of {} stars meeting GST criteria for {}'.format(
                df.loc[:,'{}_gst'.format(f)].sum(), df.shape[0], f))
        except Exception:
            df.loc[:,'{}_st'.format(f)] = np.nan
            df.loc[:,'{}_gst'.format(f)] = np.nan
            print('Could not perform culling for {}.\n{}'.format(f, traceback.format_exc()))
    return df

def make_header_table(fitsdir, search_string='*fl?.chip?.fits'):
    """Construct a table of key-value pairs from FITS headers of images
    used in dolphot run. Columns are the set of all keywords that appear
    in any header, and rows are per image.

    Inputs
    ------
    fitsdir : Path 
        directory of FITS files
    search_string : string or regex patter, optional
        string to search for FITS images with. Default is
        '*fl?.chip?.fits'

    Returns
    -------
    df : DataFrame
        A table of header key-value pairs indexed by image name.
    """
    keys = []
    headers = {}
    fitslist = list(fitsdir.glob(search_string))
    if len(fitslist) == 0: # this shouldn't happen
        print('No fits files found in {}!'.format(fitsdir))
        return pd.DataFrame()
    # get headers from each image
    for fitsfile in fitslist:
        fitsname = fitsfile.name # filename without preceding path
        head = fits.getheader(fitsfile, ignore_missing_end=True)
        headers.update({fitsname:head})
        keys += [k for k in head.keys()]
    unique_keys = np.unique(keys).tolist()
    remove_keys = ['COMMENT', 'HISTORY', '']
    for key in remove_keys:
        if key in unique_keys:
            unique_keys.remove(key)
    # construct dataframe
    df = pd.DataFrame(columns=unique_keys)
    for fitsname, head in headers.items():
        row = pd.Series(dict(head.items()))
        df.loc[fitsname.split('.fits')[0]] = row.T
    # I do not know why dask is so bad at mixed types
    # but here is my hacky solution
    try:
        df = df.infer_objects()
    except Exception:
        print("Could not infer objects")
    df_obj = df.select_dtypes(['object'])
    # iterate over columns and force types
    for c in df_obj:
        dtype = pd.api.types.infer_dtype(df[c], skipna=True)
        if dtype == 'string':
            df.loc[:,c] = df.loc[:,c].astype(str)
        elif dtype in ['float','mixed-integer-float']:
            df.loc[:,c] = df.loc[:,c].astype(float)
        elif dtype == 'integer':
            df.loc[:,c] = df.loc[:,c].astype(int)
        elif dtype == 'boolean':
            df.loc[:,c] = df.loc[:,c].astype(bool)
        else:
            print('Unrecognized datatype "{}" for column {}; coercing to string'.format(dtype, c))
            df.loc[:,c] = df.loc[:,c].astype(str)
    return df

def name_columns(colfile):
    """Construct a table of column names for dolphot output, with indices
    corresponding to the column number in dolphot output file.

    Inputs
    ------
    colfile : path
        path to file containing dolphot column descriptions

    Returns
    -------
    df : DataFrame
        A table of column descriptions and their corresponding names.
    filters : list
        List of filters included in output
    """
    df = pd.DataFrame(data=np.loadtxt(colfile, delimiter='. ', dtype=str),
                          columns=['index','desc']).drop('index', axis=1)
    df = df.assign(colnames='')
    # set first 11 column names
    df.loc[:10,'colnames'] = global_columns
    # set rest of column names
    filters_all = []
    for k, v in colname_mappings.items():
        indices = df[df.desc.str.find(k) != -1].index
        desc_split = df.loc[indices,'desc'].str.split(", ")
        # get indices for columns with combined photometry
        indices_total = indices[desc_split.str.len() == 2]
        # get indices for columns with single-frame photometry
        indices_indiv = indices[desc_split.str.len() > 2]
        filters = desc_split.loc[indices_total].str[-1].str.replace("'",'')
        imgnames = desc_split.loc[indices_indiv].str[1].str.split(' ').str[0]
        filters_all.append(filters.values)
        df.loc[indices_total,'colnames'] = filters.str.lower() + '_' + v.lower()
        df.loc[indices_indiv,'colnames'] = imgnames + '_' + v.lower()
    filters_final = np.unique(np.array(filters_all).ravel())
    print('Filters found: {}'.format(filters_final))
    return df, filters_final

def add_wcs(df, photfile):
    """Converts x and y columns to world coordinates using drizzled file
    that dolphot uses for astrometry

    Inputs
    ------
    photfile : path
        path to raw dolphot output
    df : DataFrame
        photometry table read in by read_dolphot

    Returns
    -------
    df : DataFrame
        A table of column descriptions and their corresponding names,
        with new 'ra' and 'dec' columns added.
    """
    drzfiles = list(Path(photfile).parent.glob('*_dr?.chip1.fits'))
    # neither of these should happen but just in case
    if len(drzfiles) == 0:
        print('No drizzled files found; skipping RA and Dec')
    elif len(drzfiles) > 1:
        print('Multiple drizzled files found: {}'.format(drzfiles))
    else:
        drzfile = str(drzfiles[0])
        print('Using {} as astrometric reference'.format(drzfile))
        ra, dec = WCS(drzfile).all_pix2world(df.x.values, df.y.values, 0)
        df.insert(4, 'ra', ra)
        df.insert(5, 'dec', dec)
    return df


def read_dolphot(photfile, columns_df, filters):
    """Reads in raw dolphot output (.phot file) to a DataFrame with named
    columns, and optionally writes it to a HDF5 file.

    Inputs
    ------
    photile : path
        path to raw dolphot output
    columns_df : DataFrame
        table of column names and indices, created by `name_columns`
    filters : list
        List of filters included in output, also from `name_columns`
    to_hdf : bool, optional
        Whether to write photometry table to HDF5 file. Defaults to False
        in the function definition, but defaults to True when this script
        is called from the command line.
    full : bool, optional
        Whether to include full photometry output in DataFrame. Defaults 
        to False.

    Returns
    -------
    df : DataFrame
        A table of column descriptions and their corresponding names.

    Outputs
    -------
        HDF5 file containing photometry table
    """
    #if not full:
    #    # cut individual chip columns before reading in .phot file
    #    columns_df = columns_df[columns_df.colnames.str.find('.chip') == -1]
    colnames = columns_df.colnames
    usecols = columns_df.index
    # read in dolphot output
    df = dd.read_csv(photfile, delim_whitespace=True, header=None,
                     usecols=usecols, names=colnames,
                     na_values=99.999).compute()
    #if to_hdf:
    outfile = photfile + '.hdf5'
    print('Reading in header information from individual images')
    fitsdir = Path(photfile).parent
    header_df = make_header_table(fitsdir)
    header_df.to_hdf(outfile, key='fitsinfo', mode='w', format='table',
                     complevel=9, complib='zlib')
    # lambda function to construct detector-filter pairs
    lamfunc = lambda x: '-'.join(x[~(x.str.startswith('CLEAR')|x.str.startswith('nan'))])
    filter_detectors = header_df.filter(regex='(DETECTOR)|(FILTER)').astype(str).apply(lamfunc, axis=1).unique()
    print('Writing photometry to {}'.format(outfile))
    df0 = df[colnames[colnames.str.find(r'.chip') == -1]]
    df0 = cull_photometry(df0, filter_detectors)
    df0 = add_wcs(df0, photfile)
    df0.to_hdf(outfile, key='data', mode='a', format='table', 
               complevel=9, complib='zlib')
    outfile_full = outfile.replace('.hdf5','_full.hdf5')
    os.rename(outfile, outfile_full)
    for f in filters:
        print('Writing single-frame photometry table for filter {}'.format(f))
        df.filter(regex='_{}_'.format(f)).to_hdf(outfile_full, key=f, 
                      mode='a', format='table', complevel=9, complib='zlib')
    print('Finished writing HDF5 file')

if __name__ == '__main__':
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    this_event = my_job.firing_event  # parent event obj
    parent_job = this_event.parent_job

    # config_id = this_event.options["config_id"]

# * LOG EVENT INFORMATION
    my_job.logprint(f"This Event: {this_event}")
    my_job.logprint(f"This Event Options: {this_event.options}")

# * Call drizzled image from astrodrozzle dataproduct
    this_dp_id = this_event.options["dp_id"]
    this_dp = wp.DataProduct(int(this_dp_id), group="proc")
    my_job.logprint(
        f"Data Product: {this_dp.filename}\n, Path: {this_dp.target.datapath}\n This DP options{this_dp.options}\n")
    target = this_dp.target

    my_config = this_dp.config
    my_job.logprint(
        f"Target Name: {target.name}\n TargetPath: {target.datapath}\n")


 
    photfile = this_dp.filename #if args.filebase.endswith('.phot') else args.filebase + '.phot'
    #photfile = my_config.procpath + '/' + this_dp.filename #if args.filebase.endswith('.phot') else args.filebase + '.phot'
    colfile = photfile + '.columns'
    my_job.logprint('Photometry file: {}'.format(photfile))
    my_job.logprint('Columns file: {}'.format(colfile))
    columns_df, filters = name_columns(colfile)
    
    import time
    t0 = time.time()
    df = read_dolphot(photfile, columns_df, filters)
    outfile = this_dp.filename + '_full.hdf5'
    hd5_dp = wp.DataProduct(my_config, filename=outfile, 
                              group="proc", data_type="hdf5 file", subtype="catalog")     
    t1 = time.time()
    timedelta = t1 - t0
    print('Finished in {}'.format(str(timedelta)) )
    next_event = my_job.child_event(
    name="hdf5_ready",
    options={"dp_id": hd5_dp.dp_id}
    )  # next event
    next_event.fire()
    time.sleep(150)

