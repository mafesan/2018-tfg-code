#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018 Libresoft, GSyC (URJC).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Miguel Angel Fernandez Sanchez <ma.fernandezsa@alumnos.urjc.es>
#     Gregorio Robles Martinez <grex@gsyc.urjc.es>
#

import argparse
import csv
import json
import logging
import os
import os.path
import sys

from collections import namedtuple

DESC_MSG = 'Converts positive results into URLs pointing to its raw files in GitHub'


def main(args):

    start = "https://raw.githubusercontent.com/"
    json_path = os.path.abspath(args.json_path)
    ProjectRecord = namedtuple('ProjectRecord', 'id, url, owner_id, name,\
                               descriptor, language, created_at, forked_from,\
                               deleted, updated_at')
    owners_dict = {}
    projects_dict = {}
    projects_file = args.projects_file

    with open(projects_file, "r") as csvfile:
        for contents in csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC):
            contents[0] = int(contents[0])
            contents[2] = int(contents[2])
            row = ProjectRecord(*contents)
            owner_name = row.url.split('/')[4]
            projects_dict[row.name] = row.id
            owners_dict[owner_name] = row.owner_id

    with open(args.hits_file, 'r') as hfile:
        linelist = hfile.readlines()

    with open(args.output_file, 'w') as ofile:
        for line in linelist:
            if "KeyError" in line:
                continue
            try:
                path, blob = line.split(" https://api.github.com/")
            except ValueError:
                continue
            blobList = blob.split('/')
            username = blobList[1]
            repo = blobList[2]
            if (username in owners_dict) and (repo in projects_dict):
                username_id = str(owners_dict[username])
                repo_id = str(projects_dict[repo])
            else:
                username_id = username
                repo_id = repo
            branch = obtain_branch(username_id, repo_id, json_path)
            if not branch:
                continue
            if path[-1] == ",":
                path = path[:-1]
            total = start + username + "/" + repo + "/" + branch + "/" + path
            ofile.write(total + "\r\n")


def obtain_branch(username, repo, init_path):
    """
    """
    filepath = init_path + "/default/" + username + ":" + repo + ".json"
    if os.path.isfile(filepath):
        with open(filepath) as data_file:
            data = json.load(data_file)
            try:
                return data["default_branch"]
            except KeyError:
                logger.error(filepath)
                return 0

    return "master"


logger = logging.getLogger(__name__)


def configure_logging(log_file, debug_mode_on=False):
    """Set up the logging and returns a list with the file descriptors

    :param log_file: Path for the log file
    :param debug_mode_on: If True, the level of the logger will be DEBUG

    :return: List with logging file descriptors
    """

    if debug_mode_on:
        logging_mode = logging.DEBUG
    else:
        logging_mode = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging_mode)

    # redirect logging to our log file
    fh = logging.FileHandler(log_file, 'a')
    fh.setLevel(logging_mode)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging_mode)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("[%(asctime)s - %(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    keep_fds = [fh.stream.fileno()]
    return keep_fds


def parse_args():
    """Parse arguments from the command line"""

    parser = argparse.ArgumentParser(description=DESC_MSG)

    parser.add_argument('--json-path', dest='json_path', required=True,
                        help='Path where github-api JSONS are stored')
    parser.add_argument('--projects-file', dest='projects_file', required=True,
                        help='Projects file which was used with github-api')
    parser.add_argument('--hits-file', dest='hits_file', required=True,
                        help='Path to the output file of github-tree')
    parser.add_argument('--output-file', dest='output_file', required=False,
                        help='Path to store the URLs output file', default="urls.txt")
    parser.add_argument('--log-file', dest='log_file', default='hits2urls.log',
                        required=False, help='Path to log file')
    parser.add_argument('-g', '--debug', dest='debug_mode_on', action='store_true',
                        default=False, help='Enables debug mode')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()
        keep_fds = configure_logging(args.log_file, args.debug_mode_on)
        main(args)
    except Exception as e:
        logger.exception("Exception message:")
        s = "Error: %s hits2urls is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
