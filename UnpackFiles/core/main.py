#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

"""the main entry of functions' code, which coordinate all modules"""

# import time
from concurrent.futures import ThreadPoolExecutor

from core import collect_unpack_file_path as fp
from core import compressed_files as cf
from core import logger
from core import unpack
from core.co_lib import _recv_submit_type as rst

# unpack logger
unpack_logger = logger.logger('unpack_file')
# input dir logger
input_dir_logger = logger.logger('compressed_file_dir')

# -------------------------------------------------------------------------------------------- #
#                    the entry of calling functions of submitting tasks                        #
# -------------------------------------------------------------------------------------------- #


def _call_unpack(f_dic_list, cmd_type):

    sleep_flag = 0
    # unpack compressed files one by one
    with ThreadPoolExecutor(max_workers=10) as future:
        for i, fd in enumerate(f_dic_list):
            # print progress bar
            print(i + 1)
            # unpack by following method
            future.submit(unpack.uncompress_file, fd, cmd_type, unpack_logger, i + 1)

        # # progress bars by which we can know the
        # sleep_flag += 1
        # # the if block is avoiding generate too many tasks leading to that the sever slow down
        # # generate 1 tasks every time, and sleep 100 seconds
        # if sleep_flag == 10 and cmd_type != '1':
        #     sleep_flag = 0
        #     time.sleep(120)

# -------------------------------------------------------------------------------------------- #
#                 main calling function getting files and unpacking files                      #
# -------------------------------------------------------------------------------------------- #


def call_run():
    """
    the core of all modules, which coordinate all modules

    :return:
    """

    # ------- get the directories which contain the compressed file ------------------------------ #
    paths, is_exit = fp.get_files_paths(input_dir_logger)

    if not is_exit:
        # ----------- extract dir, basename, abspath from the paths ------------------------------ #
        # create a instance of CompressedFiles class, and get the detail by its method(@property method)
        comp_files = cf.CompressedFiles(paths)
        # ------------ get the detail dict ---------- #
        files_dic_lst = comp_files.files_dict

        if not files_dic_lst:
            print('There is no compressed files')
            is_exit = True

        # ------------ get the submit command type through user typing --------------------------- #
        cmd_type = ''
        if not is_exit:
            cmd_type, is_exit = rst.input_submit_type()

        # ------------ get the qsub command parameter (CPU, Memory) ------------------------------ #
        if not is_exit and cmd_type == '1':
            is_exit = rst.get_qsub_para()

        # ------------- call unpack functions to decompress files --------------------------------- #
        if not is_exit and cmd_type:
            _call_unpack(files_dic_lst, cmd_type)
