#!/usr/bin/env python
import wpipe as wp
from astropy.io import fits
import time


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


def tag_event_dataproduct(this_event):
    """
    Tags incoming dataproducts from fired event

    Parameters:
    -----------
    this_event : Event(OptOwner)
        a fired event of a WINGS pipeline.

    Returns:
    --------
    logprint the options for the current dataproduct in the log file.

    """

    # my_job.logprint(f"{this_event.options}")
    this_dp_id = this_event.options["dp_id"]
    this_target_id = this_event.options["target_id"]
    # config_id = this_event.options["config_id"]
    # filename = this_event.options["filename"]
    # my_job.logprint(f"{config_id} {this_dp_id} {this_target_id} {filename}")

    # Call dataproduct
    # this_dp = wp.DataProduct(this_dp_id, filename=filename, group="proc")
    this_dp = wp.DataProduct(int(this_dp_id), group="proc")
    # my_job.logprint(f"{this_dp}")
    # my_job.logprint(f"{this_dp.target.datapath}")
    # * Dataproduct file pat
    procdp_path = this_dp.target.datapath + "/proc_default/" + this_dp.filename

    # Open FITS files and extract desired parameters to tag each image
    raw_hdu = fits.open(procdp_path)
    # my_job.logprint(f"{this_dp.path}")
    FILENAME = raw_hdu[0].header["FILENAME"]
    TELESCOP = raw_hdu[0].header["TELESCOP"]
    if ("JWST" not in TELESCOP): 
        RA = raw_hdu[0].header["RA_TARG"]
        DEC = raw_hdu[0].header["DEC_TARG"]
        PA = raw_hdu[0].header["PA_V3"]
        EXPTIME = raw_hdu[0].header["EXPTIME"]
        EXPFLAG = raw_hdu[0].header["EXPFLAG"]
        TARGNAME = raw_hdu[0].header["TARGNAME"]
        PROPOSALID = raw_hdu[0].header["PROPOSID"]
    else:
        RA = raw_hdu[0].header["TARG_DEC"]
        DEC = raw_hdu[0].header["TARG_DEC"]
        PA = raw_hdu[0].header["GS_V3_PA"]
        EXPTIME = raw_hdu[0].header["EFFEXPTM"]
        EXPFLAG = "MANNORMAL"
        TARGNAME = raw_hdu[0].header["TARGPROP"]
        PROPOSALID = raw_hdu[0].header["PROGRAM"]
    DETECTOR = raw_hdu[0].header["DETECTOR"]
    CAM = raw_hdu[0].header["INSTRUME"]
    FILTER = raw_hdu[0].header["FILTER"]
    if ("_i2d" in FILENAME):
        TYPE = "DRIZZLED"
    if ("_drc" in FILENAME):
        TYPE = "DRIZZLED"
    if ("_flc" in FILENAME):
        TYPE = "SCIENCE"
    if ("_flt" in FILENAME):
        TYPE = "SCIENCE"
    if ("_crf" in FILENAME):
        TYPE = "SCIENCE"
    if ("_cal" in FILENAME):
        TYPE = "SCIENCE"
    raw_hdu.close()

    # tag_event_dataproduct
    this_dp_id = this_event.options["dp_id"]
    this_dp = wp.DataProduct(
        int(this_dp_id),subtype=TYPE
        options={
            "filename": FILENAME,
            "ra": RA,
            "dec": DEC,
            "telescope": TELESCOP,
            "detector": DETECTOR,
            "orientation": ORINT,
            "Exptime": EXPTIME,
            "Expflag": EXPFLAG,
            "cam": CAM,
            "filter": FILTER,
            "targname": TARGNAME,
            "proposalid": PROPOSALID,
            "type": TYPE,
            "dp_id": this_dp_id,
            "target_id": this_target_id,
        },
    )
    my_job.logprint("Tagged Image Done")
    my_job.logprint(f"Tagged Image options{this_dp.options}")
    return this_dp

