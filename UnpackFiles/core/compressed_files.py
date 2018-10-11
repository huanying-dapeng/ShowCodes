#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

import os

from conf import settings


class CompressedFiles(object):
    """
    create a object, and we can get a detail list and its value is a dict contain abs_file_path, and its postfix

        user can create obj by inputting a dirs list, then user can obtain the result list by the files_dict()
    """
    def __init__(self, path_list):
        self.__path_list = path_list
        self.__result = []

    @staticmethod
    def __create_folder(file_dir):
        while True:
            if os.path.exists(file_dir):
                file_dir = '%s_NEW' % file_dir
            else:
                break

        os.mkdir(file_dir)
        return file_dir

    @staticmethod
    def __get_func_type(file_name):

        type_list = settings.COMPRESSED_FILE_TYPE
        fc = None
        is_cr_f = False
        if "." in file_name:
            try:
                name, pf1, pf2 = file_name.rsplit(".", 2)
                pf = '%s.%s' % (pf1, pf2)
                if pf2 in type_list and pf in type_list:
                    fc = pf
                elif pf2 in type_list:
                    fc = pf2
            except ValueError:
                name, pf1 = file_name.rsplit(".", 1)
                if pf1 in type_list:
                    fc = pf1
                if pf1 == 'zip':
                    is_cr_f = True
        return fc, is_cr_f

    def __get_all_comprsd_files(self):
        """
        get the abs_file_path and its postfix of all original and its sub-path

        :return: list(dict)
        """
        for p in self.__path_list:
            for root, dirs, files in os.walk(p):
                if files:
                    for f in files:
                        func, is_cr_file = self.__get_func_type(f)
                        if func:
                            file_dir = root
                            if is_cr_file:
                                new_dir = os.path.join(root, f.rsplit(".", 1)[0])
                                file_dir = self.__create_folder(new_dir)
                            abspath = os.path.join(root, f)
                            self.__result.append(
                                {
                                    'abspath': abspath,
                                    'file_dir': file_dir,
                                    'func': func
                                }
                            )

    @property
    def files_dict(self):
        self.__get_all_comprsd_files()
        return self.__result
