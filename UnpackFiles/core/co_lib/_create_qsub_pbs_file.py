#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/11/4

""" the function of this module is creating the file of submitting qsub task  """

import os

from conf import qsub_setting as qs

# -------------------------------------------------------------------------------------------- #
#                         the content of submitting qsub-task file                             #
# -------------------------------------------------------------------------------------------- #

con = '''
#PBS -N {task_name} 
#PBS -l nodes={nodes}:ppn={cpu}
#PBS -l mem={memory}G
#PBS -q {pool_name}
cd {file_dir}

{cmd_line}

'''

# -------------------------------------------------------------------------------------------- #
#             create file of submitting qsub-task in the compressed file folder                #
# -------------------------------------------------------------------------------------------- #


def create_file(file_dir, cmd_line, task_name=qs.NAME):
    """write con to the task file

    :param file_dir: the path of compressed file
    :param cmd_line: the command line of unpacking file
    :param task_name: task number + filename
    :return:cd .. \n ls
    """
    global con
    con = con.format(task_name=task_name, nodes=qs.NODES, cpu=qs.PPN, memory=qs.MEM,
                     pool_name=qs.POOL, file_dir=file_dir, cmd_line=cmd_line)

    # *************************** because the when xxx.fa.gz ********************************* #
    if not os.path.exists(file_dir):
        file_dir = os.path.dirname(file_dir)

    pbs_file_path = os.path.join(file_dir, r'{task_name}.qsub.sh'.format(task_name=qs.NAME))
    with open(pbs_file_path, 'w') as my_writer:
        my_writer.write(con)
    return pbs_file_path
