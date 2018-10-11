#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/23 9:05
# @File    : go_enrich.py

import csv
import re
import os
import sys
import shutil
import time
from collections import defaultdict
import subprocess
import multiprocessing

import fisher
from statsmodels.stats import multitest
import pandas as pd

from core.common import timmer
from conf import settings
from core.go.obo_parser import GODag
# from core.common.get_params_data import GOEnrichParams
from core.go.go_plot import draw_lineage, sort_terms


class GOEnrich(object):
    def __init__(self, data_reader):
        # self.__data_reader = DataReader('')
        self.__data_reader = data_reader
        outdir = self.__data_reader.params_obj.outdir
        self.diff_all_num = self.__data_reader.diff_genes_num
        self.all_num = self.__data_reader.all_genes_num
        self.data_file = os.path.join(outdir, 'go_enrichment_result.xls')
        self.bar_file = os.path.join(outdir, 'go_enrichment_bar.pdf')
        self.scatter_file = os.path.join(outdir, 'go_enrichment_scatter.pdf')
        self.go_dag_plot = os.path.join(outdir, 'go_dag_plot.png')
        self.bar_r_module = os.path.join(outdir, 'bar.R')
        self.scatter_r_module = os.path.join(outdir, 'scatter.R')
        self.out_data_titles = [
            'ID', 'Description', 'Class', 'GeneRatio', 'BgRatio', 'Enrich_factor',
            'Pvalue', 'FDR', 'GeneCount', self.__data_reader.out_gene_field_name
        ]

    @staticmethod
    def __calculate(data):
        p_value = fisher.pvalue(*data)
        return p_value.right_tail

    def __enrich(self):
        """
        fisher exact package:
        For example, for the following table:
                          ┃  Having the property ┃   Not having the property
            ━━━━━━━━━━━━━━┣━━━━━━━━━━━━━━━━━━━━━━┣━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Selected      ┃        12            ┃       5
            ━━━━━━━━━━━━━━┣━━━━━━━━━━━━━━━━━━━━━━┣━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Not selected  ┃        29            ┃       2
        :return:
        """
        all_genes_stat = self.__data_reader.all_genes_stat
        diff_genes_stat = self.__data_reader.diff_genes_stat.items()
        all_pvalues = []
        res_list = []
        for go, go_diff_val in diff_genes_stat:
            go_all_val = all_genes_stat[go]
            data = [
                go_diff_val, self.diff_all_num-go_diff_val,
                go_all_val-go_diff_val, self.all_num-self.diff_all_num-(go_all_val-go_diff_val)
            ]

            p = self.__calculate(data)
            all_pvalues.append(p)

            go_term = self.__data_reader.go_dict[go]
            res_list.append(
                {
                    'ID': go,
                    'Description': go_term.name,
                    'Class': go_term.namespace,
                    'GeneRatio': '{}/{}'.format(go_diff_val, self.diff_all_num),
                    'BgRatio': '{}/{}'.format(go_all_val, self.all_num),
                    'Enrich_factor': (go_diff_val/self.diff_all_num)/(go_all_val/self.all_num),
                    'Pvalue': p,
                    # 'GeneCount': len(self.__data_reader[go]),
                    'GeneCount': go_diff_val,
                    self.__data_reader.out_gene_field_name: '|'.join(self.__data_reader[go]),

                }
            )

        _, correct_pvalues, _, _ = multitest.multipletests(
            all_pvalues,
            alpha=self.__data_reader.params_obj.fdr_alpha,
            method=self.__data_reader.params_obj.fdr_method)
        self.__output(res_list, correct_pvalues)

    def __output(self, data: list, correct_p: list):
        demo = '\t'.join('{%s}' % i for i in self.out_data_titles) + '\n'
        with open(self.data_file, 'w') as outfile:
            outfile.write('%s\n' % '\t'.join(self.out_data_titles))
            for dic, p in sorted(zip(data, correct_p), key=lambda x: x[1]):
                outfile.write(demo.format(FDR=p, **dic))

    def enrich(self):
        self.__enrich()

    def __r_module(self):
        if not os.path.isfile(self.bar_r_module):
            class_ab = ''.join(['Class_ab   <- gsub("biological_process","BP",gsub("cellular_component",',
                                '"CC",gsub("molecular_function","MF",Class)))'])
            legend_info = ''.join(['legend_info<-c("GO Class:","BP: Biological Process","CC: Cellular Component",',
                                   '"MF : Molecular Function")'])
            with open(settings.BAR_PLOT_DEMO) as infile, open(self.bar_r_module, 'w') as outfile:
                outfile.write(infile.read() % {'class_ab': class_ab, 'legend_info': legend_info})
        if not os.path.isfile(self.scatter_r_module):
            shutil.copyfile(settings.SCATTER_PLOT_DEMO, self.scatter_r_module)
        return self.bar_r_module, self.scatter_r_module

    def __plot_go_dag(self):
        df = pd.read_table(self.data_file, sep='\t', header=0, usecols=['ID', 'Pvalue', 'FDR'])
        sub_df = df[df.FDR < 0.05]
        if len(sub_df) > 10:
            sub_df = sub_df.sort_values('FDR').ix[: 10, ('ID', 'FDR')]
        else:
            sub_df = df.sort_values('Pvalue').ix[: 10, ('ID', 'Pvalue')]
        data = [
            (i, p) for i, p in zip(sub_df.iloc[:, 0], sub_df.iloc[:, 1])
        ]
        results = sort_terms(dag_obj=self.__data_reader.go_dict, data=data)
        draw_lineage(
            self.__data_reader.go_dict, results,
            engine='pydot',
            gml=False,
            lineage_img=self.go_dag_plot,
            draw_children=False)

    @timmer.timmer('*** draw plot ***')
    def plot(self):
        bar_m, scatter_m = self.__r_module()
        filter_type = self.__data_reader.params_obj.plot_filter_type
        alpha = self.__data_reader.params_obj.fdr_alpha if filter_type == 'fdr' \
            else str(self.__data_reader.params_obj.p_alpha)
        print('\n[drawing]  bar plot', file=sys.stdout)
        pip = subprocess.PIPE
        cmd1 = ['Rscript', bar_m, self.data_file, self.bar_file, filter_type, str(alpha)]
        p1 = subprocess.Popen(cmd1, stdout=pip, stderr=pip, universal_newlines=True)
        print('[drawing]  scatter plot', file=sys.stdout)
        cmd2 = ['Rscript', scatter_m, self.data_file, self.scatter_file, filter_type, str(alpha)]
        p2 = subprocess.Popen(cmd2, stdout=pip, stderr=pip, universal_newlines=True)

        print('[drawing]  go dag plot', file=sys.stdout)
        p3 = multiprocessing.Process(target=self.__plot_go_dag)
        # self.__plot_go_dag()
        p3.start()
        p3.join()
        p1.wait()
        p2.wait()

        if p1.returncode != 0:
            if 'Warning messages' in p1.stderr:
                return
            sys.stdout.write('Drawing bar failed: \n%s\n' % p1.stderr)
        if p2.returncode != 0:
            if 'Warning messages' in p1.stderr:
                return
            sys.stdout.write('Drawing scatter failed: \n%s\n' % p2.stderr)


