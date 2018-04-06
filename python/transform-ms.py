#!/usr/bin/env python

import os
from os import walk, getcwd, listdir
from PIL import Image
import glob
from shutil import copytree
from subprocess import Popen
import sys
from argparse import ArgumentParser
import errno

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

def transform_single(idx, orig, names_f, train_f, test_f, data_f):
    # test against this percent of the dataset
    test_pct = 10
    test_idx = round(100 / test_pct)
    classifier = os.path.basename(orig)

    # Holds the bounding box data
    manifest = 'filelist_LBP.txt'

    # Rename directories with underscores
    os.rename(orig.replace('_', ' '), orig)

    # Write classifier into 'obj.names'
    names_f.write(classifier.replace('_', ' ') + '\n')

    with open(os.path.join(os.path.curdir, orig, manifest), 'r') as manifest_f:
        boxes = manifest_f.read().split('\n')

        ct = 0

        # iterate over marked boxes
        for test_ctr, box in enumerate(boxes):
            if(len(box) >= 2):
                ct = ct + 1
                img_name, xmin, ymin, xmax, ymax = box.split('\t')
                img_path = os.path.join(orig, img_name)

                # Scale box on image
                img = Image.open(img_path)
                w = int(img.size[0])
                h = int(img.size[1])

                # Store box into matching file
                with open(img_path[:-3] + 'txt', 'w') as map_f:
                    box_dims = convert((w,h), (float(xmin), float(xmax), float(ymin), float(ymax)))
                    box_dims = " ".join([str(a) for a in box_dims])
                    map_f.write('{idx} {box_dims}'.format(**locals()))

                img_rel_path = os.path.abspath(os.path.join(os.path.curdir, orig, img_name)) + '\n'

                # Write into either testing or training file
                if test_ctr % test_idx == 1:
                    test_f.write(img_rel_path)
                else:
                    train_f.write(img_rel_path)

    

def transform_multiple(root, dest, name, move):

    dest = os.path.abspath(dest)

    if not os.path.exists(root) or not os.path.isdir(root):
        print('Specified path is not a directory or does not exist')
        sys.exit(1)
    if os.path.exists(os.path.join(dest, name)):
        print('Dataset named {name} already exists in {dest}. Please remove it or pick another name'.format(**locals()))
        sys.exit(1)

    # copy to new directory
    if not move:
        print('Copying {root} to {dest} as {name}'.format(**locals()))
        copytree(root, os.path.join(dest, name))
    else:
        print('Moving {root} to {dest} as {name}'.format(**locals()))
        os.rename(root, os.path.join(dest, name))

    classes = [ d for d in listdir(os.path.join(dest, name)) if os.path.isdir(os.path.join(dest, name, d)) ]

    os.mkdir(os.path.join(dest, name, name + '-backup'))

    # open all necessary files in the root of the dataset directory
    with open(os.path.join(dest, name, name) + '.names', 'w+') as names, \
         open(os.path.join(dest, name, name) + '.train', 'w+') as train, \
         open(os.path.join(dest, name, name) + '.test', 'w+') as test, \
         open(os.path.join(dest, name, name) + '.data', 'w+') as data:
        for idx, classifier in enumerate(classes):

            print('Transforming "{classifier}" files'.format(**locals()))    
            transform_single(idx, os.path.join(dest, name, classifier.replace(' ', '_')), names, train, test, data)

        print('Writing {name}.data'.format(**locals()))
        class_ct = len(classes)
        path = os.path.join(dest, name,name)
        data_cfg = 'classes= {class_ct}\ntrain  = {path}.train\nvalid  = {path}.test\nnames = {path}.names\nbackup = {path}-backup\n'.format(**locals())
        data.write(data_cfg)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('root', help='The location of the dataset')
    parser.add_argument('name', type=str, default='obj', help='Name for the dataset to be used in naming files')
    parser.add_argument('--repo', '-r', default=os.path.join(os.path.expanduser('~'), '.datasets'), help='The directory to store datasets in')
    parser.add_argument('--move', '-m', action='store_true', default=False, help='Copy to dest instead of moving')
    args = parser.parse_args()
    transform_multiple(args.root, args.repo, args.name, args.move)
