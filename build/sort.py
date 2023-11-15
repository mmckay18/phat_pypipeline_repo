#! /usr/bin/env python

"""
Sort Task Description:
-------------------
This script is an integral part of a data processing pipeline that is responsible for the organization and processing of raw data products, with a primary focus on FITS files. It performs a series of essential tasks to facilitate data management and analysis:

1. Imports crucial libraries and modules, including 'wpipe' for pipeline management, 'astropy' for FITS file handling, 'glob' for file path matching, and 'pandas' for data manipulation.

2. Defines functions for setting up task masks and sorting raw data products based on specific criteria.

3. Ensures the script is the main entry point before proceeding with its execution.

4. Initializes a pipeline and job instance, which are fundamental for orchestrating data processing.

5. Retrieves and prints pipeline inputs, aiding in debugging and configuration.

6. Utilizes the 'make_unsorted_df' function, which sorts PHAST FLC files based on field information, creates a structured DataFrame of raw data products, and compiles a list of unique target names for further analysis.

7. Iterates through the unique target names, filtering data and creating individual target objects, streamlining the data processing workflow.

8. Prepares configurations for each target and manages the processing of raw data products. This includes copying images, starting tagging jobs, and tracking progress.

Note: This script is a critical component of a larger data processing pipeline and relies on the 'wpipe' library for efficient pipeline management and execution.
"""

import wpipe as wp
from astropy.io import fits
import glob
import pandas as pd


def register(task):
    """
    Pipeline
    This function sets up a task mask for the given task.

    Parameters:
    task (Task): The task to be registered.

    Returns:
    None
    """
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


def make_unsorted_df(my_input):
    """
    This function sorts PHAST FLC files by Field using the FITS file target name and proposal ID.
    It returns a DataFrame of all the raw data products and a list of targets.

    Parameters:
    my_input (Input): The first input to the pipeline.

    Returns:
    df (pd.DataFrame): DataFrame of all the raw data products.
    list(TARGET_LIST_df): List of targets.
    """
    # Initialize an empty list to store raw data product information
    rawdp_info_list = []

    input_data_df = pd.DataFrame(
        columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"]
    )
    # Loop through each raw data product in the input
    for my_rawdp in my_input.rawdataproducts:
        # Open the FITS file associated with the raw data product
        my_rawdp_fits_path = my_rawdp.path
        hdu = fits.open(my_rawdp_fits_path)
        # Extract necessary header information based on the telescope used
        TELESCOP = hdu[0].header["TELESCOP"]
        if ("JWST" not in TELESCOP):
            PROP_ID = str(hdu[0].header["PROPOSID"]).zfill(5)
            TARGNAME = hdu[0].header["TARGNAME"]
        else:
            TARGNAME = hdu[0].header["TARGPROP"]
            PROP_ID = hdu[0].header["PROGRAM"].zfill(5)
        FILENAME = hdu[0].header["FILENAME"]
        # Create a unique target name and add the information to the list
        TARGET_NAME = PROP_ID + "_" + TARGNAME
        hdu.close()

        rawdp_info = [FILENAME, PROP_ID, TARGNAME, TARGET_NAME]
        rawdp_info_list.append(rawdp_info)

    rawdp_df = pd.DataFrame(
        rawdp_info_list,
        columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"],
    )
    # * Append raw data information to data frame
    df = pd.concat([input_data_df, rawdp_df], ignore_index=True)

    # Dataframe of the list of targets
    TARGET_LIST_df = []
    TARGET_LIST_df = df["PROPOSID_TARGNAME"].unique()
    return df, list(TARGET_LIST_df)


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint(f"{my_pipe.inputs}")
    my_input = my_pipe.inputs[0]

    # Make a list of target names in Unsorted diectory proposal id and targetname
    unsorted_df, unsorted_targetnames_list = make_unsorted_df(
        my_pipe.inputs[0])

    # Interate through target list and assigns the raw dataproduct to target object
    for target_name in unsorted_targetnames_list:
        sorted_df = unsorted_df[unsorted_df["PROPOSID_TARGNAME"]
                                == target_name]
        # * Get list of Filename for each target
        rawdp_fn_list = sorted_df["FILENAME"].tolist()
        my_job.logprint(f"Filename {rawdp_fn_list}")
        # * Creates targets from the raw dataproducts in Unsorted directory
        my_targets = my_input.target(
            name=target_name, rawdps_to_add=rawdp_fn_list)
        my_job.logprint(
            f"{my_targets.name} {my_targets.target_id}, {my_targets.input_id}"
        )

    # Iterarte through target objects and create configuration for each target
    for target in my_input.targets:
        # * Create configeration for target and add parameters
        my_config = target.configuration(
            name="default", parameters={"target_id": target.target_id}
        )

        my_job.logprint(f"{target}")
        target_rawdata = f"{target.datapath}/raw_default/*.fits"
        target_dp_list = glob.glob(target_rawdata)
        tot_untagged_im = len(
            target_dp_list
        )  # * Get the total number of files in a given target
        my_job.logprint(
            f"# of untagged images for {target.name}, {target.target_id}: {tot_untagged_im}"
        )
        # * Copy images associated with the dataproducts from raw default to the proc directory

        # create job object options
        comp_name = "completed_" + target.name
        new_option = {comp_name: 0}
        my_job.options = new_option

        #! Iterate through target dataproducts and start tagging job
        dp_id_list = []
        for dp_fname_path in target_dp_list:
            dp_fname = dp_fname_path.split("/")[-1]
            my_rawdp = my_input.dataproduct(
                filename=dp_fname, group="raw", data_type="image"
            )
            # Append current dataproduct id to list
            dp_id_list.append(my_rawdp.dp_id)

            # Fire next task (tag_image)
            my_job.logprint("Firing Job")
            my_event = my_job.child_event(
                name="new_image",
                tag=my_rawdp.dp_id,
                options={
                    "dp_id": my_rawdp.dp_id,
                    "to_run": tot_untagged_im,
                    "filename": my_rawdp.filename,
                    "target_name": target.name,
                    "target_id": target.target_id,
                    "dp_fname_path": dp_fname_path,
                    "config_id": my_config.config_id,
                    "comp_name": "completed_" + target.name,
                    "memory": "300G"
                },
            )
            my_event.fire()
