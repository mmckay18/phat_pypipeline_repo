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
    _temp = task.mask(source="*", name="hdf5_ready", value="*")




#try:
#    import seaborn as sns; sns.set(style='white', font_scale=1.3)
#except ImportError:
#    print('install seaborn you monster')

# need better way to do this

def make_cmd(ds, path, targname, red_filter, blue_filter, y_filter, n_err=12,
             #density_kwargs={'f':'log10', 'colormap':'viridis', 'linewidth':2},
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
    color = '{}-{}'.format(blue_filter.upper(), red_filter.upper())
    blue_vega = '{}_vega'.format(blue_filter)
    red_vega = '{}_vega'.format(red_filter)
    y_vega = '{}_vega'.format(y_filter)
    ylab = '{}'.format(y_filter.upper()) 
    ds[color] = ds[blue_vega]-ds[red_vega]
    gst_criteria = ds['{}_gst'.format(red_filter)] & ds['{}_gst'.format(blue_filter)]
    name = path + "/" + targname + "_" + blue_filter + "_" + red_filter + "_" + "gst_cmd.png"
    if y_filter not in [blue_filter, red_filter]:
        # idk why you would do this but it's an option
        gst_criteria = gst_criteria & ds['{}_gst'.format(y_filter)]
    # cut dataset down to gst stars
    # could use ds.select() but i don't like it that much
    ds_gst = ds[gst_criteria]
    # haxx
    xmin = np.nanmin(ds_gst[color].tolist())
    xmax = np.nanmax(ds_gst[color].tolist())
    ymin = np.nanmin(ds_gst[y_vega].tolist())
    ymax = np.nanmax(ds_gst[y_vega].tolist())
    if xmin < -2.5:
        xmin = -2.5
    if xmax > 10.0:
        xmax = 10.0
    if ymin < 15.0:
        ymin = 15.0
    print(blue_filter,red_filter," has ",ds_gst.length()," stars in CMD.")

    if ds_gst.length() >= 50000:
        fig, ax = plt.subplots(1, figsize=(7.,5.5))
        plt.rcParams.update({'font.size': 20})
        plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)
        #data_shape = int(np.sqrt(ds_gst.length()))
        data_shape = 200
        ds_gst.plot(color, y_vega, shape=data_shape,
                    limits=[[xmin,xmax],[ymax,ymin]],
                    **density_kwargs)
        plt.rcParams['axes.linewidth'] = 5
        plt.xticks(np.arange(xmin, xmax+1, 1.0))
        plt.yticks(fontsize=20)
        plt.xticks(fontsize=20)
        ax.xaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top','bottom','left','right']:
           ax.spines[axis].set_linewidth(4)
        plt.minorticks_on()
        plt.ylabel(ylab,fontsize=20)
        plt.xlabel(color,fontsize=20)
    else:
        plt.xlim(xmin,xmax)
        plt.ylim(ymin,ymax)
        fig, ax = plt.subplots(1, figsize=(7.,5.5), linewidth=5)
        plt.rcParams.update({'font.size': 20})
        plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)
        ds_gst.scatter(color, y_vega,  **scatter_kwargs)
        plt.rcParams['axes.linewidth'] =5 
        plt.xticks(np.arange(xmin, xmax+1, 1.0))
        plt.yticks(fontsize=20)
        plt.xticks(fontsize=20)
        ax.xaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor',direction='in', length=6, width=2, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top','bottom','left','right']:
           ax.spines[axis].set_linewidth(2)
        plt.minorticks_on()
        plt.xlim(xmin,xmax)
        plt.ylim(ymin,ymax)
        plt.ylabel(ylab,fontsize=20)
        plt.xlabel(color,fontsize=20)
        ax.invert_yaxis()
    y_binned = ds_gst.mean(y_vega, binby=ds_gst[y_vega], shape=n_err)
    xerr = ds_gst.median_approx('({}_err**2 + {}_err**2)**0.5'.format(blue_filter, red_filter),
                                 binby=ds_gst[y_vega], shape=n_err)
    yerr = ds_gst.median_approx('{}_err'.format(y_filter),
                                 binby=ds_gst[y_vega], shape=n_err)
    x_binned = [xmax*0.9]*n_err
    ax.errorbar(x_binned, y_binned, yerr=yerr, xerr=xerr,
                fmt=',', color='k', lw=1.5)
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
    filters.sort()
    # how choose filters WHO KNOWS
    #make_cmd(ds, red_filter, blue_filter, y_filter)
    #make_cmd(ds, 'f160w', 'f475w', 'f160w')
    #make_cmd(ds, 'f160w', 'f110w', 'f160w')
    #make_cmd(ds, 'f160w', 'f814w', 'f160w')
    #make_cmd(ds, 'f814w', 'f475w', 'f814w')
    #make_cmd(ds, 'f475w', 'f336w', 'f475w')
    #make_cmd(ds, 'f475w', 'f275w', 'f475w')
    num_all_filters = len(filters)
    for i in range(num_all_filters-1):
       my_job.logprint("FILTERS:")  
       my_job.logprint(filters)  
       my_job.logprint(filters[i])  
       my_job.logprint(filters[i+1])  
       make_cmd(ds, procpath, my_target.name, filters[i+1].lower(),filters[i].lower(),filters[i+1].lower())
       
    next_event = my_job.child_event(
    name="cmds_ready",
    options={"target_id": my_target.target_id}
    )  # next event
    next_event.fire()
    time.sleep(150)
 

    