class DataReader(dict):

    def __init__(self, params_obj):
        super(DataReader, self).__init__()
        # self.params_obj = GOEnrichParams()
        self.params_obj = params_obj
        print('\n[{time}]: \033[31;1m{msg}\033[0m START'.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msg='*** parse obo file data ***'))
        self.go_dict = GODag(obo_file=self.params_obj.obo_file, load_obsolete=False)
        print('[{time}]: \033[31;1m{msg}\033[0m END'.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msg='*** parse obo file data ***'))
        self.__id_tran_dic = self.__convert_file()
        self.out_gene_field_name = 'GeneIDs' if self.__id_tran_dic is None else 'GeneNames'
        self.all_genes_num = 0
        self.diff_genes_num = 0
        self.all_genes_stat = None
        self.diff_genes_stat = None
        self.__run()

    @timmer.timmer('*** parse data ***')
    def __run(self):
        ensg2terms_dic = self.__asso_file()
        self.all_genes_num, self.all_genes_stat, g_list = self.__genes_reader(
            file=self.params_obj.all_genes_file,
            dic=ensg2terms_dic,
            flag='all',
        )
        self.diff_genes_num, self.diff_genes_stat, _ = self.__genes_reader(
            file=self.params_obj.diff_genes_file,
            dic=ensg2terms_dic,
            flag='diff',
            filter_list=g_list
        )
        # print(self.all_genes_num, self.diff_genes_num)

    def __convert_file(self):
        dic = None
        if self.params_obj.convert_file is not None:
            dic = defaultdict(set)
            with open(self.params_obj.convert_file) as infile:
                for ensg, gene in csv.reader(infile, delimiter='\t'):
                    dic[ensg].add(gene)
        return dic

    def __add2self(self, gene: str, terms: set):

        def trans(ensg_):
            ensg = {ensg_}
            if self.__id_tran_dic is not None:
                ensg = self.__id_tran_dic.get(ensg_, set())
            return ensg

        for term in terms:
            if term not in self:
                self[term] = set()
            self[term].update(trans(gene))

    def __asso_file(self):
        dic = defaultdict(set)
        split_pattern = re.compile('\s*;\s*')
        with open(file=self.params_obj.asso_file) as infile:
            for ensg, gos in csv.reader(infile, delimiter='\t'):
                gos = split_pattern.split(gos)
                all_gos = self.__get_all_parents(gos)
                self.__add2self(gene=ensg, terms=all_gos)
                dic[ensg].update(all_gos)
        return dic

    @staticmethod
    def __genes_reader(file, dic: dict, flag='diff', filter_list=None):
        """read all ro diff genes list

        :param file: `all gene file` or `diff gene file`
        :param dic: ensembl_id <---> {terms}
        :param flag: 'diff', 'all'
        :return:
        """
        res_dic = defaultdict(set)

        def convert_add(line_, dic_: dict, res_dic_: dict):

            gos = dic_[line_]
            for g in gos:
                res_dic_[g].add(line_)

        genes = (g for g in open(file))
        rm_g, all_g = 0, 0

        temp = set()
        for line in genes:
            line = line.strip()
            all_g += 1
            if line in dic and (line in filter_list if flag == 'diff' else 1):
                convert_add(line, dic, res_dic)
                temp.add(line)
                continue
            rm_g += 1

        print('\n*** {rm_num} in {flag} file were removed [total number: {all}]'.format(
            rm_num=rm_g, flag=flag, all=all_g
        ), file=sys.stdout, end='')

        return (all_g-rm_g), {k: len(v) for k, v in res_dic.items()}, temp if flag == 'all' else None

    def __get_all_parents(self, gos: list):
        res = set()
        for go in gos:
            term_obj = self.go_dict.get(go)
            if term_obj is None:
                # print(go, 'is obsolete', file=sys.stdout)
                continue
            res.update(term_obj.get_all_parents())  # the result is GO IDs
            res.add(go)
        return res
