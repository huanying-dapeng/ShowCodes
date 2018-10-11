#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/16 11:19
# @File    : settings.py

import os

PARENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

HTML_TEMPLATE_PATH = os.path.join(PARENT_DIR, 'db', 'template.html')
DHTML_JS = os.path.join(PARENT_DIR, 'db', 'dhtml.js')

MULTI_TERMS_COLOR = (255, 26, 146)
COLORS_JSON_FILE = os.path.join(PARENT_DIR, 'db', 'colors_list.json')

# contain ko xxx.conf, xxx.png files
KO_TO_PATHWAY = r'/mnt/ilustre/app/zhuohao/database/kegg/genes/'
# contain organisms xxx.conf, xxx.png files
PATHWAY_DIR = r'/mnt/ilustre/app/zhuohao/database/kegg/pathway'


def get_obo_version(file):
    with open(file) as infile:
        return infile.readline().strip(), infile.readline().strip()


OBO_FILE = os.path.join(PARENT_DIR, 'db', 'go-basic.obo')
PLOT_GO_TERM = '/mnt/ilustre/users/zhipeng.zhao/bin/bio_soft/goatools/scripts/go_terms_plot.py'
OBO_FILE_VERSION = get_obo_version(OBO_FILE)

# pathway.list file path which contain the following content #first class, ##second class
# #Metabolism
# ##Global and overview maps
# 01100   Metabolic pathways
# 01110   Biosynthesis of secondary metabolites
# 01120   Microbial metabolism in diverse environments
# 01130   Biosynthesis of antibiotics
PATHWAY_LIST_PATH = '/mnt/ilustre/app/zhuohao/database/kegg/pathway/pathway.list'

# ko or organisms pathway.list which contain the following content(the below is hsa's content)
# hsa:219 path:hsa00053
# hsa:223 path:hsa00053
# hsa:224 path:hsa00053
# example: hsa --- /mnt/ilustre/app/zhuohao/database/kegg/genes/organisms/hsa/hsa_pathway.list
#          ko  --- /mnt/ilustre/app/zhuohao/database/kegg/genes/ko/ko_pathway.list
# KO_OR_ORG_PATHWAY_PARENT_DIR = '/mnt/ilustre/app/zhuohao/database/kegg/genes'
KO_OR_ORG_PATHWAY_PARENT_DIR = '/mnt/ilustre/users/guantao.zheng/app/kegg_tools/database/genes'

BAR_PLOT_DEMO = os.path.join(PARENT_DIR, 'core', 'R_Demo', 'bar_plot_demo.R')
SCATTER_PLOT_DEMO = os.path.join(PARENT_DIR, 'core', 'R_Demo', 'scatter_plot_demo.R')
