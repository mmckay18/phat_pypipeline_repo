#!/usr/bin/env python

"""
Find Reference Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Using the target ID, it retrieves the targets associated dataproducts from the database with the subtype='DRIZZLED'. 

2.Looks for a reference image filter in the job configuration. If a reference image filter is found, it selects the drizzled image with the filter specified in the job configuration. If no reference image filter is found, it selects the drizzled image with the longest exposure time.

3. Update the seclected reference image subtype to 'reference' and group to 'proc'. 

4. Logs the number of drizzled images found for the target. This information is useful for tracking the progress of the pipeline.

5. Fires the prep_image task for all tagged images and the reference image.

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

import wpipe as wp
from astropy.io import fits
import numpy as np
import time
import os

# Task will look at all drizzled images for a target and choose the best
#  reference to use for DOLPHOT


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="find_ref", value="*")


# Setting up the task
if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

# Defining the target and dataproducts
    this_event = my_job.firing_event  # parent astrodrizzle event firing
    #   my_job.logprint(f"{parent_event}")

    my_target = wp.Target(this_event.options["target_id"])  # get the target

    my_config = my_job.config  # configuration for this job
    #   my_job.logprint(my_config)

    # dataproducts for the drizzled images for my_target
    my_dps = wp.DataProduct.select(
        config_id=my_config.config_id,
        subtype="DRIZZLED",
        )
    my_dps2 = wp.DataProduct.select(
           config_id=my_config.config_id,
           subtype="reference",
        )
    if len(my_dps2)>0:
        my_dps.extend(my_dps2)
    # my_dps = wp.DataProduct.select(wp.si.DataProduct.filename.regexp_match("final*"), dpowner_id=my_job.config_id)
    my_job.logprint(f"{my_dps}")

    my_job.logprint(
        f"{len(my_dps)} drizzled images found for {my_target.name}.")

# Choosing the best reference image
    try:
        ref_filt = str(my_config.parameters['reference_filter'])

        my_job.logprint(
            f"Reference image filter found, using {ref_filt} as reference filter."
        )
    except:  # setting reference as longest exposure time
        ref_filt = "None"
    my_job.logprint(f"Config has reference filter {ref_filt}")
    if "F" in ref_filt:
        for dp in my_dps:
            my_job.logprint(f"Checking for {ref_filt} in {dp.filename}")
            if ref_filt in dp.options["filter"]:
                ref_dp = dp
            else:
                continue

    try:
        filename = ref_dp.filename
    except:
        my_job.logprint(f"Didn't find {ref_filt} in any drizzled image")
        exposures = []
        for dp in my_dps:
            if "LONG" in dp.options["channel"]:
                continue
            exposures.append(dp.options["Exptime"])
            # filters.append(dp.options["filter"])
        exposuresarr = np.array(exposures)
        # filtersarr = np.array(filters)
        max_exp = exposuresarr.max()
        max_exp_ind = np.where(exposuresarr == max_exp)[0][0]
        ref_dp = my_dps[max_exp_ind]

    # Update dp for reference image
    my_job.logprint(f"Updating configuration to have {ref_dp.options['filter']} as reference")
    my_config.parameters['reference_filter'] = str(ref_dp.options["filter"])
    my_job.logprint(f"configuration reverence is now {my_config.parameters['reference_filter']}")
    new_ref_dp = wp.DataProduct(
        my_config, filename=ref_dp.filename, group="proc")
    new_ref_dp.subtype = "reference"
    new_ref_dp.options = {"detector": ref_dp.options["detector"],
                          "Exptime": ref_dp.options["Exptime"], "filter": ref_dp.options["filter"]}
    my_job.logprint(
        f"Reference is {new_ref_dp.filename} is subtype {new_ref_dp.subtype}")

# Define variable identifying the partition with most available memory
    best_partition = os.popen("""echo $(sinfo -o "%P %m" | sort -k2 -nr | head -n 1 | awk '{print $1}')""").read().strip('\n')

# Set up count for prep_image
    comp_name = 'completed_' + my_target.name
    # images prepped to be updated when each job of prep_image finishes
    options = {comp_name: 0}
    my_job.options[comp_name] = 0
    my_job.options = options
    if  my_job.options[comp_name] > 0:
        my_job.logprint("comp name is >0, exiting")
        sdfwh
# Firing the next event
    tagged_dps = wp.DataProduct.select(
        # config_id=my_config.config_id, data_type="SCIENCE", subtype="tagged")  # all tagged dps
        config_id=my_config.config_id, subtype="SCIENCE")  # all tagged dps
    print("LEN", len(tagged_dps))
    reference_dp = [new_ref_dp]  # making reference dp into a list
    all_dps = tagged_dps+reference_dp  # add reference dp to tagged dps
    my_job.logprint(f"ALL DPS {all_dps}")
    to_run = len(all_dps)
    try:
        test = my_config.parameters["run_single"]
    except:
        my_config.parameters["run_single"] = "F"
    for dp in all_dps:  # fire prep image for all tagged images and the reference image
        filename = dp.filename
        subtype = dp.subtype
        if subtype=="reference" and my_config.parameters["run_single"]=="T":
           continue
        my_job.logprint(f"Firing prep image task for {filename}")
        # have to define dp_id outside of the event or else it sets it as the same for all dps
        dp_id = dp.dp_id
        if subtype=="reference":
            my_event = my_job.child_event(
                name="prep_image", tag=dp_id,
                options={
                    'dp_id': dp_id,
                    'to_run': to_run,
                    'compname': comp_name,
                    'target_id': this_event.options['target_id'],
                    "memory": "50G",
                    "partition": best_partition
                }
            )

        else:
            my_event = my_job.child_event(
                name="prep_image", tag=dp_id,
                options={
                    'dp_id': dp_id,
                    'to_run': to_run,
                    'compname': comp_name,
                    'target_id': this_event.options['target_id'],
                    'partition': best_partition
                }
            )
        my_event.fire()
        time.sleep(1.178)
    time.sleep(150)
