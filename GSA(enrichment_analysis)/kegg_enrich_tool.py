#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/21 18:07
# @File    : kegg_enrich_tool.py

from core.common.get_params_data import KEGGEnrichParams
from core.kegg import kegg_enrich as kr


def run():
    params_obj = KEGGEnrichParams()
    if params_obj.diff_genes_file is None or params_obj.all_genes_file is None or params_obj.asso_file is None:
        return
    data_obj = kr.KEGGDict(params_obj)
    enrich_obj = kr.KEGGEnrich(data_obj)
    enrich_obj.enrich()
    enrich_obj.plot()


if __name__ == '__main__':
    run()
