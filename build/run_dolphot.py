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
    _temp = task.mask(source="*", name="DOLPHOT_warm", value="*")

import signal
def handler(signum, frame):
    print("Forever is over!")
    sys.exit(1)
    raise ValueError("end of time")

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

    param_dp = wp.DataProduct(int(param_dp_id))
    # Check that all files needed are present (ie. images, sky files, etc)
    my_job.logprint(f"{param_dp}, {param_dp.filename}")
    param_path = param_dp.relativepath
    param_filename = param_dp.filename
    if my_config.parameters["run_single"]=="T":
        dolphotout =  procpath + "/" + param_filename + ".phot"
    else:
        dolphotout = procpath + "/" + my_target.name + ".phot"
    dolphoterrlog = logpath + "/" + "dolphotout_stderr.log"
    dolphotlog = logpath + "/" + "dolphotout_stdout.log"
    # # Run Dolphot
    logdp = my_job.logprint()
    logfile = logpath + "/" + logdp.filename
    if os.path.isfile(dolphotout):
        my_job.logprint(f"Not Running DOLPHOT on {param_dp.filename} because the phot file exists")
    else:
        my_job.logprint(f"creating command DOLPHOT on {param_dp.filename}")
        dolphot_command = "cd "+procpath+" && " + \
            my_config.parameters["dolphot_path"]+"dolphot " + dolphotout + \
            ' -p' + param_path + "/" + param_filename + " >> "+logfile
        my_job.logprint(dolphot_command)
        print(dolphot_command)
        print("made it past command creation")
        dolphot_output = os.system(dolphot_command)

    # check that this gets file called just dolphotout
    signal.signal(signal.SIGALRM, handler)    
    signal.alarm(1000)
    try:
        head_tail = os.path.split(dolphotout)
        phot_dp = wp.DataProduct(
            my_config, filename=head_tail[1], group="proc", subtype="dolphot output")
    except:
        ValueError("Failed to create phot file DP. Exiting.") 
    signal.alarm(0)
    my_job.logprint(
        f"Created dataproduct for {dolphotout}, {phot_dp}")
    out_files = glob(procpath+'/*.phot.*')
    if len(out_files) < 5:
        raise exception("too few output files")

    if "warm" in this_event.name:
        warmstart_file = dolphotout+".warmstart"
        prewarm_file = dolphotout+".prewarm"
        if os.path.isfile(warmstart_file):
            my_job.logprint(f"Not overwriting {warmstart_file}")
        else:    
            catcom = "cat "+dolphotout+" | awk '{print $1,$2,$3,$4,$11,$6}' >"+warmstart_file
            os.system(catcom)
            catcom2 = "mv "+dolphotout+" "+prewarm_file
            os.system(catcom2)
        for file in out_files:
            if "prewarm" not in file:
                mvcom = "mv "+file+" "+file+".prewarm"
                os.system(mvcom)
        head_tail = os.path.split(warmstart_file)
        warmstart_dp = wp.DataProduct(
            my_config, filename=head_tail[1], group="proc", subtype="warmstart_file")
        my_job.logprint(f"Created dataproduct for {warmstart_file}")
        next_event = my_job.child_event(
            name="warmstart_done",
            options={"target_id": my_target.target_id, "warmdpid": warmstart_dp.dp_id, "memory": "5G"}
            )  # next event
        next_event.fire()
        time.sleep(150)


    else:
        for file in out_files:
            head_tail = os.path.split(file)
            dolphot_output_dp = wp.DataProduct(
                my_config, filename=head_tail[1], group="proc", subtype="dolphot output")
            my_job.logprint(
                f"Created dataproduct for {file}, {dolphot_output_dp}")
        if my_config.parameters["run_single"] == "T":
            next_event = my_job.child_event(
              name="dolphot_done",
              options={"dp_id": phot_dp.dp_id, "memory": "5G", "to_run": this_event.options["to_run"], "tracking_job_id": this_event.options["tracking_job_id"]}
            )  # next event
            next_event.fire()
            time.sleep(150)


        else:
            outfile_stats = os.stat(dolphotout)
            size = outfile_stats.st_size / (1024 * 1024 * 1024)
            mem = "10G"
            if size > 3:
                mem = "100G"
            if size > 5:
                mem = "150G"
            if size > 10:
                mem = "200G"
            if size > 30:
                mem = "750G"

            next_event = my_job.child_event(
              name="dolphot_done",
              options={"dp_id": phot_dp.dp_id, "memory": mem}
            )  # next event
            next_event.fire()
            time.sleep(150)

    
