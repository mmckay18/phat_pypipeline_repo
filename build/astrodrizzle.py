#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob
import os
from astropy.io import fits
from drizzlepac import *
from stsci.tools import teal

teal.unlearn("astrodrizzle")


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

    my_target = wp.Target(
        parent_event.options["target_id"]
    )  # Get target using the target id
    #   my_job.logprint(f"{my_target}")

    my_target_path = my_target.datapath
    target_proc_path = my_target_path + "/proc_default"
    os.chdir(target_proc_path)  # makes the correct proc directory the working directory

    my_config = my_job.config  # Get configuration for the job
    # my_job.logprint(f"{my_config}")

    my_dp = (
        my_config.procdataproducts
    )  # Get dataproducts associated with configuration (ie. dps for my_target)
    #   my_job.logprint(f"{my_dp}")

    filters = []  # Making array of filters for target
    for dp in my_dp:
        #       my_job.logprint(f"{dp}")  # Should return each dataproduct
        #       my_job.logprint(dp.options)
        filters.append(dp.options["filter"])
    all_filters = list(
        set(filters)
    )  # Remove duplicates to get array of different filters for target
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
    driz_param = [
        "reset_bits",
        "skysub",
        "sky_method",
        "driz_sep_pixfrac",
        "driz_sep_scale",
        "driz_sep_bits",
        "driz_sep_kernel",
        "combine_type",
        "combine_nlow",
        "combine_nhigh",
        "driz_cr_scale",
        "driz_cr_snr",
        "final_bits",
        "final_pixfrac",
        "final_scale",
        "final_kernel",
    ]  # possible parameters
    input_dict = {}  # parameters that will be put into AstroDrizzle
    #   my_job.logprint(my_config.parameters)
    for param in driz_param:
        if param in my_config.parameters:
            param_val = my_config.parameters[
                param
            ]  # set param to value in config file otherwise leaves it as the default value
            input_dict[param] = param_val
    if len(input_dict) >= 1:

        my_job.logprint(
            f"Custom AstroDrizzle parameters found for {my_target.name}: {input_dict}"
        )

    else:
        my_job.logprint(
            f"No custom AstroDrizzle parameters found for {my_target.name}, using default parameters."
        )
    input_dict["clean"] = "Yes"  # clean up directory

    if (
        "driz_sep_kernel" not in my_config.parameters
    ):  # adjusting individual kernel default
        if (
            "driz_sep_pixfrac" not in my_config.parameters
            or my_config.parameters["driz_sep_pixfrac"] == 1
        ):
            if (
                "driz_sep_scale" not in my_config.parameters
                or my_config.parameters["driz_sep_scale"] == 1
            ):
                input_dict["driz_sep_kernel"] = "lanczos3"
                if "driz_sep_pixfrac" not in my_config.parameters:
                    input_dict["driz_sep_pixfrac"] = 1
                if "driz_sep_scale" not in my_config.parameters:
                    input_dict["driz_sep_scale"] = 1
    if (
        "driz_sep_kernel" in my_config.parameters
        and my_config.parameters["driz_sep_kernel"] == "lanczos3"
    ):
        if "driz_sep_pixfrac" not in my_config.parameters:
            input_dict["driz_sep_pixfrac"] = 1
        if "driz_sep_scale" not in my_config.parameters:
            input_dict["driz_sep_scale"] = 1

    if "final_kernel" not in my_config.parameters:  # adjusting final kernel default
        if (
            "final_pixfrac" not in my_config.parameters
            or my_config.parameters["final_pixfrac"] == 1
        ):
            if (
                "final_scale" not in my_config.parameters
                or my_config.parameters["final_scale"] == 1
            ):
                input_dict["final_kernel"] = "lanczos3"
                if "final_pixfrac" not in my_config.parameters:
                    input_dict["final_pixfrac"] = 1
                if "final_scale" not in my_config.parameters:
                    input_dict["final_scale"] = 1
    if (
        "final_kernel" in my_config.parameters
        and my_config.parameters["final_kernel"] == "lanczos3"
    ):
        if "final_pixfrac" not in my_config.parameters:
            input_dict["final_pixfrac"] = 1
        if "final_scale" not in my_config.parameters:
            input_dict["final_scale"] = 1

    # Getting image list and setting filter specific parameters
    i = 0  # to count the number of filters AstroDrizzle has run for
    for j in all_filters:
        target_im = []
        for dp in my_dp:
            if (
                dp.options["filter"] == j
            ):  # for the filter j, pulls out which dps have the same filter
                target_im.append(dp.filename)
        inputall = target_im[0]  # the first image name in the array
        for ii in range(len(target_im) - 1):
            inputall = (
                inputall + "," + target_im[ii + 1]
            )  # writes string of file names for input to AstroDrizzle
        len_target_im = len(target_im)

        my_job.logprint(
            f"{len_target_im} images found for {my_target.name} in the {j} filter"
        )

        my_job.logprint(
            f"{len_target_im} images found for {my_target} in the {j} filter"
        )

        log_name = "astrodrizzle" + j + ".log"  # filter specific log file name
        ind_input_dict = input_dict.copy()
        ind_input_dict[
            "runfile"
        ] = log_name  # adding specific log names to input dictionary

        out_name = "final" + j  # final product name
        ind_input_dict[
            "output"
        ] = out_name  # adding filter specific final product name to input dictionary

        if (
            len_target_im >= 4 and "combine_type" not in my_config.parameters
        ):  # with at least 4 input images, median is better than default of minmed
            ind_input_dict["combine_type"] = "median"
            ind_input_dict[
                "combine_nhigh"
            ] = 1  # for 4 input images nhigh should be 1, could need to be raised for >4

        # Running AstroDrizzle
        my_job.logprint(f"Starting AstroDrizzle for {my_target.name} in filter {i}")
        if (
            len_target_im == 1
        ):  # for filters with only 1 input image, only the sky subtraction and final drizzle can run
            astrodrizzle.AstroDrizzle(
                input=inputall,
                context=True,
                build=True,
                driz_separate=False,
                median=False,
                blot=False,
                driz_cr=False,
                **ind_input_dict,
            )
        else:
            astrodrizzle.AstroDrizzle(
                input=inputall, context=True, build=True, **ind_input_dict
            )
        my_job.logprint(f"AstroDrizzle complete for {my_target.name} in filter {i}")

        # Create Dataproducts for drizzled images
        drizzleim_path = (
            "final" + j + "_drc.fits"
        )  # Already in proc directory so this is just the file name
        driz_hdu = fits.open(drizzleim_path)

        FILENAME = driz_hdu[0].header["FILENAME"]  # Parameters from header
        TELESCOP = driz_hdu[0].header["TELESCOP"]
        INSTRUME = driz_hdu[0].header["INSTRUME"]
        TARGNAME = driz_hdu[0].header["TARGNAME"]
        RA_TARG = driz_hdu[0].header["RA_TARG"]
        DEC_TARG = driz_hdu[0].header["DEC_TARG"]
        PROPOSID = driz_hdu[0].header["PROPOSID"]
        EXPTIME = driz_hdu[0].header["EXPTIME"]
        PA_V3 = driz_hdu[0].header["PA_V3"]
        DETECTOR = driz_hdu[0].header["DETECTOR"]
        FILTER = driz_hdu[0].header["FILTER"]
        driz_hdu.close()

        driz_dp = wp.DataProduct(
            my_config,
            filename=drizzleim_path,
            group="proc",  # Create dataproduct owned by config for the target
            options={
                "Filename": FILENAME,
                "Telescope": TELESCOP,
                "Instrument": INSTRUME,
                "Target_name": TARGNAME,
                "RA": RA_TARG,
                "DEC": DEC_TARG,
                "ProposalID": PROPOSID,
                "Exposure_time": EXPTIME,
                "Position_angle": PA_V3,
                "Detector": DETECTOR,
                "Filter": FILTER,
            },
        )

        dp_ids = []  # Get list of new dp ids to send to next task
        dp_ids.append(driz_dp.dp_id)

        my_job.logprint(
            f"Dataproduct for drizzled image in filter {j}: {driz_dp.options}"
        )

        i += 1  # count finished filter

        # Firing next task
        if i == num_all_filters:
            my_job.logprint(f"AstroDrizzle step complete for {my_target.name}")
            next_event = my_job.child_event(
                name="find_ref",
                options={
                    "dp_id": dp_ids,
                    "target_name": parent_event.options["target_name"],
                    "target_id": parent_event.options["target_id"],
                    "config_id": parent_event.options["config_id"],
                },
            )  # next event
            next_event.fire()