def imgclean(imgname, mdl, threshold, update=True):
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
    # print('----chip1----')
    maskimgchip1, cleaned_imgchip1 = mdl.clean(
        imgnormchip1, threshold=threshold, inpaint='medmask')
    maskimgchip1 = np.float32(maskimgchip1)
    dqchip1 = imgall[3].data
    # print('original MAST DQ:', len(np.where((dqchip1&4096) == 4096)[0]))
    dqchip1[dqchip1 & 4096 == 4096] ^= 4096
    # print('remove original check:', len(np.where((dqchip1&4096) == 4096)[0]))
    dqchip1[maskimgchip1 == 1] |= 4096
    # print('after deepCR DQ:', len(np.where((dqchip1&4096) == 4096)[0]))
    imgall[3].data = dqchip1
    # print('CR DQ update done')

    # print('----chip2----')/
    maskimgchip2, cleaned_imgchip2 = mdl.clean(
        imgnormchip2, threshold=threshold, inpaint='medmask')
    maskimgchip2 = np.float32(maskimgchip2)
    dqchip2 = imgall[6].data
    # print('original MAST DQ:', len(np.where((dqchip2&4096) == 4096)[0]))
    dqchip2[dqchip2 & 4096 == 4096] ^= 4096
    # print('remove original check:', len(np.where((dqchip2&4096) == 4096)[0]))
    dqchip2[maskimgchip2 == 1] |= 4096
    # print('after deepCR DQ:', len(np.where((dqchip2&4096) == 4096)[0]))
    imgall[6].data = dqchip2
    # print('CR DQ update done')

    if update:
        imgall.flush()
        print('update original fits file done')
    else:
        print('original fits file not updated!')
    return



