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
matplotlib.use('Agg') # check this
import matplotlib.pyplot as plt
import numpy as np
import vaex
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
    _temp = task.mask(source="*", name="spatial", value="*")




#try:
#    import seaborn as sns; sns.set(style='white', font_scale=1.3)
#except ImportError:
#    print('install seaborn you monster')

# need better way to do this

def make_spatial(ds, path, targname, red_filter, blue_filter, 
             density_kwargs={'f':'log10', 'colormap':'viridis'},
             scatter_kwargs={'c':'k', 'alpha':0.5, 's':1, 'linewidth':2}):
    """Plot a CMD with (blue_filter - red_filter) on the x-axis and 
    y_filter on the y-axis.

    Inputs
    ------
    ds : Dataset
        Vaex dataset
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
        parameters to pass to ds.plot; see vaex documentation
    scatter_kwargs : dict, optional
        parameters to pass to ds.scatter; see vaex documentation

    Returns
    -------
    Nothing

    Outputs
    -------
    some plots dude
    """
    ylab = 'Declination (J2000)'
    gst_criteria = ds['{}_gst'.format(red_filter)] & ds['{}_gst'.format(blue_filter)]
    name = path + "/" + targname + "_" + blue_filter + "_" + red_filter + "_" + "gst_spatial.png"
    ds_gst = ds[gst_criteria]
    # haxx
    xmin = np.nanmin(ds_gst['ra'].tolist())
    xmax = np.nanmax(ds_gst['ra'].tolist())
    ymin = np.nanmin(ds_gst['dec'].tolist())
    ymax = np.nanmax(ds_gst['dec'].tolist())
    meddec = (np.pi/180.0)*(ymax + ymin)/2.0
    cosdec = np.cos(meddec*np.pi/180.0)
    print(blue_filter,red_filter," has ",ds_gst.length()," stars in map.")
    
    if ds_gst.length() >= 50000:
        fig, ax = plt.subplots(1, figsize=(7.0/cosdec,5.5))
        plt.rcParams.update({'font.size': 20})
        plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)
        #data_shape = int(np.sqrt(ds_gst.length()))
        data_shape = 200
        ds_gst.plot('ra', 'dec', shape=data_shape,
                    limits=[[xmin,xmax],[ymax,ymin]],
                    **density_kwargs)
        plt.rcParams['axes.linewidth'] = 5
        plt.xticks(np.arange(int(xmin-0.5), int(xmax+0.5), 1.0),fontsize=20)
        plt.yticks(np.arange(int(ymin-0.5), int(ymax+0.5), 1.0),fontsize=20)

        ax.xaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top','bottom','left','right']:
           ax.spines[axis].set_linewidth(4)
        plt.minorticks_on()
        plt.ylabel(ylab,fontsize=20)
        plt.xlabel("Right Ascensiton (J2000)",fontsize=20)
    else:
        fig, ax = plt.subplots(1, figsize=(5.5/cosdec,5.5), linewidth=2)
        plt.rcParams.update({'font.size': 20})
        plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)
        ds_gst.scatter('ra', 'dec',  **scatter_kwargs)
        plt.rcParams['axes.linewidth'] =5 
        plt.xticks(np.arange(int(xmin-0.5), int(xmax+0.5), 1.0),fontsize=20)
        plt.yticks(np.arange(int(ymin-0.5), int(ymax+0.5), 1.0),fontsize=20)
        ax.xaxis.set_tick_params(which='minor',direction='in', length=6, width=1, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor',direction='in', length=6, width=1, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top','bottom','left','right']:
           ax.spines[axis].set_linewidth(2)
        plt.minorticks_on()
    plt.xlim(int(xmin-0.5), int(xmax+0.5))
    plt.ylim(int(ymin-0.5), int(ymax+0.5))
    plt.ylabel(ylab,fontsize=20)
    plt.xlabel("Right Ascensiton (J2000)",fontsize=20)
    fig.savefig(name)
    new_dp = wp.DataProduct(my_config, filename=name, 
                             group="proc", data_type="Map file", subtype="Map") 


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

    photfile = this_dp.filename

    #try:
    #    # I have never gotten vaex to read an hdf5 file successfully
    #    ds = vaex.open(photfile)
    #except:
    import pandas as pd
    df = pd.read_hdf(photfile, key='data')
    ds = vaex.from_pandas(df)
    #filters = my_config.parameters["filters"].split(',')
    filters = my_config.parameters["det_filters"].split(',')
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
           make_spatial(ds, procpath, my_target.name, filters[sort_inds[ind2]].lower(),filters[sort_inds[i]].lower())
       
    next_event = my_job.child_event(
    name="cmds_ready",
    options={"target_id": my_target.target_id}
    )  # next event
    next_event.fire() 
    time.sleep(150)
 

    
