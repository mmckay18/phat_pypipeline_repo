# phat_pypipeline_repo

# Contributors:

- [Myles McKay](https://github.com/mmckay18)
- Ben Williams
- Shelby Albrecht
- Adrien Thob
- Tristan
- Zhuo Chen

# Description:

Photometry pipeline for HST and JWST data products. The pipeline has a similar structure to AWS based photomerty pipeline by Ben Williams and Keith Rosema but simplifies it by being written in Python.

## Workflow

```mermaid
graph LR

sort.py --> tag_image.py --> astrodrizzle.py --> find_reference.py --> prep_image.py --> make_param.py --> run_dolphot.py

```

## Layout

| Task              | Description                                          | Link                                  |
| ----------------- | ---------------------------------------------------- | ------------------------------------- |
| sort.py           | Sort all the input image by target                   | [Click Here](build/sort.py)           |
| tag_image.py      | Tag images associated with each target               | [Click Here](build/tag_image.py)      |
| astrodrizzle.py   | Drizzle tagged images                                | [Click Here](build/astrodrizzle.py)   |
| find_reference.py | Selects reference file                               | [Click Here](build/find_reference.py) |
| prep_image.py     | Run DOLPHOT preprocessing steps                      | [Click Here](build/prep_image.py)     |
| make_param.py     | Sets DOLPHOT parameter in targete configuration file | [Click Here](build/make_param.py)     |
| run_dolphot.py    | Execute DOLPHOT to make photometry catalog           | [Click Here](build/run_dolphot.py)    |

# Requirements

- DOLPHOT - http://americano.dolphinsim.com/dolphot/
- Space Telescope Python environment - https://stenv.readthedocs.io/en/latest/
- DEEPCR - https://deepcr.readthedocs.io/en/latest/

# Instructions

0. Install wpipe: (https://github.com/benw1/WINGS)
1. Clone repository

```git
git clone https://github.com/mmckay18/phat_pypipeline_repo
```

2. Stores HST and JWST calibrated dataproducts ('\*flc.fits') in a directory called 'Unsorted/' and move to input directory
3. (Optional) Add astrodrizzle and/or DOLPHOT parameters to [config/default.conf](config/default.conf)
4. Initialize wingspipe in working directory and sets paths to the cloned repo build, input directories and configuration file

```wpipe
"wingspipe init -w /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/build/ -i /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/input/ -c /Users/mmckay/phd_projects/phat_pipeline_dev/phat_pypipeline_repo/config/default.conf"
```

5. Run wingspipe

```wpipe
wingspipe run
```

_Important Note_

All input FITS files must be in a directory called Unsorted/ to work properly
