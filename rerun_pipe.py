import os
import shutil

"""This script is used to automate the process of running a pipeline called "wingspipe" on a specific set of input data. 
It first changes the working directory to the location of the pipeline files. 
It then removes any existing "data" directory using the shutil module. 
After that, it deletes any previous pipeline runs using the "wingspipe delete" command. 
The script then initializes the pipeline using the "wingspipe init" command with the necessary configuration files. 
Finally, the pipeline is executed using the "wingspipe run" command. 
Overall, this script streamlines the process of setting up and running the pipeline, saving time and reducing the risk of manual errors."""

os.chdir(
    "/Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/test1/"
)

if os.path.exists("./data"):
    shutil.rmtree("./data")
# os.system("rm -r data/*")
os.system("wingspipe delete -y")
os.system(
    "wingspipe init -w /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/build/ -i /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/input/ -c /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/config/default.conf"
)
os.system("wingspipe run")
