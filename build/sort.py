#! /usr/bin/env python
import os
import wpipe as wp
from astropy.io import fits
import glob
import os


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


def copy_sorted_dir_to_data(sorted_dir_path, data_dir_path):
    """
    Copy sorted directory to the data directory for processing using unix command line

    Parameters:
        sorted_dir_path (str): Sorted directory

        data_dir_path (str): Data directory where the sorted directories are strored for processing


    Returns:
    """
    my_job.logprint(f"Copy {sorted_dir_path} to {data_dir_path}/")
    cmd = f"cp -R {sorted_dir_path} {data_dir_path}"
    os.system(cmd)


def add_proc_conf_log_default(data_dir_path):
    """
    Description:
        Adds proc_default, conf_deafalt, and log_deafalt directory

            Parameters:
                    data_dir_path (str): Path to data directory for processing

            Returns:
                Writes directories to data_dir_path
    """
    # Adding default directories to sorted directories
    my_job.logprint(f"Adding default directories to {data_dir_path}")
    proc_default_path = os.path.join(data_dir_path, "proc_default")
    conf_default_path = os.path.join(data_dir_path, "conf_default")
    log_default_path = os.path.join(data_dir_path, "log_default")

    os.mkdir(proc_default_path)
    os.mkdir(conf_default_path)
    os.mkdir(log_default_path)


def sort_fits(unsorted_dir_path):
    """
    Sorts HST WFC3/UVIS targets by plateifu and Target Name from target header and creates/stores in a directory in the parent directory

            Parameters:
                    unsorted_dir_path (str): Path to data directory with HST files

            Returns:
                    sorted_dir_path (str): Path to sorted directory with fits files with the same targetname and proposal ID
    """
    # List of unsorted fits files for processing
    unsorted_targ_list = glob.glob(unsorted_dir_path + "/*.fits")

    for input_filepath in unsorted_targ_list:
        hdu = fits.open(input_filepath)
        prop_id = str(hdu[0].header["PROPOSID"])
        target_name = hdu[0].header["TARGNAME"]
        filename = hdu[0].header["FILENAME"]
        hdu.close()

        # Set varibale for the name
        new_dir_name = prop_id + "_" + target_name
        sorted_dir_path = unsorted_dir_path + "/" + new_dir_name

        cmd = f"cp {input_filepath} {sorted_dir_path}"  # Unix command(cmd) to copy files to directory

        # Check if current filename exist and if not create a new dir and copies the current file
        if os.path.exists(sorted_dir_path) == True:
            my_job.logprint(f"Copy {filename} to {sorted_dir_path}")
            os.system(cmd)  # Run Unix to copy
            pass
        else:
            my_job.logprint(f"Writing directory: {sorted_dir_path}")
            os.mkdir(sorted_dir_path)
            os.system(cmd)  # Run Unix to copy

    return str(sorted_dir_path)


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("Getting Input directories/files")

    input_path = my_pipe.input_root  # input directory path
    my_job.logprint(f"Input FilePath:{input_path}")
    unsorted_input_pathlist = glob.glob(input_path + "/*")
    my_job.logprint("Start Sorting...")
    for unsorted_path in unsorted_input_pathlist:
        # Run sorting function on the unsorted data
        sorted_dir_path = sort_fits(unsorted_path)
        data_dir_path = str(my_pipe.data_root)

        # Copy sorted directories to data directory for processing
        copy_sorted_dir_to_data(sorted_dir_path, data_dir_path)
        add_proc_conf_log_default(sorted_dir_path)
    # !!! Requirement - Unsorted FITS files must be in a directory with excute permission
    # TODO Add edge case functionality when TARGNAME = ANY in unsorted FITS file header

    # Fire next event
    my_job.logprint("Firing Job")
    my_job.child_event("tag_image").fire()
