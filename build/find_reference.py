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

    my_dps = wp.DataProduct.select(config_id=my_config.config_id, data_type="image", subtype="drizzled") # dataproducts for the drizzled images for my_target
    #my_dps = wp.DataProduct.select(wp.si.DataProduct.filename.regexp_match("final*"), dpowner_id=my_job.config_id)
    # my_job.logprint(f"{my_dps}")

    my_job.logprint(f"{len(my_dps)} drizzled images found for {my_target.name}.")

# Choosing the best reference image
    if (
        'reference_filter' in my_config.parameters
    ):  # checking for set reference in parameter file
        ref_filt = my_config.parameters['reference_filter']
        ref_name = 'drizzle' + ref_filt + _drc.fits
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


#Add new dp for reference image
    new_ref_dp = ref_dp.make_copy(path=f"{my_target.datapath}/proc_default/", subtype="reference")
    #my_job.logprint(f"{new_ref_dp}")

#Set up count for prep_image
    comp_name = 'completed' + my_target.name
    options = {comp_name: 0} #images prepped to be updated when each job of prep_image finishes
    my_job.options = options

#Firing the next event
    tagged_dps = wp.DataProduct.select(config_id=my_config.config_id, data_type="image", subtype="tagged") #all tagged dps
    reference_dp = [new_ref_dp] #making reference dp into a list
    all_dps = tagged_dps+reference_dp #add reference dp to tagged dps
    #my_job.logprint(all_dps)
    to_run= len(all_dps)

    for dp in all_dps: #fire prep image for all tagged images and the reference image
        filename = dp.filename
        my_job.logprint(f"Firing prep image task for {filename}")
        dp_id = dp.dp_id #have to define dp_id outside of the event or else it sets it as the same for all dps
        my_event = my_job.child_event(
            name="prep_image", tag=dp_id,
            options={
                'dp_id': dp_id,
                'to_run': to_run,
                'compname': comp_name
            }
        )
        my_event.fire()
