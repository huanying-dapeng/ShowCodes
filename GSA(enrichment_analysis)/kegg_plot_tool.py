#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/15 17:56
# @File    : kegg_annotate_tool.py

import os

from core.common.get_params_data import AnnotParams
from core._annotate import Annotation, TermsInfo
from core.common import timmer


def annotate(params_obj, terms_obj):
    annot = Annotation(cwd=params_obj.out_dir)
    for pathway, ko_dic in terms_obj.items():

        pathway_png = os.path.join(params_obj.pathway_dir, pathway+'.png')
        pathway_conf = os.path.join(params_obj.pathway_dir, pathway+'.conf')
        # print(pathway_conf, pathway_png)
        annot.annotate(
            pathway_name=pathway,
            pic_path=pathway_png,
            conf_path=pathway_conf,
            ko_color_dic=ko_dic,
            gene_info_dic=terms_obj.gene_info_dic
        )


@timmer.timmer('-----------KEGG Annotating Program-----------')
def run():
    params = AnnotParams()
    terms_info = TermsInfo(params)
    annotate(params, terms_info)


if __name__ == '__main__':
    run()

