import numpy as np
import cv2
import os,time
import argparse
from os.path import join, getsize
#image_file1="./candidate_2018_09_15_2/am76/"
def filter_image(fileName):
    for dirpath, dirnames, filenames in os.walk(fileName):
        for f in filenames:
            if '.jpg' in f:
                image_path=join(dirpath, f)
                image_source=cv2.imread(image_path,0)
                size=image_source.shape
                if(size[0]<85 and size[1]<50):
                    os.system("rm "+image_path)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_file", help="input your Absolute path",type=str)
    args = parser.parse_args()
    filter_image(args.image_file)