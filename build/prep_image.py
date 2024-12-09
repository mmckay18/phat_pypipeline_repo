#!/usr/bin/env python

"""
Prep Image Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Sets the processing path and logs the start of the 'splitgroups' operation on the data product.

2. Executes the 'splitgroups' operation using a subprocess. This operation splits the data product into individual groups.

3. Creates data products from the output of the 'splitgroups' operation. These data products are images that have been prepped for further processing.

4. Logs the creation of each data product and its associated options.

5. Calculates the sky background for each image. If the detector option is 'UVIS', it runs the 'calcsky' operation. If the detector option is 'WFC', it logs the start of the 'calcsky' operation.

6. Creates data products from the output of the 'calcsky' operation. These data products are images that have been prepped for further processing.

7. Fires make_param event when all images are finished running prep_image

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

import wpipe as wp
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
import os
import subprocess
import glob
import time

#! - It should take the data product ID it gets handed,
#! - get the file associated with it,
#! - and run the correct DOLPHOT masking routine for the detector that produced it.
#! - Then it should run the DOLPHOT splitgroups routine on the output,.
#! - Then it should run calcsky on the output from splitgroups.
#! - Finally, it needs to make data products for all of the output files,
#! - and check to see how many other prep_image tasks have completed for the target.
#! - Check against the total, and fire a done event if it's the last one.


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="prep_image", value="*")


if __name__ == "__main__":
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

# * Get target config file
    target = this_dp.target
    my_job.logprint(
        f"Target Name: {target.name}\n TargetPath: {target.datapath}\n")

# * Get Target config parameters
    #my_config = target.configuration(
    #    name="default", parameters={"target_id": target.target_id}
    #)
    my_config = my_job.config
    config_parameters = my_config.parameters
    my_job.logprint(f"This Config Parameters: {config_parameters}")
    try:
        warm = my_config.parameters["warmstart"]
    except:
        warm = 0
    my_job.logprint(f"warm = {warm}")
# * Set proc dataproduct file path # TODO: Better way to implement this for development
    proc_path = my_config.procpath + "/"
    dp_fullpath = proc_path + this_dp.filename

# * Get dataproduct subtype for all dataproducts to pass on reference image
    this_dp_subtype = this_dp.subtype
    my_job.logprint(
        f"Dataproduct Subtype: {this_dp_subtype}, Datatype{this_dp.data_type}\n")
    #! WFC3MASK - Uses the DQ array to remove bad pixels from the image and convert image to units of electron.
    if this_dp_subtype == "DRIZZLED" and "JWST" not in this_dp.options["telescope"]:
        my_job.logprint(dp_fullpath)
        fitsname = dp_fullpath
        try:
            f = fits.open(fitsname, mode='update')
            f.info()
            del f[4]
            f.info()
            f.close()
            fits_file = get_pkg_data_filename(fitsname)
            a = fits.getval(fits_file, 'NCOMBINE', ext=1)
            fits.setval(fits_file, 'NCOMBINE', value=a)
        except:
            pass

    my_job.logprint(f'Starting mask on {dp_fullpath}')
    my_job.logprint(f'Detector {this_dp.options["detector"]}')
    if "UVIS" in this_dp.options["detector"]:
        mask_output = subprocess.run(
            [my_config.parameters['dolphot_path']+"wfc3mask", dp_fullpath], capture_output=True, text=True)
    if "IR" in this_dp.options["detector"] and "NIRCAM" not in this_dp.options["detector"]:
        mask_output = subprocess.run(
            [my_config.parameters['dolphot_path']+"wfc3mask", dp_fullpath], capture_output=True, text=True)
    if "WFC" in this_dp.options["detector"]:
        mask_output = subprocess.run(
            [my_config.parameters['dolphot_path']+"acsmask", dp_fullpath], capture_output=True, text=True)
    if "NIRCAM" in this_dp.options["detector"]:
        mask_output = subprocess.run(
            [my_config.parameters['dolphot_path']+"nircammask", dp_fullpath], capture_output=True, text=True)
    my_job.logprint(f'mask stdout: {mask_output}')

    #! SPLITGROUPS - Splits the SCI images into their own fits files for HST images.
    proc_path = my_config.procpath + "/"
    my_job.logprint(f'Starting splitgroups on {dp_fullpath}')
    splitgroups_output = subprocess.run(
        [my_config.parameters['dolphot_path']+"splitgroups", dp_fullpath], capture_output=True, text=True, cwd=proc_path)
    my_job.logprint(f'splitgroups stdout: {splitgroups_output}\n')

    try:
        run_single = my_config.parameters["run_single"]
    except:
        run_single = "F"
        my_config.parameters["run_single"] = "F"

    #! make data products from splitgroups output <'....*chip1.fits'>
    for splitgroup_output_file in glob.glob(proc_path + this_dp.filename[:-5] + '*chip?.fits'):
        sp_dp_filename = splitgroup_output_file.split("/")[-1]
        sp_dp_subtype = this_dp.subtype+"_"+"prepped"
        my_job.logprint(f'created dataproduct for {sp_dp_filename}')
        sp_dp = wp.DataProduct(my_config, filename=sp_dp_filename, group="proc", data_type="image", subtype=sp_dp_subtype, options={
                               "telescope": this_dp.options["telescope"], "channel": this_dp.options["channel"], "detector": this_dp.options["detector"], "Exptime": this_dp.options["Exptime"], "filter": this_dp.options["filter"]})
        my_job.logprint(f'DP {sp_dp_filename}: {sp_dp}')
        my_job.logprint(f'with option {sp_dp.options["detector"]}')

        #! CALCSKY - Calculates the sky background for each image for UVIS or IR.
        if this_dp.options["detector"] == "UVIS":
            my_job.logprint(
                f'Starting calcsky on {sp_dp.filename[:-5]}, {this_dp.options["detector"]}')
            calcsky_output = subprocess.run(
                [my_config.parameters['dolphot_path']+"calcsky", sp_dp.filename[:-5], "15", "35", "4", "2.25", "2.00"], capture_output=True, text=True, cwd=proc_path)
            my_job.logprint(f'calcsky stdout: {calcsky_output}\n')

        if this_dp.options["detector"] == "WFC":
            my_job.logprint(
                f'Starting calcsky on {sp_dp.filename[:-5]}, {this_dp.options["detector"]}')
            calcsky_output = subprocess.run(
                [my_config.parameters['dolphot_path']+"calcsky", sp_dp.filename[:-5], "15", "35", "4", "2.25", "2.00"], capture_output=True, text=True, cwd=proc_path)
            my_job.logprint(f'calcsky stdout: {calcsky_output}\n')

        elif this_dp.options["detector"] == "IR":
            my_job.logprint(
                f'Starting calcsky on {sp_dp.filename[:-5]}, {this_dp.options["detector"]}')
            calcsky_output = subprocess.run(
                [my_config.parameters['dolphot_path']+"calcsky", sp_dp.filename[:-5], "10", "25", "2", "2.25", "2.00"], capture_output=True, text=True, cwd=proc_path)
            my_job.logprint(f'calcsky stdout: {calcsky_output}\n')

        elif this_dp.options["detector"] == "None":
            my_job.logprint(
                f'Starting calcsky on {sp_dp.filename[:-5]}, {this_dp.options["detector"]}')
            calcsky_output = subprocess.run(
                [my_config.parameters['dolphot_path']+"calcsky", sp_dp.filename[:-5], "10", "25", "2", "2.25", "2.00"], capture_output=True, text=True, cwd=proc_path)
            my_job.logprint(f'calcsky stdout: {calcsky_output}\n')
        elif this_dp.options["detector"] == "NIRCAM":
            my_job.logprint(
                f'Starting calcsky on {this_dp.filename[:-5]}, {this_dp.options["detector"]}')
            calcsky_output = subprocess.run(
                [my_config.parameters['dolphot_path']+"calcsky", sp_dp.filename[:-5], "15", "35", "4", "2.25", "2.00"], capture_output=True, text=True, cwd=proc_path)
            my_job.logprint(f'calcsky stdout: {calcsky_output}\n')
    
        if run_single == "T":
            my_job.logprint(f'firing event for {sp_dp.filename}\n')
            my_event = my_job.child_event(name="make_single_param", tag=sp_dp.dp_id,options={"target_id": this_event.options["target_id"], "dpid": sp_dp.dp_id, "to_run": this_event.options['to_run']
            }) 
            my_event.fire()

            
    # * Counter: Update parent job option to increase by 1 when done running splitgroups
    if run_single == "T":
        time.sleep(150)
    else:
        compname = this_event.options['compname']
        update_option = parent_job.options[compname]
        to_run = this_event.options['to_run']
        update_option += 1
        my_job.logprint(f'update_option: {update_option}, to_run: {to_run}\n')

        # When last image is done running splitgroups, run calcsky for outputs

        if update_option >= to_run:

            #! Makes CALCSKY fits to pipeline dataproducts
            prep_dp_id_list = ''
            for calcsky_output_file in glob.glob(proc_path + '*sky.fits'):
                cs_dp_filename = calcsky_output_file.split("/")[-1]
                my_job.logprint(f'created dataproduct for {cs_dp_filename}')
                cs_dp = wp.DataProduct(my_config,
                                       filename=cs_dp_filename, group="proc", data_type="image", subtype="calcsky")
                my_job.logprint(f'DP {cs_dp_filename}: {cs_dp}')
    
                # * Create event option for all prep_image dataproducts
                # prep_dp_id_list.append(cs_dp.dp_id)
                # ! Add dp id to list
                prep_dp_id_list += str(cs_dp.dp_id) + ', '
            #
    
            #! Makes the prep dp id list to a string
            prep_dp_id_list = str(prep_dp_id_list)
            my_job.logprint(f'List of prep image dps: {prep_dp_id_list}\n')
    
            my_job.logprint(f'DONE: ALL DATAPRODUCTS CREATED\n')
    
            #! Fire event to make DOLPHOT parameter file
            # ! Attempting to read in a list of dps as a config parameter
            # config_parameters[{'prep_image_dp_ids': prep_dp_id_list}]
            # my_job.logprint("Config Parameters: ", config_parameters)
            if warm == 0:
                my_event = my_job.child_event(name="make_param", options={
                    "target_id": this_event.options["target_id"],
                    "memory": "2G"})
            else:
                my_event = my_job.child_event(name="make_warm1_param", options={
                    "target_id": this_event.options["target_id"],
                    "memory": "2G"})
                
            my_event.fire()
            time.sleep(150)

        else:
            pass
