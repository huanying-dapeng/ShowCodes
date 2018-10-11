#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

"""
get the directories by three ways:
    1. receive them users typing; --> function: input()
    2. from document
    3. from argv: os.argv[1:]

return a list of dirs containing all dirs and its sub-folders
"""

import os
import sys

command_argv = sys.argv
# ------------------------------------------------------------------------------------------------------------- #
#                          a global variable which decide whether the program will continue                     #
# ------------------------------------------------------------------------------------------------------------- #
# if _is_exist is False, it will continue, otherwise it will exit
_is_exit = False


# ------------------------------------------------------------------------------------------------------------- #
#                              user typing the paths through keyboard                                           #
# ------------------------------------------------------------------------------------------------------------- #


def _input_path():
    """
     receive directories users input manually, and when receive 'q', it will complete typing.

    :return:
    """
    global _is_exit
    paths = []
    while True:

        path = input('\33[33;1m[file dir path(input\33[0m \33[32;1m"end"\33[0m \33[33;1mthen\33[0m\33[32;1m complete ' +
                     "input\33[0m\33[33;1m)]\33[0m\ninput \033[32;1m'exit'\033[0m -- > \033[32;1mexit program\033[0m" +
                     '\n\33[32;1m>>>\33[0m ').strip()

        if path == 'end':
            break
        elif path == 'exit':
            _is_exit = True
            break

        if os.path.exists(path):
            paths.append(path)
        elif path == '':
            print('\33[33;1mComplete input\33[0m')
            break
        else:
            print('the path is not exist\n')

    return paths


# ------------------------------------------------------------------------------------------------------------- #
#                            get the paths through file of command argv                                         #
# ------------------------------------------------------------------------------------------------------------- #


def _read_paths(file_name, log_obj):
    """
    extract directories from file, and the object of log_obj is used to log record

    :param file_name: the directories file
    :param log_obj: object of logger
    :return: ['/a/b/a/b/n', '/a/b/a/b/n', '/a/b/a/b/n' ......]
    """
    r_paths = []
    with open(r'%s' % file_name) as my_reader:
        for line in my_reader:
            # delete the '\n'
            line = line.strip()
            if os.path.exists(line):
                r_paths.append(line)
            else:
                # save to logger
                log_obj.info('{file_dir} is not exist'.format(file_dir=line))
    return r_paths


# ------------------------------------------------------------------------------------------------------------- #
#                  the entry of this module: collect file paths through 3 ways                                  #
# ------------------------------------------------------------------------------------------------------------- #


def get_files_paths(log_obj):
    """
    obtain the compressed file directories from the file which is receive from Command Line -- argv[1].

    :param log_obj: the directories file
    :return: ['/a/b/a/b/n', '/a/b/a/b/n', '/a/b/a/b/n' ......]
    """
    #
    global _is_exit

    # to judge whether command line contain command-line arguments, by which we will give the way getting directories
    len_argv = len(command_argv)

    temp_paths = []
    if len_argv <= 1:
        # get the directories from the manual input
        temp_paths = _input_path()
        log_obj.info('user input the paths through keyboard')
    else:  # len_argv >= 2
        f = command_argv[1]
        if os.path.isfile(f):
            # get the directories from the file
            temp_paths = _read_paths(f, log_obj)
            log_obj.info('get abspath(directory) from file')
        else:
            # get the directories from the command-line --> argv[1:]
            log_obj.info("get abspath(dir) from command line argv")
            # the argv is dir; we will add it to paths_list directly
            path = command_argv[1:]
            for p in path:
                if os.path.exists(p):
                    temp_paths.append(p)
                else:
                    # save to logger
                    log_obj.info("%s is not exist" % p)

    return list(set(temp_paths)), _is_exit
