#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "zhipeng zhao"
# date: 2017/10/31

""" create the object of logging:

    1. console handler
        print in the screen
    2. file handler
        save the log to related files

"""

import logging
import os

from conf import settings

# ------------------------------------------------------------------------------------------------ #
#           default
# ------------------------------------------------------------------------------------------------ #


def logger(log_type):
    """ create object of logger, and return a log object, then we can use logger.info() and so on to log record """
    # create logger
    my_logger = logging.getLogger(log_type)
    # set the level of writing log, and the level come from settings module
    my_logger.setLevel(settings.LOG_LEVEL)

    # get the path of logging
    log_path = os.path.join(settings.BASE_DIR, 'log')
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file = os.path.join(log_path, settings.LOG_TYPES[log_type])
    # create file handler and set level to warning
    fh = logging.FileHandler(log_file)
    fh.setLevel(settings.LOG_LEVEL)

    # create formatter
    formatter = logging.Formatter(settings.FORMATTER)

    if settings.IS_STDOUT_LOG:
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(settings.LOG_LEVEL)
        # create format and fh
        ch.setFormatter(formatter)
        # add ch to logger
        my_logger.addHandler(ch)
        # add ch to logger
        my_logger.addHandler(ch)

    # create format to fh
    fh.setFormatter(formatter)
    # add fh to logger
    my_logger.addHandler(fh)

    return my_logger
