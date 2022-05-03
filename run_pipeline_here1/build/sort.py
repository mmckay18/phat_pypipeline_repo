#! /usr/bin/env python
import os
import wpipe as wp
from astropy.io import fits
import glob
import os


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


def sort_fits(unsorted_dir_path):
    """
    Sorts HST WFC3/UVIS targets by plateifu and Target Name from target header and creates/stores in a directory in the parent directory

            Parameters:
                    unsorted_dir_path (str): Path to data directory with HST files

            Returns:
                    None
    """

    unsorted_targ_list = glob.glob(unsorted_dir_path + "/*.fits")
    print(unsorted_targ_list)

    for input_filepath in unsorted_targ_list:
        my_job.logprint(input_filepath)
        hdu = fits.open(input_filepath)
        filter_name = hdu[0].header["FILTER"]
        prop_id = str(hdu[0].header["PROPOSID"])
        target_name = hdu[0].header["TARGNAME"]
        rootname = hdu[0].header["ROOTNAME"]
        filename = hdu[0].header["FILENAME"]
        hdu.close()

        new_dir_name = prop_id + "_" + target_name  # Set varibale for the name
        field_dir = unsorted_dir_path + "/" + new_dir_name
        # my_job.logprint(f"Field Directory Path: {field_dir}")

        cmd = f"cp {input_filepath} {field_dir}"  # Unix command(cmd) to copy files to directory

        # Check if current filename exist and if not create a new dir and copies the current file
        if os.path.exists(field_dir) == True:
            my_job.logprint(f"Copy {filename} to {field_dir}")
            os.system(cmd)  # Run Unix to copy
            pass
        else:
            my_job.logprint(f"Writing directory: {field_dir}")
            os.mkdir(field_dir)
            os.system(cmd)  # Run Unix to copy


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("Getting Input directories/files")

    input_path = my_pipe.input_root  # input directory path
    my_job.logprint(f"Input FilePath:{input_path}")
    unsorted_input_pathlist = glob.glob(input_path + "/*")
    # my_job.logprint(f"Unsorted FilePath:{unsorted_input_path}")
    for unsorted_path in unsorted_input_pathlist:
        # Run sorting function on the unsorted data
        sort_fits(unsorted_path)

    # TODO Make robust to allow the processing of files not in a directory

    # for unsorted_filepath in unsorted_input_path:
    #     my_job.logprint(f"Sorting data in {unsorted_filepath}")
    #     if os.path.isdir(unsorted_filepath) == True:
    #         my_job.logprint(
    #             f" {unsorted_filepath} is a directory, {os.path.isdir(unsorted_filepath)}"
    #         )
    #         continue

    #     else:
    #         unsorted_filepath = input_path
    #         my_job.logprint(f"{unsorted_filepath} is not a directory")
    #         break

    # i = 0
    # for my_input in my_pipe.inputs:
    #     # my_job.logprint(f"{i} Current Input Path: {my_input}")

    #     i += 1
    #     my_job.logprint(i, "Start Sorting")

    my_job.logprint("Firing Job")
    my_job.child_event("run_pypiper").fire()
