#!/usr/bin/env python
from deepCR import deepCR
import wpipe as wp
from astropy.io import fits
import numpy as np
from glob import glob
import time


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="deepCR", value="*")


def imgclean(imgname, mdl, threshold, update = True):
    """
    imgname: input image name
    mdl: deepCR model
    threshold: threshold for deepCR
    update: update the original fits file or not
    Three options for CR identification in the pipeline running:
    
    1. regular default pipeline (same as old pipeline):  
    - Overwrite all original DQ cr flag (to zero) for raw flc.fits data from MAST, and then perform astrodrizzle to identify DQ flag for cr
    - NOT need to specify the parameter "resetbits" in drizzlepac.astrodrizzle.AstroDrizzle, using default = 4096
    - "resetbits" allow to specify which DQ bits should be reset to a value of 0; prior to starting any of AstroDrizzle process steps

    2. NOT run deepCR within the pipeline, BUT use deepCR-processed images
    - The raw flc.fits images haven been processed using deepCR beforehand. The original DQ flag cr from MAST raw data has been removed, and updated to the DQ cr flags using deepCR
    - In the pipeline, NEED to specify the parameter "resetbits = 0" in drizzlepac.astrodrizzle.AstroDrizzle, to KEEP all deepCR-identified DQ bits, and then perform astrodrizzle TOO
    - The cr identified in both steps would be combined together to the final DQ flag

    3. RUN deepCR within the pipeline, go through deepCR task
    - Input need: trained model; self-defined threshold; update= True
    - And see option 2., also NEED to specify the parameter "resetbits = 0" to keep all deepCR-identified DQ bits, and then perform astrodrizzle TOO
    Below is the python function to perform deepCR on each image, and update the DQ cr flag:
    
    """
    print('image_name:', imgname)
    print('threshold:', threshold)
    print('update is', update)
    # open the image with all extensions
    if update:
        imgall = fits.open(imgname, mode='update')
    else:
        imgall = fits.open(imgname)
                       
    # process each chip/extension of the image, manually normalize the input
    imgorichip1 = imgall[1].data
    imgorichip1mean = imgorichip1.mean()
    imgorichip1std = imgorichip1.std()
    imgnormchip1 = (imgorichip1 - imgorichip1mean) / imgorichip1std
    imgorichip2 = imgall[4].data
    imgorichip2mean = imgorichip2.mean()
    imgorichip2std = imgorichip2.std()
    imgnormchip2 = (imgorichip2 - imgorichip2mean) / imgorichip2std
    #print('----chip1----')
    maskimgchip1, cleaned_imgchip1 = mdl.clean(imgnormchip1, threshold=threshold, inpaint='medmask')
    maskimgchip1 = np.float32(maskimgchip1)
    dqchip1 = imgall[3].data
    #print('original MAST DQ:', len(np.where((dqchip1&4096) == 4096)[0]))
    dqchip1[dqchip1&4096 == 4096] ^= 4096
    #print('remove original check:', len(np.where((dqchip1&4096) == 4096)[0]))
    dqchip1[maskimgchip1 == 1] |= 4096
    #print('after deepCR DQ:', len(np.where((dqchip1&4096) == 4096)[0]))
    imgall[3].data = dqchip1   
    #print('CR DQ update done')
    
    # print('----chip2----')/
    maskimgchip2, cleaned_imgchip2 = mdl.clean(imgnormchip2, threshold=threshold, inpaint='medmask')
    maskimgchip2 = np.float32(maskimgchip2)
    dqchip2 = imgall[6].data
    #print('original MAST DQ:', len(np.where((dqchip2&4096) == 4096)[0]))
    dqchip2[dqchip2&4096 == 4096] ^= 4096
    #print('remove original check:', len(np.where((dqchip2&4096) == 4096)[0]))
    dqchip2[maskimgchip2 == 1] |= 4096
    #print('after deepCR DQ:', len(np.where((dqchip2&4096) == 4096)[0]))
    imgall[6].data = dqchip2   
    #print('CR DQ update done')
    
    if update:
        imgall.flush()
        print('update original fits file done')
    else:
        print('original fits file not updated!')
    return


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    this_event = my_job.firing_event  # parent event obj

    # config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")
    my_job.logprint(f"Options: {this_event.options}")
    # my_job.logprint(f"Config ID: {config_id}")

    #! List of path to each image for a target
    my_config = my_job.config
    my_dp_list = my_config.procdataproducts
    procdp_path = my_config.procpath

    #! #########################################
    #! DeepCR parameters from config file
    deepcr_pth_mask = my_config.parameters["deepcr_pth"]
    threshold = my_config.parameters["deepcr_threshold"]
    my_job.logprint(f"DeepCR config parameters \n Mask .pth path{deepcr_pth_mask} \n Threshold {threshold}")
    mdl = deepCR(
        mask=deepcr_pth_mask,
        hidden=32,
    )
    my_job.logprint(f"{mdl}")

    for my_dp in my_dp_list:
        my_job.logprint(f"{my_dp}, {type(my_dp)}")
        if my_dp.filename.split("_")[-1] == "flc.fits":
            ext_flc = my_dp.filename.split("_")[-1]
            my_job.logprint(ext_flc)
            dp_filepath = procdp_path + "/" + my_dp.filename
            my_job.logprint(f"{dp_filepath}")

            #* imgclean function
            threshold = 0.1

            imgclean(dp_filepath, mdl, threshold, update=True)  # Run DeepCR on each image
        else:
            pass

    #* Fire next event
    my_event = my_job.child_event(
        name="prep_image",
        tag="*",
        options={
            "target_name": this_event.options["target_name"],
            "target_id": this_event.options["target_id"],
            "config_id": this_event.options["config_id"],
        },
    )
    my_event.fire()
    time.sleep(150)
