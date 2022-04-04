#! /usr/bin/env python
import os
import wpipe as wp
import glob
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("Preparing targets")
    for my_input in my_pipe.inputs:
        for my_dp in my_input.rawdataproducts:
            my_target = my_input.target(name=my_dp.filesplitext[0])
            print(my_target.name)
            for my_conf in my_target.configurations:
                # print(my_conf)
                my_job.logprint("Starting target " + my_target.name +
                                " config " + my_conf.name)
                input_filepath = "/Users/mmckay/phd_projects/phat_pipeline_dev/phast_pypiper_v3/input/inputA"
                
                # my_job.child_event(
                #     "run_pypiper", options={"config_id": my_conf.config_id}
                # ).fire()
