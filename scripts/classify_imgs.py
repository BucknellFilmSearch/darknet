#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
import os
import json

import psycopg2

def db_login(config_file):
    with open(config_file, 'r') as json_file:
        json_data = json.load(json_file)

    #this is super bad. put in a config file to hide
    username = json_data["DATABASE"]["username"]
    password = json_data["DATABASE"]["password"]
    host = json_data["DATABASE"]["host"]
    port = json_data["DATABASE"]["port"]
    print("Logging in as " + username)
    print("Creating images/ directory if one does not already exist")
    try:
        os.stat("images")
    except OSError:
        os.mkdir("images")

    os.stat("images")

    try:
        print("Logging into the database...")
        print(username)
        print(host)
        print(password)
        print(port)

        db_conn = psycopg2.connect(dbname='filmtvse',
                                   user=username,
                                   host=host,
                                   password=password,
                                   port=port)
        print("Login Success!")
        return db_conn
    except psycopg2.Error as err:
        print("Connection to db failed")
        print(err)
        sys.exit(1)

def process_images(db_conn, src_dir):
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT oclc_id FROM media_metadata") #unique movies
        movies = cursor.fetchall()
        for movie in movies:
            oclc_id = str(movie[0])
            darknet_dir = os.path.dirname(os.path.dirname(__file__))
            # print(darknet)
            # exit(0)
            print("In directory {oclc_id}".format(**locals()))
            directory = os.path.join(src_dir, str(movie[0]))
            try:
                os.stat(directory)
            except OSError:
                os.mkdir(directory)
            cursor.execute("SELECT line_number, db_line_id  FROM media_text WHERE oclc_id = {oclc_id}".format(**locals()))

            os.system("find {directory} -maxdepth 1 -name '*.png' -o -name '*.jpg' | {darknet_dir}/darknet detect {darknet_dir}/cfg/yolo.cfg yolo.weights | ../scripts/".format(**locals()))

            print('\tproccessed movie number {oclc_id}'.format(**locals()))

    except psycopg2.Error as e:
        print('Fetching images failed')
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Process images through darknet')
    parser.add_argument('config_file',
                        help='The config file for logging into the DB')
    parser.add_argument('darknet_dist',
                        help='The Darknet executable to use')
    parser.add_argument('src_dir',
                        help='The directory in which the movie screnshots are held')
    ARGS = parser.parse_args()

    DB_CONN = db_login(ARGS.config_file)
    process_images(DB_CONN, ARGS.src_dir)
    sys.exit(0)
