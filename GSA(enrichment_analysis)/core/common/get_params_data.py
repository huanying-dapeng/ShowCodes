#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/16 13:00
# @File    : get_params_data.py

import os
import argparse
import sys

from conf import settings
from core.common import timmer


class AnnotParams:

    def __init__(self):
        self.input_file = ''
        self.species = 'hsa'
        self.value_type = 'float'
        self.ko_to_pathway = ''
        self.gene_to_ko = ''
        self.out_dir = '.'
        self.anno_data_dir = ''
        self.pathway_dir = ''
        self.__get_params()  # 放到最后防止被覆盖

    def __get_params(self):
        p = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        p.add_argument('filename', type=str,
                       help='The file contain genes and its info: two columns --> gene <\t> info '
                            '[if info is number, info will be between zero and one]')
        p.add_argument('-s', '--species', default='hsa', type=str,
                       help="Species abbreviations such as: hsa, ko [default: %(default)s]"
                            '''(for example: ko for KEGG Orthology, hsa for Homo sapiens,
                            mmu for Mus musculus, dme for Drosophila melanogaster,
                            ath for Arabidopsis thaliana, sce for Saccharomyces
                            cerevisiae and eco for Escherichia coli K-12 MG1655),
                            e.g. -s hsa''')
        p.add_argument('-d', '--outdir', default='./result', type=str,
                       help="output directory for result [default: %(default)s]")
        p.add_argument('-t', '--type', default='float', type=str, choices=['category', 'float'],
                       help="float: 0 <= value <= 1")

        if len(sys.argv) < 2:
            p.print_help()

        args = p.parse_args()
        if not os.path.isfile(args.filename):
            raise FileNotFoundError('the file is not existent')

        self.input_file = os.path.abspath(args.filename)
        self.species = args.species
        self.value_type = 'float' if args.type == 'float' else 'str'
        self.out_dir = os.path.abspath(args.outdir)
        temp_dir = os.path.join(settings.KO_TO_PATHWAY,
                                'ko' if self.species == 'ko' else os.path.join('organisms', self.species), )
        self.ko_to_pathway = os.path.join(temp_dir, self.species+'_pathway.list')
        self.gene_to_ko = os.path.join(
            temp_dir, self.species+('_ensembl.list' if self.species != 'ko' else '_name.list'))
        self.pathway_dir = os.path.join(
            settings.PATHWAY_DIR, 'ko' if self.species == 'ko' else os.path.join('organisms', self.species))


