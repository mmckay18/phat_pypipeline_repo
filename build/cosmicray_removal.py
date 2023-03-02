#!/usr/bin/env python
import wpipe as wp
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="cosray_remove", value="*")



if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    this_event = my_job.firing_event  # parent event obj
    config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")
    my_job.logprint(f"Config ID: {config_id}")
    
    
    my_event = my_job.child_event(
            name="astrodrizzle",
            options={
                "targname": this_event.options["target_name"],
                "target_id": this_event.options["target_id"],
                "config_id": this_event.options["config_id"],
                # "dataproduct_list": this_event.options["dataproduct_list"],
            },
        )
    my_event.fire()