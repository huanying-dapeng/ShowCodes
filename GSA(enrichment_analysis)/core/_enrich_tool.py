#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/17 16:55
# @File    : _enrich_tool.py

import re
import shlex
import subprocess
import os

from core.common import timmer
from conf import settings


class EnrichTool(object, ):
    def __init__(self):
        self.__cmd = ''
        self.__wd = ''
        self.__outfile = ''
        self.__enrich_data = []

    @timmer.timmer('enrich analysis')
    def __run(self):
        result = []
        if self.__type == 'kegg':
            pattern = re.compile('(?<=/)[^/%]:[^/%]+(?=%)')
        else:
            pattern = re.compile('(?<=/)term=GO:.+')
        cmd = shlex.split(self.__cmd)
        cmd.insert(0, 'run_kobas.py')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=self.__wd, universal_newlines=True, encoding='utf8')
        for line in p.stdout:
            # print(line)
            line_ = line.strip().split('\t')
            print(line_)
            if len(line_) == 1:
                result.append(line.strip())
                continue
            genes = pattern.findall(line)
            print(genes)
            if line_ and '.' in line_[5]:
                line_.insert(-1, '|'.join(genes))
                term = line_[2]
                p_value = float(line_[5])
                q_value = float(line_[6])
                ensembls = line_[7].split('|')

                self.__enrich_data.append([term, genes, p_value, q_value, ensembls])
            else:
                line_.insert(-1, 'Enriched_Genes')
            line = '\t'.join(line_)
            if line not in result:
                result.append(line)

        p.wait()
        with open(self.__outfile, 'w') as outfile:

            outfile.write('\n'.join(result))

    def run(self, param_obj):
        """
        param.outfile
        param.work_dir
        param.line_params

        :param param_obj:
        :return:
        """
        self.__type = param_obj.analysis_type
        self.__cmd = param_obj.line_params
        self.__wd = param_obj.work_dir
        self.__outfile = param_obj.outfile
        self.__run()

    # def __get_genes(self, file):
    #     tem = []
    #     with open(file) as handler:
    #         for line in handler:
    #             tem.append(line.strip())
    #     return tem

    def __go_draw(self, path, outdir):
        p = subprocess.Popen(
            ['python3', settings.PLOT_GO_TERM, settings.OBO_FILE, '-f', path, '--disable-draw-children'], cwd=outdir)
        p.wait()

    def __kegg_draw(self, path, species, outdir):
        p = subprocess.Popen(['kegg_annotate_tool.py', path, '-s', species, '-d', outdir, '-t', 'category'])
        p.wait()

    def draw_picture(self, param_obj):
        # enrich_dic = defaultdict(dict)
        print(self.__enrich_data)
        enrich_list = sorted(self.__enrich_data, key=lambda x: x[3])
        if param_obj.analysis_type == 'go':
            temppath = os.path.join(param_obj.work_dir, 'temp_terms.list')
            with open(temppath, 'w') as handler:
                for t, gs, p, q, e in enrich_list[:10]:
                    handler.write('{}\t{}\n'.format(t, q))
                    print('{}\t{}\n'.format(t, q))
            self.__go_draw(temppath, param_obj.work_dir)
            os.remove(temppath)
        else:
            if len(enrich_list) <= 10:
                pass
            elif enrich_list[9][3] > 0.05 or enrich_list[9][2] > 0.05:
                enrich_list = enrich_list[:10]
            else:
                enrich_list = [i for i in enrich_list if i[3] < 0.05]

            temppath = os.path.join(param_obj.work_dir, 'temp_terms.list')
            with open(temppath, 'w') as handler:
                temp = set()
                for t, gs, p, q, es in enrich_list:
                    for e in es:
                        temp.add(e)
                handler.write(''.join('%s\t\n' % i for i in temp))
            self.__kegg_draw(path=temppath, outdir=param_obj.work_dir, species=param_obj.species)
            os.remove(temppath)
