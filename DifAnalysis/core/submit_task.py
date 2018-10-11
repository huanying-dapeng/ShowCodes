#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/22
# @File    : submit_task.py

import os

from conf import qsub_setting as qsub_set
from conf import settings

_qsub_sh_file_demo = '''
#! /bin/bash
#PBS -N {task_name}
#PBS -l nodes=1:ppn={cpu}
#PBS -l mem={mem}G
#PBS -q {pool_name}
#PBS -v {env}
#PBS -V
cd {run_path}

{sub_cmd} {json_file}
'''

def _get_submit_params():

    while True:
        gpu = input('input \033[32;1mCPU\033[0m size[default: 2]\n\033[32;1m>>> \033[0m').strip()
        if gpu.isnumeric():
            qsub_set.PPN = gpu
            break
        else:
            print('\033[33;1mplease input number\033[0m')
            continue

    while True:
        men = input('input \033[32;1mMEM\033[0m size[default: 2]\n\033[32;1m>>> \033[0m').strip()
        if men.isnumeric():
            qsub_set.MEM = men
            break
        else:
            print('\033[33;1mplease input number\033[0m')
            continue

    qsub_set.NAME = input('input \033[32;1mqsub task name\033[0m\n\033[32;1m>>> \033[0m').strip()

    env_list = [
        '/mnt/ilustre/users/zhipeng.zhao/anaconda3',
        '/mnt/ilustre/users/zhipeng.zhao/anaconda3/bin',
        '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib',
        '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib/python3.6',
        '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib/python3.6/site-packages'
    ]

    return {
        'task_name': qsub_set.NAME,
        'cpu': qsub_set.PPN,
        'mem': qsub_set.MEM,
        'pool_name': qsub_set.POOL,
        'run_path': None,
        'sub_cmd': settings.ENTRY_FILE_NAME,
        'json_file': settings.JSON_FILE_ABSPATH(),
        'env': ', '.join(env_list)
    }


def _create_qsub_file(file_path='', **qsub_params_dict):
    with open(r'%s' % file_path, 'w') as my_writer:
        my_writer.write(_qsub_sh_file_demo.format(**qsub_params_dict))


def submit(submit_type):
    if submit_type == "qsub":
        # get the params of qsub: MEM, CPU, task NAME
        qsub_params_dict = _get_submit_params()
        # create save qsub xx.sh file path: the current path --> .
        qsub_file_path = os.path.abspath(".")
        # assign the value to _qsub_params_dict
        qsub_params_dict['run_path'] = qsub_file_path
        # create the save xxx.sh file abspath: /usr/zhipeng.zhao/tcga/Expression/qsub_DiffAnalysis.sh
        qsub_file = os.path.join(qsub_file_path, 'qsub_%s.sh' % qsub_set.NAME)
        # create xxx.sh file in the above path
        _create_qsub_file(
            file_path=qsub_file,
            **qsub_params_dict
        )
        # submit qsub task in the command line
        os.popen('qsub {}'.format(qsub_file))
    elif submit_type == 'nohup':
        os.popen('nohup {} {} > nohup.out 2>&1 &'.format(settings.ENTRY_FILE_NAME, settings.JSON_FILE_ABSPATH()))
