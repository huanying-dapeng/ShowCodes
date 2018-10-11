#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file    : cancer_estimator.py
@author  : zhipeng.zhao
@contact: 757049042@qq.com
"""

import argparse
import os
import pickle
import sys
from threading import Lock

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline

work_dir = os.path.dirname(os.path.abspath(__file__))


class ParamObj(object):
    """
    collect and check command line parameters
    """
    def __init__(self):
        self.outdir = None
        self.data_file = None
        self.is_ready = False
        self.stdout = True
        self.__parser = argparse.ArgumentParser(
            __doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.__estimator_dict = {
            'lr': os.path.join(work_dir, 'estimators', 'logistic_estimator.pk'),
            'knn': os.path.join(work_dir, 'estimators', 'knn_estimator.pk')
        }
        self.estimator_file = None
        self.prefix = None
        self._add_params()

    def _args_check(self, args_obj):
        self.data_file = args_obj.input_file
        self.train_file = args_obj.train_data
        self.outdir = args_obj.outdir
        self.re_fit = args_obj.re_fit
        self.stdout = not args_obj.no_stdout
        self.estimator_file = self.__estimator_dict[args_obj.method]
        self.is_ready = True
        self.prefix = args_obj.method if args_obj.prefix == "" else args_obj.prefix
        if not os.path.isfile(self.data_file):
            self.is_ready = False
            print(self.data_file, 'is not exist')
        if self.train_file is not None and not os.path.isfile(self.train_file):
            self.is_ready = False
            print(self.train_file, 'is not exist')
        if self.is_ready:
            if not os.path.isdir(self.outdir):
                os.makedirs(self.outdir)
            self.is_ready = True

    def _add_params(self):
        self.parse.add_argument(
            '-i', '--input_file', required=True,
            help='input the file of test data (dataframe format). Index '
                 'is the sample names and columns is not included')
        self.parse.add_argument(
            '-m', '--method', required=True, choices=['lr', 'knn'], default='lr',
            help='select the method to predict the cancer'
                 'lr: LogisticRegression; knn: KNeighborsClassifier, [default: %(default)s]')
        self.parse.add_argument(
            '--no_stdout', default=False, required=False,
            help='add this option, then the program will not output result in std')
        self.parse.add_argument(
            '--re_fit', required=False, action='store_true',
            help='input this option, the program will re-fit the model through '
                 'the default data, and if the default data is not existent, '
                 'it will raise exception')
        self.parse.add_argument(
            '-t', '--train_data', required=False,
            help='dataframe format, and Index is the categrory labels(cancer name) '
                 'and columns is not included. And if this option is provided, then '
                 'the --refit must be added')
        self.parse.add_argument(
            '-p', '--prefix', default="",
            help='add prefix to the out file name, [default: %(default)s]')
        self.parse.add_argument(
            '-o', '--outdir', default='.', help='input outdir [default %(default)s]')

    @property
    def parse(self):
        return self.__parser

    def parse_args(self, args_num):
        argvs = sys.argv
        if '-h' in argvs or '--help' in argvs or len(argvs) < args_num:
            self.parse.print_help()
            return
        args_obj = self.parse.parse_args()

        self._args_check(args_obj)


class CancerEstimator(BaseEstimator, ClassifierMixin):
    """

    """

    __LOCK__ = Lock

    def __init__(self, param_obj: ParamObj):
        super().__init__()
        self.__estimator: Pipeline = None
        self.__param_obj = param_obj
        self.__predict_ = None
        self.__predict_probo_: np.ndarray = None
        self.__predict_df: pd.DataFrame = None
        self.__predict_probo_df: pd.DataFrame = None

    def score(self, X, y, sample_weight=None):
        return super().score(X, y, sample_weight)

    def fit(self, X: np.array=None, y: np.array=None):
        """ user can recall fit function to rebuilt the model """
        if X is None or y is None:
            print("use the default train data set")
            data = self.__get_train_data()
            if data is None:
                raise Exception("no train data to fit, please input the train data")
            else:
                X, y = data
        self.__get_estimator()
        self.__estimator.fit(X, y)

    def predict(self, X, y) -> pd.DataFrame:
        self.__predict(X)
        probo = self.__predict_probo_.max(axis=1)
        df = pd.DataFrame({
            'sample_name': y.tolist(),
            'predicted_result': self.__predict_.tolist(),
            'probability': probo.tolist()
        })
        self.__predict_df = df
        if self.__predict_probo_df is None: self.predict_probo(X, y)
        return df

    def predict_probo(self, X, y):
        self.__predict(X)
        df = pd.DataFrame(data=self.__predict_probo_, index=y, columns=self.__estimator.classes_)
        df.insert(loc=0, column='predicted_result', value=self.__predict_)
        df.index.name = 'sample_name'
        self.__predict_probo_df = df
        if self.__predict_df is None: self.predict(X, y)
        return df

    def output_predict(self):
        """ output result to local file """
        out_dir = self.__param_obj.outdir
        prefix = self.__param_obj.prefix
        brief_file = os.path.join(out_dir, prefix + "_predict_brief_result.xls")
        detail_file = os.path.join(out_dir, prefix + "_predict_detail_result.xls")
        print('\noutdir:', out_dir)
        print('  file:', brief_file)
        print('  file:', detail_file)
        self.__predict_df.to_csv(open(brief_file, 'w'), sep='\t', index=True, header=True)
        self.__predict_probo_df.to_csv(open(detail_file, 'w'), sep='\t', index=True, header=True)

    def __predict(self, X):
        self.__get_estimator()
        if self.__predict_ is None or self.__predict_probo_ is None:
            with self.__LOCK__():
                self.__predict_ = self.__estimator.predict(X)
                self.__predict_probo_ = self.__estimator.predict_proba(X)

    def __get_train_data(self):
        """
        get the train data from the program dir or user input
        :return: tuple(data: np.ndarray, lables: np.ndarray)
        """
        file = os.path.join(work_dir, 'db', 'cpg_training_clusters.txt')
        if not os.path.isfile(file):
            return None
        df = pd.read_table(file, sep='\t', header=None, index_col=0)
        return df.values, df.index

    def __get_estimator(self):
        """
        get the estimator from the pipline object pickle file
            file name: knn_estimator.pk (saved in program dir)
        :return: None
        """
        with self.__LOCK__():
            if self.__estimator is None:
                with open(self.__param_obj.estimator_file, 'rb') as infile:
                    self.__estimator = pickle.load(file=infile)





if __name__ == '__main__':
    # get params
    param_obj = ParamObj()
    param_obj.parse_args(2)

    # predict block
    if param_obj.is_ready:
        # obtain the test data from local
        data_file = param_obj.data_file
        df_test = pd.read_table(data_file, sep='\t', header=None, index_col=0)

        # get the training data, if re-fit param is True
        train_X, train_y = None, None
        if param_obj.train_file is not None:
            train_df = pd.read_table(param_obj.train_file, sep='\t', header=None, index_col=0)
            train_X = train_df.values
            train_y = train_df.index

        knn = CancerEstimator(param_obj=param_obj)
        if param_obj.re_fit:
            # rebuilt the model by the new data
            knn.fit(train_X, train_y)

        # predict
        res_df = knn.predict(df_test.values, df_test.index)

        # output predict result
        print('\n', res_df.round({'probability': 3}))
        knn.output_predict()
