#!/usr/bin/env python
"""
Run Dolphot Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Retrieves the target and configuration associated with the job. The target is retrieved from the options of the firing event, and the configuration is used to set up the processing and logging paths.

2. Iterates through all configuration dataproducts associated with the job. For each configuration dataproduct, it checks if the filename contains the string '.param' (the dolphot parameter file). If so, it retrieves the dataproduct and uses it to set up the Dolphot operation. If not, it ignores the dataproduct.

3. Retrieves the parameter file from the event options. This file contains parameters that control the behavior of the Dolphot operation.

4. Checks that all necessary files (images, sky files, etc.) are present for the Dolphot operation.

5. Constructs and executes the Dolphot command using the parameters from the parameter file. The output of the Dolphot operation is logged to a file.

6. The DOLPHOT output will the photometry catalog for the images   given by the users. 

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

# Original script by Shellby Albrecht
# Modified by Myles McKay
import wpipe as wp
import os
import time
import sys
import subprocess
from glob import glob
# from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="DOLPHOT", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_job.logprint("Starting DOLPHOT")
    my_config = my_job.config
    my_target = my_job.target
    this_event = my_job.firing_event
    my_job.logprint(this_event)
    my_job.logprint(this_event.options)
    my_config = my_job.config
    logpath = my_config.logpath
    procpath = my_config.procpath

# Get parameter file
    param_dp_id = this_event.options["param_dp_id"]
    my_job.logprint(f'{param_dp_id}, {type(param_dp_id)}')
    # param_dp = wp.DataProduct.select(
    #     dpowner_id=my_config.config_id, data_type="text file", subtype="parameter", dp_id=param_dp_id)

    for dp in my_config.confdataproducts:
        my_job.logprint(f"DP: {dp}, {dp.subtype}")
        if ".param" in dp.filename:
            param_dp = dp
            # Check that all files needed are present (ie. images, sky files, etc)
            my_job.logprint(f"{param_dp}, {param_dp.filename}")
            param_path = param_dp.relativepath
            param_filename = param_dp.filename
            dolphotout = procpath + "/" + my_target.name + ".phot"
            dolphoterrlog = logpath + "/" + "dolphotout_stderr.log"
            dolphotlog = logpath + "/" + "dolphotout_stdout.log"
            # # Run Dolphot
            logdp = my_job.logprint()
            logfile = logpath + "/" + logdp.filename
            my_job.logprint(f"Running DOLPHOT on {param_dp.filename}")
            dolphot_command = "cd "+procpath+" && " + \
                my_config.parameters["dolphot_path"]+"dolphot " + dolphotout + \
                ' -p' + param_path + "/" + param_filename + " > "+logfile
            my_job.logprint(dolphot_command)
            dolphot_output = os.system(dolphot_command)
            #    ["dolphot", dolphotout, '-p' + param_path + "/" + param_filename + " > " + logfilename], cwd=procpath)
            #    ["dolphot", dolphotout, '-p' + param_path + "/" + param_filename], capture_output=True, text=True, cwd=procpath)
            # with open(dolphotlog, 'w') as outlog:
            #    outlog.write(f'{dolphot_output.stdout}')
            # with open(dolphotouterrlog, 'w') as errlog:
            #    errlog.write(f'{dolphot_output.stderr}')

            # dolphot_output = subprocess.Popen(
            #    [my_config.parameters["dolphot_path"]+"dolphot", dolphotout, '-p' + param_path + "/" + param_filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, cwd=procpath)

            # for line in dolphot_output.stdout:
            #   # sys.stdout.write(line)
            #   my_job.logprint(line)
            # dolphot_output.wait()
            # Create dataproducts for Dolphot output files

            # check that this gets file called just dolphotout
            phot_dp = wp.DataProduct(
                my_config, filename=dolphotout, group="proc", subtype="dolphot output")
            my_job.logprint(
                f"Created dataproduct for {dolphotout}, {phot_dp}")
            out_files = glob('*.phot.*')
            for file in out_files:
                dolphot_output_dp = wp.DataProduct(
                    my_config, filename=file, group="proc", subtype="dolphot output")
                my_job.logprint(
                    f"Created dataproduct for {file}, {dolphot_output_dp}")
        else:
            pass
    next_event = my_job.child_event(
        name="dolphot_done",
        options={"dp_id": phot_dp.dp_id}
    )  # next event
    next_event.fire()
    time.sleep(150)
