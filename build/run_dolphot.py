#!/usr/bin/env python

# Original script by Shellby Albrecht
# Modified and by Myles McKay
import wpipe as wp
# import os
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
            my_job.logprint(f"Running DOLPHOT on {param_dp.filename}")
            #dolphot_output = subprocess.run(
            #    ["dolphot", dolphotout, '-p' + param_path + "/" + param_filename], capture_output=True, text=True, cwd=procpath)
            #with open(dolphotlog, 'w') as outlog:
            #    outlog.write(f'{dolphot_output.stdout}')
            #with open(dolphotouterrlog, 'w') as errlog:
            #    errlog.write(f'{dolphot_output.stderr}')

            dolphot_output = subprocess.Popen(
                ["dolphot", dolphotout, '-p' + param_path + "/" + param_filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, cwd=procpath)
            
            for line in dolphot_output.stdout:
               # sys.stdout.write(line)
               my_job.logprint(line)
            dolphot_output.wait()
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

    
