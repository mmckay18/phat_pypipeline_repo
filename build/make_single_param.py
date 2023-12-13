#!/usr/bin/env python
import wpipe as wp
import time
from astropy.io import fits


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="make_single_param", value="*")


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    my_config = my_job.config
    my_job.logprint(
        f"###### This config.parameters {my_config.parameters}, {type(my_config.parameters)} \n")
    this_event = my_job.firing_event
    my_job.logprint(f"{this_event.options}")
    dpid=this_event.options["dpid"]
    # Get the dataproduct prep_image sent
    dp= wp.DataProduct.select(dp_id=dpid)
    my_target = wp.Target(this_event.options["target_id"])
    my_job.logprint(f"###### This Target: {my_target}\n")


    # Create parameter file
    my_target_path = my_target.datapath
    parent_job = this_event.parent_job
    # path to target's conf directory
    target_conf_path = my_target_path + "/conf_default/"
    my_job.logprint(f"Target Conf Path: {target_conf_path}")

    param_filepath = target_conf_path + dp.filename + '.param'
    my_job.logprint(f"Parameter File Path: {param_filepath}")
    im_fullfile = dp.filename
    im_file = im_fullfile.split('.fits')[0]  # get rid of extension

    with open(param_filepath, 'w') as p:  # create empty file
        p.write(f'Nimg=1\n')  # write to file
        p.write(f'img0_file = {im_file}\n')

        # Define image specific parameters
        my_job.logprint(
            f'Checking for user specified individual parameters and defining any unspecified individual parameters')
        my_job.logprint(f'Checking {dp.filename}, {dp}')

        p.write(f'img{loc}_file = {im_file}\n')
        im_pars = ["apsky","shift","xform","raper","rchi","rsky0","rsky1","rpsf"]
        def_vals = ["20 35","0 0","1 0 0","2","1.5","15","35","15"]
        defined = []
        img = 'img1'
        parcount=0
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

# Define global parameters
        my_job.logprint(
            f'Checking for user specified global parameters and defining any unspecified global parameters')
        params_global = ["UseWCS","PSFPhot","FitSky","SkipSky","SkySig","SecondPass","SearchMode","SigFind","SigFindMult","SigFinal","MaxIT","NoiseMult","FSat","FlagMask","ApCor","Force1","Align","aligntol","alignstep","ACSuseCTE","WFC3useCTE","Rotate","RCentroid","PosStep","dPosMax","RCombine","SigPSF","PSFres","psfoff","DiagPlotType","CombineChi","ACSpsfType","WFC3IRpsfType","WFC3UVISpsfType","PSFPhotIt"]
        glob_vals = ["2","1","2","2","2.25","5","1","3.0","0.85","3.5","25","0.10","0.999","4","1","1","2","4","2","0","0","1","1","0.1","2.5","1.415","3.0","1","0.0","PNG","1","0","0","0","2"]
        paramcount = 0
        for globpar in params_global:
            try:
                my_config.parameters[globpar]
                p.write(f'{globpar} = {my_config.parameters[globpar]}\n')
                my_job.logprint(f'{globpar} parameter found in configuration')
            except:
                p.write(f'{globpar} = {glob_vals[paramcount]}\n')
                my_job.logprint(f'{globpar} parameter set to default')
            paramcount += 1
# Create dataproduct for parameter file
    param_dp = wp.DataProduct(my_config, filename=dp.filename + '.param', relativepath=target_conf_path,group="conf", data_type="text file", subtype="parameter")  
    my_job.logprint(f"Parameter DP: {param_dp}, {param_dp.filename}")
    my_job.logprint(
        f"\nDOLPHOT parameter file complete for {my_target.name}, firing DOLPHOT task")
    next_event = my_job.child_event(
        name="SINGLE_DOLPHOT",
        options={"param_dp_id": param_dp.dp_id, "walltime": "20:00:00", "to_run":this_event.options["to_run"], "tracking_job_id":parent_job.job_id}
    )  # next event
    next_event.fire()
    time.sleep(150)
