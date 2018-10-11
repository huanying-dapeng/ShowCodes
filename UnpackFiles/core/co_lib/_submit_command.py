#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

""" organize the decompressing commands, and submit the corresponding tasks by different cmd_type """

import os
import sys
from subprocess import Popen, PIPE

from conf import settings
from conf import qsub_setting as qs
from core.co_lib import _create_qsub_pbs_file as cf


# ---------------------------------------------------------------------------------------- #
#  class of unpack files                                                                   #
# ---------------------------------------------------------------------------------------- #

class UpackMethod(object):
    """ submit decompressing tasks:

    the following constants is in the settings module
        1.  SUBMIT_WAYS = {
                'qsub': r'com_qsub {name} 2 4G cmd: {run_cmd}',
                'nohup': r'nohup {run_cmd} &',
                'command': r'{run_cmd}'
            }
        2.  NUM_TYPE_TO_SUB = {
                '1': 'qsub',
                '2': 'nohup',
                '3': 'command'
            }
    """

    __var = None

    def __init__(self, submt_type):
        self.__submt_type = settings.NUM_TYPE_TO_SUB[submt_type]
        self.__cmd_line = settings.SUBMIT_WAYS[self.__submt_type]

    @staticmethod
    def __log_record(r, abs_path, log_obj):
        """
        log record:
            Listing the function separately is in order to reduce the duplicated code
            The following functions all use this function

        """
        if r != 0:
            log_obj.info(abs_path)

    def __get_cmd_line(self, file_dir, basename, unp_cmd, *args):
        """ main role is to add cmd_qsub name to the cmd line, if task type is 'cmd_qsub', otherwise return itself """
        if self.__submt_type == 'qsub':
            qs.NAME = 'qsub.{}.{}'.format(args[0], basename.split(".")[0])
            # run_cmd="{run_cmd}": in order to add run_cmd in the following
            # offer the entry of formatting characters: 'aksd asklfjl al {run_cmd}'.format(run_cmd='xxxxxxxxxx')
            created_file_path = cf.create_file(file_dir, unp_cmd, task_name=qs.NAME)
            return self.__cmd_line.format(run_cmd=created_file_path)
        else:
            return self.__cmd_line.format(run_cmd=unp_cmd)

    def submit_task(self, file_dir, basename, abs_path, log_obj, unp_type, *args):
        """
        submit task to the server:
            1. CMD_FORMAT: in the settings module, it contain the all submitting task type --> \
                CMD_FORMAT = {
                    'zip': r'unzip -qod {file_dir} {abspath}',
                    'gz': r'gunzip {abspath}',
                    'tar.gz': r'tar -xzf {abspath} -C {file_dir}',
                    'tar': r'tar -xf {abspath} -C {file_dir}'
                }

        :param file_dir: the dir path where the results will be saved
        :param basename: the file name --> example: test.tar.gz
        :param abs_path: the decompressed file abspath --> example: /usr/zhang/tcga/GPCR2Cancer/test.tar.gz
        :param log_obj: logger object
        :param unp_type: unpack file type
        :param args: task ID --> number starting from one
        :return:
        """
        # format: 'unzip -qod {file_dir} {abspath}' | 'tar_gz': r'tar -xzf {abspath} -C {file_dir}'

        # ********************** because file_dir may be relative path *************************** #
        file_dir = os.path.abspath(file_dir)
        abs_path = os.path.abspath(abs_path)
        uz_cmd = settings.CMD_FORMAT[unp_type].format(file_dir=file_dir, abspath=abs_path)
        # it contain: {run_cmd}
        cmd_line = self.__get_cmd_line(file_dir, basename, uz_cmd, *args)

        # r = os.system(cmd_line)
        p = Popen(cmd_line, shell=True, universal_newlines=True, stderr=PIPE)
        p.wait()
        error = p.stderr.read()
        if error and p.returncode:
            print(error, file=sys.stdout)

        # print(r'unzip -d {} {}'.format(file_dir, abs_path))
        self.__log_record(error, abs_path, log_obj)

    @classmethod
    def get_instance(cls, submt_type):
        """
        create singleton pattern:
            1. when the program run, it will create one instance
            2. submit tasks:(Usage)
                (1): cmd_qsub [ name ] [ cpu ] [ memory ] [ node ] cmd: <command line>
                (2): nohup xxxxxx &
                (3): command line
                (2) and (3) is running in the server node

        :param com_type: its value is input by user, and it is the type of submit tasks
        :return: a instance of UpackMethod class
        """
        if cls.__var:
            return cls.__var
        else:
            cls.__var = UpackMethod(submt_type)
            return cls.__var
