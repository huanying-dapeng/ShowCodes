#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/22 23:38
# @Author  : zhipeng.zhao
# @File    : go_terms_plot.py

import sys
from os import path as op
sys.path.insert(0, op.dirname(__file__))

from core.go import go_plot
from concurrent.futures import ThreadPoolExecutor
go_plot.run()
