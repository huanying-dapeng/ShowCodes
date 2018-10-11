#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/21 15:49
# @File    : kegg_enrich.py

import sys
import os
from collections import defaultdict
import subprocess
import shutil

# from scipy.stats import fisher_exact
import fisher
import pandas as pd
from statsmodels.stats import multitest

from conf.settings import BAR_PLOT_DEMO, SCATTER_PLOT_DEMO, PATHWAY_LIST_PATH
from core.common import timmer


class KEGGEnrich(object):

    def __init__(self, data_obj):
        self.__data_obj = data_obj
        self.desc_dic = self.__data_obj.desc_dic
        self.__gene_title = self.__data_obj.out_name
        self.__bar_plot_R = os.path.join(self.__data_obj.outdir, 'bar.R')
        self.__scatter_plot_R = os.path.join(self.__data_obj.outdir, 'scatter.R')
        shutil.copyfile(SCATTER_PLOT_DEMO, self.__scatter_plot_R)

        self.__outfile = os.path.join(self.__data_obj.outdir, 'kegg_enrichment_result.xls')
        self.__bar_out_file = os.path.join(self.__data_obj.outdir, 'kegg_enrichment_bar.pdf')
        self.__scatter_out_file = os.path.join(self.__data_obj.outdir, 'kegg_enrichment_scatter.pdf')
        self.__tiles = ['ID', 'Description', 'Class', 'GeneRatio', 'BgRatio',
                        'Enrich_factor', 'Pvalue', 'FDR', 'GeneCount', self.__gene_title]

    @timmer.timmer('*** start enrich ***')
    def enrich(self):
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
        all_kg = self.__data_obj.total_kgene_num
        all_diff_g = self.__data_obj.diff_kgene_num

        res = []
        p_list = []
        for pw, pw_diff_kg_num in self.__data_obj.diff_stat_dic.items():
            pw_all_kg_num = self.__data_obj.all_stat_dic[pw]
            # _, p = fisher_exact([
            #     [pw_diff_kg_num, all_diff_g - pw_diff_kg_num],
            #     [pw_all_kg_num - pw_diff_kg_num, all_kg - all_diff_g - (pw_all_kg_num - pw_diff_kg_num)]
            # ])
            p = fisher.pvalue(
                pw_diff_kg_num, all_diff_g - pw_diff_kg_num,
                pw_all_kg_num - pw_diff_kg_num, all_kg - all_diff_g - (pw_all_kg_num - pw_diff_kg_num)
            )
            p = p.right_tail
            p_list.append(p)
            res.append(
                {
                    'ID': pw,  # pathway
                    'Description': self.desc_dic[pw]['desc'],
                    'Class': self.desc_dic[pw]['class'],
                    'GeneRatio': '{diff}/{all_diff}'.format(diff=pw_diff_kg_num, all_diff=all_diff_g),
                    'BgRatio': '{pw_all}/{all}'.format(pw_all=pw_all_kg_num, all=all_kg),
                    'Enrich_factor': (pw_diff_kg_num/all_diff_g)/(pw_all_kg_num/all_kg),
                    'Pvalue': p,
                    'GeneCount': pw_diff_kg_num,
                    self.__gene_title: ','.join(self.__data_obj[pw])
                }
            )
        _, corr_pval, _, _ = multitest.multipletests(
            p_list, alpha=self.__data_obj.fdr_alpha, method=self.__data_obj.fdr_method, is_sorted=False)
        sys.stdout.write('\noutput data to excel')
        self.__out_file(res, corr_pval)

    def __out_file(self, data: list, corr_p: list):
        demo = '\t'.join('{%s}' % i for i in self.__tiles)

        temp_file = open('temp.file', 'w', encoding='utf8')
        temp_file.write('%s\n' % '\t'.join(self.__tiles))
        for dic, c_p in zip(data, corr_p):
            temp_file.write('%s\n' % demo.format(FDR=c_p, **dic))
        temp_file.close()

        df = pd.read_table('temp.file', sep='\t', header=0, encoding='utf8')
        df.sort_values(['FDR', 'Pvalue', 'GeneCount']).to_csv(self.__outfile, sep='\t', index=False)
        os.remove('temp.file')

    @timmer.timmer('*** start plot ***')
    def plot(self):
        class_ab = ''.join([
            'Class_ab <- gsub("Organismal Systems","OS",gsub("Human Diseases","HD",',
            'gsub("Genetic Information Processing","GIP",gsub("Environmental Information Processing","EIP",',
            'gsub("Drug Development","DD",gsub("Cellular Processes","CP",gsub("Metabolism","M",Class)))))))'
        ])
        legend_info = ''.join([
            'legend_info <- c("KEGG Pathway Class:","EIP: Environmental Information Processing",',
            '"GIP: Genetic Information Processing","CP : Cellular Processes","OS : Organismal Systems",',
            '"DD : Drug Development","HD : Human Diseases","M  : Metabolism")'
        ])
        if not os.path.isfile(self.__bar_plot_R):
            with open(BAR_PLOT_DEMO) as infile, open(self.__bar_plot_R, 'w') as outfile:
                demo = infile.read() % {'class_ab': class_ab, 'legend_info': legend_info}
                outfile.write(demo)
        plot_filter_type = self.__data_obj.plot_filter_type

        alpha = self.__data_obj.fdr_alpha if plot_filter_type == 'fdr' else self.__data_obj.p_alpha

        pipe = subprocess.PIPE

        cmd1 = [
            'Rscript', self.__bar_plot_R, self.__outfile, self.__bar_out_file, plot_filter_type, str(alpha)]
        sys.stdout.write(
            '\n[START drawing bar plot]\n %s\n' % ' '.join(str(i) for i in cmd1))
        p1 = subprocess.Popen(cmd1, stdout=pipe, stderr=pipe, universal_newlines=True)

        cmd2 = [
            'Rscript', self.__scatter_plot_R, self.__outfile, self.__scatter_out_file, plot_filter_type, str(alpha)]
        sys.stdout.write(
            '\n[START drawing scatter plot]\n %s' % ' '.join(str(i) for i in cmd2))
        p2 = subprocess.Popen(cmd2, stdout=pipe, stderr=pipe, universal_newlines=True)

        p1.wait()
        p2.wait()
        if p1.returncode != 0:
            sys.stdout.write('Drawing bar failed: \n%s\n' % p1.stderr)
        if p2.returncode != 0:
            sys.stdout.write('Drawing scatter failed: \n%s\n' % p2.stderr)


