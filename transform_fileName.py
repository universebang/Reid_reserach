import numpy as np
import os

fileName1="/home/disk2/homedepot/pyEvent_cropping/cropping/2_2018-09-14_09-00/"
fileName2="/home/disk2/homedepot/pyEvent_cropping/cropping/2_2018-09-14_18-00/"
candidate_path="/home/disk2/homedepot/clean_data/2018-09-14/2_2018-09-14/"
def transform_name(fileName1,fileName2,candidate_path):
    if(fileName1[-6:-1]=="09-00"):
        for file in os.listdir(fileName1):
            fileName="am"
            fileName+=file
            sourcefile=os.path.join(fileName1, file)
            print('cp -r ' +sourcefile + ' ' + candidate_path)
            os.system('cp -r ' +sourcefile + ' ' + candidate_path)
            os.rename(os.path.join(candidate_path, file), os.path.join(candidate_path, fileName))
    if (fileName2[-6:-1] == "18-00"):
        for file in os.listdir(fileName2):
            fileName = "pm"
            fileName += file
            print(os.path.join(fileName2, file))
            sourcefile = os.path.join(fileName2, file)
            print('cp -r ' +sourcefile + ' ' + candidate_path)
            os.system('cp -r ' + sourcefile + ' ' + candidate_path)
            os.rename(os.path.join(candidate_path, file), os.path.join(candidate_path, fileName))
if __name__ == '__main__':
    transform_name(fileName1,fileName2,candidate_path)
    # list1=[1,2,3,4,5,6,7,8,9,0]
    # for i in range(20):
    #     if i==19:
    #         part=list1[i:]
    #     else:
    #         part=list1[i:i+1]
    #     print(part)


