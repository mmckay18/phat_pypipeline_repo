#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob

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

if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    # Defining the target and filter
    parent_event = my_job.firing_event
    # ! Get target using the target id
    my_target = wp.Target(parent_event.options["target_id"])
    my_input = my_target.input
    my_job.logprint(f"{my_input}")
    proc_dp = my_input.procdataproducts
    for dp in proc_dp:
        my_job.logprint(f"{dp}")
        my_job.logprint(f"{dp.options}")
        if dp.option["targname"] == my_target.name:
            pass
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

    # target_path = my_target.path()

    # #Setting input parameters
    # config_file = f"{target_path}/conf_default/default.conf" #config file with custom parameter settings
    # driz_param = [skysub, driz_sep_scale, driz_cr_scale, driz_cr_snr, driz_sep_bits, final_bits, final_pixfrac, final_scale, final_kernal, reset_bits]  #possible parameters
    # input_dict = {}  #parameters that will be put into AstroDrizzle
    # for param in driz_param:
    #     if f"{param}" in config_file:
    #         #set param to value in config file otherwise leaves it as the default value (use pyfits.getval)
    #         #input_dict[param]=
    # if len(input_dict) >= 1:
    #     my_job.logprint(f"Custom AstroDrizzle parameters found for {my_target}: {input_dict}")
    # else:
    #     my_job.logprint(f"No custom AstroDrizzle parameters found for {my_target}, using default parameters.")
    # input_dict[clean]='Yes' #clean up directory

    # #Pulling the filters for the target
    # #make list of all dataproducts with targname of my_target (all_dp=[])
    # #Make list of the filter in each dataproduct
    # #Remove duplicates to make all_filters=[]
    # #num_of_allfilters= len(all_filters)
    # #my_job.logprint(f"{num_of_allfilters} filters found for {my_target}")

    # #Getting image list
    # i = 0
    # for j in all_filters:
    #     i+=1
    #     target_im=[]
    # #    target_im.append()#images where dataproduct option of Filter equals j (my_input=my_pipe.inputs[0], data=my_input.dataproducts) with file paths f"{target_path}/proc_default/*.fits"))
    # #    len_target_im = len(target_im)

    #     my_job.logprint(f"{len_target_im} images found for {my_target} in the {j} filter")

    # #Running AstroDrizzle
    #     my_job.logprint(f"Starting AstroDrizzle for {my_target} in filter {i}")

    #     astrodrizzle.AstroDrizzle(target_im, input_dict, output='final')
    #     my_job.logprint(f"AstroDrizzle complete for {my_target} in filter {i}")

    # #Firing next task
    #     if i == num_of_allfilters:
    #         my_job.logprint(f"AstroDrizzle complete for {my_target}")
    #         my_job.logprint(" ")
    #         next_event = my_job.child_event() #next event
    #         next_event.fire()
