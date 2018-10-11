#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__: zhipeng zhao
# date: 2017/11/4

""" set the parameter of qsub task """

# ---------------------- task name ------------------------ #
# default: the submitting task file-name
NAME = "Qsub_task"
# --------------------- nodes number ---------------------- #
NODES = 1
# -------------------- ppn number(CPU) -------------------- #
PPN = 2
# ------------------- memory number ----------------------- #
MEM = 4
# -------------- destination(node pool of server) --------- #
POOL = "zh"
