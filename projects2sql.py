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

from collections import OrderedDict

DESC_MSG = 'Generate SQL files extrating data from Perceval JSON files'


def main(args):
    db_name = args.db_name
    abs_path = os.path.abspath(args.json_path)
    input_file = os.path.abspath(args.input_file)

    dicc_positives = {}
    common_url = "https://raw.githubusercontent.com/"

    out_path = os.path.abspath(args.output_path)
    missing_fn = out_path + '/missing_projects.csv'
    missing = open(missing_fn, 'w')
    writer_miss = csv.writer(missing)
    writer_miss.writerow(("Project", "Issue", "Num_pos_files"))

    # Open SQL output files, one file per table to gain efficiency

    output_repos = open(out_path + "/repos.sql", "w")
    output_commits = open(out_path + "/commits.sql", "w")
    output_people = open(out_path + "/people.sql", "w")
    output_intfiles = open(out_path + "/interestingfiles.sql", "w")

    output_repos.write("USE %s;\n" % db_name)
    output_commits.write("USE %s;\n" % db_name)
    output_people.write("USE %s;\n" % db_name)
    output_intfiles.write("USE %s;\n" % db_name)

    repo_fields = 'id, name, founder, url, number_commits, first_commit, last_commit'
    commits_fields = 'id, gh_id, people_id, commit_date, cochanged, repos_id'
    people_fields = 'id, name, email'
    intfiles_fields = 'id, name, url, commits_id, repo_id'

    output_repos.write("INSERT INTO repos (%s) VALUES\n" % repo_fields)
    output_commits.write("INSERT INTO commits (%s) VALUES\n" % commits_fields)
    output_people.write("INSERT INTO people (%s) VALUES\n" % people_fields)
    output_intfiles.write("INSERT INTO interestingfiles (%s) VALUES\n" % intfiles_fields)

    first_repos = True
    first_commits = True
    first_people = True
    first_interestingfiles = True

    # Open input file, load projects and the positive file into a dictionary
    with open(input_file, 'r') as urlsfile:
        for line in urlsfile:
            if line != "":
                url_split = line.split(common_url)
                file_url = url_split[1][:-1]  # Remove "\r\n"
                project = "/".join(file_url.split("/")[0:2])
                if project in dicc_positives:
                    list_tmp = dicc_positives[project]
                    list_tmp.append(file_url)
                    dicc_positives[project] = list_tmp
                else:
                    dicc_positives[project] = [file_url]
    p_id = 0
    auth_id = 0
    commits_num = 0
    file_id = 0
    first_date = ""

    # These numbers above should be zero
    # These are values for the script before it stopped
    dicc_authors = {}

    list_pos_files = sorted(dicc_positives)

    for project in list_pos_files:  # Number of the last seen project
        gh_user = project.split("/")[0]
        gh_pname = project.split("/")[1]
        json_name = gh_user + "_" + gh_pname + ".json"
        file_path = abs_path + "/" + json_name
        commit_amount = 0
        dicc_commit_num = {}
        if not os.path.exists(file_path):
            if (args.avoid_fw) and (("framework" or "Framework") in gh_pname):
                issue = "Framework-Type"
            else:
                issue = "Not-checked"
            logger.info("Missing project %s. Issue: %s" % (project, issue))
            writer_miss.writerow((project, issue, len(dicc_positives[project])))
        else:
            with open(file_path, 'r') as jfile:
                jdata = json.load(jfile, encoding='utf-8', object_pairs_hook=OrderedDict)

            p_id += 1

            list_authors = []
            list_dates = []

            # For each element of split (i.e., each commit):
            for element in jdata:
                # Get commit id
                try:
                    commit_id = element["data"]["commit"]
                    dicc_commit_num[commit_amount] = commit_id
                    commit_amount += 1
                except IndexError as e:
                    error_desc = "%s. Project: %s, Element: %s" % (str(e), project, element)
                    logger.error(error_desc)

                # Obtain commit author

                author = element["data"]["Commit"]
                if (author != "") and (author != "<>"):
                    author = author[:-1]
                    try:
                        person = author.split(" <")[0]
                    except IndexError:
                        person = "unknown"
                    try:
                        email = author.split(" <")[1]
                    except IndexError:
                        email = "unknown"
                else:
                    author = "unknown"
                    email = "unknown"

                if author in dicc_authors:
                    my_authid = dicc_authors[author][0]
                else:
                    auth_id += 1
                    my_authid = auth_id
                    dicc_authors[author] = [my_authid]
                    query = '(' + str(auth_id) + ', "'
                    query += person.replace("'", "\\'") + '", "' + email.replace("'", "\\'") + '")'
                    if first_people:
                        output_people.write(query)
                        first_people = False
                    else:
                        output_people.write(',\n' + query)
                list_authors.append(my_authid)

                # Timestamp (Commit datetime)
                commit_date = element['updated_on']
                list_dates.append(float(commit_date))

            jfile = open(file_path, 'r')
            jdata_str = jfile.read()
            jfile.close()
            # jjson contains a list with the commits!
            jjson = json.loads(json.dumps(jdata_str.split('{')))

            json_str = '{'.join(list(jjson))
            tmp_files = json_str.split('"files":')[1:]

            # For each commit

            for element_comm in tmp_files:
                num_list = tmp_files.index(element_comm)
                comm_id = dicc_commit_num[num_list]
                commits_num += 1
                author_id = list_authors[num_list]
                date = list_dates[num_list]
                changed_files = element_comm.split('"file": ')
                changed_files = changed_files[1:]

                # Files changed in the commmit
                for ch_file in changed_files:
                    file_name = ch_file.split(',')[0][1:-1]
                    for pos_file in dicc_positives[project]:
                        pos_file_name = pos_file.split('/')[3:]
                        pos_file_name = "/".join(pos_file_name)
                        if file_name == pos_file_name:
                            file_url = common_url + pos_file
                            file_id += 1

                            # File id, File name, File url, commit id, project id
                            query = '(' + str(file_id) + ', "'
                            query += file_name.replace("'", "\\'") + '","' + file_url.replace("'", "\\'")
                            query += '", ' + str(commits_num) + ', ' + str(p_id) + ')'
                            if first_interestingfiles:
                                output_intfiles.write(query)
                                first_interestingfiles = False
                            else:
                                output_intfiles.write(',\n' + query)

                # See if it is the first commit
                if not first_date:
                    first_date = date

                # id, commit gh-id, author id, datetime, cochanged files, project id
                query = '(' + str(commits_num) + ', "' + comm_id + '", '
                query += str(author_id) + ', "' + beauty_date(date) + '", '
                query += str(len(changed_files)) + ', ' + str(p_id) + ')'
                if first_commits:
                    output_commits.write(query)
                    first_commits = False
                else:   # To avoid having too many commits in one query, split it!
                    if not commits_num % 100000:
                        output_commits.write(";\n\nINSERT INTO commits (%s) VALUES\n" % commits_fields)
                        output_commits.write(query)
                    else:
                        output_commits.write(',\n' + query)

            # Write Project/repo data
            p_url = "https://www.github.com/" + gh_user + "/" + gh_pname

            # Repo_id, repo_name, repo_founder, repo_url, number_commits, first_commit, last_commit
            query = '(' + str(p_id) + ', "' + gh_pname.replace("'", "\\'") + '", "' + gh_user.replace("'", "\\'") + '", "' + p_url.replace("'", "\\'") + '", '
            query += str(len(tmp_files)) + ', "' + beauty_date(first_date) + '", "' + beauty_date(date) + '")'
            first_date = ""
            if first_repos:
                output_repos.write(query)
                first_repos = False
            else:
                output_repos.write(',\n' + query)

            logger.info("Project %s: correct." % project)

    missing.close()
    output_repos.write(';')
    output_repos.close()
    output_commits.write(';')
    output_commits.close()
    output_people.write(';')
    output_people.close()
    output_intfiles.write(';')
    output_intfiles.close()


def beauty_date(epoch_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(epoch_time))


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

    parser.add_argument('--db-name', dest='db_name', required=True,
                        help='Database name')
    parser.add_argument('--json-path', dest='json_path', required=True,
                        help='Path where Perceval JSONs are stored into')
    parser.add_argument('--urls-file', dest='input_file', required=True,
                        help='Path to input URLs file produced with hits2urls script')
    parser.add_argument('--output-path', dest='output_path', required=False,
                        default=os.curdir, help='Path where SQL files are stored into')
    parser.add_argument('--log-file', dest='log_file', default='projects2sql.log',
                        required=False, help='Path to log file')
    parser.add_argument('--avoid-fw', dest='avoid_fw', action='store_true',
                        default=False, help='Avoid `Framework`-type projects')
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
        s = "Error: %s projects2sql is exiting now." % str(e)
        logger.error(s)
        sys.exit(1)
