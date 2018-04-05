'''
Things to do:
Add class name
configure paths
Change parsing to one file for input coordinates from
'''


# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:55:43 2015
This script is to convert the txt annotation files to appropriate format needed by YOLO
@author: Guanghan Ning
Email: gnxr9@mail.missouri.edu
"""

import os
from os import walk, getcwd, listdir
from PIL import Image
import glob
from shutil import copyfile
from subprocess import Popen
from sys import stderr

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


"""-------------------------------------------------------------------"""
def main() :
    in_dir = "bboxIn/"
    list_file = "filelist_LBP.txt"
    classes = listdir(in_dir)
    for i in range(len(classes) -1) :
        if classes[i].startswith(".") :
            classes.pop(i)
        #rename directorys with underscores
        os.rename(in_dir + classes[i], in_dir + classes[i].replace(" ", "_"))
        classes[i] = classes[i].replace(" ", "_")
    wd = getcwd()

    # Percentage of images to be used for the test set
    percentage_test = 10

    # Create and/or truncate train.txt and test.txt
    file_train = open('train.txt', 'w')
    file_test = open('test.txt', 'w')

    #Open file for obj.names, obj.data
    file_names = open('obj.names', 'w')
    file_data = open('obj.data', 'w')

    # REMEMBER: change number of classes in yolo-voc.cfg

    # Populate train.txt and test.txt
    counter = 1
    index_test = round(100 / percentage_test)

    """ Make directories """

    if not os.path.exists(in_dir):
        print("Missing input directory (bboxIn/)", file=stderr)
        return

    """ Process """
    for classifier in classes:
        # txt_file =  open("Labels/stop_sign/001.txt", "r")
        file_names.write(classifier.replace("_", " ") + '\n')
        """ Open input text files """
        txt_path = in_dir + classifier + '/' + list_file
        txt_file = open(txt_path, "r")
        lines = txt_file.read().split('\n')   #for ubuntu, use "\r\n" instead of "\n"

        """ Convert the data to YOLO format """
        ct = 0
        for line in lines:
            if(len(line) >= 2):
                ct = ct + 1
                elems = line.split('\t')
                img_path = wd + "/" + in_dir + classifier + '/' + elems[0]
                #possible rearrange
                xmin = elems[1]
                xmax = elems[3]
                ymin = elems[2]
                ymax = elems[4]

                im= Image.open(img_path)
                w= int(im.size[0])
                h= int(im.size[1])
                #w = int(xmax) - int(xmin)
                #h = int(ymax) - int(ymin)
                # print(xmin)
                b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = convert((w,h), b)
                out_file = open(img_path[0:-4] + ".txt", 'w')
                out_file.write(str(classes.index(classifier)) + " " + " ".join([str(a) for a in bb]) + '\n')
                out_file.close()
                if counter == index_test:
                    counter = 1
                    file_test.write(img_path)
                else:
                    file_train.write(img_path)
                    counter = counter + 1
        print(classifier + " preprocessed")
    file_data.write("classes= " + str(len(classes)) + "\ntrain  = train.txt\nvalid  = test.txt\nnames = obj.names\nbackup = backup/\n")
    file_data.close()
    file_names.close()
    file_test.close()
    file_train.close()
    resp = Popen("../darknet detector train obj.data ../cfg/yolo-voc.cfg ../darknet19_448.conv.23 -gpus 0".split())
    resp.wait()
if __name__ == "__main__" : main()
