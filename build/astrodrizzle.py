#!/usr/bin/env python
import wpipe as wp
import numpy as np
import glob
from astropy.io import fits
import shutil


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="astrodrizzle", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_input = my_pipe.inputs[0]
    my_targets = my_input.targets
    my_job.logprint("Starting AstroDrizzle")
