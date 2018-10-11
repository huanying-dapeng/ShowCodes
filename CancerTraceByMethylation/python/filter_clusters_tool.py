#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/7/13 10:33
# @Author  : zhipeng.zhao
# @File    : filter_clusters_tool.py
import abc
import os
import sys
import threading

import pandas as pd

from libs.comm_demo import ParamDemo, CommTools


class DataTable(object):
    __LOCK__ = threading.Lock

    def __init__(self, class_name, table_name, file_path, header=False):
        self.class_name = class_name
        self.table_name = table_name
        self.file_path = file_path
        self.__file_header = header
        self.__df = None

    def get_dataframe(self, field_list: iter):
        if len(field_list) > 2:
            raise IndexError("the length of field_list should be 2")

        if self.__df is None:
            with self.__LOCK__():
                if self.__df is None:
                    self.__read_data()

        df = self.__df.loc[:, field_list]
        df.columns = ['cluster_id', self.class_name]

        return df.set_index('cluster_id')

    def __read_data(self):
        self.__df = pd.read_table(self.file_path, sep='\t', header=None if self.__file_header is False else 0)


class FilterTools(object):

    @staticmethod
    def merge_tables(table_obj_list, field_list=None) -> pd.DataFrame:
        field_list = [0, 4] if field_list is None else field_list
        df_list = [datatable.get_dataframe(field_list) for datatable in table_obj_list]

        df = pd.concat(df_list, axis=1)

        return df

    @staticmethod
    def calculate_math_range(df: pd.DataFrame) -> pd.Series:
        temp = df.reset_index().groupby('cluster_id').mean()
        temp = temp.max() - temp.min()
        return temp

    @staticmethod
    def filter_cluster(ser: pd.Series, threshold=0.1):
        ser = ser.sort_values(ascending=False)
        len = int(ser.size * threshold)
        index = ser[:len].index
        return tuple(index)


class FilterDemo(dict, metaclass=abc.ABCMeta):
    def __init__(self, args_obj):
        super(FilterDemo, self).__init__()
        self.__args_obj = args_obj
        self.__table_list = []
        self.__initialize(data_file=args_obj.data_file_detail)

    @property
    def args_obj(self):
        return self.__args_obj

    @property
    def table_list(self):
        return self.__table_list

    def __initialize(self, data_file):
        with open(data_file) as infile:
            for line in infile:
                class_name, sample_name, file_path = line.strip().split('\t')
                item_name = class_name + "_" + sample_name
                self[item_name] = DataTable(class_name=class_name, table_name=item_name, file_path=file_path,
                                            header=False)
                self.table_list.append(item_name)

    @abc.abstractmethod
    def run(self):
        pass


class FilterTrainData(FilterDemo):

    def run(self):
        tables = [self[item] for item in self.table_list]
        df = FilterTools.merge_tables(table_obj_list=tables, field_list=[0, 4])
        df = df.T

        max_min_range_ser = FilterTools.calculate_math_range(df=df)
        final_fields = FilterTools.filter_cluster(
            ser=max_min_range_ser, threshold=self.args_obj.filter_threshold)
        final_fields = sorted(final_fields)

        df = df.loc[:, final_fields]
        self.__output_data(df)
        self.__output_clusters_boundaries(self.args_obj.cpg_boundaries_file, final_fields)

    def __output_clusters_boundaries(self, boundaries_file, final_fields):
        df = pd.read_table(boundaries_file, sep='\t', header=0, index_col=0)
        df = df.loc[final_fields, :]
        new_index = [i for i in range(1, len(final_fields) + 1)]
        df.index = new_index

        outfile = os.path.join(self.args_obj.outdir, 'filtered_cpg_training_clusters.txt')

        df.to_csv(outfile, sep='\t', header=True, index=True)

    def __output_data(self, df: pd.DataFrame):
        outfile = os.path.join(self.args_obj.outdir, 'cpg_training_clusters.txt')
        df.to_csv(outfile, sep='\t', header=False)


class FilterTestData(FilterDemo):

    def run(self):
        tables = [self[item] for item in self.table_list]
        df = FilterTools.merge_tables(table_obj_list=tables, field_list=[0, 4])
        df = df.T

        self.__output_data(df)

    def __output_data(self, df: pd.DataFrame):
        outfile = os.path.join(self.args_obj.outdir, 'cpg_training_clusters.txt')
        df.to_csv(outfile, sep='\t', header=False)


class FilterTrainClusterParam(ParamDemo):

    def __init__(self):
        super(FilterTrainClusterParam, self).__init__()
        self.is_ready = False
        self.data_file_detail = None
        self.cpg_clusters_file = None
        self.filter_threshold = 0.1
        self._add_params()
        self.parse_args(3)

    def _args_check(self, args_obj):
        self.outdir = CommTools.check_dir(args_obj.outdir)
        self.data_file_detail = CommTools.check_file(args_obj.infile)
        self.cpg_clusters_file = CommTools.check_file(args_obj.cpg_clusters)
        self.filter_threshold = args_obj.filter_threshold
        self.is_ready = True

    def _add_params(self):
        self.parse.add_argument('-i', '--infile', type=str, required=True,
                                help='the file of cpg sites files details which will be the testing dataset,' +
                                     ', and it has 3 fields: class_name<TAB>sample_name<TAB>file_abspath; ' +
                                     'If you want see the detail, see the samples in the program')
        self.parse.add_argument('-c', '--cpg_clusters', required=True, type=str,
                                help='Cpg clusters boundaries file which contain 4 columns: ' +
                                     'marker_index, chr, start, end')
        self.parse.add_argument('-f', '--filter_threshold', default=0.1, type=float,
                                help="In the filter process, we will use the methylation rangeMR--MR to " +
                                     "indicate a feature's differential power between classes, meanwhile " +
                                     "when we get the MR, we will sort the cluster by MR and will remain the " +
                                     "clusters which are in the top 10%%.")
        self.parse.add_argument('-o', '--outdir', required=False, type=str, default='FilteredTrainCluster',
                                help='Output data directory, [default "%(default)s"]')


class FilterTestClusterParam(ParamDemo):

    def __init__(self):
        super(FilterTestClusterParam, self).__init__()
        self.data_file_detail = None
        self.is_ready = False

        self._add_params()
        self.parse_args(2)

    def _args_check(self, args_obj):
        self.outdir = CommTools.check_dir(args_obj.outdir)
        self.data_file_detail = CommTools.check_file(args_obj.infile)
        self.is_ready = True

    def _add_params(self):
        self.parse.add_argument('-i', '--infile', type=str, required=True,
                                help='the file of cpg sites files details which will be the testing dataset,'
                                     ', and it has 3 fields: class_name<TAB>sample_name<TAB>file_abspath; '
                                     'If you want see the detail, see the samples in the program')
        self.parse.add_argument('-o', '--outdir', required=False, type=str, default='FilteredTestCluster',
                                help='Output data directory, [default "%(default)s"]')
