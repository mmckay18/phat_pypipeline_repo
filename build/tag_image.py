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

    # my_job.logprint(f"{this_event.options}")
    this_dp_id = this_event.options["dp_id"]
    this_target_id = this_event.options["target_id"]
    # config_id = this_event.options["config_id"]
    # filename = this_event.options["filename"]
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

    # my_job.logprint(this_dp.options)


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    # ! Get the firing event obj
    # * Selecting parent event object
    this_event = my_job.firing_event
    config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")

    #! Write parent job event option parameters
    compname = this_event.options["comp_name"]
    parent_job = this_event.parent_job
    my_job.logprint(f"parent_job options: {parent_job.options}")
    update_option = parent_job.options[compname]
    update_option += 1
    to_run = this_event.options["to_run"]
    my_job.logprint(f"{update_option}/{to_run} TAGGED")

    # ! Start tag_event_dataproduct function
    tag_event_dataproduct(this_event)

    if this_event.options["to_run"] == update_option:
        my_job.logprint(f"This Job Options: {my_job.options}")
        # comp_name = "completed_" + this_event.options["target_name"]
        new_option = {compname: 0}
        my_job.options = new_option
        my_job.logprint(f"Updated Job Options: {my_job.options}")

        # List of all filters in target
        my_config = my_job.config  # Get configuration for the job
        my_dp = wp.DataProduct.select(
            dpowner_id=my_config.config_id, data_type="image", subtype="tagged"
        )  # Get dataproducts associated with configuration (ie. dps for my_target)

        filters = []  # Making list of filters for target
        for dp in my_dp:
            filters.append(dp.options["filter"])
            all_filters = set(
                filters
            )  # Remove duplicates to get array of different filters for target

        my_config.parameters["filters"] = ",".join(
            all_filters
        )  # add list of filters to configuration
        # ? my_config.save()  # save configuration to database
        my_job.logprint(f"MY CONFIG PARM: {my_config.parameters}")

        num_all_filters = len(all_filters)
        my_job.logprint(f"{num_all_filters} filters found for target {dp.target.name}")

        #! Fire next task astrodrizzle
        my_job.logprint("FIRING NEXT ASTRODRIZZLE TASK")
        comp_name = "completed_" + this_event.options["target_name"]
        for i in all_filters:
            my_job.logprint(f"{i},{type(str(i))}")
            my_event = my_job.child_event(
                name="astrodrizzle",
                options={
                    "target_name": this_event.options["target_name"],
                    "target_id": this_event.options["target_id"],
                    "config_id": this_event.options["config_id"],
                    "filters_to_run": len(all_filters),  # num of filter to run
                    "filter": str(i),
                },
                tag=str(
                    i
                ),  #! need to set a tag for each event if firering multiple events with the same name
            )
            my_event.fire()

        # my_job.logprint(f"Firing Event Options: {my_event.options}")

    else:
        pass

    # TODO:
    # * Enable the pipeline to countdown the number of dataproducts for a target
    # * Fire astrodrizzle task after the last image for a target finish tagging
########################################
# Code originally from astrodrizzle that can be used here instead

# my_config = my_job.config  # Get configuration for the job

# my_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="tagged") # Get dataproducts associated with configuration (ie. dps for my_target)

# filters = []  # Making array of filters for target
# for dp in my_dp:
# filters.append(dp.options["filter"])
# all_filters = set(filters) # Remove duplicates to get array of different filters for target

# my_config.parameters['filters']= ','.join(all_filters) #add list of filters to configuration

# num_all_filters = len(all_filters)
# my_job.logprint(f"{num_all_filters} filters found for target {my_target.name}")
