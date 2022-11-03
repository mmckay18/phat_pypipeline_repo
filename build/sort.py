#! /usr/bin/env python
from asyncio import DatagramProtocol
import os
import wpipe as wp
from astropy.io import fits
import glob
import shutil
import pandas as pd


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


def make_unsorted_df(my_input):
    """
    Sorts PHAST FLC files into targets and stores them into a pandas dataframe

                Parameters:
                        my_input(): wp.Pipeline.inputs[0]

                Returns:
                        binary_sum (str): Binary string of the sum of a and b
                        df1 (pd.DataFrame): Dataframe of all the the raw dataproducts
                        list(TARGET_LIST_df): list of targets

    """

    rawdp_info_list = []
    input_data_df = pd.DataFrame(
        columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"]
    )
    for my_rawdp in my_input.rawdataproducts:
        my_rawdp_fits_path = my_rawdp.path
        hdu = fits.open(my_rawdp_fits_path)
        PROP_ID = str(hdu[0].header["PROPOSID"])
        TARGNAME = hdu[0].header["TARGNAME"]
        FILENAME = hdu[0].header["FILENAME"]
        TARGET_NAME = PROP_ID + "_" + TARGNAME
        hdu.close()

        rawdp_info = [FILENAME, PROP_ID, TARGNAME, TARGET_NAME]
        # * my_job.logprint(f"{rawdp_info}") # for debugging purposes
        rawdp_info_list.append(rawdp_info)

    rawdp_df = pd.DataFrame(
        rawdp_info_list,
        columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"],
    )
    # * Append raw data information to data frame
    df1 = pd.concat([input_data_df, rawdp_df], ignore_index=True)

    # my_job.logprint(f"FINAL_DF, # {len(df1)}") # * Prints the number of raw dataproducts in the DataFrame - for debugging purposes
    # my_job.logprint(f"{df1.head(10)}")

    # Dataframe of the list of targets
    TARGET_LIST_df = []
    TARGET_LIST_df = df1["PROPOSID_TARGNAME"].unique()
    return df1, list(TARGET_LIST_df)


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


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_input = my_pipe.inputs[0]

    # Make a list of target names in Unsorted diectory proposal id and targetname
    unsorted_df, unsorted_targetnames_list = make_unsorted_df(my_pipe.inputs[0])

    my_job.logprint(f"{unsorted_targetnames_list}")  # * for debugging purposes
    for target_name in unsorted_targetnames_list:
        my_job.logprint(f"{target_name}")  # * for debugging purposes
        sorted_df = unsorted_df[unsorted_df["PROPOSID_TARGNAME"] == target_name]

        # Prints all the images associated with the target in the sort log file
        my_job.logprint(f"{sorted_df.head()}")

        # Get list of Filename for each target
        rawdp_fn_list = sorted_df["FILENAME"].tolist()
        # my_job.logprint(f"{rawdp_fn_list}")  # * for debugging purposes

        # Creates targets from the raw dataproducts in Unsorted directory
        my_target = my_input.target(name=target_name, rawdps_to_add=rawdp_fn_list)

        # * Work In Progress: *
        # Copy raw dataproduct files to proc directory
        # for dp_filename in rawdp_fn_list:
        #     my_dp = my_input.dataproduct(dp_filename, group='raw')
        #     my_dp.make_copy(path=wp.Pipeline()) point to path in string format, also point to config file - get proc directory from config file
        # my_config.confpath

        # ! The raw_default keeps populating with all the images from both targets - we just fixed this

    # TODO: FIRE TAG IMAGE FROM THE PIPELINE
    my_job.logprint("Firing Job")
    my_event = my_job.child_event(
        "new_image",
    )
    my_event.fire()

    this_job = wp.ThisJob.job_id
    print("Job ID: ", this_job)

    # ? Why does each target have the all target raw datprodcuts for eah target?
    # ? What is the data produxct after I nmake the target?
    # ? Do I make new data products aftermaking the target?
    # ? What EXACTLY DOES TAGING THE IMAGE MEAN?
