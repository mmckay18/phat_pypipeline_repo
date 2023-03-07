#!/usr/bin/env python
import wpipe as wp
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


def tag_event_dataproduct(this_event):
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
    this_target_id = this_event.options["target_id"]
    config_id = this_event.options["config_id"]
    filename = this_event.options["filename"]
    # my_job.logprint(f"{config_id} {this_dp_id} {this_target_id} {filename}")
    # Call dataproduct
    # this_dp = wp.DataProduct(this_dp_id, filename=filename, group="proc")
    this_dp = wp.DataProduct(int(this_dp_id), group="proc")
    # my_job.logprint(f"{this_dp}")
    # my_job.logprint(f"{this_dp.target.datapath}")
    # * Dataproduct file pat
    procdp_path = this_dp.target.datapath + "/proc_default/" + this_dp.filename

    # Open FITS files and extract desired parameters to tag each image
    raw_hdu = fits.open(procdp_path)
    # my_job.logprint(f"{this_dp.path}")
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

    # tag_event_dataproduct
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
    config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")
    my_job.logprint(f"Config ID: {config_id}")

    # ! Start tag_event_dataproduct function
    tag_event_dataproduct(this_event)

    # my_job.logprint(this_event.options["dataproduct_list"]) # ! Doesnt work???

    if this_event.options["to_run"] == 0:
        # Fire next task (tag_image)
        my_job.logprint("Firing Job")
        my_event = my_job.child_event(
            name="astrodrizzle",
            options={
                "target_name": this_event.options["target_name"],
                "target_id": this_event.options["target_id"],
                "config_id": this_event.options["config_id"],
            },
        )
        my_event.fire()

    else:
        pass

    # TODO:
    # * Enable the pipeline to countdown the number of dataproducts for a target
    # * Fire astrodrizzle task after the last image for a target finish tagging
