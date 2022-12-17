#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob
from astropy.io import fits
import shutil


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


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_input = my_pipe.inputs[0]
    my_targets = my_input.targets
    # my_config = wp.configuration("default.conf")
    # my_job.logprint(f"{my_config.parameters.name}")

    # my_job.logprint(f"Targets: {my_targets.datapath}")

    for target in my_targets.datapath:
        # my_job.logprint(f"{target}/*.fits")
        fits_path = f"{target}/raw_default/*.fits"
        list_of_dp = glob.glob(fits_path)  # List of raw_default FLC fits files
        # my_job.logprint(f"List of dp in Target: {list_of_dp}")

        #! Get the total number of files in a given target
        tot_untagged_im = len(list_of_dp)
        my_job.logprint(f"# of untagged images for {target}: {tot_untagged_im}")

        # [done] Step 1: Copy images associated with the dataproducts from raw default to the proc directory - or copy the dataproducts from the config file?
        i = 0
        for dp_fname_path in list_of_dp:
            i += 1
            my_job.logprint(f"tagging image {i}")
            dp_fname = dp_fname_path.split("/")[-1]
            # my_job.logprint(dp_fname)
            # my_job.logprint({dp_fname_path})
            my_rawdp = my_input.dataproduct(filename=dp_fname, group="raw")
            # my_job.logprint(f" Dataproduct path {my_rawdp}")
            proc_path = f"{target}/proc_default/"
            # my_job.logprint(f"{type(proc_path)}")
            # my_job.logprint(f"Proc Directory {str(proc_path)}")
            my_job.logprint(f"Copy {dp_fname} -> {proc_path}")
            my_rawdp.make_copy(path=proc_path, group="proc")

            # Open FITS files and extract desired parameters to tag each image
            raw_hdu = fits.open(dp_fname_path)
            FILENAME = raw_hdu[0].header["FILENAME"]
            RA = raw_hdu[0].header["RA_TARG"]
            DEC = raw_hdu[0].header["DEC_TARG"]
            TELESCOP = raw_hdu[0].header["TELESCOP"]
            ORINT = raw_hdu[0].header["P1_ORINT"]
            EXPTIME = raw_hdu[0].header["EXPTIME"]
            EXPFLAG = raw_hdu[0].header["EXPFLAG"]
            CAM = raw_hdu[0].header["INSTRUME"]
            FILTER = raw_hdu[0].header["FILTER"]
            TARGNAME = raw_hdu[0].header["TARGNAME"]
            PROPOSALID = raw_hdu[0].header["PROPOSID"]

            raw_hdu.close()

            my_procdp = my_input.dataproduct(
                filename=dp_fname,
                group="proc",
                options={
                    "filename": FILENAME,
                    "ra": RA,
                    "dec": DEC,
                    "Telescope": TELESCOP,
                    "ORIENTATION": ORINT,
                    "Exptime": EXPTIME,
                    "Expflag": EXPFLAG,
                    "cam": CAM,
                    "filter": FILTER,
                    "targname": TARGNAME,
                    "proposalid": PROPOSALID,
                },
            )
            my_job.logprint(
                f" Dataproduct path {my_procdp.filename} {my_procdp.options}"  # Print the tags for each image
            )

            if i == 1:
                first_tag_targetname = str(PROPOSALID) + "-" + TARGNAME
                my_job.logprint(f"First tag {first_tag_targetname}")

            elif i == tot_untagged_im:
                my_job.logprint(f"Firing Next Task for Target: {first_tag_targetname}")
                my_job.logprint("   ")
                # Fire next task (tag_image)
                # my_job.logprint("Firing Job")
                # my_event = my_job.child_event(
                #     "new_image",
                # )
                # my_event.fire()

    # TODO:
    # - Count the total number of tagged images in for a given target
    # * Step 2: print target configuration file (default.config)

    # * Step 3: Use the default configuration to tag the associated images of a target
    # * Step 4: Fire next task

    this_config, this_job_id = run_pypiper()

    print("CONFIG ID:", this_config, "JOB ID:", this_job_id)
