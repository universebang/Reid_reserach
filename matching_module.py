#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
from matching_feature import FeatureModule


class MatchingModule(object):
    """ Matching Module

    Attributes:
        get_matching_table: return matching table
        update: input feature to update matching table
        free: release memory

    Examples:
    >>>mm = MatchingModule(configure)
    >>>mm.register(input_feature)
    >>>mm.matching(input__feature, register=True, rank=1)
    >>>mm.free()

    """

    def __init__(self, configure, data_module):
        """ Init Matching Module with configure

        Args:
            arg1 (dict): feature config
        """

        self.__threshold = configure['threshold']
        self.__data_module = data_module
        self.__feature = FeatureModule(configure, data_module)#error

    def free(self):
        """ Release memory """
        self.__feature.free()
        # print('matching module free')

    def version(self):
        return "V1.4.3"

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
            unique_id, score = self.__feature.match(feature)#error
            # parse matching result
            score_tmp = filter(lambda x: x < self.__threshold, score)
            # matched or not
            if len(score_tmp) > 0:
                ret_rank = len(score_tmp)
                if rank is not 0 and rank is not -1:
                    ret_rank = rank
                feature['object_id'] = unique_id[0:ret_rank]
                feature['score'] = score[0:ret_rank]
            elif register is True:
                unique_id = self.__feature.register(feature)#error
                feature['object_id'] = [unique_id]
                feature['score'] = [None]
            else:
                feature['object_id'] = [-1]
                feature['score'] = [0.0]
            # save matching feature
            self.__data_module.save_one_matching(feature)
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
