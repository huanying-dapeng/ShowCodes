#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

import os
import logging


# -------------------------------------------------------------------------------------------- #
#                      the cmd format of decompressing file                                    #
# -------------------------------------------------------------------------------------------- #

# ************** Note: users are not allowed to changed "{}" and content of it *************** #
# user can change options such as "-qod", "-c", "-xzf", "xf"
# --- r'gunzip -c {abspath} > {file_dir} --- #
# --- r'cd {file_dir}; gunzip {abspath} --- #
CMD_FORMAT = {
    'zip': r'unzip -qod {file_dir} {abspath}',
    'gz': r'gunzip {abspath}',
    'tar.gz': r'tar -xzf {abspath} -C {file_dir}',
    'tar': r'tar -xf {abspath} -C {file_dir}'
}

# -------------------------------------------------------------------------------------------- #
# the types of compressed files, which are used to obtain the compressed files from all files  #
# -------------------------------------------------------------------------------------------- #

# the types of compressed documents  ['gz', 'tar', 'zip', 'tar.gz']
COMPRESSED_FILE_TYPE = CMD_FORMAT.keys()




# -------------------------------------------------------------------------------------------- #
# the following parameters are used by logger module to be convenient for user to set it.      #
# -------------------------------------------------------------------------------------------- #

# set logging level
LOG_LEVEL = logging.INFO

# the output files name of logs
LOG_TYPES = {
    'unpack_file': 'decompress_file.log',
    'compressed_file_dir': 'compressed_file_dir.log'
}

# whither to output log to the current path
IS_CURRENT_PATH = False
# UnpackFiles folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if IS_CURRENT_PATH is True:
    # ******************* the current path of UnpackFiles running ******************* #
    BASE_DIR = os.path.abspath(".")

# log output format
FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# *************************** the separation times ********************************* #
# when get the failed files abspath, we need separate the line and then get the content
LOG_SEP_NUM = FORMATTER.count('-')
if 'asctime' in FORMATTER:
    LOG_SEP_NUM += 2

# -------------------------------------------------------------------------------------------- #
# the way of submitting tasks: qsub, nohup, or command                                         #
# -------------------------------------------------------------------------------------------- #

# **************** set the qsub default parameter: size of CPU and Memory ******************** #

SUBMIT_WAYS = {
        'qsub': r'qsub {run_cmd}',
        'nohup': r'nohup {run_cmd} &',
        'command': r'{run_cmd}'
    }

NUM_TYPE_TO_SUB = {
    '1': 'qsub',
    '2': 'nohup',
    '3': 'command'
}

# -------------------------------------------------------------------------------------------------------------- #
# it is a legacy: because it is only used in our server node( non-commonality )                                  #
# QSUB_PARA = {                                                                                                  #
#     'CPU': 2,                                                                                                  #
#     'Memory': 4                                                                                                #
# }                                                                                                              #
#                                                                                                                #
#                                                                                                                #
# def set_SUBMIT_WAYS(qsub_para=QSUB_PARA):                                                                      #
#     SUBMIT_WAYS['qsub'] = r'cmd_qsub {name} %s %sG cmd: {run_cmd}' % (qsub_para['CPU'], qsub_para['Memory'])   #
# -------------------------------------------------------------------------------------------------------------- #

# ************************* set the default submit command type ****************************** #
DEFAULT_SUBMIT_TYPE = '1'

# -------------------------------------------------------------------------------------------- #
#           the variable:  decide whether logs are printed in screen(STDOUT)                   #
# -------------------------------------------------------------------------------------------- #

IS_STDOUT_LOG = False

# -------------------------------------------------------------------------------------------- #
# when the compressed files' names are xxx.zip(not xxx.jpg.zip), we will create a new folder   #
# to save the result                                                                           #
# -------------------------------------------------------------------------------------------- #

IS_NEW_FOLDER = True

# -------------------------------------------------------------------------------------------- #
#                          the default param of qsub task file                                 #
# -------------------------------------------------------------------------------------------- #
# ********** the str are wrapped in double quotes and  at the same time in single quotes, because  
#     it in settings.py is invoked and then writen to file of qsub_setting.py in which it is also 
#     remaining a string when it isinvoked ****************************************************** #

QSUB_PARAM = {
    'job_name': '"Qsub_task"',
    'nodes number': 1,
    'ppn(cpu number)': 2,
    'memory size(G)': 4,
    'node name': '"zh"'
}
