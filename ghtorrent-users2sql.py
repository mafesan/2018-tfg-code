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

DESC_MSG = 'Converts the USERS table from GHTorrent (csv) into a SQL script'


def main(args):
    input_file = args.input_file
    db_name = args.db_name

    fields = 'id, login, name, company, location, email, created_at, type, fake, deleted, longi, lat, country_code, state, city'

    insert_query = 'INSERT INTO users (%s) VALUES\n' % fields

    file_name = args.out_path + '/users.sql'
    output = open(file_name, 'w')
    output.write('USE %s;\n' % db_name)
    output.write(insert_query)

    first = True
    count = 0

    logger.info("Start to fill users.sql file")
    with open(input_file, 'r') as csvfile:
        for fields in csv.reader(csvfile):
            fields = clean(fields)
            if len(fields) != 15:
                logger.debug("Fields length is greater than expected: " + str(fields))
                continue
            values = "'" + "','".join(fields) + "'"
            values = values.replace("'\\N'", 'NULL')
            values = values.replace("'NULL'", 'NULL')
            if "'\\'" in values:
                logger.debug("Fields contains undesired characters: " + str(fields))
                continue
            if first:
                output.write("(%s)" % values)
                first = False
                count += 1
            else:
                if not count % 100000:
                    output.write(';\n')
                    output.write(insert_query + '\n')
                    output.write("(%s)" % values)
                    count += 1
                else:
                    output.write(",\n(%s)" % values)
                    count += 1
    output.write(';')
    output.close()
    logger.info("Process finished")


def clean(fields):
    new_fields = []
    for field in fields:
        if field == "":
            field = "NULL"
        elif "<img src=x onerror=alert(1)>" in field:
            logger.debug("Fields contains undesired characters: " + str(fields))
            new_fields = []
            continue
        elif ";alert(" in field:
            logger.debug("Fields contains undesired characters: " + str(fields))
            new_fields = []
            continue
        new_fields.append(field.replace("'", "\\' "))
    return new_fields


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
                        help='CSV file of USERS table from GHTorrent')
    parser.add_argument('--db-name', dest='db_name', required=True,
                        help='Database name')
    parser.add_argument('--output-path', dest='out_path', required=False,
                        default=os.curdir, help='Path where users.sql script will be stored')
    parser.add_argument('--log-file', dest='log_file', default='ghtorrent-users2sql.log',
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
        s = "Error: %s ghtorrent-users2sql is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
