#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/22
# @File    : get_all_params_by_input.py

import os
import json
import glob
import re
import sys

from conf import settings


class GetParams(object):

    def __init__(self):

        # --------------------- save the params to use in the following ---------------------- #
        self.__data_files_list = []  # [{'data_file': str/None, 'group_file': str/None, 'paired_file': str/None}, ...]
        self.__params_dic = {
            'field_name': None,  # str --- if sep_status is False --> group_file will be str
            'sep_status': None  # boolean: True, False, when sep_status is None, the program will be exit
        }

        self.__params_dict = {
            'data_files': self.__data_files_list,
            'params': self.__params_dic
        }

        self.__files_dict_list = self.__params_dict['data_files']
        self.__other_params_dict = self.__params_dict['params']

        self.__is_analysis = True

    # ----------------------------------------------------------------------------------------- #
    #                            save params to json file                                       #
    # ----------------------------------------------------------------------------------------- #
    def __write_params_to_file(self):
        # write params dict to json file for program to use to submit task
        with open(r'%s' % settings.JSON_FILE_ABSPATH(), 'w') as json_writer:
            json.dump(self.__params_dict, json_writer, indent='\t')

    # ----------------------------------------------------------------------------------------- #
    #                              get params from input                                        #
    # ----------------------------------------------------------------------------------------- #
    def __get_field_name(self):

        # ---------------------- prompt of fields user can select ----------------------------- #
        fields = settings.FIELDS

        # ----------------------- print the prompt info to screen ----------------------------- #
        print(
            '{fields}\n{prompt}'.format(
                fields=fields,
                prompt='\033[33;1mplease select one field name from the names above\033[0m'
            )
        )

        while True:
            field_name = input('\033[32;1m>>> \033[0m').strip()
            if not re.findall(field_name, fields):
                print('\033[33;1mERROR field name\033[0m')
            else:
                # return field name, and complete the input
                self.__params_dic['field_name'] = field_name
                break

    # ----------------------------------------------------------------------------------------- #
    #                            get params from input                                          #
    # ----------------------------------------------------------------------------------------- #
    def __get_paras_by_input(self):

        # -------------------------- get the value of sep_status ------------------------------ #
        while True:
            con_str = 'Whether the file has been separated into several files\nSuch as: file --> cancer_file, normal_file'
            status = input('{}\n\n\033[33;1m[y/n]\033[0m \033[32;1m>>> \033[0m'.format(con_str)).strip()
            status_dic = {'y': True, 'n': False}
            if status in status_dic:
                # *************   assign value to self.__params_dict   ************* #
                self.__params_dic['sep_status'] = status_dic.get(status, None)
                break
            else:
                print('\033[33;1minput ERROR\033[0m')
                continue

        data_f_common_str = input('input Normal/All matrix data file common str[such as: .All.xls]\n>>> ').strip()
        if not os.path.exists(data_f_common_str):
            data_files = glob.iglob(r'*{}*'.format(data_f_common_str))
        else:
            data_files = glob.iglob(r'%s' % data_f_common_str)

        # -------------------- get data_file, group_file, paired_file ------------------------- #
        grouping_f_common_str = None  # the grouping field file
        file_dir = None  # the path of group file
        paired_f_common_str = None  # paired file name's common str

        for d_file in data_files:

            # --------------- this three variables is the params being get -------------------- #
            cancer = d_file.split(".")[0]
            group_file = None
            paired_file = None

            if not self.__params_dic['sep_status']:
                # ----------------- get grouping field name from input ------------------------ #
                if not self.__params_dic['field_name']:
                    # if grouping field name is not None, it will run self.__get_field_name() to
                    # get the field name
                    self.__get_field_name()

                # only grouping_f_common_str and fil_dir are None, then it will run input() function
                # to get the related common string
                grouping_f_common_str = grouping_f_common_str \
                    if grouping_f_common_str else input('input grouping file name common str\n>>> ').strip()

                file_dir = file_dir \
                    if file_dir else input('input grouping file path\n>>> ').strip()

                # judge whether the grouping_f_common_str is file and when it is None, the following
                # code line will not run
                maybe_file = os.path.join(file_dir, grouping_f_common_str)
                if not os.path.isfile(maybe_file):
                    # possible files of grouping files
                    group_file = os.path.join(
                        '{path}'.format(path=file_dir), '{}{}'.format(cancer, grouping_f_common_str)
                    )

                    if not os.path.isfile(group_file):
                        group_file = os.path.join(
                            '{path}'.format(path=file_dir), '{}{}'.format(cancer.lower(), grouping_f_common_str)
                        )
                    elif not os.path.isfile(group_file):
                        continue

                else:
                    group_file = maybe_file

            elif self.__params_dic['sep_status']:
                # ------------------- get paired field name from input ------------------------- #
                paired_f_common_str = paired_f_common_str \
                    if paired_f_common_str else input('input other paired file name common str\n>>> ')

                if not os.path.exists(paired_f_common_str):
                    paired_file = '{}{}'.format(cancer, paired_f_common_str)
                    if not os.path.exists(paired_file):
                        print('\033[33;1m{} is not exist\033[0m'.format(paired_file))
                        continue
                else:
                    paired_file = paired_f_common_str

            # -------------------- assign values to the params dict ---------------------------- #
            self.__data_files_list.append(
                {
                    'data_file': os.path.abspath(d_file) if d_file else d_file,
                    'group_file': os.path.abspath(group_file) if group_file else group_file,
                    'paired_file': os.path.abspath(paired_file) if paired_file else paired_file,
                    'cancer': cancer
                 }
            )
            # write params to json file
        self.__write_params_to_file()

    # ------------------------------------------------------------------------------------------- #
    #       provide entry of this block from which the following program can get params           #
    # ------------------------------------------------------------------------------------------- #
    @property
    def params_dict(self):

        if self.__is_analysis:
            self.__get_paras_by_input()
            self.__is_analysis = False

        return self.__other_params_dict

    @property
    def data_files_list(self):
        if self.__is_analysis:
            self.__get_paras_by_input()
            self.__is_analysis = False

        return self.__files_dict_list


# ---------------------------------- GetParamsFromFile class -------------------------------- #
class GetParamsFromFile(object):
    """
    get the params from json file:
        1. {
            'data_files': [
                {
                    'data_file': os.path.abspath(d_file),
                    'group_file': os.path.abspath(group_file),
                    'paired_file': os.path.abspath(paired_file),
                    'cancer': cancer
                }
                ... ...
            ]
            'param': {
                'field_name': None,  # str --- if sep_status is False --> group_file will be str
                'sep_status': None
            }
        }

    """
    def __init__(self):
        try:
            self.__json_file = sys.argv[1]
            self.__has_argvs = True
        except IndexError:
            self.__has_argvs = False

    @property
    def params_dict(self):

        if not self.__has_argvs:
            return None

        with open(r'%s' % settings.JSON_FILE_ABSPATH()) as json_reader:
            __params_dict = json.load(json_reader)
        return __params_dict

    @property
    def clear_params_file(self):

        with open(r'%s' % settings.JSON_FILE_ABSPATH(), 'w') as json_writer:
            json.dump({}, json_writer, indent='\t')
        return None
