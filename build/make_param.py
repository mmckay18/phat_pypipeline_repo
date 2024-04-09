#!/usr/bin/env python
"""
Make Param Task Description:
-------------------
This script is a component of a data processing pipeline designed for Flexible Image Transport System (FITS) files. It carries out several key tasks:

1. Checks for user-specified parameters in the configuration. If a parameter is not specified by the user, it sets a default value for that parameter.

2. Writes the parameters and their values to the targets configuration file. This file is used as input for other scripts in the pipeline.

3. Defines global parameters for the pipeline. These parameters control the behavior of the pipeline and are used across multiple scripts for running DOLPHOT.

4. Fires DOLPHOT events for the target.

This script relies on the 'wpipe' library, a Python package designed for efficient pipeline management and execution.
"""

import wpipe as wp
import time
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="make_param", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config
    my_job.logprint(
        f"###### This config.parameters {my_config.parameters}, {type(my_config.parameters)} \n")
    this_event = my_job.firing_event
    my_job.logprint(f"{this_event.options}")
    # prep_event_ids = this_event.options["list_prep_image_event_ids"]
    # my_job.logprint(f"Prep Event IDs: {prep_event_ids}")

    # List of DP from prep image:
    # list_of_dps = this_event.options
    tagged_dps = []
    # for dp in my_config.procdataproducts:
    #    # my_job.logprint(f"DP: {dp}, {dp.subtype}")
    #    if "drc.chip1.fits" in dp.filename:
    #        ref_dp = dp
    #        dp.subtype == "reference"  # ? Not setting the subtype?
    #        my_job.logprint(f"Reference DP: {dp}, {dp.subtype}")

    #    if "drc.chip1.fits" not in dp.filename and dp.subtype == "splitgroups":
    #        tagged_dps.append(dp)
    #        my_job.logprint(f"Tagged DP: {dp}, {dp.subtype}")
    #    else:
    #        pass
    ref_dp = wp.DataProduct.select(
        config_id=my_config.config_id, subtype="reference_prepped")
    tagged_dps = wp.DataProduct.select(
        config_id=my_config.config_id,
        data_type="image",
        subtype="SCIENCE_prepped")
    my_target = wp.Target(this_event.options["target_id"])
    my_job.logprint(f"###### This Target: {my_target}\n")

    # Get list of all dataproducts associated with target
    # my_job.logprint(f"Target DPs: {my_target.dataproducts}") #? Not working lisying target dataproducts

    # ref_dp = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image")
    #                                subtype="dolphot input reference")  # reference image
    ref_dp_list = [ref_dp[0]]  # making reference dp into a list
    my_job.logprint(f"Reference DP: {ref_dp[0].filename}, {type(ref_dp[0])}")

    # tagged_dps = wp.DataProduct.select(
    #     dpowner_id=my_config.config_id, data_type="image", subtype="dolphot input")  # all other images
    # my_job.logprint(f"Tagged DPs: {tagged_dps}, {type(tagged_dps)}")

    all_dps = ref_dp_list + tagged_dps
    my_job.logprint(f"all_dps: {all_dps}")

# Create parameter file
    my_target_path = my_target.datapath

    # path to target's conf directory
    target_conf_path = my_config.confpath + "/"
    my_job.logprint(f"Target Conf Path: {target_conf_path}")

    # TODO: Make target file
    param_filepath = target_conf_path + my_target.name + '.param'
    my_job.logprint(f"Parameter File Path: {param_filepath}")

    with open(param_filepath, 'w') as p:  # create empty file
        nimg = len(all_dps)-1  # number of images
        p.write(f'Nimg={nimg}\n')  # write to file

        # Define image specific parameters
        my_job.logprint(
            f'Checking for user specified individual parameters and defining any unspecified individual parameters')
        count = 0
        for dp in all_dps:  # all images
            my_job.logprint(f'Checking {dp.filename}, {dp}')
            # image number with reference at index 0
            # loc = tagged_dps.index(dp)
            loc = all_dps.index(dp)

            im_fullfile = dp.filename
            im_file = im_fullfile.split('.fits')[0]  # get rid of extension
            p.write(f'img{loc}_file = {im_file}\n')
            im_pars = ["apsky", "shift", "xform",
                       "raper", "rchi", "rsky0", "rsky1", "rpsf"]
            def_vals = ["20 35", "0 0", "1 0 0", "2", "1.5", "15", "35", "15"]
            if 'reference' not in dp.subtype:
                defined = []
                count += 1
                img = 'img'+str(count)
                parcount = 0
                for impar in im_pars:
                    param_name = "img"+str(count)+"_"+impar
                    cam_name = dp.options['detector']+"_"+impar
                    if "NIRCAM" in dp.options['detector']:
                        if "LONG" in dp.options['channel']:
                            cam_name = dp.options['detector']+"LW_"+impar
                    try:
                        p.write(
                            f'{param_name} = {my_config.parameters[cam_name]}\n')
                        my_job.logprint(
                            f'{param_name} parameter found in configuration')
                        defined.append(1)
                    except:
                        p.write(
                            f'{param_name} = {def_vals[parcount]}\n')
                        my_job.logprint(
                            f'{param_name} parameter default')
                        defined.append(1)
                    # if cam_name in my_config.parameters:
                    #    p.write(
                    #       f'{param_name} = {my_config.parameters[cam_name]}\n')
                    #    my_job.logprint(
                    #       f'{param_name} parameter found in configuration')
                    #    defined.append(1)
                    # else:
                    #    p.write(
                    #       f'{param_name} = {def_vals[parcount]}\n')
                    #    my_job.logprint(
                    #       f'{param_name} parameter default')
                    #    defined.append(1)
                    parcount += 1
