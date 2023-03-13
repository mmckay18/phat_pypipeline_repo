#!/usr/bin/env python
from deepCR import deepCR
import wpipe as wp
from astropy.io import fits
import numpy as np
from glob import glob


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="deepCR", value="*")


def imgclean(imgname, mdl):
    print("image_name:", imgname)

    # open the image with all extensions
    imgall = fits.open(imgname, mode="update")

    # process each chip/extension of the image, manually normalize the input for training
    imgorichip1 = imgall[1].data
    imgorichip1mean = imgorichip1.mean()
    imgorichip1std = imgorichip1.std()
    print("imgchip1mean_std:", imgorichip1mean, imgorichip1std)
    imgnormchip1 = (imgorichip1 - imgorichip1mean) / imgorichip1std
    print("chip1_normalize_done")

    imgorichip2 = imgall[4].data
    imgorichip2mean = imgorichip2.mean()
    imgorichip2std = imgorichip2.std()
    print("imgchip2mean_std:", imgorichip2mean, imgorichip2std)
    imgnormchip2 = (imgorichip2 - imgorichip2mean) / imgorichip2std
    print("chip2_normalize_done")

    # # for tweakreg purpose, threshold = 0.1 is good, mis-recognition of real sources as cr is allowed in the step
    # maskimgchip1, cleaned_imgchip1 = mdl.clean(
    #     imgnormchip1, threshold=0.10, inpaint="medmask"
    # )
    # cleaned_imgchip1ori = (
    #     cleaned_imgchip1 * imgorichip1std + imgorichip1mean
    # )  # reverse process the image to get original absolute flux
    # cleaned_imgchip1ori = np.float32(
    #     cleaned_imgchip1ori
    # )  # important! otherwise not accepted by tweakreg
    # maskimgchip1 = np.float32(maskimgchip1)
    # print("chip1_clean_done_scaleback")
    # maskimgchip2, cleaned_imgchip2 = mdl.clean(
    #     imgnormchip2, threshold=0.10, inpaint="medmask"
    # )
    # cleaned_imgchip2ori = cleaned_imgchip2 * imgorichip2std + imgorichip2mean
    # cleaned_imgchip2ori = np.float32(cleaned_imgchip2ori)
    # maskimgchip2 = np.float32(maskimgchip2)
    # print("chip2_clean_done_scaleback")
    # #  imgall[1].data = cleaned_imgchip1ori
    # #  imgall[4].data = cleaned_imgchip2ori
    # #  imgall.flush()
    # print("update original fits file done")
    ## attention, backup original files beforehand, this step will change the values of the original images
    ## not good for scientific purpose
    return


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    this_event = my_job.firing_event  # parent event obj
    # config_id = this_event.options["config_id"]
    # my_job.logprint(f"This Event: {this_event}")
    # my_job.logprint(f"Config ID: {config_id}")

    #! List of path to each image for a target
    my_config = my_job.config
    my_dp_list = my_config.procdataproducts
    procdp_path = my_config.procpath
    mdl = deepCR(
        mask="/Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/2022-10-26_mymodel8_epoch30.pth",
        hidden=32,
    )
    my_job.logprint(f"{mdl}")

    for my_dp in my_dp_list:
        my_job.logprint(f"{my_dp}, {type(my_dp)}")
        dp_filepath = procdp_path + "/" + my_dp.filename
        my_job.logprint(f"{dp_filepath}")
        imgclean(dp_filepath, mdl)  # Run DeepCR on each image

    #! DeepCR function
    # imgfull = glob(pathimgs + "*flc.fits")
    # print("all_imgs_name:", imgfull)
    # import the trained model used for UVIS images
    # mdl = deepCR(mask="/Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/2022-10-26_mymodel8_epoch30.pth", hidden=32)
    # for ii in imgfull:
    #     imgclean(ii, mdl)

    # * Fire next event
    my_event = my_job.child_event(
        name="prep_image",
        options={
            "target_name": this_event.options["target_name"],
            "target_id": this_event.options["target_id"],
            "config_id": this_event.options["config_id"],
        },
    )
    my_event.fire()
