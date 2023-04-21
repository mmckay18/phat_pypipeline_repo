#!/usr/bin/env python
import wpipe as wp
import os, subprocess
from glob import glob
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="DOLPHOT", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config
    this_event = my_job.firing_event
    my_job.logprint(this_event)

#Get parameter file
    param_dp_id = this_event.options["param_id_id"]
    param_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="text file", subtype="parameter", dp_id=param_dp_id)
    param_path = param_dp.relativepath
    param_filename = param_dp.filename

#Check that all files needed are present (ie. images, sky files, etc)

#Run Dolphot
dolphot_output = subprocess.run(["dolphot", "dolphotout", '-p' + param_path + param_filename], capture_output=True, text=True)

with open('dolphotout_stdout.log', 'w') as outlog:
    outlog.write(f'{dolphot_output.stdout}')
with open('dolphotout_stderr.log', 'w') as errlog:
    errlog.write(f'{dolphot_output.stderr}')

#Create dataproducts for Dolphot output files

out_files = glob('dolphotout*') #check that this gets file called just dolphotout
for file in out_files:
    wp.DataProduct(my_config, filename = file, group="proc", subtype = "dolphot output")