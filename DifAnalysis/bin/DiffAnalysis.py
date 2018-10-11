#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : DiffAnalysis.py


import os
import sys
import re


# -------------------------------------- add environment variable -------------------------------------- #
parent_path = os.path.dirname(os.path.abspath(__file__))
parent_folder_pattern = re.compile('DifAnalysis.*')
while True:
    if re.match(parent_folder_pattern, os.path.basename(parent_path)):
        # add parent path to environment variables to make other modules can call each other
        sys.path.append(parent_path)
        break
    else:
        parent_path = os.path.dirname(parent_path)


from conf import settings

# ----------------------------- assign parent_path to settings.PARENG_PATH ----------------------------- #
settings.PARENG_PATH = parent_path

# ------- assign this module name to settings.ENTRY_FILE_NAME to be used in the qsub submit task ------- #
settings.ENTRY_FILE_NAME = os.path.basename(__file__)

# ---------------------------------- invoke the entry of this program ---------------------------------- #
from core import main


# ------------------- invoke the main function which will control the whole process -------------------- #
if __name__ == '__main__':
    main.run()
