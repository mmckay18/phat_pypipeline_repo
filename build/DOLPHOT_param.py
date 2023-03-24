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
    ref_dp_list = [ref_dp] #making reference dp into a list

    tagged_dps = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="dolphot input") #all other images

    all_dps = ref_dp_list + tagged_dps

    ref_sky = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="reference sky") #reference sky image
    ref_sky_list = [ref_sky]

    tagged_sky = wp.DataProduct.select(dpowner_id=my_config.config_id, data_type="image", subtype="sky") #all other sky images

    all_sky = ref_sky_list + tagged_sky

#Create parameter file
    my_target_path = my_target.datapath
    target_conf_path = my_target_path + "/conf_default/" #path to target's conf directory

    with open(target_conf_path + my_target.name + '.param', 'w') as p: #create empty file

        nimg = len(ref_dp) + len(tagged_dps) #number of images
        p.write(f'Nimg={nimg}') #write to file

#Define image specific parameters

        for dp in all_dps: #all images
            loc = tagged_dps.index(dp)  # image number with reference at index 0

            im_fullfile = dp.filename
            im_file = im_fullfile.split('.')[0] #get rid of extension
            p.write(f'img{loc}_file = {im_file}')

        params = ["img_shift", "img_xform", "img_psfa", "img_psfb", "img_psfc", "img_RAper",
                  "img_RChi", "img_RSky", "img_RSky2", "img_RPSF", "img_aprad", "img_apsky"]

        #define any image specific parameters in config file
        all_individual = {}
        for param in params:
            name_parts = param.split('_')
            defined = []
            for i in range(0, len(all_dps)):
                param_name = name_parts[0] + f"{i}_" + name_parts[1]
                if param_name in my_config.paramters:
                    p.write(f'{param_name} = {my_config.parameters[param_name]}')
                    defined.append(1)
            if len(defined) == len(all_dps):
                all_individual[param] = "Yes"
            else:
                all_individual[param] = "No"

        #define all img_ default parameters, replace if in config file
        for param in params:
            if param in my_config.parameters:
                p.write(f'{param} = {my_config.parameters[param]}')
            elif all_individual[param] == "No":
                if param = "img_shift":
                    p.write(f'img_shift = 0 0')
                if param = "img_xform":
                    p.write(f'img_xform = 1 0 0')
                if param = "img_psfa":
                    p.write(f'img_psfa = 3 0 0 0 0 0')
                if param = "img_psfb":
                    p.write(f'img_psfb = 3 0 0 0 0 0')
                if param = "img_psfc":
                    p.write(f'img_psfc = 0 0 0 0 0 0')
                if param = "img_RAper":
                    p.write(f'img_RAper = 2.5')
                if param = "img_RChi":
                    p.write(f'img_RChi = -1')
                if param = "img_RSky":
                    p.write(f'img_RSky = 4.0 10.0')
                if param = "img_RSky2":
                    p.write(f'img_RSky2 = -1 -1')
                if param = "img_RPSF":
                    p.write(f'img_RPSF = 13')
                if param = "img_aprad":
                    p.write(f'img_aprad = 20')
                if param = "img_apsky":
                    p.write(f'img_apsky = 30 50')

            #if "img_shift" in my_config.parameters:
            #    p.write(f'img_shift = {my_config.parameters["img_shift"]}')
            #else:
            #    p.write(f'img_shift = 0 0')

            #if "img_xform" in my_config.parameters:
            #    p.write(f'img_xform = {my_config.parameters["img_xform"]}')
            #else:
            #    p.write(f'img_xform = 1 0 0')

            #if "img_psfa" in my_config.parameters:
            #    p.write(f'img_psfa = {my_config.parameters["img_psfa"]}')
            #else:
            #    p.write(f'img_psfa = 3 0 0 0 0 0')

            #if "img_psfb" in my_config.parameters:
            #    p.write(f'img_psfb = {my_config.parameters["img_psfb"]}')
            #else:
            #    p.write(f'img_psfb = 3 0 0 0 0 0')

            #if "img_psfc" in my_config.parameters:
            #    p.write(f'img_psfc = {my_config.parameters["img_psfc"]}')
            #else:
            #    p.write(f'img_psfc = 0 0 0 0 0 0')

            #if "img_RAper" in my_config.parameters:
            #    p.write(f'img_RAper = {my_config.parameters["img_RAper"]}')
            #else:
            #    p.write(f'img_RAper = 2.5')

            #if "img_RChi" in my_config.parameters:
            #    p.write(f'img_RChi = {my_config.parameters["img_RChi"]}')
            #else:
            #    p.write(f'img_RChi = -1')


