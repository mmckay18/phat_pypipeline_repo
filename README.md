# Stellar Photometry Data Pipeline

![Astronomy](https://img.shields.io/badge/Field-Astronomy-blue)
![Last Commit](https://img.shields.io/github/last-commit/mmckay18/phat_pypipeline_repo)
![Repo Size](https://img.shields.io/github/repo-size/mmckay18/phat_pypipeline_repo)
![Contributors](https://img.shields.io/github/contributors/mmckay18/phat_pypipeline_repo)
![Pull Requests](https://img.shields.io/github/issues-pr/mmckay18/phat_pypipeline_repo)
![License](https://img.shields.io/github/license/mmckay18/phat_pypipeline_repo)
![Issues](https://img.shields.io/github/issues/mmckay18/phat_pypipeline_repo)
![Stars](https://img.shields.io/github/stars/mmckay18/phat_pypipeline_repo)
![Forks](https://img.shields.io/github/forks/mmckay18/phat_pypipeline_repo)

## Table of Contents

- [Contributors](#contributors)
- [Description](#description)
- [Workflow](#workflow)
- [Layout](#layout)
- [Requirements](#requirements)
- [Instructions](#instructions)

# Contributors:

- [Myles McKay](https://github.com/mmckay18)
- Ben Williams
- Shelby Albrecht
- Adrien Thob
- Tristan
- Zhuo Chen

# Description:

This pipeline is designed for photometry of Hubble Space Telescope (HST) and James Webb Space Telescope (JWST) data products. It is inspired by the AWS-based photometry pipeline developed by Ben Williams and Keith Rosema but is simplified and implemented in Python for ease of use and accessibility.

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
