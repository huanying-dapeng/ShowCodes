#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/11/5

import os
import sys


def get_comp_log_file():
    """ get the path of the file and return the paths """

    # get the path of UnpackFiles folder
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.basename(parent_dir) == 'UnpackFiles':
            # parent_path = temp_path
            break
        else:
            parent_dir = os.path.dirname(parent_dir)

    # add all path to system environment variables
    sys.path.append(parent_dir)

    from conf import settings

    log_file = os.path.join(parent_dir, 'log', settings.LOG_TYPES['unpack_file'])

    return log_file


if __name__ == '__main__':
    # get the log file path
    file = get_comp_log_file()
    # get the log file name
    basename = os.path.basename(file)
    # create the saved file path
    save_path = os.path.join(os.path.abspath("."), basename)
    # print the path of saving file
    print('\033[33;1mthe result save to\033[0m \033[32;1m{path}\033[0m'.format(path=save_path))
    with open(file) as my_reader, open(save_path, 'w') as my_writer:
        for line in my_reader:
            line = line.split('-')[-1].lstrip()
            my_writer.write(line)


