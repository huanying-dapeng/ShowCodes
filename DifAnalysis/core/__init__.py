#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : zhipeng zhao
# @Date    : 2017/11/20
# @File    : __init__.py.py

import sys

# the possible paths of package
# in order to the error of invoking the third-party Python packages
env_list = [
    '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib/python3.6/site-packages',
    '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib/python3.6',
    '/mnt/ilustre/users/zhipeng.zhao/anaconda3/lib',
    '/mnt/ilustre/users/zhipeng.zhao/anaconda3'
]

# add the paths of third-party Python packages to environment variables
sys.path.extend(env_list)

__all__ = [
    'main',
]
