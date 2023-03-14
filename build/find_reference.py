#!/usr/bin/env python
import wpipe as wp
from astropy.io import fits
import numpy as np

# Task will look at all drizzled images for a target and choose the best reference to use for DOLPHOT


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="find_ref", value="*")


# Setting up the task
if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    # Defining the target and dataproducts
    parent_event = my_job.firing_event  # parent astrodrizzle event
    #   my_job.logprint(f"{parent_event}")

    my_target = wp.Target(parent_event.options["target_id"])  # get the target

    my_config = my_job.config  # configuration for this job
    #   my_job.logprint(my_config)

    my_dps = wp.DataProduct.select(
        wp.si.DataProduct.filename.regexp_match("final*"), dpowner_id=my_job.config_id
    )  # dataproducts for the drizzled images for my_target
    # my_job.logprint(f"{my_dps}")

    my_job.logprint(f"{len(my_dps)} drizzled images found for {my_target.name}.")

    # Choosing the best reference image
    if (
        "reference_filter" in my_config.parameters
    ):  # checking for set reference in parameter file
        ref_filt = my_config.parameters["reference_filter"]
        ref_name = 'final' + ref_filt + _drc.fits
        my_job.logprint(
            f"Reference image parameter found, using {ref_name} as reference image."
        )

        ref_dp = wp.DataProduct.select(
            group="proc", dpowner_id=my_job.config_id, filename=ref_name
        )  # pull correct dp for reference
    else:  # setting reference as longest exposure time
        exposures = []
        # filters=[]
        for dp in my_dps:
            exposures.append(dp.options["Exposure_time"])
            # filters.append(dp.options["Filter"])
        exposuresarr = np.array(exposures)
        # filtersarr = np.array(filters)
        max_exp = exposuresarr.max()
        max_exp_ind = np.where(exposuresarr == max_exp)[0][0]
        ref_dp = my_dps[max_exp_ind]
        # y_job.logprint(f"{my_dps}")
        # my_job.logprint(f"{exposuresarr}")
        # my_job.logprint(f"{ref_dp}")
        my_job.logprint(f"Reference image for {my_target.name} is {ref_dp.filename}")

        ##if filter is on edge and other is in middle then use other, if both on edge then use longest exposure and then closest to middle

    ##Add option to indicate reference image
    #    ref_dp.option["Reference"] = 'Yes'
    #    my_job.logprint(f"{ref_dp.options}")

    # Firing the next event
    my_event = my_job.child_event(
        name="deepCR",
        options={
            "target_name": parent_event.options["target_name"],
            "target_id": parent_event.options["target_id"],
            "config_id": parent_event.options["config_id"],
            "reference_id": ref_dp.dp_id,
        },
    )
    my_event.fire()