if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()

    # ! Get the firing event obj
    # * Selecting parent event object
    this_event = my_job.firing_event
    config_id = this_event.options["config_id"]
    my_job.logprint(f"This Event: {this_event}")

    #! Write parent job event option parameters
    compname = this_event.options["comp_name"]
    parent_job = this_event.parent_job
    my_job.logprint(f"parent_job options: {parent_job.options}")
    my_job.logprint(f"{update_option}/{to_run} TAGGED")

    # ! Start tag_event_dataproduct function
    my_dp = tag_event_dataproduct(this_event)

    #! Fire DeepCR event after tagging
    my_config_param = my_job.config.parameters
    my_job.logprint(
        f"MY CONFIG PARM: {my_config_param}, {type(my_config_param)}")
    my_job.logprint(
        f"\n parameter atrributs: {dir(my_job.config.parameters)}")
    my_job.logprint(
        f"\nRUN_DEEPCR setting: {my_job.config.parameters['RUN_DEEPCR']}, {type(my_job.config.parameters['RUN_DEEPCR'])}")
    if "JWST" not in my_dp.options["telescope"]: 
        if my_config_param['RUN_DEEPCR'] == 'T':
            my_job.logprint(f"{my_dp}, {type(my_dp)}")
            if my_dp.filename.split("_")[-1] == "flc.fits":
                ext_flc = my_dp.filename.split("_")[-1]
                my_job.logprint(ext_flc)
                dp_filepath = procdp_path + "/" + my_dp.filename
                my_job.logprint(f"{dp_filepath}")

                # * imgclean function
                threshold = 0.1

                # Run DeepCR on each image
                imgclean(dp_filepath, mdl, threshold, update=True)

            deepCR_event = my_job.child_event(
                name="deepCR",
                options={
                    "target_name": this_event.options["target_name"],
                    "target_id": this_event.options["target_id"],
                    "config_id": this_event.options["config_id"],
                },
                # ! need to set a tag for each event if firing multiple events with the same name
                tag=str(update_option),
            )
            deepCR_event.fire()

        elif my_config_param['RUN_DEEPCR'] == 'F':
            my_job.logprint(f"Not running DeepCR")
            tag = str(update_option),

        elif my_config_param['RUN_DEEPCR'] == 'Keep':
            my_job.logprint(f"Keeping DQ as RUN_DEEPCR is set to Keep.")
            tag = str(update_option),

        else:
            my_job.logprint(f"RUN_DEEPCR parameter not set... Not running DeepCR.")
            tag = str(update_option),

    # ! Check of all images have been tagged
    update_option = parent_job.options[compname]
    update_option += 1
    to_run = this_event.options["to_run"]
    if this_event.options["to_run"] == update_option:
        my_job.logprint(f"This Job Options: {my_job.options}")
        compname = "completed_" + this_event.options["target_name"]
        new_option = {compname: 0}
        my_job.options = new_option
        my_job.logprint(f"Updated Job Options: {my_job.options}")

        # List of all filters in target
        my_config = my_job.config  # Get configuration for the job
        my_dp = wp.DataProduct.select(
            dpowner_id=my_config.config_id, data_type="image", subtype="tagged"
        )  # Get dataproducts associated with configuration (ie. dps for my_target)

        filters = []  # Making list of filters for target
        jwfilters = []
        adrizfilters = []
        for dp in my_dp:
            filters.append(dp.options["filter"])
            if dp.options["telescope"] == "JWST":
               jwfilters.append(dp.options["filter"])
            else:
               adrizfilters.append(dp.options["filter"])
            all_filters = set(
                filters
            )  # Remove duplicates to get array of different filters for target
            adriz_filters = set(
                adrizfilters
            )  # Remove duplicates to get array of different filters for target

        my_config.parameters["filters"] = ",".join(
            all_filters
        )  # add list of filters to configuration
        my_config.parameters["adrizfilters"] = ",".join(
            adriz_filters
        )  # add list of filters to configuration
        # ? my_config.save()  # save configuration to database
        my_job.logprint(f"MY CONFIG PARM: {my_config.parameters}")

        num_all_filters = len(all_filters)
        num_adriz_filters = len(adriz_filters)
        my_job.logprint(
            f"{num_all_filters} filters found for target {dp.target.name}")

        #! Fire next task astrodrizzle
        my_job.logprint("FIRING NEXT ASTRODRIZZLE TASK")
        if len(adriz_filters) > 0:
            for i in adriz_filters:
                my_job.logprint(f"{i},{type(str(i))}")
                my_event = my_job.child_event(
                    name="astrodrizzle",
                    options={
                        "target_name": this_event.options["target_name"],
                        "target_id": this_event.options["target_id"],
                        "config_id": this_event.options["config_id"],
                        "to_run": len(adriz_filters),  # num of filter to run
                        "filter": str(i),
                        "comp_name": compname
                    },
                    tag=str(
                        i
                    ),  # ! need to set a tag for each event if firering multiple events with the same name
                )
                my_event.fire()
        else:
            my_job.logprint(
                f"AstroDrizzle step complete for {my_target.name}, firing find reference task.")
            next_event = my_job.child_event(
                name="find_ref",
                options={"target_id": this_event.options["target_id"]}
            )  # next event
            next_event.fire()
 
        time.sleep(150)

        # my_job.logprint(f"Firing Event Options: {my_event.options}")

    else:
        pass

    # TODO:
    # * Enable the pipeline to countdown the number of dataproducts for a target
    # * Fire astrodrizzle task after the last image for a target finish tagging
########################################
# Code originally from astrodrizzle that can be used here instead

# my_config = my_job.config  # Get configuration for the job

# my_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="tagged") # Get dataproducts associated with configuration (ie. dps for my_target)

# filters = []  # Making array of filters for target
# for dp in my_dp:
# filters.append(dp.options["filter"])
# all_filters = set(filters) # Remove duplicates to get array of different filters for target

# my_config.parameters['filters']= ','.join(all_filters) #add list of filters to configuration

# num_all_filters = len(all_filters)
# my_job.logprint(f"{num_all_filters} filters found for target {my_target.name}")
