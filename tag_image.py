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


def tagging(this_event):
    """
    Tags incoming dataproducts from fired event

    Parameters:
    -----------
    this_event : Event(OptOwner)
        a fired event of a WINGS pipeline.

    Returns:
    --------
    logprint the options for the current dataproduct in the log file.

    """

    my_job.logprint(f"{this_event.options}")
    this_dp_id = this_event.options["dp_id"]
    # this_dp_filename = this_event.options["filename"]
    this_target_id = this_event.options["target_id"]

    this_dp = wp.DataProduct(int(this_dp_id))
    dp_fitspath = this_dp.path
    my_job.logprint(f"FITS path {dp_fitspath}")

    # Open FITS files and extract desired parameters to tag each image
    raw_hdu = fits.open(dp_fitspath)
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

    # Tagging
    this_dp_id = this_event.options["dp_id"]
    this_dp = wp.DataProduct(
        int(this_dp_id),
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
            "dp_id": this_dp_id,
            "target_id": this_target_id,
        },
    )

    my_job.logprint(this_dp.options)


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    # ! Get the firing event obj
    this_event = my_job.firing_event  # parent event obj
    my_job.logprint(f"This Event: {this_event}")
    this_config = my_job.config

    # ! Start tagging function
    tagging(this_event)

    # my_job.logprint(this_event.options["dataproduct_list"]) # ! Doesnt work???

    if this_event.options["to_run"] == 0:
        # Fire next task (tag_image)
        my_job.logprint("Firing Job")
        # need to send the targetname and filter to astrodrizzle
        try:
           submission_type = this_config.parameter["submission_type"]
           my_event = my_job.child_event(
              name="astrodrizzle",
              options={
                "targname": this_event.options["target_name"],
                "target_id": this_event.options["target_id"], "submission_type": submission_type
                # "dataproduct_list": this_event.options["dataproduct_list"],
              }
        except:
           my_event = my_job.child_event(
              name="astrodrizzle",
              options={
                "targname": this_event.options["target_name"],
                "target_id": this_event.options["target_id"],
                # "dataproduct_list": this_event.options["dataproduct_list"],
              }
           )  
           
        my_event.fire()

    else:
        pass

    # TODO:
    # * Enable the pipeline to countdown the number of dataproducts for a target
    # * Fire astrodrizzle task after the last image for a target finish tagging:

    #         # Fire next task (tag_image)
    #         my_job.logprint("Firing Job")
    #         my_event = my_job.child_event(
    #             "astrodrizzle",
    #             options={"dp_id": my_procdp.dp_id, "to_run": tot_untagged_im},
    #         )
    #         my_event.fire()

    #         # if i == 1:
    #         #     first_tag_targetname = str(PROPOSALID) + "-" + TARGNAME
    #         #     my_job.logprint(f"First tag {first_tag_targetname}")

    #         # elif i == tot_untagged_im:
    #         #     my_job.logprint(f"Firing Next Task for Target: {first_tag_targetname}")
    #         #     my_job.logprint("   ")
    #         #     # Fire next task (tag_image)
    #         #     my_job.logprint("Firing Job")
    #         #     my_event = my_job.child_event(
    #         #         "astrodrizzle",
    #         #     )
    #         #     my_event.fire()
