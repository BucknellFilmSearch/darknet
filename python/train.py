#!/usr/bin/env python
import sys
from os import path
from subprocess import Popen
from argparse import ArgumentParser


def main(darknet_dir, name, repo, cfg, weights):
    # Get all absolute paths
    darknet = path.abspath(path.join(darknet_dir, 'darknet'))
    weights = path.abspath(path.join(darknet_dir, weights))
    dataset = path.abspath(path.join(repo, name))
    
    if not path.exists(dataset) or not path.isdir(dataset):
        if path.exists(path.join(path.curdir, name)) and path.isdir(path.join(path.curdir, name)):
            dataset = path.abspath(path.join(path.curdir, name))
        else:
            print('Directory "{dataset}" not found'.format(**locals()))
            sys.exit(1)
    
    dataset = path.abspath(path.join(dataset, name + '.data'))

    cmd = "{darknet} detector train {dataset} {cfg} {weights} -gpus 0".format(**locals())
    print(cmd)
    resp = Popen(cmd.split())
    resp.wait()

if __name__ == "__main__":
    parser = ArgumentParser('Train Darknet on a dataset')
    parser.add_argument('darknet', type=str, help='The directory darknet is in')
    parser.add_argument('name', type=str, help='The directory holding the dataset')
    parser.add_argument('cfg', type=str, help='The path to the config file for the neural net')
    parser.add_argument('--weights', '-w', default='starter.weights', type=str, help='The weights file name')
    parser.add_argument('--repo', '-r', default=path.join(path.expanduser('~'), '.datasets'), help='The directory datasets are stored in')

    args = parser.parse_args()
    main(args.darknet, args.name, args.repo, args.cfg, args.weights)
