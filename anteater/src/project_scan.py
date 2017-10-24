#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017 Luke Hinds <lukehinds@gmail.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"""
    Accepts the --path argument and iterates the root directory using os.walk
    If a file is a binary, or contains a blacklisted string. If any violations
    are found, the script adds the violation to a log file.
"""

from __future__ import division, print_function, absolute_import
import hashlib
import six.moves.configparser
import os
import re
import logging
from binaryornot.check import is_binary

from . import get_lists

logger = logging.getLogger(__name__)
config = six.moves.configparser.RawConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')
master_list = config.get('config', 'master_list')
ignore_list = config.get('config', 'master_list')
ignore_dirs = ['.git']
hasher = hashlib.sha256()


def prepare_project(project, project_dir):
    """ Generates blacklists / whitelists and calls main functions """

    # Get Various Lists / Project Waivers
    lists = get_lists.GetLists()

    # Get binary white list
    binary_list = lists.binary_list(project)

    # Get file name black list and project waivers
    file_audit_list, file_audit_project_list = lists.file_audit_list(project)

    # Get file content black list and project waivers
    master_list, ignore_list = lists.file_content_list(project)

    # Get File Ignore Lists
    file_ignore = lists.file_ignore()

    # Get Licence Lists
    licence_ext = lists.licence_extensions()
    licence_ignore = lists.licence_ignore()

    # Perform rudimentary scans
    scan_file(project_dir, project, binary_list,file_audit_list,
              file_audit_project_list, master_list, ignore_list,
              file_ignore)

    # Perform licence header checks
    licence_check(licence_ext, licence_ignore, project, project_dir)
    licence_root_check(project_dir, project)


def scan_file(project_dir, project, binary_list, file_audit_list,
              file_audit_project_list, master_list, ignore_list,
              file_ignore):
    """Searches for banned strings and files that are listed """
    for root, dirs, files in os.walk(project_dir):
        # Filter out ignored directories from list.
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for items in files:
            full_path = os.path.join(root, items)
            # Check for Blacklisted file names
            if file_audit_list.search(full_path) and not \
                    file_audit_project_list.search(full_path):
                match = file_audit_list.search(full_path)
                logger.error('Blacklisted filename: %s', full_path)
                logger.error('Matched String: %s', match.group())
                with open(reports_dir + "file-names_" + project + ".log",
                          "a") as gate_report:
                            gate_report. \
                                write('Blacklisted filename: {0}\n'.
                                      format(full_path))
                            gate_report. \
                                write('Matched String: {0}'.
                                      format(match.group()))

            # Check if Binary is whitelisted
            hashlist = get_lists.GetLists()
            binary_hash = hashlist.binary_hash(project, full_path)

            if is_binary(full_path) and not binary_list.search(full_path):
                with open(full_path, 'rb') as afile:
                    buf = afile.read()
                    hasher.update(buf)
                if hasher.hexdigest() in binary_hash:
                    logger.info('Found matching file hash for file: %s',
                                    full_path)
                else:
                    logger.error('Non Whitelisted Binary file: %s',
                                 full_path)
                    logger.error('Please submit patch with this hash: %s',
                                 hasher.hexdigest())
                    with open(reports_dir + "binaries-" + project + ".log",
                              "a") as gate_report:
                            gate_report.write('Non Whitelisted Binary: {0}\n'.
                                              format(full_path))

            else:
                if not items.endswith(tuple(file_ignore)):
                    try:
                        fo = open(full_path, 'r')
                        lines = fo.readlines()
                    except IOError:
                        logger.error('%s does not exist', full_path)

                    for line in lines:
                        # Check for sensitive content in project files
                        for key, value in master_list.iteritems():
                            regex = value['regex']
                            desc = value['desc']
                            if re.search(regex, line) and not re.search(
                                    ignore_list, line):
                                logger.error('File contains violation: %s',
                                             full_path)
                                logger.error('Flagged Content: %s',
                                             line.rstrip())
                                logger.error('Matched Regular Exp: %s', regex)
                                logger.error('Rationale: %s', desc.rstrip())
                                with open(reports_dir + "contents-" + project
                                                  + ".log", "a") \
                                        as gate_report:
                                    gate_report. \
                                        write('File contains violation: {0}\n'.
                                              format(full_path))
                                    gate_report. \
                                        write('Flagged Content: {0}'.
                                              format(line))
                                    gate_report. \
                                        write('Matched Regular Exp: {0}'.
                                              format(regex))
                                    gate_report. \
                                        write('Rationale: {0}\n'.
                                              format(desc.rstrip()))



def licence_root_check(project_dir, project):
    if os.path.isfile(project_dir + '/LICENSE'):
        logger.info('LICENSE file present in: %s', project_dir)
    else:
        logger.error('LICENSE file missing in: %s', project_dir)
        with open(reports_dir + "licence-" + project + ".log",
                  "a") \
                as gate_report:
            gate_report.write('LICENSE file missing in: {0}\n'.
                              format(project_dir))


def licence_check(licence_ext, licence_ignore, project, project_dir):
    """ Peform basic checks for the presence of licence strings """
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(tuple(licence_ext)) \
                    and file not in licence_ignore:
                full_path = os.path.join(root, file)
                if not is_binary(full_path):
                    fo = open(full_path, 'r')
                    content = fo.read()
                    # Note: Hardcoded use of 'copyright' & 'spdx' is the result
                    # of a decision made at 2017 plugfest to limit searches to
                    # just these two strings.
                    patterns = ['copyright', 'spdx',
                                'http://creativecommons.org/licenses/by/4.0']
                    if any(i in content.lower() for i in patterns):
                        logger.info('Licence string present: %s', full_path)
                    else:
                        logger.error('Licence header missing: %s', full_path)
                        with open(reports_dir + "licence-" + project + ".log",
                                  "a") \
                                as gate_report:
                            gate_report.write('Licence header missing: {0}\n'.
                                              format(full_path))