class EnrichParams:
    def __init__(self):
        self.filename = ''
        self.analysis_type = ''
        self.species = ''
        self.__type_trans = {
            'fasta_pro': 'fasta:pro',
            'fasta_nuc': 'fasta:nuc',
            'blastout_xml': 'blastout:xml',
            'blastout_tab': 'blastout:tab',
            'ncbigi_id': 'id:ncbigi',
            'uniprot_id': 'id:uniprot',
            'ensembl_id': 'id:ensembl',
            'ncbigene_id': 'id:ncbigene'
        }
        self.__analysis_trans = {
            'kegg': '/K',
            'go': '/G'
        }

        args = self.__get_params()
        self.outfile = ''
        self.work_dir = ''
        self.line_params = ' '.join(' '.join(map(str, lst)) for lst in self.__parse_params(parse_obj=args))

    def __parse_params(self, parse_obj):
        self.work_dir = os.path.abspath(parse_obj.outdir)
        self.outfile = os.path.join(self.work_dir, parse_obj.outfile)
        self.analysis_type = parse_obj.analysis_type
        self.species = parse_obj.species
        self.filename = parse_obj.filename

        if not os.path.exists(parse_obj.outdir):
            os.makedirs(self.work_dir)

        return [
            ('-i', os.path.abspath(parse_obj.filename)),
            ('-s', parse_obj.species),
            ('-t', self.__type_trans[parse_obj.datatype.strip()]),
            ('-E', parse_obj.evalue),
            ('-d', self.__analysis_trans[self.analysis_type]),
            ('-m', parse_obj.method),
            ('-n', parse_obj.fdr),
            ('-c', parse_obj.cutoff),
            # ('-o', self.outfile)
        ]

    @timmer.timmer('judge and parse args')
    def __get_params(self):
        p = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        p.add_argument('filename', type=str,
                       help='The input file contain genes: one columns --> ENSG00000196136')
        p.add_argument('-s', '--species', default='hsa', type=str,
                       help="Species abbreviations such as: hsa, ko, [default: %(default)s]"
                            '''(for example: ko for KEGG Orthology, hsa for Homo sapiens,
                            mmu for Mus musculus, dme for Drosophila melanogaster,
                            ath for Arabidopsis thaliana, sce for Saccharomyces
                            cerevisiae and eco for Escherichia coli K-12 MG1655),
                            e.g. -s hsa, [default: %(default)s]''')
        p.add_argument('-t', '--datatype', default='ensembl_id', type=str,
                       help='''input type (fasta_pro, fasta_nuc, blastout_xml,
                            blastout_tab, ncbigi_id, uniprot_id, ensembl_id,
                            ncbigene_id), [default: %(default)s]''')
        p.add_argument('-o', '--outdir', default='kegg_result', type=str,
                       help='output directory, [default: %(default)s]')
        p.add_argument('-f', '--outfile', default='kegg_enrichment.xls', type=str,
                       help='output file name, [default: %(default)s]')
        p.add_argument('-e', '--evalue', default=1e-5, type=float,
                       help="expect threshold for BLAST, default 1e-5")
        p.add_argument('-d', '--analysis_type', default='kegg', type=str, choices=['kegg', 'go'],
                       help='''enrich database type, [default: %(default)s]''')
        p.add_argument('-m', '--method', default='h', type=str,
                       help='''choose statistical test method: b for binomial test, c
                            for chi-square test, h for hypergeometric test /
                            Fisher's exact test, and x for frequency list, [default: %(default)s]''')
        p.add_argument('-n', '--fdr', default='BH', type=str,
                       help='''choose false discovery rate (FDR) correction method:
                            BH for Benjamini and Hochberg, BY for Benjamini and
                            Yekutieli, QVALUE, and None, [default: %(default)s]''')
        p.add_argument('-c', '--cutoff', default=5, type=int,
                       help='''the gene number in a term is not less than the cutoff, 
                       [default: %(default)s]''')

        if len(sys.argv) < 2:
            p.print_help()

        args = p.parse_args()
        if not os.path.isfile(args.filename):
            raise FileNotFoundError('%s file is not existent' % args.filename)

        return args


