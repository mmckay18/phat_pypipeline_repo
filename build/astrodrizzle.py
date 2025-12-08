#!/usr/bin/env python

"""
Astrodrizzle Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Navigates to the /proc directory of the target from the firing parent event and loads the appropriate configuration file. This configuration file contains parameters that control the behavior of the pipeline.

2. Retrieves the filter from the firing event. This filter is used to select specific raw data products from the list, creating a filtered list of data products for further processing.

3. If the RUN_DEEPCR parameter is set to 'T' and the files are Ultraviolet Imaging Spectrograph (UVIS) files, it runs the DeepCR algorithm, which is designed to identify and replace cosmic rays in the images. If the detector is Infrared (IR) or if RUN_DEEPCR is set to 'F', this step is skipped.

4. Sets the default parameters for AstroDrizzle using the first image in the list. AstroDrizzle is a software package used for the automated combination of dithered images into a single composite image. These parameters are then appended to the configuration file.

5. Executes AstroDrizzle on the list of images using the default parameters. This step combines the dithered images into a single, cleaned image then fires find_reference.py.

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

import wpipe as wp
import numpy as np
import glob
import os
from astropy.io import fits
from drizzlepac import *
from stsci.tools import teal
import random
import time

teal.unlearn("astrodrizzle")


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="astrodrizzle", value="*")


# Setting up the task
if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    #   my_job.logprint(f"{my_job}")
    
    #add in a random sleep time to unsync it from parallel astrodrizzle jobs writing to the same dir
    timeDelay = random.randrange(0, 60)
    time.sleep(timeDelay)

    # Defining the target and filter
    this_event = my_job.firing_event
    #   my_job.logprint(f"{parent_event}")

    parent_job = this_event.parent_job

    my_target = wp.Target(
        this_event.options["target_id"]
    )  # Get target using the target id

    my_filter = this_event.options["filter"]  # Get filter
    my_config = my_job.config  # Get configuration for the job

    my_job.logprint(
        f"Running Astrodrizzle task for {my_target.name} in filter {my_filter}.")

    my_target_path = my_target.datapath
    target_proc_path = my_config.procpath + "/"
    # makes the correct proc directory the working directory
    os.chdir(target_proc_path)

    # my_job.logprint(f"{my_config}")

    # Setting input parameters
    # driz_param = [
    #    'skysub',
    #    'sky_method',
    #    #'driz_sep_pixfrac',
    #    #'driz_sep_scale',
    #    'driz_sep_bits',
    #    'driz_sep_kernel',
    #    'combine_type',
    #    'combine_nlow',
    #    'combine_nhigh',
    #    'driz_cr_scale',
    #    'driz_cr_snr',
    #    'final_bits',
    #    'final_pixfrac',
    #    'final_scale',
    #    'final_kernel',
    # ]  # possible parameters
    input_dict = {}  # parameters that will be put into AstroDrizzle
    # my_job.logprint(my_config.parameters)
    # for param in driz_param:
    #    if param in my_config.parameters:
    #        param_val = my_config.parameters[
    #            param
    #        ]  # set param to value in config file otherwise leaves it as the default value
    #        input_dict[param] = param_val
    # if len(input_dict) >= 1:

    #    my_job.logprint(
    #        f"Custom AstroDrizzle parameters found for {my_target.name}: {input_dict}"
    #    )

    # else:
    #    my_job.logprint(
    #        f"No custom AstroDrizzle parameters found for {my_target.name}, using default parameters."
    #    )
    input_dict["clean"] = True  # clean up directory
    input_dict["preserve"] = False

    # if (
    #    "driz_sep_kernel" not in my_config.parameters
    # ):  # adjusting individual kernel default
    #    #if (
    #    #    "driz_sep_pixfrac" not in my_config.parameters
    #    #    or my_config.parameters["driz_sep_pixfrac"] == 1
    #    #):
    #    #    if (
    #    #        "driz_sep_scale" not in my_config.parameters
    #    #        or my_config.parameters["driz_sep_scale"] == "INDEF"
    #    #    ):
    #     input_dict["driz_sep_kernel"] = "lanczos3"
    #    #        if "driz_sep_pixfrac" not in my_config.parameters:
    #    #            input_dict["driz_sep_pixfrac"] = 1
    #    #        if "driz_sep_scale" not in my_config.parameters:
    #    #            input_dict["driz_sep_scale"] = "INDEF"
    # if (
    #    "driz_sep_kernel" in my_config.parameters
    #    and my_config.parameters["driz_sep_kernel"] == "lanczos3"
    # ):
    #    if "driz_sep_pixfrac" not in my_config.parameters:
    #        input_dict["driz_sep_pixfrac"] = 1
    #    if "driz_sep_scale" not in my_config.parameters:
    #        input_dict["driz_sep_scale"] = "INDEF"
    input_dict["driz_sep_kernel"] = "lanczos3"

    input_dict["final_kernel"] = "lanczos3"

    # Getting image list and setting filter specific parameters
    my_dp = wp.DataProduct.select(
        dpowner_id=my_config.config_id, group="proc"
    )
    target_im = []
    print("DPs are", len(my_dp))
    for dp in my_dp:
        my_job.logprint(f"testing {dp.filename}")
        try:
            check = dp.options["filter"]
        except:
            continue
        if (
            dp.options["filter"] == my_filter
        ):  # for the filter j, pulls out which dps have the same filter
            target_im.append(dp.filename)
            detector = dp.options["detector"]
    inputall = target_im[0]  # the first image name in the array
    #! DeepCR
    config_param = my_config.parameters
    try:
        resetbits = config_param["deepcr_resetbits"]
    except:
        resetbits = 4096
    if detector == "UVIS":
        input_dict["resetbits"] = resetbits
    if detector == "WFC":
        input_dict["resetbits"] = resetbits
    if detector == "IR":
        input_dict["driz_cr"] = False
        input_dict["resetbits"] = 0
        input_dict["median"] = False
        input_dict["blot"] = False
    for ii in range(len(target_im) - 1):
        inputall = (
            inputall + "," + target_im[ii + 1]
        )  # writes string of file names for input to AstroDrizzle
    len_target_im = len(target_im)

    my_job.logprint(
        f"{len_target_im} images found for {my_target.name} in the {my_filter} filter"
    )

    log_name = "astrodrizzle" + my_filter + ".log"  # filter specific log file name
    ind_input_dict = input_dict.copy()
    ind_input_dict[
        "runfile"
    ] = log_name  # adding specific log names to input dictionary

    out_name = my_target.name + '_' + my_filter  # final product name
    ind_input_dict[
        "output"
    ] = out_name  # adding filter specific final product name to input dictionary
    # Create Dataproducts for drizzled images
    print("DETEC", detector)
    if ("IR" in detector):
        drizzleim_path = (
            out_name + "_drz.fits"
        )  # Already in proc directory so this is just the file name
    else:
        drizzleim_path = (
            out_name + "_drc.fits"
        )  # Already in proc directory so this is just the file name
    if os.path.isfile(drizzleim_path):
        my_job.logprint(f"Drizzled image {drizzleim_path} already exists, skipping")
    else:
        if (
            len_target_im >= 4 and "combine_type" not in my_config.parameters
        ):  # with at least 4 input images, median is better than default of minmed
            ind_input_dict["combine_type"] = "median"
            # ind_input_dict[
            #    "combine_nhigh"
            # ] = 1  # for 4 input images nhigh should be 1, could need to be raised for >4

        # Running AstroDrizzle
        my_job.logprint(
            f"Starting AstroDrizzle for {my_target.name} in filter {my_filter}")

        if len_target_im == 1:  # for filters with only 1 input image, only the sky subtraction and final drizzle can run
            ind_input_dict["blot"] = False
            ind_input_dict["driz_separate"] = False
            ind_input_dict["driz_cr"] = False
            ind_input_dict["median"] = False
            my_job.logprint('astrodrizzle.AstroDrizzle(input=')
            my_job.logprint(inputall)
            my_job.logprint(', context=True, build=True,')
            my_job.logprint(ind_input_dict)
            my_job.logprint(",)")
            astrodrizzle.AstroDrizzle(input=inputall, context=True, build=True, **ind_input_dict,
                                  )
        else:
            my_job.logprint('astrodrizzle.AstroDrizzle(input=')
            my_job.logprint(inputall)
            my_job.logprint(',context=True, build=True,')
            my_job.logprint(ind_input_dict)
            my_job.logprint(",)")

            astrodrizzle.AstroDrizzle(
                # input=inputall, context=True, build=True, preserve=False, driz_cr=False, blot=False, median=False, **ind_input_dict,
                input=inputall, context=True, build=True, **ind_input_dict,
            )
            my_job.logprint(''.join(["astrodrizzle input: ",inputall," , build=True , "]))
            print("Input dictionary:")
            print(ind_input_dict)
        my_job.logprint(
            f"AstroDrizzle complete for {my_target.name} in filter {my_filter}")

    driz_hdu = fits.open(drizzleim_path)

    FILENAME = driz_hdu[0].header["FILENAME"]  # Parameters from header
    TELESCOP = driz_hdu[0].header["TELESCOP"]
    INSTRUME = driz_hdu[0].header["INSTRUME"]
    TARGNAME = driz_hdu[0].header["TARGNAME"]
    RA_TARG = driz_hdu[1].header["RA_APER"]
    DEC_TARG = driz_hdu[1].header["DEC_APER"]
    PROPOSID = driz_hdu[0].header["PROPOSID"]
    EXPTIME = driz_hdu[0].header["EXPTIME"]
    PA_V3 = driz_hdu[1].header["ORIENTAT"]
    DETECTOR = driz_hdu[0].header["DETECTOR"]
    CHANNEL = driz_hdu[0].header["DETECTOR"]
    FILTER = my_filter
    driz_hdu.close()

    driz_dp = wp.DataProduct(
        my_config,
        filename=drizzleim_path,
        # Create dataproduct owned by config for the target
        group="proc", subtype="DRIZZLED",
        options={
            "filename": FILENAME,
            "telescope": TELESCOP,
            "instrument": INSTRUME,
            "target_name": TARGNAME,
            "ra": RA_TARG,
            "dec": DEC_TARG,
            "proposalid": PROPOSID,
            "Exptime": EXPTIME,
            "position_angle": PA_V3,
            "detector": DETECTOR,
            "channel": CHANNEL,
            "filter": FILTER,
            "type": "DRIZZLED",
        },
    )

    my_job.logprint(
        f"Dataproduct for drizzled image in filter {my_filter}: {driz_dp.options}"
    )

    compname = this_event.options['comp_name']
    update_option = parent_job.options[compname]
    update_option += 1
    to_run = this_event.options['to_run']
    my_job.logprint(update_option)
    my_job.logprint(to_run)

    #! Define variable identifying the partition with most available memory
    best_partition = os.popen("""echo $(sinfo -o "%P %m" | sort -k2 -nr | head -n 1 | awk '{print $1}')""").read().strip('\n')

    # Firing next task
    if update_option >= to_run:
        my_job.logprint(
            f"AstroDrizzle step complete for {my_target.name}, firing find reference task.")
        next_event = my_job.child_event(
            name="find_ref",
            options={"target_id": this_event.options["target_id"], "memory": "3G", "partition": best_partition}
        )  # next event
        next_event.fire()
        time.sleep(150)
