#!/usr/bin/env python
import wpipe as wp
import numpy as np

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



# TODO:
# * Step 1: Copy images associated with the dataproducts from raw default


def run_pypiper():
    this_config = wp.ThisJob.config
    print("Running run_pypiper task")
    return this_config


if __name__ == "__main__":
    # conf_params = wp.ThisJob.config.parameters
    run_pypiper()
