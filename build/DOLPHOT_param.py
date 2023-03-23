#!/usr/bin/env python
import wpipe as wp
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="dolphot_param", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config

#Read in target and necessary dataproducts

    my_target = wp.Target(parent_event.options["target_id"])

    ref_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="dolphot input reference") #reference image

    tagged_dps = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="dolphot input") #all other images

    ref_sky = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="reference sky") #reference sky image

    tagged_sky = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="sky") #all other sky images

#Create parameter file
    my_target_path = my_target.datapath
    target_conf_path = my_target_path + "/conf_default/" #path to target's conf directory

    with open(target_conf_path + my_target.name + '.param', 'w') as p: #create empty file

        nimg = len(ref_dp) + len(tagged_dps) #number of images
        p.write(f'Nimg={nimg}')

#Define image specific parameters
        im0_file = ref_dp.filename #get rid of extension
        #write to file

        #other image names
        #write to file

        #other parameters, if in config file then write that parameter to the param file, otherwise use the ones I set here

#Define global parameters
        #If in config file then write that parameter to the param file, otherwise use the ones I set here