class KEGGEnrichParams(object):
    def __init__(self):
        self.__trans_dic = {
            'HS': 'holm-sidak',
            'BH': 'fdr_bh',
            'BY': 'fdr_by',
            'TSBH': 'fdr_tsbh',
            'TSBKY': 'fdr_tsbky'
        }
        self.diff_genes_file = ''
        self.all_genes_file = ''
        self.asso_file = ''
        self.fdr_method = ''
        self.species = ''
        self.p_alpha = ''
        self.fdr_alpha = ''
        self.convert_file = None
        self.plot_filter_type = 'fdr'
        self.__get_params()
        self.cls_pathway_file = settings.PATHWAY_LIST_PATH
        self.org_pathway_list = os.path.join(
            settings.KO_OR_ORG_PATHWAY_PARENT_DIR,
            *(('ko', 'ko_pathway.list') if self.species == 'ko' else (
                'organisms', self.species, self.species + '_pathway.list')))

    @staticmethod
    def __dir_file_exist_check(*args, type_='file'):
        """check and create dir or check file

        :param args: files or dirs list
        :param type_: file or dir
        :return:
        """
        if type_ == 'file':
            for f in args:
                if not os.path.isfile(f):
                    raise FileExistsError('%s is not existent' % f)
        elif type_ == 'dir':
            for d in args:
                if not os.path.exists(d):
                    os.makedirs(d)
        else:
            raise TypeError('the type_ is not existent, please check the func DOC')

    @staticmethod
    def __check_alpha(msg, value):
        import warnings
        if value > 0.05:
            warnings.warn('%s is usually less than or equal to `0.05`' % msg)

    def __check_args(self, args):

        self.diff_genes_file, self.all_genes_file, self.asso_file = [os.path.abspath(p) for p in args.filenames]
        # check file
        self.__dir_file_exist_check(self.diff_genes_file, self.all_genes_file, self.asso_file, type_='file')
        self.convert_file = args.convert_file
        # check file
        if self.convert_file is not None:
            self.__dir_file_exist_check(self.convert_file, type_='file')
        self.fdr_method = self.__trans_dic.get(args.fdr_method, 'fdr_bh')
        self.species = args.species
        self.p_alpha = args.p_alpha
        # check alpha value
        self.__check_alpha('pvalue alpha', self.p_alpha)
        self.fdr_alpha = args.q_alpha
        # check alpha value
        self.__check_alpha('fdr alpha', self.fdr_alpha)
        self.outdir = os.path.abspath(args.outdir)
        # check directory
        self.__dir_file_exist_check(self.outdir, type_='dir')
        self.plot_filter_type = args.plot_filter_type

    def __get_params(self):
        p = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        p.add_argument('filenames', type=str, nargs=3,
                       help='there need three files: diff_genes.list all_genes.list association_gene2kegggene.list')
        p.add_argument('-n', '--fdr_method', default='BH', type=str, choices=self.__trans_dic.values(),
                       help='''choose false discovery rate (FDR) correction method:
                                    `BH` for Benjamini/Hochberg  (non-negative) ,
                                    `BY` for Benjamini/Yekutieli (negative), 
                                    `TSBH` for two stage fdr correction (non-negative), 
                                    `TSBKY` for two stage fdr correction (non-negative), [default: %(default)s]''')
        p.add_argument('-s', '--species', default='hsa', type=str,
                       help="Species abbreviations such as: hsa, ko, [default: %(default)s]"
                            '''(for example: ko for KEGG Orthology, hsa for Homo sapiens,
                            mmu for Mus musculus, dme for Drosophila melanogaster,
                            ath for Arabidopsis thaliana, sce for Saccharomyces
                            cerevisiae and eco for Escherichia coli K-12 MG1655),
                            e.g. -s hsa, [default: %(default)s]''')
        p.add_argument('-p', '--p_alpha', default=0.05, type=float,
                       help='the threshold of pvalue, [default: %(default)s]')
        p.add_argument('-q', '--q_alpha', default=0.05, type=float,
                       help='the threshold of fdr, [default: %(default)s]')
        p.add_argument('-t', '--plot_filter_type', default='fdr', type=str, choices=['fdr', 'pvalue'],
                       help='the threshold of fdr, [default: %(default)s]')
        p.add_argument('-f', '--convert_file', default=None, type=str,
                       help='convert ensembl id to gene name, which contain two fields: ensembl_id  gene_name')
        p.add_argument('-o', '--outdir', default='./kegg_enrichment', type=str,
                       help='output directory of results, [default: %(default)s]')

        if len(sys.argv) < 4:
            p.print_help()

        args = p.parse_args()

        self.__check_args(args)


class GOPlotParams(object):
    def __init__(self):
        from core.go.obo_parser import GraphEngines
        self.graph_engines = GraphEngines

    def __get_params(self):
        import optparse
        p = optparse.OptionParser("%prog [obo_file]")
        p.add_option("--description", dest="desc",
                     help="write term descriptions to stdout"
                          " from the obo file specified in args", action="store_true")
        p.add_option("-t", "--term", dest="term", help="write the parents and children"
                                                       " of the query term", action="store", type="string",
                     default=None)
        p.add_option("-e", "--engine", default="pydot",
                     choices=self.graph_engines,
                     help="Graph plot engine, must be one of {0} [default: %default]".format(
                         "|".join(self.graph_engines))
                     )
        p.add_option("--gml", action="store_true",
                     help="Write GML output (for Cytoscape) [default: %default]")
        p.add_option("--disable-draw-parents",
                     action="store_false",
                     dest='draw_parents',
                     help="Do not draw parents of the query term")
        p.add_option("--disable-draw-children",
                     action="store_false",
                     dest='draw_children',
                     help="Do not draw children of the query term")
        p.add_option("-f", "--terms_file",
                     dest='terms_file',
                     default=None,
                     help="the file contains terms list")

        p.set_defaults(draw_parents=True)
        p.set_defaults(draw_children=True)

        opts_, args_ = p.parse_args()

        if len(sys.argv) < 2:
            p.print_help()

        if not len(args_):
            obo_file_ = settings.OBO_FILE
        else:
            obo_file_ = args_[0]
            assert os.path.exists(obo_file_), "file %s not found!" % obo_file_

        return opts_, obo_file_

    def get_args(self):
        return self.__get_params()