#Define global parameters
        params_global = ["photsec", "RCentroid", "SigFind", "SigFindMult", "SigFinal", "MaxIT",
                         "FPSF", "PSFPhot", "PSFPhotIt", "FitSky", "SkipSky", "SkySig", "NegSky",
                         "ForceSameMag", "NoiseMult", "FSat", "Zero", "PosStep", "dPosMax",
                         "RCombine", "sigPSF", "PSFStep", "MinS", "MaxS", "MaxE", "UseWCS",
                         "Align", "AlignIter", "AlignTol", "AlignStep", "Rotate", "SubResRef",
                         "SecondPass", "SearchMode", "Force1", "EPSF", "PSFsol", "PSFres",
                         "psfstars", "psfoff", "ApCor", "SubPixel", "FakeStars", "FakeOut",
                         "FakeMatch", "FakePSF", "FakeStarPSF", "FakePad", "RandomFake", "UsePhot",
                         "DiagPlotType", "VerboseData"]
        for globpar in params_global:
            if globpar in my_config.parameters:
                p.write(f'{globpar} = {my_config.parameters[globpar]}')
            else:
                if globpar = "photsec":
                    pass
                if globpar = "RCentroid":
                    p.write(f'RCentroid = 1')
                if globpar = "SigFind":
                    p.write(f'SigFind = 2.5')
                if globpar = "SigFindMult":
                    p.write(f'SigFindMult = 0.85')
                if globpar = "SigFinal":
                    p.write(f'SigFinal = 3.5')
                if globpar = "MaxIT":
                    p.write(f'MaxIT = 25')
                if globpar = "FPSF":
                    p.write(f'FPSF = G+L')
                if globpar = "PSFPhot":
                    p.write(f'PSFPhot = 1')
                if globpar = "PSFPhotIt":
                    p.write(f'PSFPhotIt = 1')
                if globpar = "FitSky":
                    p.write(f'FitSky = 1')
                if globpar = "SkipSky":
                    p.write(f'SkipSky = 1')
                if globpar = "SkySig":
                    p.write(f'SkySig = 2.25')
                if globpar = "NegSky":
                    p.write(f'NegSky = 1')
                if globpar = "ForceSameMag":
                    p.write(f'ForceSameMag = 0')
                if globpar = "NoiseMult":
                    p.write(f'NoiseMult = 0.05')
                if globpar = "FSat":
                    p.write(f'FSat = 0.999')
                if globpar = "Zero":
                    p.write(f'Zero = 25.0')
                if globpar = "PosStep":
                    p.write(f'PosStep = 0.25')
                if globpar = "dPosMax":
                    p.write(f'dPosMax = 3.0')
                if globpar = "RCombine":
                    p.write(f'RCombine = 2.0')
                if globpar = "sigPSF":
                    p.write(f'sigPSF = 10.0')
                if globpar = "PSFStep":
                    p.write(f'PSFStep = 0.25')
                if globpar = "MinS":
                    p.write(f'MinS = 0.65')
                if globpar = "MaxS":
                    p.write(f'MaxS = 2.0')
                if globpar = "MaxE":
                    p.write(f'MaxE = 0.5')
                if globpar = "UseWCS":
                    p.write(f'UseWCS = 0')
                if globpar = "Align":
                    p.write(f'Align = 1')
                if globpar = "AlignIter":
                    p.write(f'AlignIter = 1')
                if globpar = "AlignTol":
                    p.write(f'AlignTol = 0')
                if globpar = "AlignStep":
                    p.write(f'AlignStep = 1')
                if globpar = "Rotate":
                    p.write(f'Rotate = 0')
                if globpar = "SubResRef":
                    p.write(f'SubResRef = 1')
                if globpar = "SecondPass":
                    p.write(f'SecondPass = 1')
                if globpar = "SearchMode":
                    p.write(f'SearchMode = 1')
                if globpar = "Force1":
                    p.write(f'Force1 = 0')
                if globpar = "EPSF":
                    p.write(f'EPSF = 1')
                if globpar = "PSFsol":
                    p.write(f'PSFsol = 1')
                if globpar = "PSFres":
                    p.write(f'PSFres = 1')
                if globpar = "psfstars":
                    p.write(f'psfstars = :')
                if globpar = "psfoff":
                    p.write(f'psfoff = 0.0')
                if globpar = "ApCor":
                    p.write(f'ApCor = 1')
                if globpar = "SubPixel":
                    p.write(f'SubPixel = 1')
                if globpar = "FakeStars":
                    p.write(f'FakeStars = :')
                if globpar = "FakeOut":
                    p.write(f'FakeOut = :')
                if globpar = "FakeMatch":
                    p.write(f'FakeMatch = 3.0')
                if globpar = "FakePSF":
                    p.write(f'FakePSF = 1.5')
                if globpar = "FakeStarPSF":
                    p.write(f'FakeStarPSF = 0')
                if globpar = "FakePad":
                    p.write(f'FakePad = 0')
                if globpar = "RandomFake":
                    p.write(f'RandomFake = 1')
                if globpar = "UsePhot":
                    p.write(f'UsePhot = :')
                if globpar = "DiagPlotType":
                    p.write(f'DiagPlotType = :')
                if globpar = "VerboseData":
                    p.write(f'VerboseData = 0')
        #If in config file then write that parameter to the param file, otherwise use the ones I set here

