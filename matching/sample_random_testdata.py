#!/usr/bin/python2
# -*- coding: utf-8 -*-

import timeit
import json
import shutil
import datetime

from matching.matching_module import MatchingModule

# For test data generate by get_test_data.py
# A suitable max_threshold=3 for euclidean distance
# A suitable max_threshold=0.3 for cosine distance


MM_CONFIG = {
    'cache_dir': './tmpdir',
    'feature_dim': 512,
    'distance_method': 'cosine',
    'threshold': 0.3,
    'use_time_match': False,
    'time_match_interval': [-10, -2],
}


def main():
    with open('register.json', 'r') as file:
        register = json.load(file)
    with open('matching.json', 'r') as file:
        matching = json.load(file)

    # parse register feature
    count = 0
    register_feature = {}
    register_feature_number = 0
    for key in register.keys():
        for f in register[key]:
            one_feature = {}
            one_feature['camera_id'] = int(key)
            one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            one_feature['feature'] = [f]
            register_feature[count] = one_feature
            register_feature_number += len(one_feature['feature'])
            if MM_CONFIG['use_time_match'] is True:
                print 'skiptime', count, timeit.timeit('"-".join(str(n) for n in range(500))', number=3000)
            count += 1
            break

    # parse matching feature
    matching_feature = {}
    matching_feature_number = 0
    for key in matching.keys():
        for f in matching[key]:
            one_feature = {}
            one_feature['camera_id'] = int(key)
            one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            one_feature['feature'] = [f, f]
            matching_feature[count] = one_feature
            matching_feature_number += len(one_feature['feature'])
            count += 1

    # register
    mm = MatchingModule(MM_CONFIG)
    tic = timeit.default_timer()
    register_out = mm.register(register_feature)
    toc = timeit.default_timer()
    print('average register time: %.2f msec / %d features register(%d unique person)' %
          ((toc - tic)*1000 / register_feature_number, register_feature_number, len(register_feature)))
    mm.free()

    # matching
    mm = MatchingModule(MM_CONFIG)
    tic = timeit.default_timer()
    matching_out = mm.match(matching_feature, register=False, rank=5)
    toc = timeit.default_timer()
    print('average match time: %.2f msec / %d features matching(%d unique person)\n' %
          ((toc - tic)*1000 / matching_feature_number, matching_feature_number, len(matching_feature)))

    with open('register_out.json', 'w') as file:
        json.dump(register_out, file, indent=4)
    json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')
    with open('matching_out.json', 'w') as file:
        json.dump(matching_out, file, indent=4)

    # calculate precisoin
    precision = 0
    feature_num = 0
    for mkey in matching_out.keys():
        # print 'rank=', len(matching_out[mkey]['object_id']), len(matching_out[mkey]['score'])
        mobject_id = matching_out[mkey]['object_id'][0]
        mcamera_id = matching_out[mkey]['camera_id']
        for rkey in register_out.keys():
            if register_out[rkey]['camera_id'] == mcamera_id:
                robject_id = register_out[rkey]['object_id'][0]
                break
        print 'matched_id=', mobject_id, ', register_id=', robject_id, ',score=', matching_out[mkey]['score'][0]
        precision += 1 if mobject_id == robject_id else 0
        feature_num += 1
    print 'precision =', precision * 100.0 / feature_num, '%'

    mm.free()


if __name__ == '__main__':
    try:
        shutil.rmtree(MM_CONFIG['cache_dir'])
    except OSError:
        print MM_CONFIG['cache_dir'], 'not exists'
    main()
