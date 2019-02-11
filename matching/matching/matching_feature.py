#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import time
import json
import numpy as np


def mkdirs(path):
    """ Recursively create directories
    Args:
        arg1(str): innermost directory
    """
    if not os.path.isdir(path):
        mkdirs(os.path.split(path)[0])
    else:
        return
    try:
        os.mkdir(path)
    except OSError:
        pass


class FeatureModule(object):
    """ get the unique index of input feature, use feature only compare or hash transform

    Attributes:
        get_matching_table: return matching table
        update: input feature to update matching table
        free: release memory

    Examples:
    >>>ft = FeatureModule(feature_cfg, hash_cfg)
    >>>ft.process(input_feature)
    >>>ft.free()
    """
    def __init__(self, feat_config):
        """ Init Feature Module with configure

        Args:
            arg1 (dict): feature config
                         @distance_method: only support eculidean distance and cosine distance
                         @max_threshold: maximum threshold
                         @max_second_diff: difference threshold of maximum confidence and second maximum confidence

        Raises:
            ValueError: Distance method not supported
        """

        self.__register_dir = feat_config['register_dir']
        self.__feature_dim = feat_config['feature_dim']
        self.__threshold = feat_config['threshold']

        # time match
        self.__use_time_match = feat_config['use_time_match'] if 'use_time_match' in feat_config.keys() else False
        self.__time_match_interval = feat_config['time_match_interval'] if 'time_match_interval' in feat_config.keys() else [-100, -10]

        # register info
        self.__next_unique_number = 1
        self.__next_feature_index = 0
        # 第一行为unique_id，第二行为time_stamp，每一列代表一个目标
        self.__register_info = np.empty(shape=[2, 1000], dtype=np.int64)
        self.__register_features = np.empty(shape=[1000, self.__feature_dim], dtype=np.float32)

        # init distance function and compare function
        if (feat_config['distance_method'] == 'cosine'):
            self.__dist_method = self.__cosine_distance
        elif (feat_config['distance_method'] == 'euclidean'):
            self.__dist_method = self.__euclidean_distance
        else:
            raise ValueError('Distance method %s Not supported' % feat_config['distance_method'])

        # read all register info to feature_list
        try:
            # load register features
            json_list = os.listdir(self.__register_dir)
            for json_file in json_list:
                unique_id, ext = os.path.splitext(json_file)
                if ext != '.json':
                    continue
                feature = self.__load_feature(self.__register_dir + json_file)
                for f in feature:
                    self.__update_register_features(int(unique_id), f)

            if self.__next_feature_index > 0:
                self.__next_unique_number = np.max(self.__register_info[0][0:self.__next_feature_index]) + 1
        # OSError indicate feature_directory not exists
        except(OSError):
            mkdirs(self.__register_dir)

    def free(self):
        """ Release memory """
        self.__register_info = None
        self.__register_features = None
        # print('feature module free')

    def __save_feature(self, unique_id, unique_dict):
        """ Save Features to file

        Args:
            arg1 (int): unique id for index
            arg2 (dict): unique dict
        """
        json_file = self.__register_dir + str(unique_id) + '.json'
        feature_list = self.__load_feature(json_file)

        feature_list.append(unique_dict)
        with open(json_file, 'w') as file:
            json.dump(feature_list, file)

        return len(feature_list)

    def __load_feature(self, json_file):
        """ Load Features to list

        Args:
            arg1 (str): file name

        Returns:
            list: feature
        """
        try:
            with open(json_file, 'r') as file:
                feature_list = json.load(file)
        # IOError indicates file not exists，ValueError indicates parse json failed
        except(IOError, ValueError):
            feature_list = []
        return feature_list

    def __euclidean_distance(self, register_features, query_feature):
        """ Calculate Euclidean distance """
        score = np.empty(shape=[len(query_feature['feature']), register_features.shape[0]], dtype=np.float32)
        for index, feature in enumerate(query_feature['feature']):
            ff = np.tile(feature, register_features.shape[0])
            ff = np.reshape(ff, (register_features.shape[0], register_features.shape[1]))
            diff = register_features - ff
            score[index] = np.linalg.norm(np.dot(diff, diff.T), axis=1)
        return score

    def __cosine_distance(self, register_features, query_feature):
        """ Calculate Cosine distance """
        dot = np.dot(query_feature['feature'], np.transpose(register_features))
        # dot = np.dot(register_features, norm_feature)
        return np.ones(shape=dot.shape) - dot

    def __update_register_features(self, unique_id, feature):
        """ Update register features array """

        if self.__next_feature_index > self.__register_features.shape[0] - len(feature):
            self.__register_features = np.concatenate((self.__register_features, np.empty(shape=self.__register_features.shape, dtype=np.float32)))
            self.__register_info = np.concatenate((self.__register_info, np.empty(shape=self.__register_info.shape, dtype=np.int64)))

        for f in feature['feature']:
            self.__register_features[self.__next_feature_index] = f
            self.__register_info[0][self.__next_feature_index] = unique_id
            self.__register_info[1][self.__next_feature_index] = int(time.mktime(time.strptime(feature['time_stamp'], "%Y-%m-%d %H:%M:%S")))
            self.__next_feature_index += 1

    def __get_time_match_index(self, query_time_stamp):
        """ Get register index with time_match_interval """
        time_stamp = int(time.mktime(time.strptime(query_time_stamp, "%Y-%m-%d %H:%M:%S")))
        time_interval = [self.__time_match_interval[0]+time_stamp, self.__time_match_interval[1]+time_stamp]
        index1 = np.where(self.__register_info[1][0:self.__next_feature_index] > min(time_interval))[0].tolist()
        index2 = np.where(self.__register_info[1][0:self.__next_feature_index] < max(time_interval))[0].tolist()
        return [x for x in index1 if x in index2]

    def match(self, query_feature):
        """ Calculate similarity between all features saved and this input feature
        Args:
            arg1 (dict): normalized feature

        Returns:
            int: unique_id of input feature
            float: similarity score
        """
        # get register feature
        if self.__use_time_match is True:
            match_index = self.__get_time_match_index(query_feature['time_stamp'])
        else:
            match_index = range(0, self.__next_feature_index)
        register_features = self.__register_features[match_index]

        # calculate score
        score = self.__dist_method(register_features, query_feature)
        index = np.argsort(score, axis=1)

        # get result
        score_list = []
        unique_id_list = []
        for i in range(0, index.shape[0]):
            score_list.append(score[i][index[i]].tolist())
            unique_id_list.append(self.__register_info[0][match_index][index[i]].tolist())

        return unique_id_list, score_list

    def register(self, feature):
        """ Register feature
        Args:
            arg1 (dict): normalized features

        Returns:
            int: unique_id of input feature
        """

        unique_id = self.__next_unique_number
        self.__next_unique_number += 1

        # update register_features
        self.__update_register_features(unique_id, feature)
        self.__save_feature(unique_id, feature)

        return unique_id
