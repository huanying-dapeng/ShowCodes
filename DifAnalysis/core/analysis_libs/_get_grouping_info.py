#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : get_grouping_field.py

import pandas as pd
from collections import defaultdict

from conf import settings


class GetGroupsSamples(object):
    __sd_obj = None

    def __init__(self, sep_filed):
        self.__field_name = sep_filed
        # ------------------------------- the file of containing the grouping fields --------------------------- #
        self.__file_name = ''
        # ------------------------------------------ the result list ------------------------------------------- #
        self.__group_list = []

        self.__is_run_analysis = False

    # ---------------------------------------------------------------------------------------------------------- #
    #                                     resolve age grouping problem                                           #
    # ---------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def __sort_age(age):
        age_to_sorted_age = settings.AGE_TO_AGEGROUP
        return age_to_sorted_age.get(age)

    # ---------------------------------------------------------------------------------------------------------- #
    #                                   grouping samples to certain groups                                       #
    # ---------------------------------------------------------------------------------------------------------- #
    def __get_grouping_list(self):

        """ get the grouping key words and assign it to the variable of instance """
        group_dict = defaultdict(list)
        try:
            df = pd.read_table(
                r'%s' % self.__file_name, sep='\t', usecols=[settings.SAMPLE_FIELD_NAME, self.__field_name]
            )
        except FileNotFoundError as e:
            print(e.args)

        # ------------------------------------------ delete NA ------------------------------------------------- #
        if settings.IS_DEL_NA:
            df.dropna(inplace=True)

        # ----------------------------- separate samples into different groups --------------------------------- #
        for g, f in zip(df[settings.SAMPLE_FIELD_NAME], df[self.__field_name]):

            # ------------------------------- resolve age groups ----------------------------------------------- #
            if self.__field_name.lower() == 'age':
                f = self.__sort_age(f)

            group_dict[f].append(g)

        # ---------------------------------- translate the result to list -------------------------------------- #
        for k, v in group_dict.items():
            self.__group_list.append(v)

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             property function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @property
    def group_file(self):
        return None

    @group_file.setter
    def group_file(self, file_name):
        """
        assign file name to the instance of SepData

        :param file_name: str
            grouping file name
        :return: None
        """
        self.__sd_obj.__group_list = []
        self.__is_run_analysis = True
        self.__file_name = file_name

    @property
    def group_keys_list(self):
        """
        provide the result of analysis:
            [df1, df2, ......]

        :return: data-frame list
        """
        if self.__is_run_analysis:
            self.__get_grouping_list()
            self.__is_run_analysis = False
        return self.__group_list

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             singleton pattern                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @classmethod
    def get_instance(cls, sep_filed):
        """ create singleton pattern """
        if cls.__sd_obj is None:
            # create a instance of SepData
            cls.__sd_obj = GetGroupsSamples(sep_filed)

        return cls.__sd_obj
