from demo import pfextractor
import os, time
import multiprocessing
from os.path import join, getsize
from scipy.spatial import distance
import timeit
import json
import shutil
import datetime
from matching_module import MatchingModule

#extractor = pfextractor('PED_EXT_001.pkl')
cam1_path = '../1_2018-09-14/'
cam2_path = '../2_2018-09-14/'
# candidate_path = '../candidate_2018-09-14/'
candidate_path = '../candidate_2018_09_14_3/'
cam2_dict = {}
cam1_image_list = []
cam2_image_list = []
multiprocessing_register = []
multiprocessing_match = []
lock = multiprocessing.Lock()
# count_register=0
# count_match=0
MM_CONFIG = {
    'cache_dir': '../candidate_2018_09_14_2/',
    'feature_dim': 2048,
    'distance_method': 'euclidean',
    'threshold': 999,
    'use_time_match': False,
    'time_match_interval': [-10, -2],
}


# MM_CONFIG = {
#     'cache_dir': '../candidate_2018_09_14_2/',
#     'feature_dim': 2048,
#     'distance_method': 'cosine',
#     'threshold': 999,
#     'use_time_match': False,
#     'time_match_interval': [-10, -2],
# }
def extract_register(data_register, lock, average_register, register_feature, count_register):
    lock.acquire()
    #global extractor
    # global register_feature
    extractor = pfextractor('PED_EXT_001.pkl')
    for i in range(0, len(data_register)):
        s = getsize(data_register[i])
        # try:
        fea = extractor.extract(data_register[i])
        one_feature = {}
        one_feature['camera_id'] = data_register[i]
        one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        one_feature['feature'] = [fea]
        register_feature[i + count_register.value] = one_feature
    # register_feature[i] = one_feature
    # print(i)
    # print i+count_register
    print len(register_feature)
    count_register.value += average_register.value
    print count_register
    # except:
    # 	continue
    print("finished ext cam2 images features")
    # register
    lock.release()


def extract_match(data_match, lock, average_match, match_feature, count_match, register_out):
    # lock.acquire()
    # global count_match
    #global extractor
    extractor = pfextractor('PED_EXT_001.pkl')
    for i in range(0, len(data_match)):
        s = getsize(data_match[i])
        # try:
        fea = extractor.extract(data_match[i])
        one_feature = {}
        one_feature['camera_id'] = data_match[i]
        one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        one_feature['feature'] = [fea]
        # match_feature[i+count_match.value] = one_feature
        match_feature[i] = one_feature
        print(i)
    # 	print(average_match.value)
    # 	print i+count_match.value
    # count_match.value +=average_match.value
    print("2222222222222222222222222222222222222222222", len(match_feature))
    # print count_match.value
    # except:
    # continue
    print("finished ext cam1 images features")
    # parse matching feature

    # matching
    mm = MatchingModule(MM_CONFIG)
    matching_out = mm.match(match_feature, register=False, rank=5)
    # with open('register_out.json', 'w') as file:
    #     json.dump(register_out, file, indent=4)
    # json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')
    # with open('matching_out.json', 'w') as file:
    #     json.dump(matching_out, file, indent=4)

    # calculate precisoin
    candidate_path_ids = []
    for i in range(0, len(cam1_image_list)):
        print(i)
        id = cam1_image_list[i].split('/')[-2]
        candidate_path_id = candidate_path + id
        if not os.path.exists(str(candidate_path_id)):
            os.system('mkdir ' + candidate_path_id)
        candidate_path_ids.append(candidate_path_id)
    # precision = 0
    # feature_num = 0
    print("------------------------------------------")
    print(candidate_path_ids)
    for mkey in matching_out:
        try:
            mobject_id = matching_out[mkey]['object_id'][0]
            mcamera_id = matching_out[mkey]['camera_id']
            print(mobject_id)
            print(mcamera_id)
            print(len(register_out))
            for rkey in register_out.keys():
                robject_id = register_out[rkey]['object_id'][0]
                rcamera_id = register_out[rkey]['camera_id']
                print("111111111111111111111111111111111")
                print(robject_id)
                print(rcamera_id)
                if robject_id == mobject_id:
                    print("find-------------")
                    os.system('cp ' + rcamera_id + ' ' + candidate_path_ids[mobject_id - 1] + '/')
                    break
        except:
            continue
    # print 'rank=', len(matching_out[mkey]['object_id']), len(matching_out[mkey]['score'])

    # print 'matched_id=', mobject_id, ', register_id=', robject_id, ',score=', matching_out[mkey]['score'][0]
    # precision += 1 if mobject_id == robject_id else 0
    # feature_num += 1
    # print 'precision =', precision * 100.0 / feature_num, '%'
    mm.free()


