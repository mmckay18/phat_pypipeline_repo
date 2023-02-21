#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob
import os

# import glob
from astropy.io import fits

# import shutil
from drizzlepac import photeq
from drizzlepac import astrodrizzle


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="astrodrizzle", value="*")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Old pipeline docstring
# This is a perl task that is part of the acs reduction pipeline.
# It's job is to run astrodrizzle on images in a target directory
# to flag cosmic rays for dolphot.
#
#
# This task is meant to be invoked in a target subdirectory -
# Configuration information is obtained from the target configuration
# utilites, which reference data stored in a configuration database.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# if __name__ == "__main__":
#     my_pipe = wp.Pipeline()
#     my_job = wp.Job()
#     my_input = my_pipe.inputs[0]
#     my_targets = my_input.targets
#     my_job.logprint("Starting AstroDrizzle")

#     # my_targets = wp.Target(my_input)
#     # my_job.logprint(f"{my_targets.name}")
#     for targetname in my_targets.name:
#         my_job.logprint(f"{targetname}")
#         new_target = my_input.target(targetname)

#         my_job.logprint(f"{new_target}")
#         my_job.logprint(f"{my_input.procdataproducts}")

#     #! 1 - Seperate target images by filter
#     #! 2 - Run astrodrizzle on each target image using the default configuration
#     #! 3 - read in config file for each target
#     #! 4 - Fire next task

# Setting up the task
if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
#   my_job.logprint(f"{my_job}")

    # Defining the target and filters
    parent_event = my_job.firing_event
#   my_job.logprint(f"{parent_event}")

    parent_job = parent_event.parent_job
#   my_job.logprint(f"{parent_job}")

    my_target = wp.Target(parent_event.options["target_id"])  # Get target using the target id
#   my_job.logprint(f"{my_target}")

    my_target_path = my_target.datapath
    target_proc_path = my_target_path + '/proc_default'
    os.chdir(target_proc_path)  # makes the correct proc directory the working directory

    my_config = my_job.config # Get configuration for the job
#   my_job.logprint(f"{my_config}")

    my_dp = my_config.procdataproducts  # Get dataproducts associated with configuration (ie. dps for my_target)
#   my_job.logprint(f"{my_dp}")

    filters = []  # Making array of filters for target
    for dp in my_dp:
#       my_job.logprint(f"{dp}")  # Should return each dataproduct
#       my_job.logprint(dp.options)
        filters.append(dp.options['filter'])
    all_filters = list(set(filters))  # Remove duplicates to get array of different filters for target
    num_all_filters = len(all_filters)
    my_job.logprint(f"{num_all_filters} filters found for target {my_target.name}")

    ################################

    # if dp.option["targname"] == my_target.name:
    #    pass
    # my_job.logprint(f"{dp.options['filter']}")


    # # ! Get the list of dataproducts for this target and gets there filter parameter from dataproducts options
    # target_path = my_target.datapath
    # proc_path = target_path + "/proc_default/"
    # for fits_filename in glob.glob(proc_path + "/*.fits"):
    #     my_job.logprint(f"{fits_filename}")
    #     my_dp = wp.DataProduct(my_target.input, fits_filename, group="proc")
    #     my_job.logprint(f"{my_dp}")

    # proc_dp = my_input.procdataproducts
    # # my_job.logprint(f"{proc_dp}")
    # for dp in proc_dp:
    #     my_job.logprint(f"{dp}")
    # my_job.logprint(f"{dp.options}")
    # my_job.logprint(f"{dp.options['filter']}")

    # my_target = parent_event.options["targname"]
    # my_filter = parent_event.options["filter"]

    # my_job.logprint(f"{parent_target}")
    # my_job.logprint(f"{parent_filter}")
    ###############################################

    # Setting input parameters
    driz_param = ['skysub', 'driz_sep_scale', 'driz_cr_scale', 'driz_cr_snr', 'driz_sep_bits', 'final_bits',
                'final_pixfrac', 'final_scale', 'final_kernal', 'reset_bits']  # possible parameters
    input_dict = {}  # parameters that will be put into AstroDrizzle
#   my_job.logprint(my_config.parameters)
    for param in driz_param:
        if param in my_config.parameters:
            param_val = my_config.parameters[param]  # set param to value in config file otherwise leaves it as the default value
            input_dict[param] = param_val
    if len(input_dict) >= 1:
        my_job.logprint(f"Custom AstroDrizzle parameters found for {my_target}: {input_dict}")
    else:
        my_job.logprint(f"No custom AstroDrizzle parameters found for {my_target}, using default parameters.")
    input_dict["clean"] = 'Yes'  # clean up directory
# can add any other parameters here that we want to default to different values than the astrodrizzle defaults

# Getting image list
    i = 0  # to count the number of filters astrodrizzle has run for
    for j in all_filters:
        i += 1
        target_im = []
        for dp in my_dp:
            if dp.options['filter'] == j:  # for the filter j, pulls out which dps have the same filter
                target_im.append(dp.options['filename'])
        inputall = target_im[0]  # the first image name in the array
        for ii in range(len(target_im) - 1):
            inputall = inputall + ',' + target_im[ii + 1]  # writes string of file names for input to astrodrizzle
        len_target_im = len(target_im)

        my_job.logprint(f"{len_target_im} images found for {my_target} in the {j} filter")

# Running AstroDrizzle
        my_job.logprint(f"Starting AstroDrizzle for {my_target} in filter {i}")

        astrodrizzle.AstroDrizzle(input=inputall, input_dict= input_dict, output='final')
        my_job.logprint(f"AstroDrizzle complete for {my_target} in filter {i}")

# Firing next task
        if i == num_all_filters:
            my_job.logprint(f"AstroDrizzle complete for {my_target}")
#            my_job.logprint(" ")
#            next_event = my_job.child_event() #next event
#            next_event.fire()
