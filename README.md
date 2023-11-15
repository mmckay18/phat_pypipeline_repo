# phat_pypipeline_repo

# Authors:

- Myles McKay
- Ben Williams
- Shelby Albrecht
- Adrien Thob
- Tristan
- Zhuo Chen

# Description:

Photometry pipeline for HST and JWST data products. The pipeline has a similar structure to AWS based photomerty pipeline by Ben Williams and Keith Rosema but simplifies it by being written in Python.

# How it works

- User stores there HST and JWST calibrated dataproducts ('\*flc.fits') in a directory called 'Unsorted'

_Important Note_

All input FITS files must be in a directory called Unsorted/ to work properly
