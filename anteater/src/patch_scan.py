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
    Accepts the --patchset argument and iterates through each line of the
    patchset file to perform various checks such as if the file is a binary, or
    contains a blacklisted string. If any violations are found, the script
    exits with code 1 and logs the violation(s) found.
"""

from __future__ import division, print_function, absolute_import
from binaryornot.check import is_binary
import logging
import hashlib
import six.moves.configparser
import sys
import re

from . import get_lists

logger = logging.getLogger(__name__)
config = six.moves.configparser.SafeConfigParser()
config.read('anteater.conf')
anteater_files = config.get('config', 'anteater_files')
reports_dir = config.get('config', 'reports_dir')
ignore_dirs = ['.git', 'examples', anteater_files]
failure = False
hasher = hashlib.sha256()


def prepare_patchset(project, patchset, bincheck):
    """ Create black/white lists and default / project waivers
        and iterates over patchset file """
    # Get Various Lists / Project Waivers
    lists = get_lists.GetLists()

    # Get file name black list and project waivers
    file_audit_list, file_audit_project_list = lists.file_audit_list(project)

    # Get file content black list and project waivers
    flag_list, ignore_list = lists.file_content_list(project)

    # Get File Ignore Lists
    file_ignore = lists.file_ignore()

    # Open patch set to get file list
    try:
        fo = open(patchset, 'r')
        lines = fo.readlines()
    except IOError:
        logger.error('%s does not exist', patchset)
        sys.exit(1)

    for line in lines:
        patch_file = line.strip('\n')
        # Perform binary and file / content checks
        scan_patch(project, patch_file, bincheck, file_audit_list,
                   file_audit_project_list, flag_list, ignore_list,
                   file_ignore)

    # Process each file in patch set using waivers generated above
    # Process final result
    process_failure()


def scan_patch(project, patch_file, bincheck, file_audit_list,
               file_audit_project_list, flag_list, ignore_list, file_ignore):
    """ Scan actions for each commited file in patch set """
    global failure
    if is_binary(patch_file) and bincheck:
        hashlist = get_lists.GetLists()
        split_path = patch_file.split(project + '/', 1)[-1]
        binary_hash = hashlist.binary_hash(project, split_path)
        with open(patch_file, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        if hasher.hexdigest() in binary_hash:
            logger.info('Found matching file hash for: %s',
                        patch_file)
        else:
            logger.error('Non Whitelisted Binary file: %s',
                         patch_file)
            logger.error('Submit patch with the following hash: %s',
                         hasher.hexdigest())
        failure = True
        with open(reports_dir + "binaries-" + project + ".log", "a") \
                as gate_report:
            gate_report.write('Non Whitelisted Binary file: {0}\n'.
                              format(patch_file))
    else:
        # Check file names / extensions
        if file_audit_list.search(patch_file) and not \
                    file_audit_project_list.search(patch_file):
            match = file_audit_list.search(patch_file)
            logger.error('Blacklisted file: %s', patch_file)
            logger.error('Matched String: %s', match.group())
            failure = True
            with open(reports_dir + "file-names_" + project + ".log", "a") \
                    as gate_report:
                gate_report.write('Blacklisted file: {0}\n'.
                                  format(patch_file))
                gate_report.write('Matched String: {0}'.
                                  format(match.group()))

        # Open file to check for blacklisted content
        try:
            fo = open(patch_file, 'r')
            lines = fo.readlines()
            file_exists = True
        except IOError:
            file_exists = False

        if file_exists and not patch_file.endswith(tuple(file_ignore)):
            for line in lines:
                for key, value in flag_list.iteritems():
                    regex = value['regex']
                    desc = value['desc']
                    if re.search(regex, line) and not re.search(
                            ignore_list, line):
                        logger.error('File contains violation: %s', patch_file)
                        logger.error('Flagged Content: %s', line.rstrip())
                        logger.error('Rationale: %s', desc.rstrip())
                        failure = True
                        with open(reports_dir + "contents_" + project + ".log",
                                  "a") as gate_report:
                            gate_report.write('File contains violation: {0}\n'.
                                              format(patch_file))
                            gate_report.write('Flagged Content: {0}'.
                                              format(line))
                            gate_report.write('Matched Regular Exp: {0}\n'.
                                              format(regex))
                            gate_report.write('Rationale: {0}\n'.
                                              format(desc.rstrip()))


def process_failure():
    """ If any scan operations register a failure, sys.exit(1) is called
        to allow jjb to register a failure"""
    if failure:
        sys.exit(1)
