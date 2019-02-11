from demo import pfextractor
import os,time
import multiprocessing
from os.path import join, getsize
from scipy.spatial import distance
import timeit
import json
import shutil
import datetime
from matching_module import MatchingModule
from data_module import DataModule

extractor = pfextractor('PED_EXT_001.pkl',0)
cam1_path = '../1_2018-09-15/'
cam2_path = '../2_2018-09-15/'
#candidate_path = '../candidate_2018-09-14/'
candidate_path = '../candidate_2018_09_14_7/'
cam2_dict = {}
cam1_image_list = []
cam2_image_list = []
register_feature = {}
match_feature={}
multiprocessing_register=[]
multiprocessing_match=[]
MM_CONFIG = {
    'feature_dim': 2048,
    'distance_method': 'euclidean',
    'threshold': 999,
    'use_time_match': False,
    'time_match_interval': [-10, -2],
}
cache_dir='../candidate_2018_09_14_2/'
# MM_CONFIG = {
#     'cache_dir': '../candidate_2018_09_14_2/',
#     'feature_dim': 2048,
#     'distance_method': 'cosine',
#     'threshold': 999,
#     'use_time_match': False,
#     'time_match_interval': [-10, -2],
# }
def extract_register():
	for i in range(0,len(cam2_image_list)):
		s = getsize(cam2_image_list[i])
    	#try:
		fea = extractor.extract(cam2_image_list[i])
		one_feature = {}
		one_feature['camera_id'] = cam2_image_list[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		register_feature[i] = one_feature
		print i
		# except:
		# 	continue
	print "finished ext cam2 images features"
def extract_match():
	for i in range(0,len(cam1_image_list)):
		s = getsize(cam1_image_list[i])
    	#try:
		fea = extractor.extract(cam1_image_list[i])
		one_feature = {}
		one_feature['camera_id'] = cam1_image_list[i]
		one_feature['time_stamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		one_feature['feature'] = [fea]
		match_feature[i] = one_feature
		print i
		#except:
			#continue
	print "finished ext cam1 images features"
    # parse matching feature

    # register
	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	register_out = mm.register(register_feature)
	mm.free()
    # matching
	dm = DataModule(cache_dir)
	mm = MatchingModule(MM_CONFIG,dm)
	tic = timeit.default_timer()
	matching_out = mm.match(match_feature, register=False, rank=5)
	toc = timeit.default_timer()
	print('match time: %.2f' % ((toc - tic) * 1000))
	print('match time: %.2f' % ((toc - tic) * 1000 / len(matching_out)))
    # with open('register_out.json', 'w') as file:
    #     json.dump(register_out, file, indent=4)
    # json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')
    # with open('matching_out.json', 'w') as file:
    #     json.dump(matching_out, file, indent=4)

    # calculate precisoin
	candidate_path_ids=[]
	for i in range(0,len(cam1_image_list)):
		print i
		id = cam1_image_list[i].split('/')[-2]
		candidate_path_id = candidate_path+id
		if not os.path.exists(str(candidate_path_id)):
			os.system('mkdir '+candidate_path_id)
		candidate_path_ids.append(candidate_path_id)
	# precision = 0
	# feature_num = 0
	print "------------------------------------------"
	print candidate_path_ids
	for mkey in matching_out.keys():
		try:
			mobject_id = matching_out[mkey]['object_id'][0]
			mcamera_id = matching_out[mkey]['camera_id']
			file_name = mcamera_id.split('/')[2]
			allName = ''
			allName = candidate_path + str(file_name) + "/"
			print('file location is:', allName)
			print mobject_id
			print mcamera_id
			for rkey in register_out.keys():
				robject_id = register_out[rkey]['object_id'][0]
				rcamera_id = register_out[rkey]['camera_id']
				print robject_id
				print rcamera_id
				if robject_id==mobject_id:
					print "find-------------"
					os.system('cp '+rcamera_id+' '+allName)
					break
		except:
			continue
        # print 'rank=', len(matching_out[mkey]['object_id']), len(matching_out[mkey]['score'])
        
        #print 'matched_id=', mobject_id, ', register_id=', robject_id, ',score=', matching_out[mkey]['score'][0]
        # precision += 1 if mobject_id == robject_id else 0
        # feature_num += 1
    #print 'precision =', precision * 100.0 / feature_num, '%'
	mm.free()
def main():
	num=0
	for dirpath, dirnames, filenames in os.walk(cam2_path):
		for f in filenames:
			if num==100:
				break
			print f 
			if '.jpg' in f:
				cam2_image_list.append(join(dirpath,f))
				num+=1
	print "cam2 images num:"
	print len(cam2_image_list)
	# average=cam2_image_list//5
	# for i in range(0,5):
	# 	if i==4:
	# 		multiprocessing_register.append(cam2_image_list[i*average:])
	# 	else:
	# 		multiprocessing_register.append(cam2_image_list[i*average:(i+1)*average])
	#
	num=0
	for dirpath, dirnames, filenames in os.walk(cam1_path):
		for f in filenames:
			if num==50:
				break
			print f
			if '.jpg' in f:
				cam1_image_list.append(join(dirpath,f))
				num+=1
	print "cam1 images num:"
	print len(cam1_image_list)
	extract_register()
	extract_match()
	# plist = []
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