# lock.release()


def main():
    num = 0
    for dirpath, dirnames, filenames in os.walk(cam2_path):
        for f in filenames:
            if num == 100:
                break
            print(f)
            if '.jpg' in f:
                cam2_image_list.append(join(dirpath, f))
                num += 1
    print("cam2 images num:")
    print(len(cam2_image_list))
    average_register = len(cam2_image_list) // 5
    for i in range(0, 5):
        if i == 4:
            multiprocessing_register.append(cam2_image_list[i * average_register:])
        else:
            multiprocessing_register.append(cam2_image_list[i * average_register:(i + 1) * average_register])

    num = 0
    for dirpath, dirnames, filenames in os.walk(cam1_path):
        for f in filenames:
            if num == 50:
                break
            print(f)
            if '.jpg' in f:
                cam1_image_list.append(join(dirpath, f))
                num += 1
    print("cam1 images num:")
    print(len(cam1_image_list))
    average_match = len(cam1_image_list) // 5

    for i in range(0, 5):
        if i == 4:
            multiprocessing_match.append(cam1_image_list[i * average_match:])
        else:
            multiprocessing_match.append(cam1_image_list[i * average_match:(i + 1) * average_match])

    # print multiprocessing_match[0]
    # print len(multiprocessing_match[0])
    # print multiprocessing_match[1]
    # print len(multiprocessing_match[1])
    # print multiprocessing_match[2]
    # print len(multiprocessing_match[2])
    # print multiprocessing_match[3]
    # print len(multiprocessing_match[3])
    # print multiprocessing_match[4]
    # print len(multiprocessing_match[4])
    # exit(1)

    plist_register = []

    # with multiprocessing.Manager() as MG:
    tic = timeit.default_timer()

    register_feature = multiprocessing.Manager().dict()
    average_register = multiprocessing.Value("d", average_register)
    count_register = multiprocessing.Value("d", 0)
    pool = multiprocessing.Pool(processes=5)
    register_pool = []
    for count in range(5):
        #print type(multiprocessing_register[count])
        # print len(multiprocessing_register[i][0])
        # print len(multiprocessing_register[i])
        # p = multiprocessing.Process(target=extract_register,args=(multiprocessing_register[i],lock))
        # p = multiprocessing.Process(target=extract_register, args=(
        # multiprocessing_register[count], lock, average_register, register_feature, count_register))
        # p.start()
        # plist_register.append(p)
        register_pool.append(pool.apply_async(extract_register, (multiprocessing_register[count], lock, average_register, register_feature, count_register)))
    # for p_register in plist_register:
    #     p_register.join()
    pool.close()
    pool.join()
    # if register_pool.successful():
    #     print 'successful'
    print("--------------------", len(register_feature))

    mm = MatchingModule(MM_CONFIG)
    register_out = mm.register(register_feature)
    mm.free()

    toc = timeit.default_timer()
    print('register time: %.2f' % ((toc - tic) * 1000))

    tic = timeit.default_timer()
    plist_match = []
    # lock_match = multiprocessing.Lock()
    match_feature = multiprocessing.Manager().dict()
    average_match = multiprocessing.Value("d", average_match)
    count_match = multiprocessing.Value("d", 0)

    for j in range(5):
        # p = multiprocessing.Process(target=extract_match,args=(multiprocessing_match[i],lock))
        print type(multiprocessing_match[j])
        print len(multiprocessing_match[j])
        p = multiprocessing.Process(target=extract_match, args=(
        multiprocessing_match[j], lock, average_match, match_feature, count_match, register_out))
        p.start()
        plist_match.append(p)
    for p_match in plist_match:
        p_match.join()
    toc = timeit.default_timer()
    print('match time: %.2f' % ((toc - tic) * 1000))


# print("--------------------", len(match_feature))
# extract_register()
# extract_match()
#
# lock = multiprocessing.Lock()
# for j in range(5):
#     p = multiprocessing.Process(target=extract_register,args=('process',lock))
#     p.start()
#     plist.append(p)
# p.join()

# plist1 = []
# lock1 = multiprocessing.Lock()
# for j in range(5):
#     p = multiprocessing.Process(target=extract_match,args=('process',lock1))
#     p.start()
#     plist1.append(p)
# p.join()
if __name__ == '__main__':
    # try:
    #     shutil.rmtree(MM_CONFIG['cache_dir'])
    # except OSError:
    #     print MM_CONFIG['cache_dir'], 'not exists'
    tic = timeit.default_timer()
    main()
    toc = timeit.default_timer()
    print('all time: %.2f' % ((toc - tic) * 1000))
