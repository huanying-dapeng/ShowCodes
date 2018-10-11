#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

import os

from conf import settings
# from core import lib
from core.co_lib import _submit_command as sc

# the functions other modules can import
# Note:  more names are added to __all__ later.
__all__ = ['uncompress_file']


# ---------------------------------------------------------------------------------------- #
# the entry of this module                                                                 #
# ---------------------------------------------------------------------------------------- #


def uncompress_file(dic, qsub_type, log_obj, *args):
    """
    the entry of this module, by which the related function will be called to decompressed the files
    dic = {
        'abspath': abspath,
        'file_dir': file_dir,
        'func': func
    }

    :param dic:
    :param cmd_type:
    :param log_obj:
    :param args:
    :return:
    """

    func = dic['func']
    abs_file_path = dic['abspath']
    # folder's abspath of saving result
    file_dir = dic['file_dir']  # a/b/c/e

    # the name of compressed file
    basename = os.path.basename(abs_file_path)  # a.txt.gz
    # abspath of compressed file containing the postfix
    abs_path = abs_file_path  # a/b/c/e.txt.gz

    if settings.CMD_FORMAT.get(func):
        submit_handler = sc.UpackMethod.get_instance(qsub_type)
        # submit_task(self, file_dir, basename, abs_path, log_obj, unp_type)
        # get the related function through the dict <-- func_dict
        submit_handler.submit_task(file_dir, basename, abs_path, log_obj, func, *args)
