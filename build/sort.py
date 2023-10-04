#! /usr/bin/env python
# from asyncio import DatagramProtocol
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
    Sorts PHAST FLC files by Field using the FITS file targetname and proposal ID

                Parameters:
                        my_input(): wp.Pipeline.inputs[0]

                Returns:
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
        TELESCOP = hdu[0].header["TELESCOP"]
        if ("JWST" not in TELESCOP):
            PROP_ID = str(hdu[0].header["PROPOSID"])
            TARGNAME = hdu[0].header["TARGNAME"]
        else:
            TARGNAME = hdu[0].header["TARGPROP"]
            PROP_ID = hdu[0].header["PROGRAM"]
        FILENAME = hdu[0].header["FILENAME"]
        FILTER = hdu[0].header["FILTER"]
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


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint(f"{my_pipe.inputs}")  # * for debugging purposes
    my_input = my_pipe.inputs[0]

    # Make a list of target names in Unsorted diectory proposal id and targetname
    unsorted_df, unsorted_targetnames_list = make_unsorted_df(
        my_pipe.inputs[0])

    # my_job.logprint(f"{unsorted_targetnames_list}")  # * for debugging purposes
    for target_name in unsorted_targetnames_list:
        sorted_df = unsorted_df[unsorted_df["PROPOSID_TARGNAME"]
                                == target_name]
        # * Get list of Filename for each target
        rawdp_fn_list = sorted_df["FILENAME"].tolist()
        # my_job.logprint(f"{rawdp_fn_list}")  # * for debugging purposes
        print("FN ", rawdp_fn_list)
        # * Creates targets from the raw dataproducts in Unsorted directory
        my_targets = my_input.target(
            name=target_name, rawdps_to_add=rawdp_fn_list)
        my_job.logprint(
            f"{my_targets.name} {my_targets.target_id}, {my_targets.input_id}"
        )
    # Iterarte through targets
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
        # * Step 1: Copy images associated with the dataproducts from raw default to the proc directory - or copy the dataproducts from the config file?
        # i = tot_untagged_im
        dp_id_list = []
        # create hjob option
        comp_name = "completed_" + target.name
        new_option = {comp_name: 0}
        my_job.options = new_option
        #! Iterate through target dataproducts and start tagging job
        for dp_fname_path in target_dp_list:
            # my_job.logprint(f"tagging image {dp_fname_path}")
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
                    "dataproduct_list": dp_id_list,
                    "dp_fname_path": dp_fname_path,
                    "config_id": my_config.config_id,
                    "comp_name": "completed_" + target.name,
                },
            )
            my_event.fire()
