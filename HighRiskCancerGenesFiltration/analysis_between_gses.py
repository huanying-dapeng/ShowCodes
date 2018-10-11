#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/6/1 8:48
# @File    : analysis_between_gses.py

import argparse
import csv
import json
import os
import pickle
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

import numpy as np
import pandas as pd
from Bio import SeqIO
from scipy.stats import ttest_ind

if sys.version_info.major < 3:
    raise Exception("this program need python3 interpreter")
loc_dir = os.path.dirname(__file__)


class AnaParams(object):
    """obtain the command-line argument and assign them to AnaParams's instance

    content:
        p_alpha: p_value significance level; alpha
        fc_alpha: the threshold of filtering fold change
        data_detail_file: GSExxxx or other data set basic information
            1. name field: data set unique name -- used to distinguish between different data sets,
                and it may not meaningful
            2. id field: data set ID, it may be not unique
            3. path field: data set file path
            4. tissue name field: ... used to group data set from broad categories
            5. tissue type field: such as WBC, Blood, Tumor, ... used to tag result file and make us understand
                the data sets being compared ----- W_VS_T...

    """

    def __init__(self):
        self.p_alpha = 0.001
        self.fc_alpha = 5
        self.data_detail_file = None
        self.asso_file_path = None
        self.pro_num = 5
        self.outdir = None
        self.not_output_raw_data = True
        self.merge_file = False
        self.group_field_name = 'exp_org_name'
        self.out_positive_rate = True
        self.not_add_mean2merge = False
        # this function must be in the end of __init__() to make sure the top property do not re-assigned
        self.__parser()

    def __check_file(self, args_obj):
        files = args_obj.files
        for f in files:
            if not os.path.isfile(f):
                raise FileNotFoundError('%s is not existent' % f)
        self.data_detail_file, self.asso_file_path = files
        self.p_alpha = args_obj.p_alpha
        self.fc_alpha = args_obj.fc_threshold
        self.pro_num = args_obj.process_num
        self.outdir = args_obj.outdir
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.merge_file = args_obj.merge_file
        self.group_field_name = args_obj.group_field_name
        self.not_add_mean2merge = args_obj.not_add_mean2merge
        self.out_positive_rate = args_obj.out_positive_rate
        self.not_output_raw_data = args_obj.not_output_raw_data

    def __parser(self):
        final_print = ' '.join([
            'USAGE Example: analysis_between_gses.py ctc_gse_data_info.list ctc_vs_wbc.asso -f 5 -o CTC_VS_WBC -p 10',
            '--merge_file -g exp_org_name exp_gse_id --not_add_mean2merge --out_positive_rate\n\n'
        ])
        p = argparse.ArgumentParser(__doc__, formatter_class=argparse.RawTextHelpFormatter, epilog=final_print)
        p.add_argument('files', nargs=2, type=str,
                       help='[USE: xxx.py data_info.txt asso.txt], \n'
                            '[data_info.txt]:\n'
                            'name\tgse_id\tpath\ttissue_name\ttissue_type\n'
                            'xxxx1\tGSE98139\t/usr/xxx/xxx1.txt\tbreast\ttissue\n'
                            'xxxx1\tGSE98002\t/usr/xxx/xxx2.txt\tblood\twbc\n'
                            '[asso.txt]:\n'
                            'experimental_group_name\tcontrol_group_name\n'
                            'xxxx1\txxxx2\n')
        p.add_argument('-a', '--p_alpha', type=float, default=0.001,
                       help='filter data through p_value alpha threshold, [alpha: %(default)s]')
        p.add_argument('-f', '--fc_threshold', type=float, default=5,
                       help='filter data through fold change threshold, [fc threshold: %(default)s]')
        p.add_argument('-o', '--outdir', type=str, default='./01.analysis_result',
                       help='output result dir, [default: %(default)s]')
        p.add_argument('-p', '--process_num', type=int, default=3,
                       help='set the process number of the program, [default %(default)s]')
        p.add_argument('--not_output_raw_data', default=True, action='store_false',
                       help='when add this option, program will not output raw data, [default: %(default)s]')
        p.add_argument('--merge_file', action='store_true',
                       help='add this option. The program will merge the analysis result by the group_field_name (-g)')
        p.add_argument('-g', '--group_field_name', default='exp_org_name', nargs='+',
                       choices=['exp_org_name', 'ctr_org_name', 'exp_gse_id', 'ctr_gse_id'],
                       help='this option need a field name used to group data. And org == tissue')
        p.add_argument('--not_add_mean2merge', action='store_true',
                       help='when add this option, it will not output raw data mean to merge file')
        p.add_argument('--out_positive_rate', action='store_true',
                       help='when add this option, it will output positive_rate to merge file')
        if len(sys.argv) < 2:
            p.print_help()

        self.__check_file(p.parse_args())


