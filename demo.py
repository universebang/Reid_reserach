import numpy as np
import torch
from PIL import Image

from mgn_den import mgn_dense
from torchvision import transforms
from torch.autograd import Variable

class pfextractor():
	def __init__(self, save_path,id):
		torch.cuda.set_device(id)
		print(torch.cuda.current_device())
		self.id = id
		model_structure = mgn_dense().cuda()

		self.model = self.load_network(model_structure, save_path)
		self.transform = transforms.Compose([
				transforms.Resize((384, 128)),
				transforms.ToTensor(),
				transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]
			)
	
	def load_network(self, network, save_path):
		model_dict = torch.load(save_path)
		temp_dict = {}
		for temp in model_dict:
			temp_dict[temp.split('module.')[-1]] = model_dict.pop(temp)
		network.load_state_dict(temp_dict)
		return network

	def image_loader(self, image_file_name):
		img_data = Image.open(image_file_name)
		img_data = self.transform(img_data)
		img_data = img_data.unsqueeze_(0).float()
		return Variable(img_data).cuda()

	def extract(self,img):
		self.model.eval()
		#try:
		img = self.image_loader(img)
		output = self.model(img,False)
		return output.tolist()[0]

'''
if __name__ == '__main__':
	extractor = pfextractor('PED_EXT_001.pkl',id)
	fea = extractor.extract('test.jpg')
	print(type(fea))
	print(fea,len(fea))
'''





