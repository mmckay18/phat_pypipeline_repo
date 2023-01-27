#!/usr/bin/env python
import wpipe as wp
import numpy as np

# import glob
from astropy.io import fits

# import shutil
from drizzlepac import photeq
from drizzlepac import astrodrizzle


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="astrodrizzle", value="*")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Old pipeline docstring
# This is a perl task that is part of the acs reduction pipeline.
# It's job is to run astrodrizzle on images in a target directory
# to flag cosmic rays for dolphot.
#
#
# This task is meant to be invoked in a target subdirectory -
# Configuration information is obtained from the target configuration
# utilites, which reference data stored in a configuration database.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_input = my_pipe.inputs[0]
    my_targets = my_input.targets
    my_job.logprint("Starting AstroDrizzle")

    # my_targets = wp.Target(my_input)
    # my_job.logprint(f"{my_targets.name}")
    for targetname in my_targets.name:
        my_job.logprint(f"{targetname}")
        new_target = my_input.target(targetname)

        my_job.logprint(f"{new_target}")
        my_job.logprint(f"{my_input.procdataproducts}")

    #! 1 - Seperate target images by filter
    #! 2 - Run astrodrizzle on each target image using the default configuration
    #! 3 - read in config file for each target
    #! 4 - Fire next task
