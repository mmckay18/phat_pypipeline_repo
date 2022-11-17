#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="new_image", value="*")


"""
Original funtion docstring for tag_image.pl:

# This is a perl task that is part of the acs reduction pipeline.
# It's job is to review data that has been deposited into the target/proc   
# directory and tag each image with values from the header to make
# sorting of images simpler for later processing steps.
#
#
# This task is meant to be invoked in or on the proc subdirectory of a
# target.
# Configuration information is obtained from the target configuration
# utilites, which reference data stored in a configuration database.


"""


def run_pypiper():
    """Test function"""
    this_config = wp.ThisJob.config
    this_job_id = wp.ThisJob.job_id
    print("Running run_pypiper task")
    return this_config, this_job_id


def copy_rawdp_proc():

    my_dp = my_input.dataproduct(filename, group)


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_input = my_pipe.inputs[0]
    my_targets = my_input.targets

    my_job.logprint(f"Targets: {my_targets.datapath}")
    for target in my_targets.datapath:
        my_job.logprint(f"{target}/*.fits")
        fits_path = f"{target}/raw_default/*.fits"
        list_of_dp = glob.glob(fits_path)  # List of raw_default FLC fits files
        my_job.logprint(f"List of dp in Target: {list_of_dp}")

        # create dataproduct object
        for dp_fname in list_of_dp:
            my_dp = my_input.dataproduct(filename=dp_fname, group="raw")
            my_job.logprint(f" Dataproduct path {my_dp.suffix}")

            # Make a copy of the dataproduct to the proc dirtectory of the target
            proc_path = f"{target}/proc_default/"
            my_job.logprint(f"Proc dirtectory: {proc_path}")
            # my_dp.make_copy(path=proc_path)
            # my_job.logprint(f"Copying {dp_fname} to {target}/proc_default/*.fits")

    # my_job.logprint(f"Targets: {my_targets.dataraws}")
    # my_input = wp.Input(my_pipe, my_pipe.input_root)
    # my_input = my_pipe.inputs[0]
    # my_targets_list = my_pipe.inputs.target()
    # my_target_list = wp.Target(my_input)
    # my_job.logprint(f"Targets: {my_target_list}")

    # TODO:
    # * Step 1: Copy images associated with the dataproducts from raw default to the proc directory - or copy the dataproducts from the config file?

    # * Work In Progress: *
    # Copy raw dataproduct files to proc directory
    # for dp_filename in rawdp_fn_list:
    #     my_dp = my_input.dataproduct(dp_filename, group='raw')
    #     my_dp.make_copy(path=wp.Pipeline()) #point to path in string format, also point to config file - get proc directory from config file
    #     my_config.confpath

    # * Step 2: print target configuration file (default.config)
    # * Step 3: Use the default configuration to tag the associated images of a target
    # * Step 4: Fire next task

    # conf_params = wp.ThisJob.config.parameters

    this_config, this_job_id = run_pypiper()

    print("CONFIG ID:", this_config, "JOB ID:", this_job_id)


# TODO: !REMOVE THIS -> using for reference
# def sort_input_dataproduct(my_input):
#     """ """

#     for my_rawdp in my_input.rawdataproducts:

#         my_rawdp_fits_path = my_rawdp.path

#         # 1. Grab fitsfile header info directly from the dataproduct
#         hdu = fits.open(my_rawdp_fits_path)
#         prop_id = str(hdu[0].header["PROPOSID"])
#         targname = hdu[0].header["TARGNAME"]
#         hdu.close()

#         # ! Field target name
#         target_name = prop_id + "_" + targname

#         # Create a new test target
#         # TODO my_target = my_input.target('target', rawdps_to_add='raw.dat')
#         my_target = my_input.target(name=target_name, rawdps_to_add=my_rawdp)

#         # * Grab default configuration
#         # ? my_config = my_target.configurations[<name_of_config>]
#         my_config = my_target.configurations["default"]
#         # my_job.logprint(
#         #     f"Target: {my_target.name} Config: {my_config.name}, inputname: {my_rawdp.filename}"
#         # )

#         # my_job.logprint(f""
#         # create new dataproduct with the name of the input image
#         _dp = my_config.dataproduct(
#             filename=my_rawdp.filename,
#             relativepath=my_config.rawpath,
#             group="raw",
#             subtype="image",
#         )
#         # my_job.logprint(f"DP: {_dp.filename}") # * for debugging purposes
#     return _dp
