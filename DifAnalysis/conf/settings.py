#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : settings.py

import os

# ----------------------------------------------------------------------------------------------------- #
#             the fields which users can select to group data to several groups                         #
# ----------------------------------------------------------------------------------------------------- #
FIELDS = '''
    gender;              age;               vital_status;   race;           ethnicity;      tumor_tissue_site;   
    clinical_stage;      hpv_types_other;   pathologic_T;   pathologic_N;   pathologic_M;   menopause_status;     
    histological_type;   tumor_response;    tumor_status; 
'''
# ----------------------------------------------------------------------------------------------------- #
#                          samples field name or the field being grouped                                #
# ----------------------------------------------------------------------------------------------------- #
SAMPLE_FIELD_NAME = 'patient_barcode'

# ----------------------------------------------------------------------------------------------------- #
#          the variable decide whether drop the line which contain NAN/nan/NaN/....                     #
# ----------------------------------------------------------------------------------------------------- #
IS_DEL_NA = True

# ----------------------------------------------------------------------------------------------------- #
#          the variable decide whether judge the number of samples of each DataFrame                    #
# ----------------------------------------------------------------------------------------------------- #
IS_JUDGE_SAMPLE_NUM = False

# ----------------------------------------------------------------------------------------------------- #
#          the variable decide whether del the DataFrame which contain less than 3 samples              #
# ----------------------------------------------------------------------------------------------------- #
IS_DEL_FAIL = True

# ----------------------------------------------------------------------------------------------------- #
#                                    group the age to age groups                                        #
# ----------------------------------------------------------------------------------------------------- #
# AGE_SORT_DICT = {
#     '<= 20': [],
#     '20 - 40': [],
#     '40 - 60': [],
#     '60 - 80': [],
#     '> 80': []
# }
# ------------------------   legacy AGE_TO_AGEGROUP   --------------------------- #
# AGE_TO_AGEGROUP = {
#     **dict.fromkeys([i for i in range(1,20)], '<= 20'),
#     **dict.fromkeys([i for i in range(20,40)], '20 - 40'),
#     **dict.fromkeys([i for i in range(40,60)], '40 - 60'),
#     **dict.fromkeys([i for i in range(60,80)], '60 - 80'),
#     **dict.fromkeys([i for i in range(80,150)], '> 80'),
# }
# --------------------------   new AGE_TO_AGEGROUP   ---------------------------- #
# the advantage --> change the step value quickly
#       only change the following _STEP variable


def group_ages():
    age_dic = dict()
    # main block of generate dict
    _STEP = 20
    _LARGE_AGE = 150
    _FINAL_STR = ''
    for i, s in enumerate(range(0, _LARGE_AGE, _STEP)):
        if i == 0:
            continue
        elif i == 1:
            group_str = '<= {}'.format(s)
        elif s == 100-100 % _STEP:
            group_str = '> {}'.format(s - _STEP)
            _FINAL_STR = group_str
        elif s > 100-100 % _STEP:
            group_str = _FINAL_STR
        else:
            group_str = '{} - {}'.format(s-_STEP, s)

        age_dic.update(
            {
                **dict.fromkeys([i for i in range(s-_STEP, s)], group_str)
            }
        )
    return age_dic


AGE_TO_AGEGROUP = group_ages()

# ----------------------------------------------------------------------------------------------------- #
#                                    the DifAnalysis's path                                             #
# ----------------------------------------------------------------------------------------------------- #
# PARENG_PATH's value will get the path from the block of DiffAnalysis.py
PARENG_PATH = ''

def JSON_FILE_ABSPATH():
    # JSON_FILE_ABSPATH = os.path.join(PARENG_PATH, 'bd', 'temporarily_save_params.json')
    return os.path.join(PARENG_PATH, 'db', 'temporarily_save_params.json')

# ----------------------------------------------------------------------------------------------------- #
#                        ENTRY_FILE_NAME: save the module name of program tarting                       #
# ----------------------------------------------------------------------------------------------------- #
# ENTRY_FILE_NAME DiffAnalysis.py module will assign value to in the start of program running
ENTRY_FILE_NAME = ''
