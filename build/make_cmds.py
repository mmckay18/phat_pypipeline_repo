#! /usr/bin/env python

"""Makes CMDs of GST measurements.

Authors
-------
    Meredith Durbin, February 2018

Use
---
    This script is intended to be executed from the command line as
    such:
    ::
        python make_cmds.py ['filebase']
    
    Parameters:
    (Required) [filebase] - Path to .phot.hdf5 file
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import wpipe as wp
import dask.dataframe as dd
import os
import pandas as pd
import traceback
from astropy.io import fits
import argparse
from astropy.wcs import WCS
from pathlib import Path
import time


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="hdf5_ready", value="*")

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



#try:
#    import seaborn as sns; sns.set(style='white', font_scale=1.3)
#except ImportError:
#    print('install seaborn you monster')

# need better way to do this
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
    df = pd.DataFrame(data=np.genfromtxt(colfile, delimiter='. ', dtype=str),
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

def make_cmd(df, path, targname, red_filter, blue_filter, y_filter, n_err=12,
             #density_kwargs={'f':'log10', 'colormap':'viridis', 'linewidth':2},
             density_kwargs={'f':'log10', 'colormap':'viridis'},
             scatter_kwargs={'c':'k', 'alpha':0.5, 's':1, 'linewidth':2}):
    """Plot a CMD with (blue_filter - red_filter) on the x-axis and 
    y_filter on the y-axis.

    Inputs
    ------
    df : Dataset
        Pandas dataset
    red_filter : string
        filter name for "red" filter
    blue_filter : string
        filter name for "blue" filter
    y_filter : string
        filter name for filter on y-axis (usually same as red_filter)
    n_err : int, optional
        number of bins to calculate median photometric errors for
        default: 12
    density_kwargs : dict, optional
        parameters to pass to plt.hist2d; see documentation
    scatter_kwargs : dict, optional
        parameters to pass to plt.scatter; see documentation

    Returns
    -------
    Nothing

    Outputs
    -------
    some plots dude
    """
    color = f"{blue_filter.upper()}-{red_filter.upper()}"
    blue_vega = f"{blue_filter}_vega"
    red_vega = f"{red_filter}_vega"
    y_vega = f"{y_filter}_vega"
    ylab = y_filter.upper()

    df[color] = df[blue_vega]-df[red_vega]
    gst_criteria = df[f"{red_filter}_gst"] & df[f"{blue_filter}_gst"]
    #gst_criteria = ds['({}_gst == True) & ({}_gst == True)'.format(red_filter, blue_filter)]
    
    if y_filter not in [blue_filter, red_filter]:
        # idk why you would do this but it's an option
        gst_criteria = gst_criteria & df[f"{y_filter}_gst"]
    # cut dataset down to gst stars
    # could use ds.select() but i don't like it that much
    df_gst = df[gst_criteria].copy()
    # haxx
    # Range limits
    xmin = df_gst[color].min()
    xmax = df_gst[color].max()
    ymin = df_gst[y_vega].min()
    ymax = df_gst[y_vega].max()

    if xmin < -2.5:
        if "f2" in blue_filter:
            xmin = -3
        else:
            xmin = -2
    if xmax > 10.0:
        if "f2" in blue_filter:
            xmax = 7
        else:
            xmax = 10

    if ymin < 15.0:
        ymin = 15.0
    print(blue_filter,red_filter," has ",len(df_gst)," stars in CMD.")

    # Plotting
    fig, ax = plt.subplots(1, figsize=(7.,5.5))
    plt.rcParams.update({'font.size': 20})
    plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)

    if len(df_gst) >= 20000:
        # 2D density plot
        data_shape = 200
        plt.hist2d(
            df_gst[color],
            df_gst[y_vega],
            bins=data_shape,
            range=[[xmin, xmax], [ymax, ymin]],
            cmap=density_kwargs.get("colormap", "viridis"),
            norm=None
        )
        plt.colorbar()
    else:
        plt.scatter(df_gst[color], df_gst[y_vega], **scatter_kwargs)

    # Style
    plt.xticks(np.arange(int(xmin-0.5), int(xmax+0.5), 1.0))
    plt.yticks(np.arange(int(ymin-0.5), int(ymax+0.5), 1.0))
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(3)

    plt.minorticks_on()
    plt.xlim(int(xmin-0.5), int(xmax+0.5))
    plt.ylim(int(ymin-0.5), int(ymax+0.5))
    ax.invert_yaxis()
    plt.xlabel(color)
    plt.ylabel(ylab)

    # Binned errors
    bins = pd.qcut(df_gst[y_vega], q=n_err, duplicates="drop")

    y_binned = df_gst.groupby(bins)[y_vega].mean().values

    xerr_val = (df_gst[f"{blue_filter}_err"]**2 +
                df_gst[f"{red_filter}_err"]**2)**0.5
    xerr = df_gst.groupby(bins)[xerr_val].median().values

    yerr = df_gst.groupby(bins)[f"{y_filter}_err"].median().values

    x_binned = [xmax * 0.9] * len(y_binned)

    ax.errorbar(x_binned, y_binned, yerr=yerr, xerr=xerr,
                fmt=',', color='k', lw=1.5)
    
    #Save
    name = path + "/" + targname + "_" + blue_filter + "_" + red_filter + "_" + "gst_cmd.png"
    fig.savefig(name)
    new_dp = wp.DataProduct(my_config, filename=name, 
                             group="proc", data_type="CMD file", subtype="CMD") 


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
    this_dp_id = this_event.options["dp_id"]
    this_dp = wp.DataProduct(int(this_dp_id), group="proc")
    my_job.logprint(
        f"Data Product: {this_dp.filename}\n, Path: {this_dp.target.datapath}\n This DP options{this_dp.options}\n")

    photfile = my_config.procpath  +  "/" + this_dp.filename

    import pandas as pd
    df = pd.read_hdf(photfile, key='data')

    #filters = my_config.parameters["det_filters"].split(',')
    colfile = my_config.parameters["colfile"]
    my_job.logprint('Columns file: {}'.format(colfile))
    columns_df, filters = name_columns(colfile)

    waves = []
    for filt in filters:
        pre, suf = filt.split('_')
        wave = suf[1:4]
        if "NIRCAM" in pre:
            wave = 10*int(wave)
        if "WFC3" in pre and "F1" in suf:
            wave = 10*int(wave)
        my_job.logprint(waves)  
        waves.append(int(wave))

    my_job.logprint(waves)  
    sort_inds = np.argsort(waves)
        
    num_all_filters = len(filters)
    for i in range(num_all_filters-1):
       for j in range(num_all_filters-i-1):
           ind2=i+1+j
           my_job.logprint(filters[sort_inds[i]])  
           my_job.logprint(filters[sort_inds[ind2]])  
           try:
               make_cmd(df, procpath, my_target.name, filters[sort_inds[ind2]].lower(),filters[sort_inds[i]].lower(),filters[sort_inds[ind2]].lower())
           except:
               my_job.logprint(f"{filters[sort_inds[i]]} and {filters[sort_inds[ind2]]} failed")
               continue
       
    next_event = my_job.child_event(
    name="cmds_ready",
    options={"target_id": my_target.target_id}
    )  # next event
    #next_event.fire() 
    #time.sleep(150)
 

    