############################
        # params = ["img_shift", "img_xform", "img_RAper",
        #          "img_RChi", "img_RSky", "img_RSky2", "img_RPSF", "img_aprad", "img_apsky"]

        # define any image specific parameters given in config file
        # all_individual = {}
        # for param in params:  # run for all image specific parameters
        #    name_parts = param.split('_')
        #    defined = []
        #    for i in range(0, len(all_dps)):  # for every input image
        #        # get image specific parameter name (ex. img2_shift)
        #        param_name = name_parts[0] + f"{i}_" + name_parts[1]
        #        if param_name in my_config.parameters:  # check config for this parameter
        #            p.write(
        #                f'{param_name} = {my_config.parameters[param_name]}\n')
        #            my_job.logprint(
        #                f'{param_name} parameter found in configuration')
        #            defined.append(1)
        #    # if image s

        # specific parameter is defined for all input images
        #    if len(defined) == len(all_dps):
        #        all_individual[param] = "Yes"
        #    else:
        #        all_individual[param] = "No"

        # define img_ default parameters which are used if img#_ parameter for an image isn't defined, replace if in config file
        # for param in params:  # run for all image specific parameters
        #    if param in my_config.parameters:  # check config for this parameter
        #        p.write(f'{param} = {my_config.parameters[param]}\n')
        #        my_job.logprint(f'{param} parameter found in configuration')
        #    # defining defaults if not in config file AND if the parameter wasn't defined for all images individually above.
        #    elif all_individual[param] == "No":
        #        if param == "img_shift":
        #            p.write(f'img_shift = 0 0\n')
        #        if param == "img_xform":
        #            p.write(f'img_xform = 1 0 0\n')
        #        #if param == "img_psfa":
        #        #    p.write(f'img_psfa = 3 0 0 0 0 0\n')
        #        #if param == "img_psfb":
        #        #    p.write(f'img_psfb = 3 0 0 0 0 0\n')
        #        #if param == "img_psfc":
        #        #    p.write(f'img_psfc = 0 0 0 0 0 0\n')
        #        if param == "img_RAper":
        #            p.write(f'img_RAper = 2.5\n')
        #        if param == "img_RChi":
        #            p.write(f'img_RChi = 2\n')
        #        if param == "img_RSky":
        #            p.write(f'img_RSky = 4.0 10.0\n')
        #        if param == "img_RSky2":
        #            p.write(f'img_RSky2 = -1 -1\n')
        #        if param == "img_RPSF":
        #            p.write(f'img_RPSF = 10\n')
        #        if param == "img_aprad":
        #            p.write(f'img_aprad = 20\n')
        #        if param == "img_apsky":
        #            p.write(f'img_apsky = 30 50\n')

            # original method I was using to define parameters which would require setting all of them individually

            # if "img_shift" in my_config.parameters:
            #    p.write(f'img_shift = {my_config.parameters["img_shift"]}')
            # else:
            #    p.write(f'img_shift = 0 0')

            # if "img_xform" in my_config.parameters:
            #    p.write(f'img_xform = {my_config.parameters["img_xform"]}')
            # else:
            #    p.write(f'img_xform = 1 0 0')

            # if "img_psfa" in my_config.parameters:
            #    p.write(f'img_psfa = {my_config.parameters["img_psfa"]}')
            # else:
            #    p.write(f'img_psfa = 3 0 0 0 0 0')

            # if "img_psfb" in my_config.parameters:
            #    p.write(f'img_psfb = {my_config.parameters["img_psfb"]}')
            # else:
            #    p.write(f'img_psfb = 3 0 0 0 0 0')

            # if "img_psfc" in my_config.parameters:
            #    p.write(f'img_psfc = {my_config.parameters["img_psfc"]}')
            # else:
            #    p.write(f'img_psfc = 0 0 0 0 0 0')

            # if "img_RAper" in my_config.parameters:
            #    p.write(f'img_RAper = {my_config.parameters["img_RAper"]}')
            # else:
            #    p.write(f'img_RAper = 2.5')

            # if "img_RChi" in my_config.parameters:
            #    p.write(f'img_RChi = {my_config.parameters["img_RChi"]}')
            # else:
            #    p.write(f'img_RChi = -1')
