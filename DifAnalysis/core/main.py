#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : mian.py

import os
import numpy as np

from core import sep_data_to_groups as sep_g
from core import dif_analysis as anls
from core import get_all_params_by_input as get_params_m
from core import submit_task as sub_t


def _output_data(
        pvalue=None, fold_change=None, delta_beta=None, var_value=None, mean_value=None, median_value=None,
        save_file='', save_path=''
):
    """
    output the data to file

    :param p_value: dict
    :param fold_ch: dict
    :param save_file: str
    :param save_path: str
    :return: None
    """
    # -------------------  create saving file path if it is not exist  ---------------- #
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_file = os.path.join(save_path, save_file)

    # -----------------------------  output data to file  ----------------------------- #
    if pvalue and fold_change is None:
        #  **********    only p_value    **********  #
        with open(r'%s' % save_file, 'w') as my_writer:
            # title -- the first line of file
            my_writer.write('gene\tp_value\n')
            for k, v in pvalue.items():
                my_writer.write('{}\t{}\n'.format(k, v))

    elif fold_change and fold_change:
        #  *******    both p_value and fold_change    **********  #
        with open(r'%s' % save_file, 'w') as my_writer:
            # title -- the first line of file
            value_list = [
                ('p_value', pvalue),
                ('log2_fc', fold_change),
                ('delta_beta', delta_beta),
                ('N_mean', mean_value[0]),
                ('T_mean', mean_value[1]),
                ('N_median', median_value[0]),
                ('T_median', median_value[1]),
                ('N_var', var_value[0]),
                ('T_var', var_value[1]),
            ]
            my_writer.write('{}\n'.format('\t'.join(['gene', *[i[0] for i in value_list]])))
            for k in fold_change:
                my_writer.write('{}\n'.format('\t'.join([k, *[str(i[1].get(k, np.nan)) for i in value_list]])))


def _main(group_file=None, data_file=None, paired_file=None, cancer=None, field_name=None, sep_status=None):

    # ------------------------------- separate data ----------------------------------- #
    if not sep_status:
        groups_obj = sep_g.SepData.get_instance(field_name)
        # --- add corresponding files to grouping_obj to get the data_groups list ----- #
        groups_obj.group_file = group_file
        groups_obj.data_file = data_file
    else:
        groups_obj = sep_g.ExtractSepedData.get_instance()
        groups_obj.file_list = [data_file, paired_file]

    # -------------------------- differential analysis instance ------------------------ #
    analysis = anls.DifferentAnalysis.get_instance(groups_obj)

    # ----------------------------- output data to files ------------------------------- #
    save_file_name = '{}_{}_diff_analysis_result.tsv'.format(cancer, field_name if field_name else 'N_T')
    save_folder = '{}_differential_analysis_result'.format(field_name if field_name else 'N_T')
    _output_data(
        pvalue=analysis.pvalue,
        fold_change=analysis.fold_change,
        delta_beta=analysis.delta_beta,
        mean_value=analysis.mean_value,
        var_value=analysis.var_value,
        median_value=analysis.median_value,
        save_file=save_file_name,
        save_path=save_folder
    )


def _submit_type():
    submit_type_dict = {'1': 'qsub', '2': 'nohup', '3': 'cmd_line'}

    while True:
        qsub_type = input('\033[33;1m1\033[0m: qsub, \033[33;1m2\033[0m: nohup, \033[33;1m3\033[0m: cmd_line' +
                          '\nplease \033[33;1minput 1/2/3\033[0m \033[32;1m>>>\033[0m')
        if qsub_type not in submit_type_dict:
            print('input ERROR')
            continue
        break
    return submit_type_dict[qsub_type]


def run():
    """
    the entry of this program core:
        it will regulate all the program

    :return: None
    """
    get_fparams = get_params_m.GetParamsFromFile()
    fparams_dict = get_fparams.params_dict

    # judge whether code is running in the cmd_line
    _is_cmd_line = True

    if not fparams_dict:

        get_param = get_params_m.GetParams()
        #  [{'data_file': str/None, 'group_file': str/None, 'paired_file': str/None}, ...]
        files_dict_list = get_param.data_files_list
        params_dict = get_param.params_dict

        qsub_type = _submit_type()

        if qsub_type != 'cmd_line':
            sub_t.submit(qsub_type)
            _is_cmd_line = False

    else:
        _is_cmd_line = True
        files_dict_list, params_dict = (lambda data_files='', params='': (data_files, params))(**fparams_dict)

    # ----- That sep_status is None indicates that the content use typing is Error ----- #
    if _is_cmd_line:
        for files_dict in files_dict_list:
            # invoke the main function
            _main(**files_dict, **params_dict)
