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
    _temp = task.mask(source="*", name="fake_hdf5_ready", value="*")

def _find_magin_column_for_filter(df, filter_name):
    """
    Heuristic: find the first column that contains '_magin' and also contains
    the filter name (case-insensitive). If none contains the filter name,
    return the first column containing '_magin'.
    """
    magin_cols = [c for c in df.columns if "_magin" in c]
    if not magin_cols:
        return None
    # try to find one that contains the filter name
    for c in magin_cols:
        if filter_name.lower() in c.lower():
            return c
    return magin_cols[0]

#try:
#    import seaborn as sns; sns.set(style='white', font_scale=1.3)
#except ImportError:
#    print('install seaborn you monster')

# need better way to do this

def make_resid_plot(my_job,df, path, targname, filter, n_err=12,
             #density_kwargs={'f':'log10', 'colormap':'viridis', 'linewidth':2},
             density_kwargs={'f':'log10', 'colormap':'viridis'},
             scatter_kwargs={'c':'k', 'alpha':0.5, 's':1, 'linewidth':2}):
    """Plot residuals (out - in) versus input magnitude for GST-selected stars.

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
    vega = f"{filter}_vega"

    # Find an input magnitude column in the table with suffix '_magin'
    incolname = _find_magin_column_for_filter(df, filter)
    if incolname is None:
        my_job.logprint(f"No '*_magin' column found in table for filter {filter}")
        raise ValueError("No input (magin) column found")

    try:
        my_job.logprint(f"found input column {incolname} for {vega}")
    except Exception:
        my_job.logprint(f"No found input column for {vega}")
    
    xlab = f"{filter.upper()} IN"
    ylab = "Out - In" 
    gst_col = f"{filter}_gst" 
    name = path + "/" + targname + "_" + filter + "_" + "gst_asts.png"
    # GST selection (ensure column exists)
    if gst_col not in df.columns:
        my_job.logprint(f"GST column {gst_col} not found; selecting all rows")
        df_gst = df.copy()
    else:
        df_gst = df[df[gst_col]].copy()

    # haxx
    xmin = np.nanmin(df_gst[incolname].to_numpy())
    xmax = np.nanmax(df_gst[incolname].to_numpy())
    ymin = -1.0
    ymax = 1.0

    # compute diff (out - in)
    if vega not in df_gst.columns:
        my_job.logprint(f"Vega column {vega} not found in data.")
        raise ValueError(f"Vega column {vega} not present")
    diff = df_gst[vega] - df_gst[incolname]

    # compute ranges (use safe numpy functions)
    if df_gst.empty:
        my_job.logprint("No GST-selected stars found; aborting plot")
        return
    
    my_job.logprint(f"{filter} has {len(df_gst)} / {len(df)} stars recovered.")

    # make plot
    fig, ax = plt.subplots(1, figsize=(7., 5.5))
    plt.rcParams.update({'font.size': 20})
    plt.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)

    if len(df_gst) >= 50000:
        # density plot via hist2d
        data_shape = 200
        h = plt.hist2d(df_gst[incolname].to_numpy(), diff.to_numpy(),
                       bins=data_shape,
                       range=[[xmin, xmax], [ymin, ymax]],
                       cmap=density_kwargs.get('colormap', 'viridis'))
        plt.colorbar()
        plt.xticks(np.arange(int(xmin-0.5), int(xmax+0.5), 1.0), fontsize=20)
        plt.yticks(np.arange(int(ymin-0.5), int(ymax+0.5), 1.0), fontsize=20)

        ax.xaxis.set_tick_params(which='minor', direction='in', length=6, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor', direction='in', length=6, width=2, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(4)
        plt.minorticks_on()

    else:
        # scatter plot
        ax.scatter(df_gst[incolname].to_numpy(), diff.to_numpy(), **scatter_kwargs)
        plt.rcParams['axes.linewidth'] = 5
        plt.xticks(np.arange(int(xmin-0.5), int(xmax+0.5), 1.0), fontsize=20)
        plt.yticks(np.arange(int(ymin-0.5), int(ymax+0.5), 1.0), fontsize=20)
        ax.xaxis.set_tick_params(which='minor', direction='in', length=6, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(which='minor', direction='in', length=6, width=2, top=True, right=True)
        ax.xaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        ax.yaxis.set_tick_params(direction='in', length=8, width=2, top=True, right=True)
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(2)
        plt.minorticks_on()

    # set limits, labels, invert y-axis to match original plotting style
    plt.xlim(int(xmin - 0.5), int(xmax + 0.5))
    plt.ylim(int(ymin - 0.5), int(ymax + 0.5))
    plt.ylabel(ylab, fontsize=20)
    plt.xlabel(xlab, fontsize=20)
    ax.invert_yaxis()

    # Binned statistics
    # bin by the input magnitude (incolname)
    try:
        bins = pd.qcut(df_gst[incolname], q=n_err, duplicates='drop')
    except Exception:
        # fallback to linspace bins if qcut fails (e.g., too many identical values)
        bin_edges = np.linspace(xmin, xmax, n_err + 1)
        bins = pd.cut(df_gst[incolname], bins=bin_edges, include_lowest=True)

    # compute binned centroids and error estimates
    grouped = df_gst.groupby(bins)
    # y_binned: mean of diff in bin (this approximates average residual per bin)
    y_binned = grouped.apply(lambda g: np.nanmean((g[vega] - g[incolname]).to_numpy()))
    y_binned = y_binned.values
    # xerr: try to compute a combined error column if available; fallback to median absolute deviation of diff
    # We try common error column names; if none found, use group std dev as xerr placeholder.
    err_candidates = []
    for suffix in ("_err", "err"):
        c1 = f"{filter}{suffix}"
        c2 = f"{filter}_err"
        if c1 in df_gst.columns:
            err_candidates.append(c1)
        if c2 in df_gst.columns:
            err_candidates.append(c2)
    if err_candidates:
        # pick first candidate and compute sqrt(err_in**2 + err_out**2) if both exist
        errcol = err_candidates[0]
        # guess an input err column corresponding to incolname (replace magin with err)
        in_err_col = incolname.replace("_magin", "_err") if "_magin" in incolname else incolname + "_err"
        if in_err_col in df_gst.columns:
            comb_err = np.sqrt(df_gst[errcol].to_numpy()**2 + df_gst[in_err_col].to_numpy()**2)
            xerr = grouped.apply(lambda g: np.nanmedian(np.sqrt((g[errcol].to_numpy()**2) + (g.get(in_err_col, np.zeros(len(g))).to_numpy()**2))))
            xerr = xerr.values
        else:
            # fallback: use median absolute deviation of diff within each bin as xerr
            xerr = grouped.apply(lambda g: np.nanmedian(np.abs((g[vega] - g[incolname]).to_numpy())))
            xerr = xerr.values
    else:
        # fallback: use group std.dev of diff
        xerr = grouped.apply(lambda g: np.nanstd((g[vega] - g[incolname]).to_numpy()))
        xerr = xerr.values

    # yerr: use std deviation in each bin as uncertainty on mean
    yerr = grouped.apply(lambda g: np.nanstd((g[vega] - g[incolname]).to_numpy()) / np.sqrt(max(len(g), 1)))
    yerr = yerr.values

    # x positions for errorbars: place at 90% of xmax like original code
    n_points = len(y_binned)
    if n_points == 0:
        my_job.logprint("No binned points to plot; saving figure and returning.")
        fig.savefig(name)
        new_dp = wp.DataProduct(my_config, filename=name,
                                group="proc", data_type="CMD file", subtype="CMD")
        return
    x_binned = [xmax * 0.9] * n_points

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

    import pandas as pd
    df = pd.read_hdf(photfile, key='data')

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
            try:
                make_resid_plot(my_job, df, procpath, my_target.name,
                                filters[sort_inds[ind2]].lower(), n_err=12)
            except Exception as e:
                my_job.logprint(f"An error occurred: {e}")
                my_job.logprint(f"{filters[sort_inds[i]]} and {filters[sort_inds[ind2]]} failed")
                continue
       
    next_event = my_job.child_event(
    name="cmds_ready",
    options={"target_id": my_target.target_id}
    )  # next event
    next_event.fire() 
    time.sleep(150)
 

    
