#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/11/2

""" To receive input from user typing, and the input will decide the submitting command """

from conf import settings
from conf import qsub_setting as qs


def input_submit_type():
    """ obtain the cmd type (cmd_qsub, nohup, or in the command line) through inputting by users """

    con = '''\033[32;1minput the submit task type\033[0m:
    \033[32;1m 1\033[0m: \033[33;1m'qsub'\033[0m --> cmd_qsub
    \033[32;1m 2\033[0m: \033[33;1m'nohup'\033[0m --> nohup xxxxx &
    \033[32;1m 3\033[0m: \033[33;1m'command'\033[0m --> gunzip xxxx (example)
    \033[32;1mPlease enter the\033[0m corresponding number\033[33;1m(1, 2, 3)\033[0m
    
    input \033[32;1m'exit'\033[0m -- > \033[33;1mexit program\033[0m
    '''
    # ----------------------------------------------------------------------------- #
    #       print the prompting about what the users should type                    #
    # ----------------------------------------------------------------------------- #
    print(con)
    is_exit = False
    iut = input("[\033[32;1m 1\033[0m: \033[33;1m'qsub'\033[0m" +
                "\033[32;1m 2\033[0m: \033[33;1m'nohup'\033[0m" +
                "\033[32;1m 3\033[0m: \033[33;1m'command'\033[0m] " +
                "\033[32;1m>>> \033[0m")
    if iut == 'exit':
        is_exit = True
    elif iut not in settings.NUM_TYPE_TO_SUB:
        iut = settings.DEFAULT_SUBMIT_TYPE

    return iut.strip(), is_exit


def get_qsub_para():
    """ get the qsub parameter """
    con = '''\033[32;1minput the cmd_qsub parameter[CUP | Memory]\033[0m:

    \033[32;1minput number\033[0m otherwise please press any key(Not a Number, default: cpu -> {cpu}; memory -> {mem}) 
    input \033[32;1m'exit'\033[0m -- > \033[33;1mexit program\033[0m
    '''.format(cpu=qs.PPN, mem=qs.MEM)
    print(con)

    def print_result(para_type):  # para_type --> default or new para
        print('\033[33;1mreset to the {}\033[0m: cpu --> \033[32;1m{}\033[0m; memory --> \033[32;1m{}\033[0m'.format(
            para_type, qs.PPN, qs.MEM))
    is_exit = False
    is_process = []
    for i, t in enumerate(['CPU', 'Memory', 'yes or no (\033[32;1mone chance to change them\033[0m)', 'CPU', 'Memory'], 1):
        v = input('\033[32;1m[{}] >>> \033[0m'.format(t))
        is_process.append(v)
        if len(is_process) == 2 and is_process[0] == '' and is_process[1] == '':
            print_result('default')
            break
        if v == 'exit':
            is_exit = True
            break
        elif (v == 'no' or v == 'n') and i == 3:
            print_result('paras user sets')
            break
        elif i == 5 or (i == 3 and v == ''):
            print_result('paras user sets')
            break

        if v.isnumeric():
            try:
                # change the number of CPU and memory
                if t == 'CPU':
                    qs.PPN = v
                elif t == 'Memory':
                    qs.MEM = v
            except KeyError:
                pass

    return is_exit
