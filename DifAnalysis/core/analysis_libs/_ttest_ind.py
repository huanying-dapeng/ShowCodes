#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : ttest_ind.py

import numpy as np

from scipy.stats import ttest_ind

from conf import ttest_setting as ts

# -------- ignore invalid value warnings such as RuntimeWarning --------- #
np.seterr(invalid='ignore')


class TtestInd(object):

    def __init__(self, data_obj):
        self.__data_groups_list = data_obj.data_groups_list

        # ----------------------------------- result of calculating ------------------------------------- #
        self.__p_val_result = None
        self.__delta_beta = None
        self.__fold_change = None
        self.__group_mean = None
        self.__group_var = None

    # --------------------------------------------------------------------------------------------------- #
    #                                          analysis function                                          #
    # --------------------------------------------------------------------------------------------------- #
    def __analysis(self):

        # group_one, group_two = None, None

        try:
            group_one, group_two = self.__data_groups_list
        except ValueError as e:
            print(e.args)
            # group_one = self.__data_groups_list[0]
            # group_two = self.__data_groups_list[1]

        # ---------------------- calculate the mean of every group -------------------------------------- #
        group_one_mean = group_one.mean(axis=ts.AXIS)
        group_two_mean = group_two.mean(axis=ts.AXIS)

        self.__group_mean = [
            {k: v for k, v in group_one_mean.items()},
            {k: v for k, v in group_two_mean.items()}
        ]

        # ------------------------------ calculate fold change ------------------------------------------ #
        with np.errstate(divide='ignore'):
            self.__fold_change = {k: v for k, v in np.log2(group_two_mean / group_one_mean).items()}

        # *************  Prompt  ************** #
        # and translate the result to a dict
        self.__fold_change = {k: v for k, v in self.__fold_change.items()}

        # ---------------------- calculate the median of every group ---------------------------------- #
        group_one_median = group_one.median(axis=ts.AXIS)
        group_two_median = group_two.median(axis=ts.AXIS)
        self.__group_median = [
            {k: v for k, v in group_one_median.items()},
            {k: v for k, v in group_two_median.items()}
        ]

        # ----------------------- calculate the delta beta value of every group ------------------------- #
        # **********  group_one_median - group_two_median  ********** #
        self.__delta_beta = {
            k: v for k, v in (group_two_median - group_one_median).items()
        }

        # ---------------------- calculate the variance of every group ---------------------------------- #
        self.__group_var = [
            {k: v for k, v in group_one.var(axis=ts.AXIS).items()},
            {k: v for k, v in group_two.var(axis=ts.AXIS).items()}
        ]

        # ------------------------ calculate the variance of every group -------------------------------- #
        try:
            # test_result = ttest_ind(group_one, group_two, axis=ts.AXIS, equal_var=ts.EQUAL_VAR)
            test_result = ttest_ind(*self.__data_groups_list, axis=ts.AXIS, equal_var=ts.EQUAL_VAR)
            # *************  Prompt  ************** #
            # there we only provide the p-values of testing
            # and translate the result to a dict

            self.__p_val_result = {k: v for k, v in zip(self.__data_groups_list[0].index, test_result.pvalue)}
        except TypeError:
            pass

    # --------------------------------------------------------------------------------------------------- #
    #                                     property function of pvalue                                     #
    # --------------------------------------------------------------------------------------------------- #
    @property
    def pvalue(self):
        if self.__p_val_result is None:
            self.__analysis()

        return self.__p_val_result

    @property
    def fold_change(self):
        if self.__p_val_result is None:
            self.__analysis()
        return self.__fold_change

    @property
    def delta_beta(self):
        if self.__p_val_result is None:
            self.__analysis()
        return self.__delta_beta

    @property
    def mean_value(self):
        if self.__p_val_result is None:
            self.__analysis()
        return self.__group_mean

    @property
    def var_value(self):
        if self.__p_val_result is None:
            self.__analysis()
        return self.__group_var

    @property
    def median_value(self):
        if self.__p_val_result is None:
            self.__analysis()
        return self.__group_median