class KEGGDict(dict):
    def __init__(self, param_obj, *args, **kwargs):
        super(KEGGDict, self).__init__(*args, **kwargs)
        # from core.common.get_params_data import KEGGEnrichParams
        # self.__args_obj = KEGGEnrichParams()
        self.__args_obj = param_obj
        self.out_name = 'GeneID'
        self.fdr_alpha = 0.05
        self.fdr_method = self.__args_obj.fdr_method
        self.plot_filter_type = self.__args_obj.plot_filter_type
        self.total_kgene_num = 0
        self.diff_kgene_num = 0
        self.outdir = ''
        self.diff_stat_dic = defaultdict(int)
        self.all_stat_dic = defaultdict(int)
        self.desc_dic = defaultdict(dict)
        self.__solve_args()

    @timmer.timmer('*** pre-process the data ***')
    def __solve_args(self):

        # solve convert file
        self.__parse_convert_file(self.__args_obj.convert_file)
        self.fdr_alpha = self.__args_obj.fdr_alpha
        self.p_alpha = self.__args_obj.p_alpha
        self.outdir = self.__args_obj.outdir
        g2kg_dic = self.__solve_gene2kgene_file(self.__args_obj.asso_file)
        kg2pw_dic = self.__solve_kg2pw_file(self.__args_obj.org_pathway_list)
        diff_kg2g_dic = self.__parse_gene_file(self.__args_obj.diff_genes_file, g2kg_dic, kg2pw_dic, type_='diff')
        all_kg_set = self.__parse_gene_file(self.__args_obj.all_genes_file, g2kg_dic, kg2pw_dic, type_='all_gene')

        self.__stat_pw_diff_gene(diff_kg2g_dic=diff_kg2g_dic, kg2pw_dic=kg2pw_dic, all_kg_set=all_kg_set)
        self.__solve_desc_file(PATHWAY_LIST_PATH)

    def __stat_pw_diff_gene(self, diff_kg2g_dic, kg2pw_dic, all_kg_set):
        for k in all_kg_set:
            for pw in kg2pw_dic[k]:
                if k in diff_kg2g_dic:
                    self.diff_stat_dic[pw] += 1
                    if pw not in self:
                        self[pw] = set()
                    self[pw].update(diff_kg2g_dic[k])

                self.all_stat_dic[pw] += 1

    def __parse_convert_file(self, file):
        if file is None:
            return
        self.out_name = 'GeneName'
        self.convert_dic = dict()
        df = pd.read_table(file, sep='\t', header=None, dtype=str)
        for id_, name in zip(df[0], df[1]):
            self.convert_dic[id_] = name

    def __parse_gene_file(self, file, g2kg_dic, kg2pw_dic, type_: str='all_gene'):
        """parse gene list with type_

        :param file: str
        :param type_: `all_gene`, `diff_gene`
        :return:
        """

        genes = (line.strip() for line in open(file))
        remove_gene = 0
        tem_ds = defaultdict(set)
        all = 0
        if type_ == 'all_gene':
            tem_ds = set()
            for line in genes:
                all += 1
                if line not in g2kg_dic:
                    remove_gene += 1
                    continue
                kg = g2kg_dic[line]
                if kg not in kg2pw_dic:
                    continue
                tem_ds.add(kg)
            self.total_kgene_num = len(tem_ds)

        else:
            for line in genes:
                all += 1
                if line not in g2kg_dic:
                    remove_gene += 1
                    continue
                kg = g2kg_dic[line]
                if kg not in kg2pw_dic:
                    continue
                tem_ds[kg].add(line)
            self.diff_kgene_num = len(tem_ds)

        sys.stdout.write(
            '\n{num} genes in {name} genes were removed [total number of {name} genes is {all_num}]'.format(
                num=remove_gene,
                name='all' if type_ == 'all_gene' else 'diff',
                all_num=all))

        return tem_ds

    @staticmethod
    def __solve_gene2kgene_file(file):
        dic = dict()
        with open(file) as infile:
            for line in infile:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                try:
                    gene, kegg_gene = line.split('\t')
                except ValueError:
                    continue

                dic[gene] = kegg_gene
            return dic

    @staticmethod
    def __solve_kg2pw_file(file):
        df = pd.read_table(file, sep='\t', header=None, dtype=str)
        df[1] = df[1].str.replace('path:', '')
        temp_dic = defaultdict(set)
        for k, v in zip(df[0], df[1]):
            temp_dic[k].add(v)
        return temp_dic

    def __solve_desc_file(self, file):
        dic = defaultdict(dict)
        with open(file) as infile:
            class_1 = None
            for line in infile:
                line = line.strip()
                if line.startswith('##'):
                    # class_2 = line.replace('#', '')
                    continue
                elif line.startswith('#'):
                    class_1 = line.replace('#', '')
                else:
                    pw, desc = line.split('\t')
                    pw = '{}{}'.format(self.__args_obj.species, pw)
                    dic[pw]['desc'] = desc
                    dic[pw]['class'] = class_1
        self.desc_dic = dic
