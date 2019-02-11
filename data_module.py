import os
import json


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


class DataModule(object):
    def __init__(self, main_dir):
        self.__main_dir = main_dir
        self.__register_dir = main_dir + '/register/'
        self.__matching_dir = main_dir + '/matching/'
        self.__save_matching_index = 0
        mkdirs(self.__register_dir)
        mkdirs(self.__matching_dir)

    def __load_one_register(self, json_file):
        """ Load one object feature to list """
        try:
            with open(json_file, 'r') as file:
                feature_list = json.load(file)
        except(IOError, ValueError):
            feature_list = []
        return feature_list

    def save_one_register(self, unique_id, feature):
        """ Save one object feature to file """
        json_file = self.__register_dir + str(unique_id) + '.json'
        feature_list = self.__load_one_register(json_file)

        feature_list.append(feature)
        with open(json_file, 'w') as file:
            json.dump(feature_list, file)

    def load_all_register(self):
        """ Load all object features """
        json_list = os.listdir(self.__register_dir)
        feature_list = []
        unique_id_list = []
        for json_file in json_list:
            unique_id, ext = os.path.splitext(json_file)
            if ext != '.json':
                continue
            feature = self.__load_one_register(self.__register_dir + json_file)
            for f in feature:
                feature_list.append(f)
                unique_id_list.append(int(unique_id))
        return feature_list, unique_id_list

    def save_one_matching(self, feature):
        """ Save matching object """
        json_file = self.__matching_dir + str(self.__save_matching_index) + '.json'
        with open(json_file, 'w') as file:
            json.dump(feature, file)
        self.__save_matching_index += 1
