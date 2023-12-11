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

## Workflow

The workflow gives instructions on the steps you should take to get started with the sample pipeline. The steps are as follows:

```mermaid
graph LR

PreFlightChecklist --> Cluster --> Delegate --> Secrets --> Connectors --> Project --> Pipeline --> PipelineExecution

```

## Layout

| Docs | Description | Link |
| --- | --- | --- |
| PreFlight Checklist | A checklist for all the pre-requisites | [Click Here](docs/PreFlightChecklist.md) |
| Cluster | Steps to set up GKE and AKS| [Click Here](docs/clusters) 
| Delegate | Steps to set up the Harness Delegate  | [Click Here](docs/delegates) |
| Secrets | Learn about Secrets and steps to set them up | [Click Here](docs/secrets) |
| Connectors | Steps the to set up Docker and GitHub Connectors  | [Click Here](docs/connectors) |



_Important Note_

All input FITS files must be in a directory called Unsorted/ to work properly
