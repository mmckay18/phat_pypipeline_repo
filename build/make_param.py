#!/usr/bin/env python
"""
Make Param Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Checks for user-specified parameters in the configuration. If a parameter is not specified by the user, it sets a default value for that parameter.

2. Writes the parameters and their values to the targets configuration file. This file is used as input for other scripts in the pipeline.

3. Defines global parameters for the pipeline. These parameters control the behavior of the pipeline and are used across multiple scripts for running DOLPHOT.

4. Fires DOLPHOT events for the target.

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

import wpipe as wp
import time
from astropy.io import fits
import os

def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="make_param", value="*")
    _temp = task.mask(source="*", name="make_warm1_param", value="*")
    _temp = task.mask(source="*", name="warmstart_done", value="*")

if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config
    my_job.logprint(
        f"###### This config.parameters {my_config.parameters}, {type(my_config.parameters)} \n")
    this_event = my_job.firing_event
    my_job.logprint(f"{this_event.options}")
    warm = 0
    if "warm1" in this_event.name:
        warm = 1
    if "warmstart_done" in this_event.name:
        warm = 2
    # prep_event_ids = this_event.options["list_prep_image_event_ids"]
    # my_job.logprint(f"Prep Event IDs: {prep_event_ids}")

    # List of DP from prep image:
    # list_of_dps = this_event.options
    tagged_dps = []
    # for dp in my_config.procdataproducts:
    #    # my_job.logprint(f"DP: {dp}, {dp.subtype}")
    #    if "drc.chip1.fits" in dp.filename:
    #        ref_dp = dp
    #        dp.subtype == "reference"  # ? Not setting the subtype?
    #        my_job.logprint(f"Reference DP: {dp}, {dp.subtype}")

    #    if "drc.chip1.fits" not in dp.filename and dp.subtype == "splitgroups":
    #        tagged_dps.append(dp)
    #        my_job.logprint(f"Tagged DP: {dp}, {dp.subtype}")
    #    else:
    #        pass
    ref_dp = wp.DataProduct.select(
        config_id=my_config.config_id, subtype="reference_prepped")
    ref_filt = my_config.parameters["reference_filter"]
    tagged_dps = wp.DataProduct.select(
        config_id=my_config.config_id,
        data_type="image",
        subtype="SCIENCE_prepped")
    if warm == 1:
        my_job.logprint("warm is 1, so removing LW and WFC3/IR from this run")
        my_job.logprint(f"list starts with a length of {len(tagged_dps)}")
        count = 0
        tagged_dps1 = tagged_dps
        tagged_dps = []
        for dp in tagged_dps1:
            if "LONG" in dp.options['channel']:
                continue
            if "IR" in dp.options['detector'] and "CAM" not in dp.options['detector']:
                continue
            tagged_dps.append(dp)
        my_job.logprint(f"list ends with a length of {len(tagged_dps)}")
        
    my_target = wp.Target(this_event.options["target_id"])
    my_job.logprint(f"###### This Target: {my_target}\n")

    # Get list of all dataproducts associated with target
    # my_job.logprint(f"Target DPs: {my_target.dataproducts}") #? Not working lisying target dataproducts

    # ref_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image")
    #                                subtype="dolphot input reference")  # reference image
    count = 0
    for cand_ref in ref_dp:
        if cand_ref.options["filter"] == ref_filt:
            ref_dp_list = [ref_dp[count]]
        count += 1
    my_job.logprint(f"Reference DP: {ref_dp_list[0].filename}, {type(ref_dp_list[0])}")


    all_dps = ref_dp_list + tagged_dps
    my_job.logprint(f"all_dps: {all_dps}")

# Create parameter file
    my_target_path = my_target.datapath

    # path to target's conf directory
    target_conf_path = my_config.confpath + "/"
    my_job.logprint(f"Target Conf Path: {target_conf_path}")

    # TODO: Make target file
    param_filepath = target_conf_path + my_target.name + '.param'
    my_job.logprint(f"Parameter File Path: {param_filepath}")

    with open(param_filepath, 'w') as p:  # create empty file
        nimg = len(all_dps)-1  # number of images
        p.write(f'Nimg={nimg}\n')  # write to file

        # Define image specific parameters
        my_job.logprint(
            f'Checking for user specified individual parameters and defining any unspecified individual parameters')
        count = 0
        for dp in all_dps:  # all images
            my_job.logprint(f'Checking {dp.filename}, {dp}')
            # image number with reference at index 0
            # loc = tagged_dps.index(dp)
            loc = all_dps.index(dp)

            im_fullfile = dp.filename
            im_file = im_fullfile.split('.fits')[0]  # get rid of extension
            p.write(f'img{loc}_file = {im_file}\n')
            im_pars = ["apsky", "shift", "xform",
                       "raper", "rchi", "rsky0", "rsky1", "rpsf"]
            def_vals = ["20 35", "0 0", "1 0 0", "2", "1.5", "15", "35", "15"]
            if 'reference' not in dp.subtype:
                defined = []
                count += 1
                img = 'img'+str(count)
                parcount = 0
                for impar in im_pars:
                    param_name = "img"+str(count)+"_"+impar
                    cam_name = dp.options['detector']+"_"+impar
                    if "NIRCAM" in dp.options['detector']:
                        if "LONG" in dp.options['channel']:
                            cam_name = dp.options['detector']+"LW_"+impar
                    try:
                        p.write(
                            f'{param_name} = {my_config.parameters[cam_name]}\n')
                        my_job.logprint(
                            f'{param_name} parameter found in configuration')
                        defined.append(1)
                    except:
                        p.write(
                            f'{param_name} = {def_vals[parcount]}\n')
                        my_job.logprint(
                            f'{param_name} parameter default')
                        defined.append(1)
                    parcount += 1

# Define global parameters
        my_job.logprint(
            f'Checking for user specified global parameters and defining any unspecified global parameters')
        params_global = ["UseWCS", "PSFPhot", "FitSky", "SkipSky", "SkySig", "SecondPass", "SearchMode", "SigFind", "SigFindMult", "SigFinal", "MaxIT", "NoiseMult", "FSat", "FlagMask", "ApCor", "Force1", "Align", "aligntol",
                         "alignstep", "ACSuseCTE", "WFC3useCTE", "Rotate", "RCentroid", "PosStep", "dPosMax", "RCombine", "SigPSF", "PSFres", "psfoff", "DiagPlotType", "CombineChi", "ACSpsfType", "WFC3IRpsfType", "WFC3UVISpsfType", "PSFPhotIt"]
        glob_vals = ["2", "1", "2", "2", "2.25", "5", "1", "3.0", "0.85", "3.5", "25", "0.10", "0.999", "4", "1", "1",
                     "2", "4", "2", "0", "0", "1", "1", "0.1", "2.5", "1.415", "3.0", "1", "0.0", "PNG", "1", "0", "0", "0", "2"]
        # params_global = ["MaxIT","PSFPhot", "PSFPhotIt", "FitSky", "SkipSky", "SkySig", "SigFindMult", "FSat", "PosStep", "sigPSF", "UseWCS", "NoiseMult", "SecondPass", "Force1", "WFC3UVISpsfType","ACSpsfType","WFC3IRpsfType","ACSuseCTE", "WFC3useCTE","FlagMask","InterpPSFlib", "CombineChi", "RCombine", "PSFres"]
        # glob_vals = ["25","1","2","2","1","2.25","0.85","0.999","0.25","5.0","2","0.1","5","0","0","0","0","0","0","4","1","0","1.5","1"]
        paramcount = 0
        for globpar in params_global:
            try:
                my_config.parameters[globpar]
                p.write(f'{globpar} = {my_config.parameters[globpar]}\n')
                my_job.logprint(f'{globpar} parameter found in configuration')
            except:
                p.write(f'{globpar} = {glob_vals[paramcount]}\n')
                my_job.logprint(f'{globpar} parameter set to default')
            paramcount += 1
        if warm == 2:
            my_job.logprint("warm is 2")
            warmdpid = this_event.options["warmdpid"]
            warmdp = wp.DataProduct(int(warmdpid))
            warmname = warmdp.filename
            my_job.logprint("adding xytfile = {warmname}")
            p.write(f'xytfile = {warmname}')
##############################
#! Define variable identifying the partition with most available memory
    best_partition = os.popen("""echo $(sinfo -o "%P %m" | sort -k2 -nr | head -n 1 | awk '{print $1}')""").read().strip('\n')

# Create dataproduct for parameter file
    param_dp = wp.DataProduct(my_config, filename=my_target.name + '.param', relativepath=target_conf_path,
                              group="conf", data_type="text file", subtype="parameter")  # Create dataproduct owned by config for the parameter file
    my_config.parameters["param_file"] = my_target.name + '.param'
    my_job.logprint(f"Parameter DP: {param_dp}, {param_dp.filename}")
    my_job.logprint(
        f"\nDOLPHOT parameter file complete for {my_target.name}, firing DOLPHOT task")
    mem = "50G"
    wall = "100:00:00"
    if count < 10:
        mem = "10G"
        wall = "50:00:00"
    if count > 50:
        mem = "100G"
        wall = "200:00:00"
    if count > 100:
        mem = "150G"
        wall = "250:00:00"
    if count > 200:
        mem = "250G"
        wall = "400:00:00"
    if warm == 1: 
        next_event = my_job.child_event(
            name="DOLPHOT_warm",
            options={"param_dp_id": param_dp.dp_id, "walltime": wall, "memory": mem, "partition": best_partition}
        )  # next event
    else:
        next_event = my_job.child_event(
            name="DOLPHOT",
            options={"param_dp_id": param_dp.dp_id, "walltime": wall, "memory": mem, "partition": best_partition}
        )  # next event
    next_event.fire()
    time.sleep(150)
