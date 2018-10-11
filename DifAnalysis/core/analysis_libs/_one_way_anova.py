#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : one_way_anova.py


from scipy.stats import f_oneway


# -------- ignore invalid value warnings such as RuntimeWarning --------- #
import numpy as np
np.seterr(invalid='ignore')


class OneWayAnova(object):

    def __init__(self, data_obj):

        # -------------- transpose the DataFrame to be convenient for calculate diff_p-value ------------------- #
        self.__data_groups_list = [i.T for i in data_obj.data_groups_list]

        # ------------------------------------- result of calculating ------------------------------------------ #
        # self.__group_mean = None
        # self.__group_var = None
        self.__test_result = None

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             analysis function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    def __analysis(self):

        # ------------------------------ calculate the variance of every group --------------------------------- #
        try:

            self.__test_result = f_oneway(*self.__data_groups_list)
            # *************  Prompt  ************** #
            # there we only provide the p-values of testing
            # and translate the result to a dict
            self.__test_result = {k: v for k, v in zip(self.__data_groups_list[0].columns, self.__test_result.pvalue)}
        except TypeError:
            pass

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             property function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @property
    def pvalue(self):
        # invoke analysis function
        self.__analysis()
        return self.__test_result

    # ---------------------------------------------------------------------------------------------------------- #
    #                                             property function                                              #
    # ---------------------------------------------------------------------------------------------------------- #
    @property
    def fold_change(self):
        return None
