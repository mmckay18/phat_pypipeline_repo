import os
import shutil

os.chdir(
    "/Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/test_pypiper"
)
shutil.rmtree("./data")
# os.system("rm -r data/*")
os.system("wingspipe delete -y")
os.system(
    "wingspipe init -w /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/build/ -i /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/input/ -c /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/config/default.conf"
)
os.system("wingspipe run")
