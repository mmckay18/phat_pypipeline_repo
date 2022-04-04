#!/usr/bin/env python
import wpipe as wp
import numpy as np


def register(task):
    _temp = task.mask(source='*', name='start', value=task.name)
    _temp = task.mask(source='*', name='run_pypiper', value='*')


def run_pypiper():
    this_config = wp.ThisJob.config
    print('Running run_pypiper task')
    return this_config

# def sort_input_by_filter():


#     return


if __name__ == '__main__':
    # conf_params = wp.ThisJob.config.parameters
    run_pypiper()
