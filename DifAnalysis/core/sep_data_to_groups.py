#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : sep_data_to_groups.py

import pandas as pd

from core.analysis_libs import _get_grouping_info as get_g


class SepData(object):

    __sep_obj = None

    def __init__(self, sep_field):
        self.__data_file = ''
        self.__group_file = ''
        self.__data_groups = []
        self.__sep_field = sep_field

        self.__is_run_analysis = False

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             analysis function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    def __group_data(self):

        # --------------------------------------- get grouping keys list --------------------------------------- #
        # get the grouping key words list: [[group one], [group two], ...]
        group_obj = get_g.GetGroupsSamples.get_instance(self.__sep_field)
        # add file name to group_obj instance
        group_obj.group_file = self.__group_file
        # get the group words list
        group_keys_list = group_obj.group_keys_list

        # --------------------------------------- separate the data file --------------------------------------- #
        data_df = pd.read_table(r'%s' % self.__data_file, sep='\t', index_col=0)
        columns = data_df.columns
        if len(group_keys_list[0][0].split("-")) != len(columns[0].split("-")):
            columns = [i.rsplit("-", 1)[0] for i in columns]
            data_df.columns = columns

        # group data and add it to self.__data_groups
        for g in group_keys_list:
            g = [i.strip() for i in g]
            # data_df[list(set(g) & set(columns)):
            # get intersection elements to avoid some samples not in the data file columns which will cause error
            self.__data_groups.append(data_df[list(set(g) & set(columns))])

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             property function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @property
    def data_groups_list(self):
        """ provide a entry of getting result """
        if self.__is_run_analysis:
            self.__group_data()
            self.__is_run_analysis = False
        return self.__data_groups

    @property
    def data_file(self):
        return None

    @data_file.setter
    def data_file(self, d_file):
        """
        set data_file

        :param d_file:
            contain the expression or other data which will be analyzed by ttest_ind or ANOVA
        :return:
        """
        self.__data_file = d_file

    @property
    def group_file(self):
        return None

    @group_file.setter
    def group_file(self, g_file):
        """
        set group_file

        :param g_file:  the file contains the grouping field
        :return:
        """
        self.__group_file = g_file

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             singleton pattern                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @classmethod
    def get_instance(cls, sep_field):
        """
        create singleton pattern

        :param sep_field: str
        :return: instance of SepData class
        """
        if cls.__sep_obj is None:
            cls.__sep_obj = SepData(sep_field)
        # in order to make sure that the analysis is invoked only once every group file
        cls.__sep_obj.__is_run_analysis = True
        cls.__sep_obj.__data_groups = []

        return cls.__sep_obj


class ExtractSepedData(object):

    __obj = ''

    def __init__(self):
        self.__data_groups_list = []
        self.__file_list = []
        self.__is_run_analysis = False

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             analysis function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    def __extract_dataframe(self):
        """get the dataframes of files to list

            1. get the common indexes of dataframes
            2. only get the data of common indexes
                get the data through the orders of indexes list
        """
        for f in self.__file_list:
            df = pd.read_table(r'%s' % f, sep='\t', index_col=0)
            self.__data_groups_list.append(df)
        # get the common indexes
        common_set = set(self.__data_groups_list[0].index)
        for d in self.__data_groups_list:
            common_set = common_set & set(d.index)
        # change the indexes set to an list to make the data has common index list
        common_list = list(common_set)
        # get the common indexes data to list
        self.__data_groups_list = [d.ix[common_list] for d in self.__data_groups_list]

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             property function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @property
    def file_list(self):
        return None

    @file_list.setter
    def file_list(self, args_list):
        self.__file_list = args_list

    @property
    def data_groups_list(self):
        if self.__is_run_analysis:
            self.__extract_dataframe()
            self.__is_run_analysis = False
        return self.__data_groups_list

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             singleton pattern                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @classmethod
    def get_instance(cls):

        if not cls.__obj:
            cls.__obj = ExtractSepedData()
        cls.__obj.__is_run_analysis = True
        cls.__obj.__data_groups_list = []

        return cls.__obj
