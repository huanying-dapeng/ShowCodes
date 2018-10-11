#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/23 15:40
# @File    : go_enrich_tool.py

import sys

from core.common import timmer
from core.go import go_enrich
from core.common.get_params_data import GOEnrichParams


@timmer.timmer('------------ GO Enrich Program ------------')
def run():
    print('|', file=sys.stdout)
    param_obj = GOEnrichParams()
    data_obj = go_enrich.DataReader(params_obj=param_obj)
    go_obj = go_enrich.GOEnrich(data_reader=data_obj)
    go_obj.enrich()
    go_obj.plot()


if __name__ == '__main__':
    import time
    s = time.time()
    run()
    print(time.time()-s)