#########################################

# Define global parameters
        my_job.logprint(
            f'Checking for user specified global parameters and defining any unspecified global parameters')
        params_global = ["UseWCS", "PSFPhot", "FitSky", "SkipSky", "SkySig", "SecondPass", "SearchMode", "SigFind", "SigFindMult", "SigFinal", "MaxIT", "NoiseMult", "FSat", "FlagMask", "ApCor", "Force1", "Align", "aligntol",
                         "alignstep", "ACSuseCTE", "WFC3useCTE", "Rotate", "RCentroid", "PosStep", "dPosMax", "RCombine", "SigPSF", "PSFres", "psfoff", "DiagPlotType", "CombineChi", "ACSpsfType", "WFC3IRpsfType", "WFC3UVISpsfType", "PSFPhotIt"]
        glob_vals = ["2", "1", "2", "2", "2.25", "5", "1", "3.0", "0.85", "3.5", "25", "0.10", "0.999", "4", "1", "1",
                     "2", "4", "2", "0", "0", "1", "1", "0.1", "2.5", "1.415", "3.0", "1", "0.0", "PNG", "1", "0", "0", "0", "2"]
        # params_global = ["MaxIT","PSFPhot", "PSFPhotIt", "FitSky", "SkipSky", "SkySig", "SigFindMult", "FSat", "PosStep", "sigPSF", "UseWCS", "NoiseMult", "SecondPass", "Force1", "WFC3UVISpsfType","ACSpsfType","WFC3IRpsfType","ACSuseCTE", "WFC3useCTE","FlagMask","InterpPSFlib", "CombineChi", "RCombine", "PSFres"]
        # glob_vals = ["25","1","2","2","1","2.25","0.85","0.999","0.25","5.0","2","0.1","5","0","0","0","0","0","0","4","1","0","1.5","1"]
        paramcount = 0
        for globpar in params_global:
            try:
                my_config.parameters[globpar]
                p.write(f'{globpar} = {my_config.parameters[globpar]}\n')
                my_job.logprint(f'{globpar} parameter found in configuration')
            except:
                p.write(f'{globpar} = {glob_vals[paramcount]}\n')
                my_job.logprint(f'{globpar} parameter set to default')
            # if globpar in my_config.parameters:  # check for any global parameters in config
            #    p.write(f'{globpar} = {my_config.parameters[globpar]}\n')
            #    my_job.logprint(f'{globpar} parameter found in configuration')
            # else:  # define defaults if not defined in config
            #    p.write(f'{globpar} = {glob_vals[paramcount]}\n')
            #    my_job.logprint(f'{globpar} parameter set to default')
            paramcount += 1
