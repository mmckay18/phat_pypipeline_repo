#!/usr/bin/env python
import wpipe as wp
from astropy.io import fits

#! - It should take the data product ID it gets handed,
#! - get the file associated with it,
#! - and run the correct DOLPHOT masking routine for the camera that produced it.
#! - Then it should run the DOLPHOT splitgroups routine on the output,.
#! - Then it should run calcsky on the output from splitgroups.
#! - Finally, it needs to make data products for all of the output files,
#! - and check to see how many other prep_image tasks have completed for the target.
#! - Check against the total, and fire a done event if it's the last one.


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="prep_image_final", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config
    this_event = my_job.firing_event

    # Read in target and necessary dataproducts

    my_target = wp.Target(this_event.options["target_id"])

    ref_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image",
                                   subtype="dolphot input reference")  # reference image
    ref_dp_list = [ref_dp]  # making reference dp into a list

    tagged_dps = wp.DataProduct.select(
        dpowner_id=my_config.config_id, data_type="image", subtype="dolphot input")  # all other images

    all_dps = ref_dp_list + tagged_dps

# Create parameter file
    my_target_path = my_target.datapath

    # path to target's conf directory
    target_conf_path = my_target_path + "/conf_default/"
    my_job.logprint(f"Target Conf Path: {target_conf_path}")

    # TODO: Make target file
    param_filepath = target_conf_path + my_target.name + '.param'
    my_job.logprint(f"Parameter File Path: {param_filepath}")

    with open(param_filepath, 'w') as p:  # create empty file
        nimg = len(ref_dp) + len(tagged_dps)  # number of images
        p.write(f'Nimg={nimg}\n')  # write to file

    # Call dataproduct
    # this_dp = wp.DataProduct(int(this_dp_id), group="proc")

    # # Run DOLPHOT masking routine
    # # - Get

    # # config_id = this_event.options["config_id"]

    # my_job.logprint(f"This Event: {this_event}")
    # my_job.logprint(f"This Event: {this_event.options}")

    # # my_job.logprint(f"Config ID: {config_id}")

    # compname = this_event.options['compname']
    # update_option = parent_job.options[compname]
    # update_option += 1
    # to_run = this_event.options['to_run']

    # if update_option == to_run:
    #     #! Fire event to make DOLPHOT parameter file
    #     my_event = my_job.child_event(name="param_dolphot", options={
    #         "target_id": this_event.options["target_id"],
    #     },
    #     )
    #     my_event.fire()
