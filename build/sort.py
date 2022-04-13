#! /usr/bin/env python
import os
import wpipe as wp


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("Preparing targets")
    print("Doing stuff with target")
    # print(my_pipe.inputs, type(my_pipe.inputs))
    # for my_input in my_pipe.inputs:
    #     # print(my_input, type(my_input))
    #     for my_dp in my_input.rawdataproducts:
    #         my_target = my_input.target(name=my_dp.filesplitext[0])
    #         print(
    #             my_dp,
    #             my_target,
    #         )
    #         # print(my_target.configurations)
    #         # for my_conf in my_target.configurations:
    #         #     # print(my_conf)
    #         #     # my_job.logprint("Starting target " + my_target.name +
    #         #     #                 " config " + my_conf.name)
    my_job.logprint("Firing Job")
    my_job.child_event("run_pypiper").fire()