####################
            #    if globpar == "photsec":
            #        pass
            #    if globpar == "RCentroid":
            #        p.write(f'RCentroid = 1\n')
            #    if globpar == "SigFind":
            #        p.write(f'SigFind = 2.5\n')
            #    if globpar == "SigFindMult":
            #        p.write(f'SigFindMult = 0.85\n')
            #    if globpar == "SigFinal":
            #        p.write(f'SigFinal = 3.5\n')
            #    if globpar == "MaxIT":
            #        p.write(f'MaxIT = 25\n')
            #    if globpar == "FPSF":
            #        p.write(f'FPSF = G+L\n')
            #    if globpar == "PSFPhot":
            #        p.write(f'PSFPhot = 1\n')
            #    if globpar == "PSFPhotIt":
            #        p.write(f'PSFPhotIt = 1\n')
            #    if globpar == "FitSky":
            #        p.write(f'FitSky = 1\n')
            #    if globpar == "SkipSky":
            #        p.write(f'SkipSky = 1\n')
            #    if globpar == "SkySig":
            #        p.write(f'SkySig = 2.25\n')
            #    if globpar == "NegSky":
            #        p.write(f'NegSky = 1\n')
            #    if globpar == "ForceSameMag":
            #        p.write(f'ForceSameMag = 0\n')
            #    if globpar == "NoiseMult":
            #        p.write(f'NoiseMult = 0.05\n')
            #    if globpar == "FSat":
            #        p.write(f'FSat = 0.999\n')
            #    if globpar == "Zero":
            #        p.write(f'Zero = 25.0\n')
            #    if globpar == "PosStep":
            #        p.write(f'PosStep = 0.25\n')
            #    if globpar == "dPosMax":
            #        p.write(f'dPosMax = 3.0\n')
            #    if globpar == "RCombine":
            #        p.write(f'RCombine = 2.0\n')
            #    if globpar == "sigPSF":
            #        p.write(f'sigPSF = 10.0\n')
            #    if globpar == "PSFStep":
            #        p.write(f'PSFStep = 0.25\n')
            #    if globpar == "MinS":
            #        p.write(f'MinS = 0.65\n')
            #    if globpar == "MaxS":
            #        p.write(f'MaxS = 2.0\n')
            #    if globpar == "MaxE":
            #        p.write(f'MaxE = 0.5\n')
            #    if globpar == "UseWCS":
            #        p.write(f'UseWCS = 0\n')
            #    if globpar == "Align":
            #        p.write(f'Align = 1\n')
            #    if globpar == "AlignIter":
            #        p.write(f'AlignIter = 1\n')
            #    if globpar == "AlignTol":
            #        p.write(f'AlignTol = 0\n')
            #    if globpar == "AlignStep":
            #        p.write(f'AlignStep = 1\n')
            #    if globpar == "Rotate":
            #        p.write(f'Rotate = 0\n')
            #    if globpar == "SubResRef":
            #        p.write(f'SubResRef = 1\n')
            #    if globpar == "SecondPass":
            #        p.write(f'SecondPass = 1\n')
            #    if globpar == "SearchMode":
            #        p.write(f'SearchMode = 1\n')
            #    if globpar == "Force1":
            #        p.write(f'Force1 = 0\n')
            #    if globpar == "EPSF":
            #        p.write(f'EPSF = 1\n')
            #    if globpar == "PSFsol":
            #        p.write(f'PSFsol = 1\n')
            #    if globpar == "PSFres":
            #        p.write(f'PSFres = 1\n')
            #    if globpar == "psfstars":
            #        p.write(f'psfstars = :\n')
            #    if globpar == "psfoff":
            #        p.write(f'psfoff = 0.0\n')
            #    if globpar == "ApCor":
            #        p.write(f'ApCor = 1\n')
            #    if globpar == "SubPixel":
            #        p.write(f'SubPixel = 1\n')
            #    if globpar == "FakeStars":
            #        p.write(f'FakeStars = :\n')
            #    if globpar == "FakeOut":
            #        p.write(f'FakeOut = :\n')
            #    if globpar == "FakeMatch":
            #        p.write(f'FakeMatch = 3.0\n')
            #    if globpar == "FakePSF":
            #        p.write(f'FakePSF = 1.5\n')
            #    if globpar == "FakeStarPSF":
            #        p.write(f'FakeStarPSF = 0\n')
            #    if globpar == "FakePad":
            #        p.write(f'FakePad = 0\n')
            #    if globpar == "RandomFake":
            #        p.write(f'RandomFake = 1\n')
            #    if globpar == "UsePhot":
            #        p.write(f'UsePhot = :\n')
            #    if globpar == "DiagPlotType":
            #        p.write(f'DiagPlotType = :\n')
            #    if globpar == "VerboseData":
            #        p.write(f'VerboseData = 0\n')
##############################
# Create dataproduct for parameter file
    param_dp = wp.DataProduct(my_config, filename=my_target.name + '.param', relativepath=target_conf_path,
                              group="conf", data_type="text file", subtype="parameter")  # Create dataproduct owned by config for the parameter file
    my_job.logprint(f"Parameter DP: {param_dp}, {param_dp.filename}")
    my_job.logprint(
        f"\nDOLPHOT parameter file complete for {my_target.name}, firing DOLPHOT task")
    next_event = my_job.child_event(
        name="DOLPHOT",
        options={"param_dp_id": param_dp.dp_id, "walltime": "400:00:00"}
    )  # next event
    next_event.fire()
    time.sleep(150)
