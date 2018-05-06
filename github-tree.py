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
import json
import logging
import os
import sys
import yaml

DESC_MSG = 'Look for patterns and heuristics into Git-trees and return a list of positive results'


def main(args):

    logger.info('GitHub-Tree starts...')

    with open(os.path.abspath(args.heuristics_file), 'r') as hfile:
        try:
            heuristics = yaml.load(hfile)
        except yaml.YAMLError as e:
            logger.error(e)
            raise SystemExit

    logger.info("Looking for JSON files into: %s" % args.trees_path)
    repo_jsons = os.listdir(args.trees_path)
    for jsonfile_path in repo_jsons:
        jsonfile = "%s/%s" % (os.path.abspath(args.trees_path), jsonfile_path)
        (owner_id, repo_id) = jsonfile_path.split(":")
        repo_id = repo_id[:-5]

        logger.debug("Opening %s" % jsonfile)
        with open(jsonfile, 'r') as data_file:
            data = json.load(data_file)

        try:
            tree = data["tree"]
        except KeyError:
            logger.error("KeyError in file: %s" % jsonfile)
            continue

        for file_dict in tree:
            if file_dict["type"] != "tree":
                try:
                    if ("path" in file_dict) and ("url" in file_dict):
                        if interesting(file_dict["path"], heuristics):
                            print("%s, %s\r\n" %(file_dict["path"], file_dict["url"]))
                        else:
                            pass
                except UnicodeEncodeError:
                    logger.error("UnicodeEncodeError in file: %s" % jsonfile)

def interesting(path, heuristics):
    ext = extension(path)
    if ext in heuristics['level-one_exts']:
        return 1
    if ext in heuristics['level-two_exts']:
        for keyword in heuristics['keywords']:
            if keyword in filename(path):
                return 1
        return 0
    else:
        return 0

def extension(path):
    """"
    Given a path, return its extension
    """
    tmp_list = path.split('.')
    if len(tmp_list) > 1:
        return tmp_list[-1].lower()
    else:
        return ""

def filename(path):
    """"
    Given a path, return its filename (without extension)
    """
    tmp_list = path.split('/')
    if len(tmp_list) > 1:
        full_name = tmp_list[-1] # with extension
        if '.' in full_name:
            full_name = '.'.join(full_name.split('.')[:-1])
        return full_name.lower()
    else:
        return ""

def tree(path):
    """"
    Given a path, return its tree (without the final filename)
    """
    tmp_list = path.split('/')
    if len(tmp_list) > 1:
        return '/'.join(tmp_list[:-1])
    else:
        return ""

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
    ch.setLevel(logging.ERROR)

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

    parser.add_argument('--heuristics-file', dest='heuristics_file', required=True,
                        help='File with patterns and other heuristics')
    parser.add_argument('--trees-path', dest='trees_path', required=True,
                        help='Path to folder containing trees information')
    parser.add_argument('--log-file', dest='log_file', default='github-tree.log',
                        required=False, help='Log file')
    parser.add_argument('-g', '--debug', dest='debug_mode_on', action='store_true',
                        default=False, help='Enables debug mode')
    return parser.parse_args()


if __name__ == '__main__':
    # TODO: Add documentation
    # TODO: Support heuristics file
    try:
        args = parse_args()
        keep_fds = configure_logging(args.log_file, args.debug_mode_on)
        main(args)
    except Exception as e:
        logger.exception("Exception message:")
        s = "Error: %s github-tree is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
