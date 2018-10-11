#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/11/5

import os
import sys

# ---------------------------------------------------------------------------------------------------------- #
#     temporarily add UnpackFiles path of UnpackFiles to system environment variables      #
# ---------------------------------------------------------------------------------------------------------- #

# get the path of UnpackFiles folder
parent_dir = os.path.dirname(os.path.abspath(__file__))
while True:
    if os.path.basename(parent_dir) == 'UnpackFiles':
        # parent_path = temp_path
        break
    else:
        parent_dir = os.path.dirname(parent_dir)

# add all path to system environment variables
sys.path.append(parent_dir)


# ---------------------------------------------------------------------------------------------------------- #
#     import main module of core package, and call the call_run function of the main module                  #
# ---------------------------------------------------------------------------------------------------------- #

from conf import settings


com_file = os.path.join(parent_dir, 'log', settings.LOG_TYPES['unpack_file'])
decom_file = os.path.join(parent_dir, 'log', settings.LOG_TYPES['compressed_file_dir'])

with open(com_file, 'w') as _, open(decom_file, 'w') as __:
    pass