class GOEnrichParams(object):
    def __init__(self):
        self.__trans_dic = {
            'HS': 'holm-sidak',
            'BH': 'fdr_bh',
            'BY': 'fdr_by',
            'TSBH': 'fdr_tsbh',
            'TSBKY': 'fdr_tsbky'
        }
        self.diff_genes_file = ''
        self.all_genes_file = ''
        self.asso_file = ''
        self.fdr_method = ''
        self.p_alpha = ''
        self.fdr_alpha = ''
        self.convert_file = None
        self.plot_filter_type = 'fdr'
        self.__get_params()

    @staticmethod
    def __dir_file_exist_check(*args, type_='file'):
        """check and create dir or check file

        :param args: files or dirs list
        :param type_: file or dir
        :return:
        """
        if type_ == 'file':
            for f in args:
                if not os.path.isfile(f):
                    raise FileExistsError('%s is not existent' % f)
        elif type_ == 'dir':
            for d in args:
                if not os.path.exists(d):
                    os.makedirs(d)
        else:
            raise TypeError('the type_ is not existent, please check the func DOC')

    def __obo_file_check(self, file):
        if file == os.path.basename(settings.OBO_FILE):
            file = settings.OBO_FILE
        elif not os.path.isfile(file):
            raise FileExistsError('%s is not existent' % file)
        return os.path.abspath(file)

    @staticmethod
    def __check_alpha(msg, value):
        import warnings
        if value > 0.05:
            warnings.warn('%s is usually less than or equal to `0.05`' % msg)

    def __check_args(self, args):

        self.diff_genes_file, self.all_genes_file, self.asso_file = [os.path.abspath(p) for p in args.filenames]
        # check file
        self.__dir_file_exist_check(self.diff_genes_file, self.all_genes_file, self.asso_file, type_='file')
        self.convert_file = args.convert_file
        # check file
        if self.convert_file is not None:
            self.__dir_file_exist_check(self.convert_file, type_='file')
        self.fdr_method = self.__trans_dic.get(args.fdr_method, 'fdr_bh')
        self.p_alpha = args.p_alpha
        # check alpha value
        self.__check_alpha('pvalue alpha', self.p_alpha)
        self.fdr_alpha = args.q_alpha
        # check alpha value
        self.__check_alpha('fdr alpha', self.fdr_alpha)
        self.outdir = os.path.abspath(args.outdir)
        # check directory
        self.__dir_file_exist_check(self.outdir, type_='dir')
        self.plot_filter_type = args.plot_filter_type
        self.obo_file = self.__obo_file_check(args.obo_file)

    def __get_params(self):
        p = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        p.add_argument('filenames', type=str, nargs=3,
                       help='there need three files: diff_genes.list all_genes.list association_gene2goterm.list')
        p.add_argument('-b', '--obo_file', default=os.path.basename(settings.OBO_FILE), type=str,
                       help='if the default do not meet your requirement, you can add it by this optional '
                            'parameter, [default: %s]' % ' '.join(settings.OBO_FILE_VERSION))
        p.add_argument('-n', '--fdr_method', default='BH', type=str, choices=self.__trans_dic.keys(),
                       help='''choose false discovery rate (FDR) correction method:
                                    `BH` for Benjamini/Hochberg  (non-negative) ,
                                    `BY` for Benjamini/Yekutieli (negative), 
                                    `TSBH` for two stage fdr correction (non-negative), 
                                    `TSBKY` for two stage fdr correction (non-negative), [default: %(default)s]''')
        p.add_argument('-p', '--p_alpha', default=0.05, type=float,
                       help='the threshold of pvalue, [default: %(default)s]')
        p.add_argument('-q', '--q_alpha', default=0.05, type=float,
                       help='the threshold of fdr, [default: %(default)s]')
        p.add_argument('-t', '--plot_filter_type', default='fdr', type=str, choices=['fdr', 'pvalue'],
                       help='the threshold of fdr, [default: %(default)s]')
        p.add_argument('-f', '--convert_file', default=None, type=str,
                       help='convert ensembl id to gene name, which contain two fields: ensembl_id  gene_name')
        p.add_argument('-o', '--outdir', default='./go_enrichment', type=str,
                       help='output directory of results, [default: %(default)s]')

        if len(sys.argv) < 4:
            p.print_help()

        args = p.parse_args()

        self.__check_args(args)
