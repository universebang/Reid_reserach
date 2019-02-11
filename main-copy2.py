from demo import pfextractor
import os,time
from os.path import join, getsize
from scipy.spatial import distance
import timeit
import json
import shutil
import datetime
import torch
from matching_module import MatchingModule
# from multiprocessing import process
import multiprocessing
from data_module import DataModule

#extractor = pfextractor('PED_EXT_001.pkl')
cam1_path = '../1_2018-09-14/'
cam2_path = '../2_2018-09-14/'
#candidate_path = '../candidate_2018-09-14/'
candidate_path = '../candidate_2018_09_14_6/'
cam2_dict = {}
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
#@profile
def extract_register(data_register,lock,count,length,register_feature,id): #,average_register,register_feature,count_register):

	# lock.acquire()
	#global register_feature

	#register_feature = {}
	print("output card:",id)
	# id="cuda:"+str(id)
	# print("output card:", id)
	CUDA_VISIBLE_DEVICES = id
	extractor = pfextractor('PED_EXT_001.pkl',id)
	for i in range(0,len(data_register)): #len(data_register)):
		# s = getsize(data_register[i])
    	#try:
		fea = extractor.extract(data_register[i])
		one_feature = {}
		one_feature['camera_id'] = data_register[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		#lock.acquire()
		register_feature[i+length] = one_feature
		del one_feature
		print("count",count)
		#lock.release()

	# count_register.value+=average_register.value
	#print('-----------count',count, len(register_feature), register_feature[0], register_feature[1])

	print("finished ext cam2 images features")
	# register
	# lock.release()
#@profile
def extract_match(data_match,lock,j,length, register_out,id): #,match_feature): #,average_match,count_match,register_out):
	#lock.acquire()
	#global count_match
	#lock.acquire()
	tic = timeit.default_timer()
	print("output card:",id)
	#print(torch.cuda.current_device())
	CUDA_VISIBLE_DEVICES = id
	#torch.cuda.set_device(id)
	extractor = pfextractor('PED_EXT_001.pkl',id)
	toc = timeit.default_timer()
	print('all time: %.2f' % ((toc - tic) * 1000))
	print("process are ", j)
	#lock.release()
	match_feature = {}
	for i in range(0,len(data_match)): #len(data_match)):
		# s = getsize(data_match[i])
    	#try:
		fea = extractor.extract(data_match[i])
		one_feature = {}
		one_feature['camera_id'] = data_match[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		#match_feature[i+count_match.value] = one_feature
		match_feature[i] = one_feature
		del one_feature
	#print("process is ",j)
	# print("finished ext cam1 images features")
	# print("finished ext cam1 images features")
	# for ii in range(len(match_feature)):
	# 	print(j,len(match_feature), match_feature[ii])

    # matching
	print("------------------",len(match_feature))

	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	matching_out = mm.match(match_feature, register=False, rank=5)
	mm.free()
	del match_feature
	print('result is----------------',len(matching_out))
    #calculate precisoin
	candidate_path_ids=[]
	for i in range(len(cam1_image_list)):  #len(cam1_image_list)):
		# print(i)
		id = cam1_image_list[i].split('/')[-2]
		candidate_path_id = candidate_path+id
		print("mkdir is ",candidate_path_id)
		if not os.path.exists(str(candidate_path_id)):
			os.system('mkdir '+candidate_path_id)
		candidate_path_ids.append(candidate_path_id)
	# print candidate_path_ids
	# print("wenjian list is",len(candidate_path_ids))
	# print( "------------------------------------------")
	for mkey in matching_out:
		# try:
		mobject_id = matching_out[mkey]['object_id'][0]
		mcamera_id = matching_out[mkey]['camera_id']
		file_name=mcamera_id.split('/')[2]
		allName=''
		allName=candidate_path+str(file_name)+"/"
		print('file location is:',allName)
		# print(len(register_out))
		for rkey in register_out.keys():
			robject_id = register_out[rkey]['object_id'][0]
			rcamera_id = register_out[rkey]['camera_id']

			print(robject_id)
			print(rcamera_id)
			if robject_id==mobject_id:
				print("find-------------")
				print mobject_id
				print
				#print('cp ' + rcamera_id + ' ' + allName)
				os.system('cp '+rcamera_id+' '+allName)

				# break
		# except:
		# 	print('---ERROR---')
		# 	continue
	#lock.release()


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
	average_match=len(cam1_image_list)//4

	for i in range(4):
		if i==3:
			multiprocessing_match.append(cam1_image_list[i*average_match:])
		else:
			multiprocessing_match.append(cam1_image_list[i*average_match:(i+1)*average_match])

	plist_register = []
	tic = timeit.default_timer()


	register_feature = multiprocessing.Manager().dict()
	# average_register = multiprocessing.Value("d", average_register)
	# count_register=multiprocessing.Value("d", 0)

	for count in range(4):
		length=count*average_register

		p = multiprocessing.Process(target=extract_register,args=(multiprocessing_register[count],lock,count,length,register_feature,count)) #,average_register,register_feature,count_register))
		p.start()
		plist_register.append(p)

	for p_register in plist_register:
		p_register.join()



	print("--------------------",len(register_feature))

	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	register_out = mm.register(register_feature)
	mm.free()
	toc = timeit.default_timer()
	print('register time: %.2f' % ((toc - tic) * 1000))

	tic = timeit.default_timer()
	plist_match = []

	for j in range(4):
		length=j*average_match
		p = multiprocessing.Process(target=extract_match,args=(multiprocessing_match[j],lock,j,length,register_out,j)) #,match_feature)) #,average_match,count_match,register_out))
		p.start()
		plist_match.append(p)

	for p_match in plist_match:
		p_match.join()

	toc = timeit.default_timer()
	print('match time: %.2f' % ((toc - tic) * 1000))


if __name__ == '__main__':

	lock = multiprocessing.Lock()
	tic = timeit.default_timer()
	main()
	toc = timeit.default_timer()
	print('all time: %.2f'%((toc - tic) * 1000))
