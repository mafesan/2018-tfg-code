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
import logging
import os
import sys

from collections import namedtuple

DESC_MSG = 'Adapt projects.csv file from GHTorrent dump with preliminary filter(s)'


def main(args):

    formatted_file = format_projects_file(args)
    filter_projects_file(args, formatted_file)


def format_projects_file(args):

    input_file = open(os.path.abspath(args.input_file), 'r')
    try:
        output_filename = args.input_file.replace('.csv', '_formatted.csv')
    except Exception:
        logger.error("Your input file has not a '.csv' extension")
        raise SystemExit

    output_file = open(os.path.abspath(output_filename), 'w')

    linecounter = 0
    lastline = ""

    while 1:
        try:
            line = input_file.readline()
            linecounter += 1
            if not line:
                break
            output_file.write(line.replace('\\N', '0'))
            lastline = line
        except Exception as e:
            logger.error(str(e))
            logger.debug("Exception at line %s" % str(linecounter))
            logger.debug("Error line: %s\r\nLast line: %s" % (line, lastline))
            raise SystemExit

    input_file.close()
    output_file.close()
    logger.info("Number of lines: %s" % str(linecounter))
    return output_filename


def filter_projects_file(args, formatted_file):

    ProjectRecord = namedtuple('ProjectRecord', 'id, url, owner_id, name, descriptor,\
                               language, created_at, forked_from, deleted, updated_at')

    count = 0

    with open(os.path.abspath(args.output_file), 'w') as output_file:
        csvout = csv.writer(output_file, delimiter=',', escapechar="\\", quoting=csv.QUOTE_NONNUMERIC)
        with open(os.path.abspath(formatted_file), 'r') as csvfile:
            logger.info("Filtering projects: Not forked and Not deleted...")
            for contents in csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\"):
                row = ProjectRecord(*contents)
                if not row.forked_from and not row.deleted:
                    count += 1
                    csvout.writerow(contents)

    logger.info("Number of hits: %s" % str(count))


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

    parser.add_argument('--input-file', dest='input_file', required=True,
                        help='Input projects CSV file')
    parser.add_argument('--output-file', dest='output_file', required=True,
                        help='Output projects CSV file')
    parser.add_argument('--log-file', dest='log_file', default='get-project-list.log',
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
        s = "Error: %s get-project-list is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
