#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
from matching_feature import FeatureModule
from matching_feature import mkdirs


class MatchingModule:
    """ Matching Module

    Attributes:
        get_matching_table: return matching table
        update: input feature to update matching table
        free: release memory

    Examples:
    >>>mm = MatchingModule(configure)
    >>>mm.update(input_feature)
    >>>mm.free()

    """

    def __init__(self, mm_configure):
        """ Init Matching Module with configure

        Args:
            arg1 (dict): feature config
        """

        self.__config = mm_configure
        self.__config['register_dir'] = mm_configure['cache_dir'] + '/register/'
        self.__feature = FeatureModule(self.__config)

        self.__matching_dir = mm_configure['cache_dir'] + '/matching/'
        mkdirs(self.__matching_dir)
        json_list = os.listdir(self.__matching_dir)
        self.__save_index = len(json_list) + 1

    def free(self):
        """ Release memory """
        self.__feature.free()
        # print('matching module free')

    def version(self):
        return "V1.4.0"

    def __save_matching_feature(self, feature):
        """ Save matching feature """
        json_file = self.__matching_dir + str(self.__save_index) + '.json'
        with open(json_file, 'w') as file:
            json.dump(feature, file)
        self.__save_index += 1

    def match(self, matching_feature, register=True, rank=1):
        """ Process matching process

        Args:
            arg1 (dict): matching features
            register (bool): if not matched register feature or not
            rank (int): 0 and -1 for all return

        Returns:
            dict: delete feature list in matching_feature, add object_id and score
        """

        ret_dict = {}
        # process every input feature
        for key in matching_feature.keys():
            feature = matching_feature[key]
            norms = np.linalg.norm(feature['feature'], axis=1)
            feature['feature'] = (feature['feature'] /
                                  np.reshape(norms, (len(feature['feature']), 1))).tolist()
            unique_id, score = self.__feature.match(feature)
            # parse matching result
            average_unique_id = np.mean(unique_id, axis=0)
            average_score = np.mean(score, axis=0)
            index1 = np.where(average_score < self.__config['threshold'])[0].tolist()
            index2 = np.where(average_unique_id == unique_id[0])[0].tolist()
            index = [x for x in index1 if x in index2]
            # matched or not
            if len(index) > 0:
                ret_rank = len(index)
                if rank is not 0 or rank is not -1:
                    ret_rank = rank
                feature['object_id'] = average_unique_id[index].astype(np.int).tolist()[0:ret_rank]
                feature['score'] = average_score[index].tolist()[0:ret_rank]
            elif register is True:
                unique_id = self.__feature.register(feature)
                feature['object_id'] = [unique_id]
                feature['score'] = [None]
            else:
                feature['object_id'] = [-1]
                feature['score'] = [0.0]
            # save matching feature
            self.__save_matching_feature(feature)
            # get return result
            del feature['feature']
            ret_dict[key] = feature
        return ret_dict

    def register(self, register_feature):
        """ Process register process

        Args:
            arg1 (dict): register features

        Returns:
            dict: delete feature list in matching_feature, add object_id and score
        """
        ret_dict = {}
        # process every input feature
        for key in register_feature.keys():
            feature = register_feature[key]
            norms = np.linalg.norm(feature['feature'], axis=1)
            feature['feature'] = (feature['feature'] /
                                  np.reshape(norms, (len(feature['feature']), 1))).tolist()
            unique_id = self.__feature.register(feature)
            del feature['feature']
            feature['object_id'] = [unique_id]
            feature['score'] = [None]
            ret_dict[key] = feature

        return ret_dict
