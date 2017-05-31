#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017 Luke Hinds <lhinds@redhat.com>, Red Hat
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
import anteater.utils.anteater_logger as antlog
import anteater.src.get_lists as get_lists
import ConfigParser
import sys
import re


logger = antlog.Logger(__name__).getLogger()
config = ConfigParser.RawConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')
failure = False


def prepare_patchset(project, patchset):
    """ Create black/white lists and default / project waivers
        and iterates over patchset file """

    # Get Various Lists / Project Waivers
    lists = get_lists.GetLists()
    # Get binary white list
    binary_list, binary_project_list = lists.binary_list(project)

    # Get file name black list and project waivers
    file_audit_list, file_audit_project_list = lists.file_audit_list(project)

    # Get file content black list and project waivers
    file_content_list, \
        file_content_project_list = lists.file_content_list(project)

    # Get Licence Lists
    licence_ext = lists.licence_extensions()
    licence_ignore = lists.licence_ignore()

    # Open patch set to get file list
    fo = open(patchset, 'r')
    lines = fo.readlines()

    for line in lines:
        patch_file = line.strip('\n')
        # Perform binary and file / content checks
        scan_patch(project, patch_file, binary_list, binary_project_list,
                   file_audit_list, file_audit_project_list,
                   file_content_list, file_content_project_list, licence_ext,
                   licence_ignore)

    # Process each file in patch set using waivers generated above
    # Process final result
    process_failure()


def scan_patch(project, patch_file, binary_list, binary_project_list,
               file_audit_list, file_audit_project_list, file_content_list,
               file_content_project_list, licence_ext, licence_ignore):
    """ Scan actions for each commited file in patch set """
    global failure
    if is_binary(patch_file):
        if not binary_list.search(patch_file) and not binary_project_list\
                .search(patch_file):
            logger.error('Non Whitelisted Binary file: {0}'.
                         format(patch_file))
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
            logger.error('Blacklisted file: {0}'.
                         format(patch_file))
            logger.error('Matched String: {0}'.
                         format(match.group()))
            failure = True
            with open(reports_dir + "file-names_" + project + ".log", "a") \
                    as gate_report:
                gate_report.write('Blacklisted file: {0}\n'.
                                  format(patch_file))
                gate_report.write('Matched String: {0}'.
                                  format(match.group()))

        # Open file to check for blacklisted content
        fo = open(patch_file, 'r')
        lines = fo.readlines()

        for line in lines:
            if file_content_list.search(line) and not \
                    file_content_project_list.search(line):
                match = file_content_list.search(line)
                logger.error('File contains violation: {0}'.
                             format(patch_file))
                logger.error('Flagged Content: {0}'.
                             format(line.rstrip()))
                logger.error('Matched String: {0}'.
                             format(match.group()))
                failure = True
                with open(reports_dir + "contents_" + project + ".log",
                          "a") as gate_report:
                    gate_report.write('File contains violation: {0}\n'.
                                      format(patch_file))
                    gate_report.write('Flagged Content: {0}'.
                                      format(line))
                    gate_report.write('Matched String: {0}\n'.
                                      format(match.group()))

        # Run license check
        licence_check(project, licence_ext, licence_ignore, patch_file)


def licence_check(project, licence_ext,
                  licence_ignore, patch_file):
    """ Performs licence checks """
    global failure
    if patch_file.endswith(tuple(licence_ext)) \
            and patch_file not in licence_ignore:
        fo = open(patch_file, 'r')
        content = fo.read()
        # Note: Hardcoded use of 'copyright' & 'spdx' is the result
        # of a decision made at 2017 plugfest to limit searches to
        # just these two strings.
        if re.search("copyright", content, re.IGNORECASE):
            logger.info('Contains needed Licence string: {0}'.
                        format(patch_file))
        elif re.search("spdx", content, re.IGNORECASE):
            logger.info('Contains needed Licence string: {0}'.
                        format(patch_file))
        else:
            logger.error('Licence header missing in file: {0}'.
                         format(patch_file))
            failure = True
            with open(reports_dir + "licence-" + project + ".log", "a") \
                    as gate_report:
                gate_report.write('Licence header missing in file: {0}\n'.
                                  format(patch_file))


def process_failure():
    """ If any scan operations register a failure, sys.exit(1) is called
        to allow jjb to register a failure"""
    if failure:
        logger.error('Failures registered')
        sys.exit(1)
