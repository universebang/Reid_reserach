from demo import pfextractor
import os
import timeit
from os.path import join, getsize
from scipy.spatial import distance
import pickle

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
def save_obj(obj,name):
    with open('../candidate_2018_09_14_1/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	tic = timeit.default_timer()
	extractor = pfextractor('PED_EXT_001.pkl',0)

	cam1_path = '../1_2018-09-15_test/'
	cam2_path = '../2_2018-09-15_test/'
	#candidate_path = '../candidate_2018-09-14/'
	candidate_path = '../candidate_2018_09_15_5/'
	cam2_dict = {}
	#num=0
	cam1_image_list = []
	cam2_image_list = []
	num=0
	for dirpath, dirnames, filenames in os.walk(cam2_path):
		for f in filenames:
			# if num==1000:
			# 	break
			print f 
			if '.jpg' in f:
				print(join(dirpath,f))
				cam2_image_list.append(join(dirpath,f))
				#num+=1
	print "cam2 images num:"
	print len(cam2_image_list)

	for i in range(0,len(cam2_image_list)):
		s = getsize(cam2_image_list[i])
		try:
			fea = extractor.extract(cam2_image_list[i])
			#print(len(fea))
			cam2_dict[cam2_image_list[i]] = fea
			print i
		except:
			continue
	#save_obj(cam2_dict,"register111")
	print "finished ext cam2 images features"
	num=0
	for dirpath, dirnames, filenames in os.walk(cam1_path):
		for f in filenames:
			# if num==50:
			# 	break
			# if num==200:
			# 	break
			print f
			if '.jpg' in f:
				cam1_image_list.append(join(dirpath,f))
				#num+=1
	print "cam1 images num:"
	print len(cam1_image_list)

	#compare
	for i in range(0,len(cam1_image_list)):
		print i
		id = cam1_image_list[i].split('/')[-2]
		candidate_path_id = candidate_path+id
		if not os.path.exists(str(candidate_path_id)):
		#if not os.path.exists(id):
			os.system('mkdir '+candidate_path_id)

		try:
			fea = extractor.extract(cam1_image_list[i])
			min_dis = 999
			min_filename = ''
			for tempf in cam2_dict:
				dist = distance.euclidean(fea,cam2_dict[tempf])
				if dist < min_dis:
					min_dis = dist
					min_filename = tempf
		# 	save file to cadidate folder
			print min_filename
			print candidate_path_id
			os.system('cp '+min_filename+' '+candidate_path_id+'/')
		except:
			continue
	toc = timeit.default_timer()
	print('all time: %.2f' % ((toc - tic) * 1000))









