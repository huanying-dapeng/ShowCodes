#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/16 19:21
# @File    : timmer.py

import time
from functools import wraps


def timmer(msg=''):
    def _timmer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            print('\n[{time}]: \033[31;1m{msg}\033[0m START'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msg=msg), end=' ------ ')
            res = func(*args, **kwargs)
            print('\n[{time}]: \033[31;1m{msg}\033[0m END\n'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msg=msg), end='')
            return res
        return inner
    return _timmer
