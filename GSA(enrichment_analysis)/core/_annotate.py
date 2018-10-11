#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/14 15:13
# @File    : _annotate.py

import os
import csv
import re
import json
import threading

import shutil
import cv2
import pandas as pd

from core.common import timmer
from conf import settings


class TermsInfo(dict):
    def __init__(self, obj, *args, **kwargs):
        super(TermsInfo, self).__init__(*args, **kwargs)
        self.__terms_obj = obj
        # self.__file = obj.input_file
        # self.__species = obj.species
        self.__value_type = obj.value_type
        self.colors = self.__get_colors(settings.COLORS_JSON_FILE)
        self.multi_color = settings.MULTI_TERMS_COLOR  # (255, 26, 146)
        self.gene_info_dic = None
        self.__solve_data()

    @staticmethod
    def __get_colors(file):
        with open(file) as infile:
            return json.load(infile)

    def __gene_info(self):
        import numpy as np
        df = pd.read_table(self.__terms_obj.input_file, sep='\t', header=None,
                           dtype={0: 'str', 1: self.__terms_obj.value_type})
        df.replace(to_replace=np.nan, value='', inplace=True)
        self.gene_info_dic = {k: v for k, v in zip(df[0], df[1])}

        values = sorted(
            set(int(i*10) for i in df[1]) if self.__terms_obj.value_type == 'float' else set(i for i in df[1]))
        ratio = 10 / len(values)
        color_index = {k: v for k, v in zip(values, (int(i*ratio) for i in range(len(values))))}
        return color_index

    def __gene_to_ko(self, color_index):
        dic = dict()

        with open(self.__terms_obj.gene_to_ko) as infile:
            for ko, gene in csv.reader(infile, delimiter='\t'):
                gene = gene.replace('ensembl:', '').strip()

                if gene not in self.gene_info_dic:
                    continue

                if ko not in dic:
                    dic[ko] = dict()

                dic[ko][gene] = color_index[self.gene_info_dic[gene]]
                # color_index[self.gene_info_dic[gene]]
        return dic

    def __gene_to_pathway(self, ko_gene_dic: dict):
        dic = dict()
        with open(self.__terms_obj.ko_to_pathway) as infile:
            for ko, pathway in csv.reader(infile, delimiter='\t'):
                pathway = pathway.replace('path:', '').strip()

                if ko not in ko_gene_dic:
                    continue

                if pathway not in dic:
                    dic[pathway] = dict()

                dic[pathway][ko] = ko_gene_dic[ko]

        return dic

    @timmer.timmer('get gene and related info')
    def __solve_data(self):
        color_index_dic = self.__gene_info()
        print(color_index_dic)
        ko_gene_index = self.__gene_to_ko(color_index_dic)
        res_dic = self.__gene_to_pathway(ko_gene_index)
        for k, dic in res_dic.items():
            for sub_k, sub_dic in dic.items():
                values = sorted(set(i for i in sub_dic.values()))
                color_index = values[0] if len(values) == 1 else \
                    (max(values) if self.__terms_obj.value_type == 'float' else -1)

                if k not in self:
                    self[k] = dict()
                self[k][sub_k] = {k: color_index for k in sub_dic}