class DataTable(object):
    """here one table is a DataTable() instance

        1. read data method: which inert, the instance is only saving the data file path, and
            data is read only when the method is called in order to save memory and the size of instance self
    """

    def __init__(
            self, data_file_path, tissue_name='breast', tissue_type='wbc', data_type='rpkm', gse_id='GSE0000000'):
        self.__table_path = data_file_path
        # self.group_type = group_type
        self.data_type = data_type.lower()
        self.tissue_name = tissue_name.lower()
        self.tissue_type = tissue_type.lower()
        self.gse_id = gse_id
        self.__gene_info_file = os.path.join(loc_dir, 'gene_ensg_name.json')

    def __solve_id_problem(self, raw_df, group_field='Gene_ID'):
        """ translate ensg_id to gene symbol, and if gene symbol repeat, we will group df by gene id field
        and then deal with it by mean() method

        :return: DataFrame
        """
        name_demo = raw_df.index[0]
        if not name_demo.startswith('ENSG'):
            return raw_df

        with open(self.__gene_info_file) as infile:
            _dic = json.load(infile)
        id_tran_dic = {k: _dic.get(k, '__NAN__') for k in raw_df.index}
        raw_df = raw_df.rename(index=id_tran_dic).reset_index().groupby(group_field).mean()
        raw_df = raw_df[raw_df.index != '__NAN__']
        if raw_df.index.name != group_field:
            raw_df.index.name = group_field
        return raw_df

    @staticmethod
    def __solve_rep_index(df: pd.DataFrame, group_field: str = 'Gene_ID'):
        """Remove duplicate data from the DataFrame
            if on ID has multi-records, we will take the mean of these records

        :param df: DataFrame
        :param group_field: DataFrame index name
        :return: DataFrame
        """
        index_list = df.index
        if len(index_list) != len(set(index_list)):
            try:
                df = df.reset_index().groupby(group_field).mean()
                # df.reset_index().rename(columns={'index': 'Gene_ID'})
            except TypeError:
                pass
        if df.index.name != group_field:
            df.index.name = group_field
        return df

    @staticmethod
    def __solve_str_values(df) -> pd.DataFrame:

        def trans_str2float(elem):
            """ the method will check the string in the DataFrame and translate it to 0 """

            # noinspection PyBroadException
            try:
                temp = float(elem)
            except TypeError:
                temp = 0
            except Exception:
                temp = 0

            return temp

        # noinspection PyBroadException
        try:
            temp_df = df + 0
        except TypeError:
            temp_df = df.applymap(trans_str2float)
        except Exception:
            temp_df = df.applymap(trans_str2float)

        return temp_df

    @property
    def df_table(self):
        """
        read data and check the ID and duplicate data, if the id is ensembl id, we will tranlate it to gene symbol
        """
        group_field = 'Gene_ID'
        df = pd.read_table(self.__table_path, sep='\t', header=0, index_col=0).dropna(how='all')
        df.index.name = group_field
        if df.empty:
            raise Exception('%s no data' % self.__table_path)
        df = self.__solve_str_values(df=df)
        df = self.__solve_id_problem(raw_df=df, group_field=group_field)
        df = self.__solve_rep_index(df=df, group_field=group_field)
        return df


