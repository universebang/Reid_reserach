#!/usr/bin/python2
# -*- coding: utf-8 -*-

import time
import numpy as np


class FeatureModule(object):
    """ get the unique index of input feature, use feature only compare or hash transform

    Examples:
    >>>ft = FeatureModule(configure)
    >>>ft.register(input_feature)
    >>>ft.matching(input_feature)
    >>>ft.free()
    """
    def __init__(self, configure, data_module):
        """ Init Feature Module with configure

        Args:
            arg1 (dict): configure
                         @distance_method: only support eculidean distance and cosine distance
                         @feature_dim: feature dimention
                         @use_time_match: use time information
                         @time_match_interval: time match information
            arg2 (DataModule): data_module

        Raises:
            ValueError: Distance method not supported
        """

        self.__feature_dim = configure['feature_dim']
        self.__data_module = data_module

        # time match
        self.__use_time_match = configure['use_time_match'] if 'use_time_match' in configure.keys() else False
        self.__time_match_interval = configure['time_match_interval'] if 'time_match_interval' in configure.keys() else [-100, -10]

        # register info
        self.__next_unique_number = 1
        self.__next_feature_index = 0
        # 第一行为unique_id，第二行为time_stamp，每一列代表一个目标
        self.__register_info = np.empty(shape=[2, 1000], dtype=np.int64)
        self.__register_features = np.empty(shape=[1000, self.__feature_dim], dtype=np.float32)

        # init distance function and compare function
        if (configure['distance_method'] == 'cosine'):
            self.__dist_method = self.__cosine_distance
        elif (configure['distance_method'] == 'euclidean'):
            self.__dist_method = self.__euclidean_distance
        else:
            raise ValueError('Distance method %s Not supported' % configure['distance_method'])

        # read all register info to feature_list
        feature_list, unique_id_list = self.__data_module.load_all_register()
        for i, f in enumerate(feature_list):
            self.__update_register_features(unique_id_list[i], f)

        if self.__next_feature_index > 0:
            self.__next_unique_number = np.max(self.__register_info[0][0:self.__next_feature_index]) + 1

    def free(self):
        """ Release memory """
        self.__register_info = None
        self.__register_features = None
        # print('feature module free')

    def __euclidean_distance(self, register_features, query_feature):
        """ Calculate Euclidean distance """
        average_part = register_features.shape[0] // 10
        score = np.empty(shape=[len(query_feature['feature']), register_features.shape[0]], dtype=np.float32)
        for index, feature in enumerate(query_feature['feature']):
            mylist = []
            for count in range(10):
                if count==9:
                    register_features_part = register_features[count * average_part:, :]
                else:
                    register_features_part=register_features[count*average_part:(count+1)*average_part,:]
                ff = np.tile(feature, register_features_part.shape[0])
                ff = np.reshape(ff, (register_features_part.shape[0], register_features.shape[1]))
                diff = register_features_part - ff
                mylist.extend(np.linalg.norm(np.dot(diff, diff.T), axis=1))
            score[index]=mylist
            del mylist
        return score

    # def __euclidean_distance(self, register_features, query_feature):
    #     """ Calculate Euclidean distance """
    #     score = np.empty(shape=[len(query_feature['feature']), register_features.shape[0]], dtype=np.float32)
    #     for index, feature in enumerate(query_feature['feature']):
    #         ff = np.tile(feature, register_features.shape[0])
    #         ff = np.reshape(ff, (register_features.shape[0], register_features.shape[1]))
    #         diff = register_features - ff
    #         score[index] = np.linalg.norm(np.dot(diff, diff.T), axis=1)
    #     return score
    def __cosine_distance(self, register_features, query_feature):
        """ Calculate Cosine distance """
        dot = np.dot(query_feature['feature'], np.transpose(register_features))
        # dot = np.dot(register_features, norm_feature)
        return np.ones(shape=dot.shape) - dot

    def __update_register_features(self, unique_id, feature):
        """ Update register features array """

        if self.__next_feature_index > self.__register_features.shape[0] - len(feature['feature']):
            self.__register_features = np.concatenate((self.__register_features, np.empty(shape=self.__register_features.shape, dtype=np.float32)))
            self.__register_info = np.concatenate((self.__register_info, np.empty(shape=self.__register_info.shape, dtype=np.int64)), axis=1)

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
        score = np.mean(self.__dist_method(register_features, query_feature), axis=0)
        index = np.argsort(score)

        return self.__register_info[0][match_index][index].tolist(), score[index].tolist()

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
        self.__data_module.save_one_register(unique_id, feature)

        return unique_id
