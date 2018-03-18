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
import sys
import time
import urllib.request

from collections import namedtuple

DESC_MSG = 'Extracts git trees (list of files) from GitHub repositories'


def main(args):

    logger.info('GitHub-API starts...')
    github_key = args.github_token
    ProjectRecord = namedtuple('ProjectRecord', 'id, url, owner_id, name, descriptor, language, created_at, forked_from, deleted, updated_at')

    if not os.path.exists("master"):
        os.mkdir("master")
    if not os.path.exists("default"):
        os.mkdir("default")
    if not os.path.exists("trees"):
        os.mkdir("trees")

    alreadyList = os.listdir("master")

    with open(args.projects_file, "r") as csvfile:
        for contents in csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL):
            # For each line in csv file...
            contents[0] = str(int(contents[0]))
            contents[2] = str(int(contents[2]))
            repo = ProjectRecord(*contents)

            if repo.owner_id + ":" + repo.id + ".json" in alreadyList:
                continue  # Break loop, if json is already downloaded
            if not get_json(repo, github_key, "master", "/branches/master"):
                continue  # Break loop, ¿?
            sha_hash = read_json(repo, "master", ["commit", "commit", "tree", "sha"])

            if not sha_hash:
                logger.debug("Master branch not found: %s", repo.url)
                if not get_json(repo, github_key, "default"):
                    continue
                default = read_json(repo, "default", ["default_branch"])

                if not default:
                    logger.debug("No default branch found: %s", repo.url)
                    time.sleep(1.40)
                    continue
                if not get_json(repo, github_key, "master", "/branches/" + default):
                    continue
                sha_hash = read_json(repo, "master", ["commit", "commit", "tree", "sha"])

                if not sha_hash:
                    logger.debug("Default branch not found: %s", repo.url)
                    time.sleep(2.10)
                    continue
            if not get_json(repo, github_key, "trees", "/git/trees/" + sha_hash + "?recursive=1"):
                continue
            time.sleep(1.40)

    logger.info("End of program")


def lookup(dic, key, *keys):
    """
    Given the dictionary dic, it provides the value with the given key(s)
    From StackOverflow: http://stackoverflow.com/a/11701539

    For instance, to obtain data["commit"]["commit"]["tree"]["sha"]
    you should call:
    lookup(data, ["commit", "commit", "tree", "sha"])
    """
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key)


def get_json(repo, github_key, directory, url_append=""):
    """
    Given the repo tuple (username, repository_name)
    and the directory to store the json
    it performs a query to the repos GitHub v3 API

    url_append offers the possibility to append something to the call
    """
    url = repo.url + url_append
    if "?" in url_append:
        url = url + "&" + github_key
    else:
        url = url + "?" + github_key
    try:
        logger.info("Retrieve: %s", repo.url)
    except UnicodeEncodeError as e:
        logger.debug("%s, %s", str(e), str(repo))
        logger.debug("directory: %s", directory)
        return 0
    try:
        json_name = "%s/%s:%s.json" % (directory, str(repo.owner_id), str(repo.id))
        urllib.request.urlretrieve(url, json_name)
    except IOError as e:
        logger.debug("%s, url: %s", str(e), url)
        return 0
    return 1


def read_json(repo, directory, lookup_list):
    """
    Given the repo tuple (username, repository_name)
    the directory where the json has been stored
    it looks up for a given value in the JSON (given as a list)
    and returns its value
    """
    json_name = "%s/%s:%s.json" % (directory, str(repo.owner_id), str(repo.id))
    with open(json_name) as data_file:
        try:
            data = json.load(data_file)
        except ValueError as e:
            logger.error(str(e))
            logger.debug("Error with file: %s", json_name)
    try:
        return lookup(data, *lookup_list)
    except KeyError:
        return 0


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

    parser.add_argument('--github-token', dest='github_token', required=True,
                        help='GitHub token')
    parser.add_argument('--projects-file', dest='projects_file', required=True,
                        help='Projects file')
    parser.add_argument('--log-file', dest='log_file', default='github-api.log',
                        required=False, help='Log file')
    parser.add_argument('-g', '--debug', dest='debug_mode_on', action='store_true',
                        default=False, help='Enables debug mode')
    return parser.parse_args()


if __name__ == '__main__':
    # TODO: Add documentation
    # TODO: Add new methods to reduce main
    # TODO: Check if response is truncated
    try:
        args = parse_args()
        keep_fds = configure_logging(args.log_file, args.debug_mode_on)
        main(args)
    except Exception as e:
        logger.exception("Exception message:")
        s = "Error: %s github-api is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