class Annotation(object):
    """ kegg annotation: create one html and annotated picture """
    __obj = None
    __LOCK__ = threading.Lock

    def __init__(self, cwd='.'):
        self.__pic = ''
        self.__conf = ''
        self.__tem_html = settings.HTML_TEMPLATE_PATH
        self.__dhtml_js = settings.DHTML_JS
        self.__cwd = self.__create_dir(cwd)
        self.colors = self.__get_colors(settings.COLORS_JSON_FILE)
        self.multi_color = settings.MULTI_TERMS_COLOR  # (255, 26, 146)
        self.pic = None
        self.html = None
        self.static_dir = self.__create_dir(os.path.join(self.__cwd, 'static'))
        self.pathway_name = ''
        self.__copy()

        self.conf_rect_info = []

    def __new__(cls, *args, **kwargs):
        # singleton pattern
        with cls.__LOCK__():
            if cls.__obj is None:
                cls.__obj = super().__new__(cls)
            return cls.__obj

    @staticmethod
    def __is_exist(file):
        if not os.path.isfile(file):
            raise FileNotFoundError('文件不存在')
        return file

    @staticmethod
    def __get_colors(file):
        with open(file) as infile:
            return json.load(infile)

    @staticmethod
    def __create_dir(cwd):
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        return cwd

    def __copy(self):
        temp = os.path.join(self.static_dir, os.path.basename(self.__dhtml_js))
        if os.path.isfile(temp):
            return
        shutil.copy(self.__dhtml_js, temp)

    @timmer.timmer('create html file')
    def __create_html(self, ko_dic: dict, gene_dic: dict):
        url_ = 'http://www.kegg.jp'
        demo = '<area shape={shape}	coords={coords}	href="{url}"	title="{title}"%s/>'
        on_demo = ' onmouseover="popupTimer({sp}{name}{sp}, {sp}{anno}{sp}, {sp}{col}{sp})" onmouseout="hideMapTn()" '
        print('pathway: %s' % self.pathway_name, end='')

        def conf_iter():
            title_patt1 = re.compile('(?P<name>[^\s:]+)\s+.*?')
            title_patt2 = re.compile('(?P<name>[^\s:]+):?\s*.*?')
            ko_pattern = re.compile('hsa:\d+(?=[+]?)')
            rep = re.compile('\d+')

            with open(self.__conf, 'r') as conf_handler:
                for s, url, t in csv.reader(conf_handler, delimiter='\t'):
                    shape, coord = s.strip().split(' ', 1)
                    coords = rep.findall(coord)

                    anno = ['\n']
                    res = title_patt1.match(t)
                    res = title_patt2.match(t) if res is None else res

                    position = [int(i) for i in coords]
                    if shape == 'rect':
                        ko_tuple = ko_pattern.findall(url)
                        ko_color_indix_tuple = []

                        for ko in ko_pattern.findall(url):
                            if ko not in ko_dic:
                                continue

                            anno.extend(['{}\t{}'.format(k, gene_dic[k]) for k in ko_dic[ko]])
                            ko_color_indix_tuple.append(ko_dic[ko])
                        # print(ko_dic)
                        ko_color_indix_tuple = tuple(j for i in ko_tuple if i in ko_dic for j in ko_dic[i].values())
                        if ko_tuple and ko_color_indix_tuple:
                            if -1 in ko_tuple:
                                # 当为输入数据为分类信息, 如果一个[rect]包含多个基因[如 hsa00111 多个]时取特定值
                                color = self.multi_color
                            else:
                                # 如果一个[rect]包含多个基因[如 hsa00111 多个], 则取至最大的映射颜色值
                                color = self.colors[max(ko_color_indix_tuple)]

                            self.conf_rect_info.append([tuple(position[:2]), tuple(position[2:]), color])

                    name = res.group('name')
                    temp = demo.format(shape=shape, coords=','.join(coords), url=url_+url, title=t+'\n'.join(anno))
                    if not name.isnumeric():
                        temp = temp % on_demo.format(
                            sp='&quot;', name=name, anno=t, col='#ffffff')
                    else:
                        temp = temp % ''
                    yield temp

        with open(self.__tem_html, 'r') as infile, open(self.html, 'w') as out_handler:
            string = infile.read()

            string_ = string % {'pic_path': os.path.basename(self.pic), 'map_str': '\n'.join(conf_iter())}
            out_handler.write(string_)

    @timmer.timmer('modifypathway picture')
    def __anno_pic(self):
        print('pathway: %s' % self.pathway_name, end='')
        img = cv2.imread(self.__pic)
        top_pathways = {
            'hsa01100', 'hsa1110', 'hsa01120', 'hsa01130', 'hsa01200', 'hsa01210', 'hsa01212', 'hsa01230', 'hsa01220'}
        if self.pathway_name not in top_pathways and self.conf_rect_info:
            for lst in self.conf_rect_info:
                cv2.rectangle(img, *lst, 2)
        cv2.imwrite(self.pic, img)
        self.conf_rect_info = []

    def annotate(self, pathway_name: str, pic_path: str, conf_path: str, ko_color_dic: dict, gene_info_dic: dict):
        self.__pic = pic_path
        self.__conf = conf_path
        self.pathway_name = pathway_name
        pic_name = os.path.basename(self.__pic)
        self.pic = os.path.join(self.__cwd, pic_name)
        self.html = os.path.join(self.__cwd, str(pic_name.rsplit('.', 1)[0]) + '.html')
        self.__create_html(ko_dic=ko_color_dic, gene_dic=gene_info_dic)
        self.__anno_pic()


if __name__ == '__main__':
    test = Annotation()
    test.annotate(
        pathway_name='hsa00053',
        pic_path=r"C:\Users\fantasy\Desktop\hsa00053.png",
        conf_path=r"C:\Users\fantasy\Desktop\hsa00053.conf",
        ko_color_dic=dict(),
        gene_info_dic=dict()
    )