class DataReaderDict(dict):
    """
        1. store the relation of data name and data set info and dataframe
        2. store the experimental and control groups relation

    """

    def __init__(self, params_obj):
        super(DataReaderDict, self).__init__()
        self.args_obj = params_obj
        self.args_obj = AnaParams()  # test use
        self.__parse_data_info()

    @property
    def asso_list(self):
        """ provide the VS files """

        with open(self.args_obj.asso_file_path) as infile:
            flag = set()
            try:

                for exp, contr in csv.reader(infile, delimiter='\t'):
                    yield exp, contr
                    flag.add((exp, contr))
            except ValueError:
                infile.seek(0)
                for line in infile:
                    exp, contr = re.split('\s+', line.strip('\r\n'))
                    if (exp, contr) in flag:
                        continue
                    yield exp, contr

    def __parse_data_info(self):
        """ create DataTable instance of data table in file and add them to DataReaderDict instance """
        with open(self.args_obj.data_detail_file) as infile:
            for name, gse_id, path, tissue_name, tissue_type, data_type in csv.reader(infile, delimiter='\t', ):
                self[name] = DataTable(data_file_path=path, tissue_name=tissue_name, tissue_type=tissue_type,
                                       data_type=data_type, gse_id=gse_id)


class PreMethodDict(dict):
    """the method set to pre-process the data

    """

    def __init__(self):
        super(PreMethodDict, self).__init__()
        self.__file_name = os.path.join(loc_dir, "Homo_sapiens.GRCh38.cdna.all.fa")
        self.__file_json = self.__file_name + '.json'
        self.index_name = 'Gene_ID'
        self.alt_index_name = 'Gene'
        self.reads_len_dict = self.__get_reads_info()
        self.__add_meth2self()

    @staticmethod
    def prepro_data(func_flow: list, args=None):
        solve_type = func_flow[-1]
        df = args
        for func in func_flow[: -1]:
            df = func(df)
        return solve_type, df

    def __add_meth2self(self):
        self.update({  # use enumeration method to solve the multi-data_type problems
            ('counts', 'rpkm'): [self.calculate_rpkm, self.calculate_log2, 'rpkm'],
            ('rpkm', 'counts'): [self.calculate_log2, 'rpkm'],

            ('counts', 'fpkm'): [self.calculate_rpkm, self.calculate_log2, 'fpkm'],
            ('fpkm', 'counts'): [self.calculate_log2, 'fpkm'],

            ('counts', 'tpm'): [self.calculate_tpm, self.calculate_log2, 'tpm'],
            ('tpm', 'counts'): [self.calculate_log2, 'tpm'],

            ('counts', 'signal'): [self.calculate_tpm, self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('signal', 'counts'): [self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('counts', 'rpm'): [self.calculate_rpkm, self.calculate_log2, 'rpkm'],
            ('rpm', 'counts'): [self.rpm2rpkm, self.calculate_log2, 'rpkm'],

            ('counts', 'med'): [self.calculate_med, self.calculate_log2, 'med'],
            ('med', 'counts'): [self.calculate_log2, 'med'],

            ('signal', 'rpkm'): [self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('rpkm', 'signal'): [self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('signal', 'rpm'): [self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('rpm', 'signal'): [self.rpm2rpkm, self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('signal', 'fpkm'): [self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('fpkm', 'signal'): [self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('signal', 'tpm'): [self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('tpm', 'signal'): [self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('rpm', 'rpkm'): [self.rpm2rpkm, self.calculate_log2, 'rpkm'],
            ('rpkm', 'rpm'): [self.rpm2rpkm, self.calculate_log2, 'rpkm'],

            ('rpm', 'fpkm'): [self.rpm2rpkm, self.calculate_log2, 'rpkm'],
            ('fpkm', 'rpm'): [self.rpm2rpkm, self.calculate_log2, 'rpkm'],

            ('rpm', 'tpm'): [self.rpm2rpkm, self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('tpm', 'rpm'): [self.calculate_log2, self.calculate_z_score, 'z_score'],

            ('signal', 'signal'): [self.calculate_log2, self.calculate_z_score, 'z_score'],
            ('rpm', 'rpm'): [self.rpm2rpkm, self.calculate_log2, 'rpm'],
            ('fpkm', 'fpkm'): [self.calculate_log2, 'fpkm'],
            ('tpm', 'tpm'): [self.calculate_log2, 'tpm'],
            ('rpkm', 'rpkm'): [self.calculate_log2, 'rpkm'],
            ('counts', 'counts'): [self.calculate_tpm, self.calculate_log2, 'tpm'],
        })

    def __get_reads_info(self):
        """ read gene cDNA length info
                1. get it from "Homo_sapiens.GRCh38.cdna.all.fa"
                2. get it from "Homo_sapiens.GRCh38.cdna.all.fa.json" which is created when firstly obtain
                   cDNA length info from the raw "xxxx.cdna.all.fa" file. Since then program will get cDNA
                   length info from "xxxx.cdna.all.fa.json" to save time

        """
        # judge whether the annotation json file is existent, because json file only contain gene length
        # information that its format is dict, which will save much time
        if os.path.exists(self.__file_json):
            with open(self.__file_json) as infile:
                dic = json.load(infile)
                return dic

        dic = dict()
        # if self._file_path is None which will indicate that this file is non-existent, the self.__dic will be empty
        if self.__file_name is None:
            raise FileNotFoundError('%s is not existent' % self.__file_name)

        gene_pattern = re.compile('gene_symbol:(.+?) ')
        for line in SeqIO.parse(self.__file_name, "fasta"):
            try:
                gene = gene_pattern.findall(line.description)[0]
            except IndexError:
                # if the line do not contain gene_symbol: ..., it will not be what we want, so skip this loop
                continue
            seq_len = len(line.seq)

            if dic.get(gene, 0) <= seq_len:
                dic[gene] = seq_len

        with open(self.__file_json, 'w') as out_handler:
            json.dump(dic, out_handler, indent='\t')

        return dic

    @staticmethod
    def calculate_log2(df):
        """solve df's value with `log2(value)`

        :param df: `pd.DataFrame`
        :return: `pd.DataFrame`
        """
        # log2
        max_val = df.max().max()
        # if max_val > 20:
        if max_val > 1000:
            df = np.log2(df + 1)
        return df

    @staticmethod
    def calculate_z_score(df):
        """
        :param df: `pd.DataFrame`
        :return: `pd.DataFrame`
        """
        if df.empty:
            return df
        # z_score
        df = (df - df.mean()) / df.std()
        df = df.round(5)
        return df

    @staticmethod
    def min_max_standardize(df):
        """min-max standardization

        :param df:
        :return: `pd.DataFrame`
        """
        max_val = df.max().max()
        min_val = df.min().min()

        return (df - min_val) / (max_val - min_val)

    def calculate_tpm(self, df):
        """
        :param df: `pd.DataFrame`
        :return: `pd.DataFrame`
        """
        if df.empty:
            return df

        reads_len_dict = self.reads_len_dict

        # get the reads bases, and its unit is kilobase or kb
        genes_len_dic = [reads_len_dict.get(k, np.nan) / 1000 for k in df.index]
        # gene_len_series = pd.Series(genes_len_dic)
        gene_len_series = pd.DataFrame(
            {'Gene_ID': list(df.index), 'value': genes_len_dic}).set_index('Gene_ID')['value']
        # Divide the read counts by the length of each gene in kilobases. This gives you reads per kilobase (RPK)
        df = df.divide(gene_len_series, axis='index')
        # Count up all the RPK values in a sample and divide this number by 1,000,000. This is your "per million"
        # scaling factor. Divide the RPK values by the "per million" scaling factor. This gives you TPM.
        map_reads_sum = df.sum() / 1000000
        # TPM result
        df = df.divide(map_reads_sum, axis='columns')
        # drop the line where values are all NA
        df = df.dropna(how='all').round(5)

        return df

    def calculate_rpkm(self, df):
        """
        1. Count up the total reads in a sample and divide that number by 1,000,000 - this is our
        "per million" scaling factor. Divide the read counts by the "per million" scaling factor.
        2. Divide the RPM values by the length of the gene, in kilobases. This gives you RPKM

        :param df: `pd.DataFrame`
        :return: `pd.DataFrame`
        """
        if df.empty:
            return df

        reads_len_dict = self.reads_len_dict

        # This normalizes for sequencing depth, giving you reads per million (RPM)
        map_reads_sum = df.sum() / 1000000
        df = df.divide(map_reads_sum, axis='columns')

        # Divide the RPM values by the length of the gene, in kilobases. This gives you RPKM
        genes_dic = {k: reads_len_dict.get(k, np.nan) / 1000 for k in df.index}
        gene_len_series = pd.Series(genes_dic)
        df = df.divide(gene_len_series, axis='index')

        # back up database
        if df.index.name is None or df.index.name != 'Gene_ID':
            df.index.name = 'Gene_ID'
        return df

    @staticmethod
    def calculate_med(df):
        """Normalization method
            ***  Med: Gene counts are divided by the median number of mapped reads
                (or library size) associated with their lane and multiplied by the
                mean median count across all the samples of the dataset
        :param df:
        :return: pd.DataFrame
        """
        medians = df.median(axis=0)
        mean_med = medians.mean()
        df = (df / medians) * mean_med
        return df

    def rpm2rpkm(self, df):
        """
        1. Divide the RPM values by the length of the gene, in kilobases. This gives you RPKM

        :param df:
        :return: `pd.DataFrame`
        """
        if df.empty:
            return df
        reads_len_dict = self.reads_len_dict

        # get the reads bases, and its unit is kilobase or kb
        genes_dic = {k: reads_len_dict.get(k, np.nan) / 1000 for k in df.index}
        gene_len_series = pd.Series(genes_dic)
        df = df.divide(gene_len_series, axis='index')
        return df


class DiffAnalysis(object):
    def __init__(self):
        self.__meth_dict_obj = pickle.dumps(PreMethodDict())
        self.merge_progrm = 'result_merge.py'
        self.analysis_res_info_table = 'result_file_dataset_detail_info.txt'  # info_table
        self.outdir_dic = {
            'exp_gse_id': '02.per_exp_gse_merge',
            'exp_org_name': '02.per_exp_org_merge',
            'ctr_gse_id': '02.per_ctr_gse_merge',
            'ctr_org_name': '02.per_ctr_org_merge'
        }
        self.sub_txt = [
            '#PBS -N {task_name} ',
            '#PBS -l nodes=1:ppn={pro_num}',
            '#PBS -l mem={men}',
            '#PBS -q zh',
            'cd {work_dir}\n',
            ' '.join([self.merge_progrm,
                      '{info_table} -g {group} -f {fc_threshold}{out_positive_rate}{not_out_mean} -o {out_dir}'])
        ]

    @staticmethod
    def multi_analysis(name, pickle_method_dic_obj, exp_obj, ctr_obj, queue, fc_alpha=5, p_alpha=0.001,
                       raw_df_is_out=False, outdir='.'):
        """the exp_obj and ctr_obj are instances of DataTable(...) class
            ```  the following is its methods and property
            table =  DataTable(...)
            table.gse_id
            table.data_type
            table.tissue_name
            table.data_type
            table.df_table
            ```
        :param name: exp_name + ctr_name
        :param pickle_method_dic_obj: the import pickle str of PreMethodDict()
        :param exp_obj: experimental group DataTable obj
        :param ctr_obj: control group DataTable ojb
        :param queue: Queue()
        :param fc_alpha: use to filter data through fold change value
        :param p_alpha: use to filter data through p value
        :param raw_df_is_out: judge whether it need output raw data to disk
        :param outdir: output data directory
        :return: None
        """
        del p_alpha

        def ttest(df1, df2):
            """ use scipy.stats.ttest_ind """
            comm_cols = df1.index & df2.index
            df1 = df1[df1.index.isin(comm_cols)]
            df2 = df2[df2.index.isin(comm_cols)]
            with np.errstate(invalid='ignore'):
                test_result = ttest_ind(df1, df2, axis=1, equal_var=False)
                p_value = pd.Series({k: v for k, v in zip(df1.index, test_result[1])})
            return p_value

        def out_raw_data(df1, df2, out_path_: str, flag_1: str, flag_2: str):
            raw_df1 = df1.add_prefix('%s_' % flag_1).reset_index()
            raw_df2 = df2.add_prefix('%s_' % flag_2).reset_index()
            raw_df1.merge(raw_df2, on='Gene_ID').round(10).to_csv(out_path_, sep='\t', index=False)

        def create_dir(dir_name):
            dir_name = os.path.abspath(dir_name)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            return dir_name

        # get the methods instance of pre-processing data class
        meth_dict_obj = pickle.loads(pickle_method_dic_obj)
        exp_key = (exp_obj.data_type, ctr_obj.data_type)  # (counts, rpm) --> (experimental group, control group)
        ctr_key = tuple(reversed(exp_key))  # (rpm, counts) --> (control group, experimental group)

        # get the DataFrame from DataTable's instance and pre-process the data to unify the form of the data
        #   1. exp: experimental group
        #   2. ctr: control group
        #   If no solution is fond which represents that we can not translate them to the common type, we will use
        #   the methods in `methods_list` [<1>log2, <2>z-score] and the fold-change will be meaningless.
        methods_list = [meth_dict_obj.calculate_log2, meth_dict_obj.calculate_z_score, 'z_score']
        exp_data_type, exp_df = meth_dict_obj.prepro_data(meth_dict_obj.get(exp_key, methods_list), exp_obj.df_table)
        ctr_data_type, ctr_df = meth_dict_obj.prepro_data(meth_dict_obj.get(ctr_key, methods_list), ctr_obj.df_table)

        if exp_data_type != ctr_data_type:
            raise TypeError('The method in the PreMethodDict() instance is error, please check it in line 129')

        # extract data of the common genes
        comm_index = exp_df.index & ctr_df.index
        exp_df = exp_df.loc[exp_df.index.isin(comm_index)]
        ctr_df = ctr_df.loc[ctr_df.index.isin(comm_index)]

        cancer = exp_obj.tissue_name

        # calculate mean of dataframe
        exp_mean = exp_df.mean(axis=1)
        ctr_mean = ctr_df.mean(axis=1)

        # calculate log2 fold change
        log2_fc = exp_mean - ctr_mean

        # calculate positive rate
        rate_df = exp_df.sub(ctr_mean, axis='index')
        rate_df[rate_df < fc_alpha] = np.nan
        positive_rate = rate_df.count(axis=1).divide(exp_df.count(axis=1))

        # calculate p_value
        p_val_ser = ttest(df1=exp_df, df2=ctr_df)

        exp_flag = exp_obj.tissue_type[0].upper()  # C, T, ...
        ctr_flag = ctr_obj.tissue_type[0].upper()  # W, C, ...
        ord_fields_list = [
            'p_value',
            'log2_fc',
            'E_{}_{}'.format(exp_flag, exp_data_type),
            'E_{}_{}'.format(ctr_flag, exp_data_type),
            'positive_rate'
        ]
        ana_res_df = pd.DataFrame(
            {
                ord_fields_list[0]: p_val_ser,
                ord_fields_list[1]: log2_fc,
                ord_fields_list[2]: exp_mean,
                ord_fields_list[3]: ctr_mean,
                ord_fields_list[4]: positive_rate
            }
        ).loc[:, ord_fields_list]  # to make sure the order of fields

        # output data to local
        raw_out_path = None
        if raw_df_is_out is True:
            raw_out_name = '{}_{}_VS_{}_{}_{}_Data.xls'.format(exp_flag, exp_obj.gse_id, ctr_flag, ctr_obj.gse_id,
                                                               exp_data_type)
            raw_out_path = os.path.join(create_dir(os.path.join(outdir, exp_obj.tissue_name.upper())), raw_out_name)
            out_raw_data(exp_df, ctr_df, raw_out_path, flag_1=exp_flag, flag_2=ctr_flag)
        ana_out_name = '{}_{}_{}_VS_{}_{}_Analysis_Result.xls'.format(cancer.upper(), exp_flag, exp_obj.gse_id,
                                                                      ctr_flag, ctr_obj.gse_id)
        out_path = os.path.join(create_dir(os.path.join(outdir, exp_obj.tissue_name.upper())), ana_out_name)
        ana_res_df.sort_values([ord_fields_list[0], ord_fields_list[2]], ascending=[True, False]).dropna(
            how='all').to_csv(out_path, sep='\t', index=True, index_label='gene')
        queue.put({
            'name': name,
            'final_data_type': exp_data_type,
            'exp_org_name': exp_obj.tissue_name,
            'ctr_org_name': ctr_obj.tissue_name,
            'exp_gse_id': exp_obj.gse_id,
            'ctr_gse_id': ctr_obj.gse_id,
            'exp_org_type': exp_obj.tissue_type,
            'ctr_org_type': ctr_obj.tissue_type,
            'raw_data_path': raw_out_path,
            'analysis_res_path': out_path
        })
        print(exp_obj.gse_id, '_VS_', ctr_obj.gse_id, ' done', sep='', end='\n', file=sys.stdout)

    def _merge_file(self, params_obj):
        """merge the data through the group name in group_list
                1. this function is just submit PBS tasks by using result_merge.py script

        :param params_obj:
        :return: None
        """

        cmd = '\n'.join(self.sub_txt)
        group_list = params_obj.group_field_name
        if isinstance(group_list, str):
            group_list = [group_list]
        pro_list = []
        for gn in group_list:
            task_name = str(time.time()) + '.' + gn.upper()
            outdir = os.path.abspath(params_obj.outdir)
            cmd_ = cmd.format(task_name=task_name,
                              pro_num=params_obj.pro_num,
                              men=int(params_obj.pro_num * 1.5) + 1,
                              work_dir=outdir,
                              info_table=self.analysis_res_info_table,
                              group=gn,
                              fc_threshold=params_obj.fc_alpha,
                              not_out_mean=' --not_output_rawdata_mean' if params_obj.not_add_mean2merge else '',
                              out_positive_rate=(' --out_positive_rate' if params_obj.out_positive_rate else ''),
                              out_dir=self.outdir_dic.get(gn, str(time.time()) + gn + 'merge'))

            # create the PBS task file and than use qsub file to submit the task
            cmd_file = os.path.join(outdir, task_name + '.sh')
            with open(cmd_file, 'w') as outfile:
                outfile.write(cmd_)

            # submit task
            pro_list.append(subprocess.Popen('qsub ' + cmd_file, shell=True, cwd=outdir))
        _ = [p.wait() for p in pro_list]

    def run(self):
        """ Run logic of this script """

        # get the params from command line
        params_obj = AnaParams()
        if params_obj.asso_file_path is None or params_obj.data_detail_file is None:
            return

        # the agent of data instance
        data_obj = DataReaderDict(params_obj=params_obj)
        # collect the result from processes
        queue = Manager().Queue()

        res_stat_dic = dict()
        pro_list = []
        with ProcessPoolExecutor(max_workers=params_obj.pro_num) as future:
            for exp_name, contr_name in data_obj.asso_list:
                name = exp_name + contr_name
                res_stat_dic[name] = dict()
                exp_data_obj = data_obj[exp_name]
                ctr_data_obj = data_obj[contr_name]
                pro_list.append(
                    future.submit(self.multi_analysis, name, self.__meth_dict_obj, exp_data_obj, ctr_data_obj, queue,
                                  fc_alpha=params_obj.fc_alpha, p_alpha=0.001,
                                  raw_df_is_out=params_obj.not_output_raw_data,
                                  outdir=params_obj.outdir))
        # the following code is used to check whether error is  thrown
        _ = [p.result() for p in pro_list]

        # output the intermediate file to local
        titles = ['name', 'final_data_type', 'exp_org_name', 'ctr_org_name', 'exp_gse_id', 'ctr_gse_id', 'exp_org_type',
                  'ctr_org_type', 'raw_data_path', 'analysis_res_path']
        self.analysis_res_info_table = os.path.join(os.path.abspath(params_obj.outdir),
                                                    'result_file_dataset_detail_info.txt')

        # create the intermediate file which will be used for the input of result_merge.py script
        handler = open(self.analysis_res_info_table, 'w')
        handler.write('%s\n' % '\t'.join(titles))
        line_demo = '\t'.join('{%s}' % i for i in titles) + '\n'  # demo '{a}\t{b}...'
        while 1:
            if queue.empty():
                break

            res_dic = queue.get()
            name = res_dic.get('name')

            handler.write(line_demo.format(**res_dic))
            res_stat_dic[name] = res_dic

        handler.close()

        if params_obj.merge_file is True:
            # call the merge data method
            self._merge_file(params_obj=params_obj)


if __name__ == '__main__':
    DiffAnalysis().run()
