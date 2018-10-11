#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : analysis.py

from core.analysis_libs import _ttest_ind
from core.analysis_libs import _one_way_anova
from conf import settings


class DifferentAnalysis(object):

    __dif_ana_obj = None

    def __init__(self):
        self.__data_obj = ''
        self.__test_obj = ''
        self.__is_run_analysis = False

    # ----------------------------------------------------------------------------------------------------- #
    #                                          analysis function                                            #
    # ----------------------------------------------------------------------------------------------------- #
    def __analysis(self):

        num_val = len(self.__data_obj.data_groups_list)

        if num_val > 2:

            # -------------------------------- use ANOVA to analyze the data ------------------------------ #
            is_analysis = True

            # ---------------------  resolve the DataFrame of not meeting requirement  -------------------- #
            if settings.IS_JUDGE_SAMPLE_NUM:

                if settings.IS_DEL_FAIL:

                    #  ------------------------------  del the fail data  --------------------------------- #
                    for i, gd in enumerate(self.__data_obj.data_groups_list):
                        if len(gd) < 3:
                            # del the less than 3 samples list
                            del self.__data_obj.data_groups_list[i]
                else:
                    # ------------------ judge the num of samples of each DataFrame ----------------------- #
                    #  *********  if num is less than 3, give up calculate its test  **********  #
                    for gd in self.__data_obj.data_groups_list:
                        if len(gd) < 3:
                            is_analysis = False

            if is_analysis:
                # ----------------- only when is_analysis is True, the following will run ----------------- #
                self.__test_obj = _one_way_anova.OneWayAnova(self.__data_obj)

        elif num_val == 2:

            # ------------------------------ use ttest_ind to analyze the data ---------------------------- #
            is_analysis = True
            for gd in self.__data_obj.data_groups_list:
                if len(gd) < 3:
                    is_analysis = False
            if is_analysis:
                self.__test_obj = _ttest_ind.TtestInd(self.__data_obj)

    # ----------------------------------------------------------------------------------------------------- #
    #                                          property function                                            #
    # ----------------------------------------------------------------------------------------------------- #
    @property
    def pvalue(self):
        p_value = None
        # ----------  judge whether the __test_obj is None; If it is None, that will illustrate ----------- #
        # ----------------------  that self.__analysis() is not running  ---------------------------------- #
        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        # ---------------- resolve the AttributeError, because self.__test_obj may be empty --------------- #
        try:
            p_value = self.__test_obj.pvalue
        except AttributeError:
            pass
        finally:
            return p_value

    @property
    def fold_change(self):
        f_ch = None

        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        # resolve the AttributeError, because self.__test_obj may be empty
        try:
            f_ch = self.__test_obj.fold_change
        except AttributeError:
            pass
        finally:
            return f_ch

    @property
    def delta_beta(self):

        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        try:
            d_beta = self.__test_obj.delta_beta
        except AttributeError:
            d_beta = None
        finally:
            return d_beta

    @property
    def mean_value(self):

        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        try:
            m_value = self.__test_obj.mean_value
        except AttributeError:
            m_value = None
        finally:
            return m_value

    @property
    def var_value(self):

        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        try:
            v_value = self.__test_obj.var_value
        except AttributeError:
            v_value = None
        finally:
            return v_value

    @property
    def median_value(self):

        if self.__is_run_analysis:
            self.__analysis()
            self.__is_run_analysis = False

        try:
            md_value = self.__test_obj.median_value
        except AttributeError:
            md_value = None
        finally:
            return md_value

    # ----------------------------------------------------------------------------------------------------- #
    #                                          singleton pattern                                            #
    # ----------------------------------------------------------------------------------------------------- #
    @classmethod
    def get_instance(cls, data_group_obj):
        """ create singleton pattern """
        if cls.__dif_ana_obj is None:
            cls.__dif_ana_obj = DifferentAnalysis()

        cls.__dif_ana_obj.__data_obj = data_group_obj
        cls.__dif_ana_obj.__is_run_analysis = True

        return cls.__dif_ana_obj
