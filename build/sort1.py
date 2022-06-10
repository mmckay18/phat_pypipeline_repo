#! /usr/bin/env python
import os
import wpipe as wp
from astropy.io import fits
import glob
import shutil
import pandas as pd


def register(task):
    _temp = task.mask(source="*", name="start", value=task.name)
    _temp = task.mask(source="*", name="__init__", value="*")


# def list_of_rawDataProducts(my_input):
#     rawdp_fn_list = []
#     input_rawpath_list = glob.glob(my_input.rawspath + "/*.fits")
#     my_job.logprint(f"{len(input_rawpath_list), input_rawpath_list}")
#     for rawpath in input_rawpath_list:
#         # my_job.logprint(f"list of rawdataproducts: {rawpath}")
#         rawdataproducts_fn = rawpath.split("/")[-1]
#         # my_job.logprint(f"rawdataproducts: {rawdataproducts_fn}")
#         rawdp_fn_list.append(rawdataproducts_fn)

#     my_job.logprint(f"rawDP_fn_list: {rawdp_fn_list}")
#     return rawdp_fn_list, input_rawpath_list


def targetname_list(my_input):
    targetname_list = []
    rawdp_info_list = []
    df = pd.DataFrame(columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"])
    for my_rawdp in my_input.rawdataproducts:

        my_rawdp_fits_path = my_rawdp.path

        # 1. Grab fitsfile header info directly from the dataproduct
        hdu = fits.open(my_rawdp_fits_path)
        prop_id = str(hdu[0].header["PROPOSID"])
        targname = hdu[0].header["TARGNAME"]
        filename = hdu[0].header["FILENAME"]
        hdu.close()
        target_name = prop_id + "_" + targname

        rawdp_info = [filename, prop_id, targname, target_name]
        my_job.logprint(f"{rawdp_info}")
        rawdp_info_list.append(rawdp_info)

    rawdp_df = pd.DataFrame(
        rawdp_info_list,
        columns=["FILENAME", "PROPOSID", "TARGNAME", "PROPOSID_TARGNAME"],
    )
    # my_job.logprint(f"{rawdp_df.head()}")

    df1 = pd.concat([df, rawdp_df], ignore_index=True)
    my_job.logprint(f"FINAL_DF, # {len(df1)}")
    my_job.logprint(f"{df1.head(10)}")

    # my_job.logprint(f"{df1.head()}")
    # if target_name not in targetname_list:
    #     targetname_list.append(target_name)
    targetname_list = df1["PROPOSID_TARGNAME"].unique()
    return df1, list(targetname_list)


def sort_input_dataproduct(my_input):
    """ """

    for my_rawdp in my_input.rawdataproducts:

        my_rawdp_fits_path = my_rawdp.path

        # 1. Grab fitsfile header info directly from the dataproduct
        hdu = fits.open(my_rawdp_fits_path)
        prop_id = str(hdu[0].header["PROPOSID"])
        targname = hdu[0].header["TARGNAME"]
        hdu.close()

        target_name = prop_id + "_" + targname

        # 2. Create a new test target
        # TODO my_target = my_input.target('target', rawdps_to_add='raw.dat')
        my_target = my_input.target(name=target_name, rawdps_to_add=my_rawdp)

        # 3. Grab configuration
        # my_config = my_target.configuration(name = <name_of_config >)
        # my_config = my_target.configurations[<name_of_config>]
        my_config = my_target.configurations["default"]
        my_job.logprint(
            f"Target: {my_target.name} Config: {my_config.name}, inputname: {my_rawdp.filename}"
        )

        # my_job.logprint(f""
        # 4. create new dataproduct with the name of the input image
        _dp = my_config.dataproduct(
            filename=my_rawdp.filename,
            relativepath=my_config.rawpath,
            group="raw",
            subtype="image",
        )
        my_job.logprint(f"DP: {_dp.filename}")
    return _dp


if __name__ == "__main__":
    my_pipe = wp.Pipeline()
    my_job = wp.Job()
    test = my_job.logprint("Run Sorting Function")
    my_job.logprint(f"Sort: {test}")
    my_input = my_pipe.inputs[0]
    # Make a list  of raw dataproduct file names
    # rawdps_fn_list, input_rawpath_list = list_of_rawDataProducts(my_pipe.inputs[0])

    # Make a list of target names rom the proposal id and targetname
    unsorted_df, unsorted_targetnames_list = targetname_list(my_pipe.inputs[0])

    # Seperate dataframe by target
    my_job.logprint(f"{unsorted_targetnames_list}")
    for target_name in unsorted_targetnames_list:
        my_job.logprint(f"{target_name} DataFrame")
        sorted_df = unsorted_df[unsorted_df["PROPOSID_TARGNAME"] == target_name]
        my_job.logprint(f"{sorted_df.head()}")

        # Get list of Filename for each target
        rawdp_fn_list = sorted_df["FILENAME"].tolist()
        my_job.logprint(f"{rawdp_fn_list}")

        # Creates targets from dataproducts
        my_target = my_input.target(name=target_name, rawdps_to_add=rawdp_fn_list)
        my_job.logprint(
            f"Target: {my_target.name} Config: {my_target.configurations['default']}"
        )
        option_name = my_target.name + "_Completed"
        # my_job.options(option_name=0)

    # TODO Sorting function and creates targets that the pipeline will owns
    # sort_input_dataproduct(my_pipe.inputs[0])

    # # Making dataproducts from targets made from
    # for my_target in my_pipe.inputs[0].targets:
    #     my_job.logprint(
    #         f"Target: {my_target.name} Config: {my_target.configurations['default']}"
    #     )
    #     option_name = my_target.name + "_Completed"
    #     # my_job.options(option_name=0)

    #     # Grab configuration of the target
    #     my_config = my_target.configurations["default"]

    #     # Make dataproduct for each target
    #     my_dps = my_config.rawdataproducts

    #     # Add parameters to default configuration
    #     my_params = my_config.parameters
    #     # TODO: Not saving paramenters to default.log?
    #     my_params["job_id"] = my_job.job_id

    #     # Number of targets
    #     my_params["N_images"] = len(my_dps)

    #     # Print the conf paramerters from default.conf
    #     my_job.logprint(f"Conf parameters {my_params} from {my_config.name}")

    #     # image_num = len(my_dps)

    #     # Interate through the dataproducts and make an event
    #     for dp in my_dps:
    #         my_job.logprint(f"DP Name {dp.filename}, {len(my_dps)}")

    #         my_event = my_job.child_event(
    #             "new_image",
    #             options={
    #                 "config_id": my_config.config_id,
    #                 "dp_ID": dp.dp_id,
    #                 "total_images": len(my_dps),
    #             },
    #             tag=dp.filename,
    #         )
    #         my_event.fire()

    # TODO Keep track the number of images - need multiple counts simulataniously

    # # making targets
    # for my_target in target_list:
    #     # my_job.logprint
    #     # my_target = my_input.target(name=my_dp.filesplitext[0])
    #     _target = my_job.inputs.target(my_target)

    # Loop through image and make an event for each target
    # Know what each image belongs to target
    # for my_input in my_pipe.inputs:
    # my_input = wp.Input(my_pipe, my_pipe.inputs[0].rawspath)
    # # Grab config

    # for my_dp in my_input.rawdataproducts:

    #     # target name
    #     test_target_name = prop_id + "_" + target_name
    #     # my_job.logprint(f"{test_target_name}")

    #     # Get target name from the directory
    #     my_target = my_input.target(name=test_target_name)
    #     # my_target = wp.Target(name=test_target_name)  # issue with name parameters
    #     # my_job.logprint(f"Raw data product: {my_input.rawdataproducts}")
    #     # my_target = my_input.target(name=my_dp.filesplitext[0])
    #     my_conf = my_target.configurations[0]
    #     im_dp = my_conf.dataproduct(
    #         filename=my_dp.filename, relativepath=my_conf.rawpath
    #     )
    #     # my_params = my_conf.parameters

    #

    #     my_event.fire()
    # Move the data to raw

    # my_job.logprint(f"Interate through the {my_pipe.input_root}")
    # for my_input in my_pipe.inputs:
    # sort_input_dataproduct(my_input=my_input)

    # Grab all input directories and move to data directory
    # dir_list = os.listdir(path)

    # my_job.logprint("Firing Job")
    # my_event = (
    #     my_job.child_event(
    #         "whatever_name_of_the_event", options={"config_id": new_conf.config_id}
    #     ),
    # )  # Add image name as an option
    # my_event = my_job.child_event(
    #     "whatever_name_of_the_event",
    #     tag="here_for_diferentiating_same_name_events",
    #     options={"config_id": new_conf.config_id},
    # )  # tag should be the image name as a tag and option(arg)
    # my_event.fire()
    # my_job.child_event("tag_image").fire()

    # for my_dp in my_input.rawdataproducts:
    #     my_dp_fits_path = my_dp.path
    # my_job.logprint(f"{my_dp_fits_path}")
    # sort input data product

    # hdu = fits.open(my_dp_fits_path)
    # my_job.logprint(f"{hdu[0].header['FILENAME']}")
    # for my_input in my_pipe.inputs:

    # for my_dp in my_input.rawdataproducts:
    #     my_job.logprint(f"Raw data product: {my_input.rawdataproducts}")

    #     my_target = my_input.target(name=my_dp.filesplitext[0])
    #     my_conf = my_target.configurations[0]
    #

    #     # Get the fits file path
    #     my_dp_fits_path = my_dp.path + ".fits"

    #     # for my_conf in my_target.configurations:
    #     #     # Add parameters
    #     #     my_params["job_id"] = my_job.job_id
    #     #     my_job.logprint(f"Conf parameters {my_params} from {my_conf.name}")

    #     #     # Add sort directory path to cionfig
    #     #     my_params["job_id"] = my_job.job_id
    #     #     my_job.logprint(f"Conf parameters {my_params} from {my_conf.name}")

    # # Add configurations aparameters to default.conf
    # my_params = my_conf.parameters
    # # Print the conf paramerters from default.conf
    # my_job.logprint(f"Conf parameters {my_params} from {my_conf.name}")
    # my_params["job_id"] = my_job.job_id
    # # my_job.logprint(f"{my_job.job_id}")
    # my_job.logprint(
    #     "Starting target "
    #     + my_target.name
    #     + " config "
    #     + my_conf.name
    #     + " Job ID "
    #     + str(my_job.job_id)
    #     + " Config ID "
    #     + str(my_conf.config_id)
    # )
    # my_job.logprint(f"{my_conf.procpath}")
    # my_job.logprint(f"{my_conf.confpath}")
    # my_job.logprint(f"{my_conf.logpath}")

    # # Create a dataproduct from the target
    # # _dp = my_conf.dataproduct(filename=filename, relativepath=my_conf.procpath{if in proc/], group='group_name [proc if it is in proc]',subtype='[name a type of file]', filtername=filtname [if it is an image with a filter], options={[key,value pairs for options you may want to keep track of})
    # _dp = my_conf.dataproduct(
    #     filename=my_target.name,
    #     relativepath=my_conf.procpath,
    #     group="proc",
    #     subtype="",
    #     filtername="",
    #     options={},
    # )
    # my_job.logprint(f"{_dp}")
    # my_job.logprint(f"{_dp.path}.fits")
    # my_job.logprint(f"{_dp.ra}, {_dp.dec}")
    # # my_job.logprint(f"{_dp.pointing_angle} \n")
    # # Grab all data products in a config and store as a list
    # my_dp = [_temp for _temp in my_conf.dataproducts]
    # my_job.logprint(f"{my_dp.path} \n")

    # for my_conf in my_target.configurations:
    #     my_job.logprint("Starting target "+my_target.name+" config "+my_conf.name)
    #     my_job.child_event('run_mcmc', options={'config_id': my_conf.config_id}).fire()
    # new_target = my_job.target.input.target('name_of_new_target')
    # my_job.logprint("Target")

    # ----------------------------------------------------------------# Fire next event
    # my_job.logprint("Firing Job")
    # my_event = my_job.child_event('whatever_name_of_the_event', options={'config_id': new_conf.config_id}), # Add image name as an option
    # my_event = my_job.child_event('whatever_name_of_the_event', tag='here_for_diferentiating_same_name_events', options={'config_id': new_conf.config_id}) # tag should be the image name as a tag and option(arg)
    # my_event.fire()
    # my_job.child_event("tag_image").fire()
