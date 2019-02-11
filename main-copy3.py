from demo import pfextractor
import os,time
from os.path import join, getsize
from scipy.spatial import distance
import timeit
import json
import shutil
import datetime
import torch
import pickle
from matching_module import MatchingModule
# from multiprocessing import process
import multiprocessing
from data_module import DataModule

#CUDA_VISIBLE_DEVICES=1
cam1_path = '../1_2018-09-15/'
cam2_path = '../2_2018-09-15/'
candidate_path = '../candidate_2018_09_14_7/'
cam2_dict = {}
#image_batch=10
cam1_image_list = []
cam2_image_list = []
multiprocessing_register=[]
multiprocessing_match=[]
# count_register=0
# count_match=0
MM_CONFIG = {
    'feature_dim': 2048,
    'distance_method': 'euclidean',
    'threshold': 999,
    'use_time_match': False,
    'time_match_interval': [-10, -2],
}
cache_dir='../candidate_2018_09_14_6/'
def load_obj(name ):
    with open('../candidate_2018_09_14_1/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
def save_obj(obj,name):
    with open('../candidate_2018_09_14_1/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def extract_register(data_register,count,length,register_feature,id): #,average_register,register_feature,count_register):
	print("output card:",id)
	#CUDA_VISIBLE_DEVICES = id
	extractor = pfextractor('PED_EXT_001.pkl',id)
	for i in range(0,len(data_register)): #len(data_register)):
		fea = extractor.extract(data_register[i])
		one_feature = {}
		one_feature['camera_id'] = data_register[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		register_feature[i+length] = one_feature
		del one_feature
		print("count", count)
	print("finished ext cam2 images features")
def extract_match(data_match,j,register_out,id): #,match_feature): #,average_match,count_match,register_out):
	tic = timeit.default_timer()
	print("output card:",id)
	#print("count----------", count)
	#CUDA_VISIBLE_DEVICES = id
	extractor = pfextractor('PED_EXT_001.pkl',id)
	toc = timeit.default_timer()
	print('all time: %.2f' % ((toc - tic) * 1000))
	print("process are ", j)
	match_feature = {}
	for i in range(0,len(data_match)): #len(data_match)):
		fea = extractor.extract(data_match[i])
		one_feature = {}
		one_feature['camera_id'] = data_match[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		match_feature[i] = one_feature
		del one_feature
	print("------------------",len(match_feature))


	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	tic = timeit.default_timer()
	matching_out = mm.match(match_feature, register=False, rank=5)
	toc = timeit.default_timer()
	print('match------- time: %.2f' % ((toc - tic) * 1000))
	print("per----------time:%.2f"%((toc - tic) * 1000/len(matching_out)))
	mm.free()
	del match_feature
	print('result is----------------',len(matching_out))
    #calculate precisoin
	candidate_path_ids=[]
	for i in range(len(cam1_image_list)):  #len(cam1_image_list)):
		# print(i)
		id = cam1_image_list[i].split('/')[-2]
		candidate_path_id = candidate_path+id
		#print("mkdir is ",candidate_path_id)
		if not os.path.exists(str(candidate_path_id)):
			os.system('mkdir '+candidate_path_id)
		candidate_path_ids.append(candidate_path_id)
	for mkey in matching_out:
		mobject_id = matching_out[mkey]['object_id'][0]
		mcamera_id = matching_out[mkey]['camera_id']
		file_name=mcamera_id.split('/')[2]
		allName=candidate_path+str(file_name)+"/"
		#print('file location is:',allName)
		for rkey in register_out.keys():
			robject_id = register_out[rkey]['object_id'][0]
			rcamera_id = register_out[rkey]['camera_id']
			if robject_id==mobject_id:
				print("----------------find--------------")
				os.system('cp '+rcamera_id+' '+allName)


def main():
	num=0
	for dirpath, dirnames, filenames in os.walk(cam2_path):
		for f in filenames:
			if num==100:
				break
			print(f)
			if '.jpg' in f:
				cam2_image_list.append(join(dirpath,f))
				num+=1
	print("cam2 images num:")
	print(len(cam2_image_list))
	average_register=len(cam2_image_list)//4

	# calculate precisoin
	for i in range(4):
		if i==3:
			multiprocessing_register.append(cam2_image_list[i*average_register:])
		else:
			multiprocessing_register.append(cam2_image_list[i*average_register:(i+1)*average_register])


	num=0
	for dirpath, dirnames, filenames in os.walk(cam1_path):
		for f in filenames:
			if num==50:
				break
			print(f)
			if '.jpg' in f:
				cam1_image_list.append(join(dirpath,f))
				num+=1
	print("cam1 images num:")
	print(len(cam1_image_list))
	#num_match=len(cam1_image_list)//4
	num_match=len(cam1_image_list)//4
	print(num_match)
	for i in range(num_match):
		if i==3:
			multiprocessing_match.append(cam1_image_list[i*num_match:])
		else:
			multiprocessing_match.append(cam1_image_list[i*num_match:(i+1)*num_match])
	register_feature = multiprocessing.Manager().dict()
	tic = timeit.default_timer()
	plist_register = []
	for count in range(4):
		length=count*average_register
		p = multiprocessing.Process(target=extract_register,args=(multiprocessing_register[count],count,length,register_feature,count)) #,average_register,register_feature,count_register))
		p.start()
		plist_register.append(p)

	for p_register in plist_register:
		p_register.join()
	print("--------------------",len(register_feature))

	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	register_out = mm.register(register_feature)
	print(len(register_out))
	#save_obj(register_out,"register_out1")
	mm.free()
	toc = timeit.default_timer()
	print('register time: %.2f' % ((toc - tic) * 1000))

	#register_out=load_obj("register_out2")
	print("1111111111111111111111")
	tic = timeit.default_timer()

	print(num_match)
	# for j in range(0,num_match,4):
	# 	plist_match = []
	# 	process=num_match-j if (j+3)>num_match else 4
	# 	for count in range(process):
	# 		print(j+count)
	# 		p = multiprocessing.Process(target=extract_match,args=(multiprocessing_match[j+count],lock,count,register_out,count%3+1)) #,match_feature)) #,average_match,count_match,register_out))
	# 		p.start()
	# 		plist_match.append(p)
	#
	# 	for p_match in plist_match:
	# 		p_match.join()
	# 	del plist_match
	plist_match = []
	for j in range(4):
		p = multiprocessing.Process(target=extract_match,args=(multiprocessing_match[j],j,register_out,j)) #,match_feature)) #,average_match,count_match,register_out))
		p.start()
		plist_match.append(p)
	for p_match in plist_match:
		p_match.join()
	del plist_match
	toc = timeit.default_timer()
	print('match time: %.2f' % ((toc - tic) * 1000))

	# match_result=[]
	# for i in range(5):
	# 	if i==4:


if __name__ == '__main__':

	lock = multiprocessing.Lock()
	tic = timeit.default_timer()
	main()
	toc = timeit.default_timer()
	print('all time: %.2f'%((toc - tic) * 1000))
