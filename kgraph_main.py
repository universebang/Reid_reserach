import pykgraph
import numpy as np
from demo import pfextractor
import os
import timeit
from os.path import join, getsize
from scipy.spatial import distance
import pickle
import torch
import multiprocessing

def load_obj(name):
    with open('../candidate_2018_09_14_1/' + name + '.pkl', 'rb') as f:
        print('../candidate_2018_09_14_1/' + name + '.pkl')
        return pickle.load(f)
def save_obj(obj,name):
    with open('../candidate_2018_09_14_1/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
#extractor = pfextractor('PED_EXT_001.pkl',0)
cam1_path = '../1_2018-09-15/'
cam2_path = '../2_2018-09-15/'
candidate_path = '../candidate_2018_09_15_1/'
cam2_dict = {}
image_batch=3000
#image_batch=10
cam1_image_list = []
cam2_image_list = []
multiprocessing_register=[]
multiprocessing_match=[]
candidate_path_ids=[]
# register_feature={}
# match_feature={}


def extract_register(data_register,count,register_feature,id): #,average_register,register_feature,count_register):

    print("output card:",id)
    #CUDA_VISIBLE_DEVICES = id
    extractor = pfextractor('PED_EXT_001.pkl',id)
    for i in range(0,len(data_register)): #len(data_register)):
        fea = extractor.extract(data_register[i])
        register_feature[data_register[i]] = fea
        del fea
        print("count",count)
    del extractor
    print "finished ext cam2 images features"
def extract_query(data_match,count,match_feature,id):
    print("output card:", id)
    #CUDA_VISIBLE_DEVICES = id
    extractor = pfextractor('PED_EXT_001.pkl', id)
    for i in range(0, len(data_match)):
        fea = extractor.extract(data_match[i])
        match_feature[data_match[i]] = fea
        del fea
        print("count", count)
    print "finished ext cam1 images features"
def main():
    num = 0
    for dirpath, dirnames, filenames in os.walk(cam2_path):
        for f in filenames:
            # if num==100:
            #     break
            print f
            if '.jpg' in f:
                print(join(dirpath, f))
                cam2_image_list.append(join(dirpath, f))
            #num+=1
    print "cam2 images num:"
    print len(cam2_image_list)
    # average_register = len(cam2_image_list) // 4
    #
    # for i in range(4):
    #     if i==3:
    #         multiprocessing_register.append(cam2_image_list[i*average_register:])
    #     else:
    #         multiprocessing_register.append(cam2_image_list[i*average_register:(i+1)*average_register])
    # num = 0
    for dirpath, dirnames, filenames in os.walk(cam1_path):
        for f in filenames:
            # if num==50:
            #     break
            print f
            if '.jpg' in f:
                cam1_image_list.append(join(dirpath, f))
            #num+=1
    print "cam1 images num:"
    print len(cam1_image_list)
    for i in range(len(cam1_image_list)):  # len(cam1_image_list)):
        #print(i)
        id = cam1_image_list[i].split('/')[-2]
        candidate_path_id = candidate_path + id
        # print("mkdir is ",candidate_path_id)
        if not os.path.exists(str(candidate_path_id)):
            os.system('mkdir ' + candidate_path_id)
        candidate_path_ids.append(candidate_path_id)
    #num_match = len(cam1_image_list) // 4
    #num_match = len(cam1_image_list) // image_batch


    #print("batch size is:",num_match)
    # for i in range(4):
    #     if i == 3:
    #         multiprocessing_match.append(cam1_image_list[i * num_match:])
    #     else:
    #         multiprocessing_match.append(cam1_image_list[i * num_match:(i + 1) * num_match])
    # for i in range(num_match):
    #     if i == num_match-1:
    #         multiprocessing_match.append(cam1_image_list[i * num_match:])
    #     else:
    #         multiprocessing_match.append(cam1_image_list[i * num_match:(i + 1) * num_match])
    #register_feature = multiprocessing.Manager().dict()
    #
    #
    tic = timeit.default_timer()
    plist_register = []
    # for count in range(4):
    #     #length=count*average_register
    #     p = multiprocessing.Process(target=extract_register,args=(multiprocessing_register[count],count,register_feature,count)) #,average_register,register_feature,count_register))
    #     p.start()
    #     plist_register.append(p)
    #
    # for p_register in plist_register:
    #     p_register.join()
    register_feature=load_obj("register111")
    print("--------------------",len(register_feature))
    print("register feature is %d" % len(register_feature))
    #save_obj(register_feature,"gallery")
    toc = timeit.default_timer()
    print('register time: %.2f' % ((toc - tic) * 1000))
    tic = timeit.default_timer()
    # match_feature = multiprocessing.Manager().dict()
    # plist_match = []
    # for j in range(4):
    #     p = multiprocessing.Process(target=extract_query, args=(multiprocessing_match[j],j,match_feature,j))  # ,match_feature)) #,average_match,count_match,register_out))
    #     p.start()
    #     plist_match.append(p)
    #
    # for p_match in plist_match:
    #     p_match.join()
    # del plist_match
    # for j in range(0,num_match,4):
    #     print j
    #     plist_match = []
    #     process = num_match - j if (j + 4) > num_match else 4
    #     for i in range(process):
    #         p = multiprocessing.Process(target=extract_query, args=(multiprocessing_match[j+i],i,match_feature,i))  # ,match_feature)) #,average_match,count_match,register_out))
    #         p.start()
    #         plist_match.append(p)
    #
    #     for p_match in plist_match:
    #         p_match.join()
    #     del plist_match
    toc = timeit.default_timer()
    #print(len(match_feature))
    #save_obj(dict(match_feature),"query")
    match_feature=load_obj("query")
    print(type(match_feature))
    print(len(match_feature))
    #print(match_feature1)

    print('match time: %.2f' % ((toc - tic) * 1000))
    print("match feature is %d"%len(match_feature))
    dataset =np.array(register_feature.values())
    print("dataset is {},type is {}".format(len(dataset),type(dataset)))
    query =np.array(match_feature.values())
    print("query is {},type is {}".format(len(query), type(query)))

    index = pykgraph.KGraph(dataset, 'euclidean')  # another option is 'angular'
    index.build(reverse=-1)  #
    #index.save("index_file.txt")
    tic = timeit.default_timer()
    knn = index.search(query, K=1)
    toc = timeit.default_timer()
    print('match time: %.2f' % ((toc - tic) * 1000))
    print('match time: %.2f' % ((toc - tic) * 1000/len(query)))
    print(len(cam2_image_list))
    print(cam1_image_list[0])
    print(len(knn))
    for i,index in enumerate(knn):
        print(i,index[0])
        print('cp ' + cam2_image_list[index[0]] + ' ' +candidate_path+cam1_image_list[i].split('/')[-2]+"/")
        os.system('cp ' + cam2_image_list[index[0]] + ' ' +candidate_path+cam1_image_list[i].split('/')[-2]+"/")
if __name__ == '__main__':
    tic = timeit.default_timer()
    main()
    toc = timeit.default_timer()
    print('all time: %.2f' % ((toc - tic) * 1000))