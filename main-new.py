from demo import pfextractor
import os
from os.path import join, getsize
from scipy.spatial import distance
import pickle
import hnswlib
import numpy as np
def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def save_obj(obj, name):
    with open('../candidate_2018_09_14_1/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
dim=2048
num_elements=200
if __name__ == '__main__':

    extractor = pfextractor('PED_EXT_001.pkl',0)

    cam1_path = '../1_2018-09-14/'
    cam2_path = '../2_2018-09-14/'
    # candidate_path = '../candidate_2018-09-14/'
    candidate_path = '../candidate_2018_09_14_6/'
    cam2_dict = {}
    # num=0
    cam1_image_list = []
    cam2_image_list = []
    data = np.float32(np.random.random((num_elements, dim)))
    # Declaring index
    p = hnswlib.Index(space='l2', dim=dim)  # possible options are l2, cosine or ip
    num=0
    for dirpath, dirnames, filenames in os.walk(cam2_path):
        for f in filenames:
            if num == 100:
                break
            print f
            if '.jpg' in f:
                print(join(dirpath,f))
                cam2_image_list.append(join(dirpath,f))
                num+=1
    print "cam2 images num:"
    print len(cam2_image_list)
    for i in range(0,len(cam2_image_list)):
        s = getsize(cam2_image_list[i])
        fea = extractor.extract(cam2_image_list[i])
        #print(len(fea))
        cam2_dict[cam2_image_list[i]] = fea
        print i
    # parameters can be varied
    p.init_index(max_elements=len(cam2_dict), ef_construction=100, M=32)
    p.set_ef(10)
    p.set_num_threads(4)
    print("Adding first batch of %d elements" % (len(cam2_dict)))
    p.add_items(cam2_dict.values())
    print "finished ext cam2 images features"
    num = 0
    for dirpath, dirnames, filenames in os.walk(cam1_path):
        for f in filenames:
            if num==50:
                break
            print f
            if '.jpg' in f:
                cam1_image_list.append(join(dirpath, f))
            num+=1
    print "cam1 images num:"
    print len(cam1_image_list)

    # compare
    for i in range(0, len(cam1_image_list)):
        print i
        id = cam1_image_list[i].split('/')[-2]
        candidate_path_id = candidate_path + id
        if not os.path.exists(str(candidate_path_id)):
            # if not os.path.exists(id):
            os.system('mkdir ' + candidate_path_id)

        fea = extractor.extract(cam1_image_list[i])
        data=cam2_dict.values().append(fea)
        print(len([fea]))
        p.add_items([fea])
        labels, distances = p.knn_query(data, k=1)
        print(labels)
        print(len(labels))
        print(labels[len(cam2_dict)+i])
            # min_dis = 999
            # min_filename = ''
            # for tempf in cam2_dict:
            #     dist = distance.euclidean(fea, cam2_dict[tempf])
            #     if dist < min_dis:
            #         min_dis = dist
            #         min_filename = tempf
            # # 	save file to cadidate folder
            # print min_filename
            # print candidate_path_id
            # os.system('cp ' + min_filename + ' ' + candidate_path_id + '/')









