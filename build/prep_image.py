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
    _temp = task.mask(source="*", name="prep_image", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    this_event = my_job.firing_event  # parent event obj
    parent_job = this_event.parent_job
    #config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")
    #my_job.logprint(f"Config ID: {config_id}")

    compname = this_event.options['compname']
    update_option = parent_job.options[compname]
    update_option += 1
    to_run = this_event.options['to_run']

    if update_option == to_run:
    # Fire event
        my_event = my_job.child_event(name="param_dolphot", options={
            "target_id": this_event.options["target_id"],
         },
     )
        my_event.fire()
