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
import shutil
import sys
import urllib.request

from perceval.backends.core.git import Git

DESC_MSG = 'Calls GrimoireLab-Perceval to extract git information from the output file of hits2urls.py script'


def remove_dir(directory):
    if os.path.exists(directory):
        logger.debug("Removing directory: ", directory)
        shutil.rmtree(directory, ignore_errors=True)


def main(args):
    github_key = args.github_token
    list_jsons = os.listdir(os.path.abspath(args.output_path))
    repo_set = set()
    with open(args.urls_file, 'r') as url_file:
        os.chdir(os.path.abspath(args.output_path))
        for line in url_file:
            try:
                url = line.split('/')
                repo = "%s/%s" % (url[3], url[4])
            except IndexError:
                logger.error("Error in repo (line) " + line + "\r\n")
                continue

            repo_set.add(repo)

    for repo in sorted(repo_set):
        api_url = "https://api.github.com/repos/" + str(repo) + "?" + github_key
        logger.info("Checking metadata for repo %s" % repo)
        response = urllib.request.FancyURLopener({})
        with response.open(api_url) as url_opener:
            json_data = url_opener.read().decode('utf-8')
            dicc_out = json.loads(json_data)

        repo_split = repo.split('/')
        outfile_name = "%s_%s.json" % (repo_split[0], repo_split[1])
        outfile_path = "%s/%s" % (args.output_path, outfile_name)
        if 'message' in dicc_out:
            result = dicc_out['message']
        elif dicc_out == {}:
            result = 'False'
        else:
            result = dicc_out['private']

        if result == 'Not Found':
            logger.error("Not found: %s" % repo)
        elif result == 'True':
            logger.error("Private: %s" % repo)
        else:
            repo_url = "https://github.com/%s" % repo

            if outfile_name in list_jsons:
                logger.info("Already downloaded: %s " % outfile_name)
            else:
                logger.info('Executing Perceval with repo: %s' % repo)
                logger.debug('Repo stats. Size: %s KB' % dicc_out["size"])
                gitpath = '%s/%s' % (os.path.abspath(args.perceval_path), repo)
                git = Git(uri=repo_url, gitpath=gitpath)
                commits = [commit for commit in git.fetch()]
                logger.info('Exporting results to JSON...')
                with open(outfile_path, "w", encoding='utf-8') as jfile:
                    json.dump(commits, jfile, indent=4, sort_keys=True)
                logger.info('Exported to %s' % outfile_path)
                if not args.cache_mode_on:
                    remove_dir(gitpath)


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

    parser.add_argument('--github-token', dest='github_token', required=True,
                        help='GitHub token')
    parser.add_argument('--urls-file', dest='urls_file', required=True,
                        help='Path to URLs file (output from hits2urls.py)')
    parser.add_argument('--output-path', dest='output_path', required=True,
                        help='Path where Perceval JSONs will be saved into')
    parser.add_argument('--perceval-path', dest='perceval_path', required=True,
                        help='Path where Perceval store its cache information')
    parser.add_argument('--log-file', dest='log_file', default='perceval-handler.log',
                        required=False, help='Path to log file')
    parser.add_argument('-c', '--keep-cache', dest='cache_mode_on', action='store_true',
                        default=False, help='Keep Perceval cache')
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
        s = "Error: %s perceval-handler is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
