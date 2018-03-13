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
import ipaddress
import json
import logging
import hashlib
import six.moves.configparser
import sys
import os
import re
import time
from binaryornot.check import is_binary
from . import get_lists
from . import virus_total

logger = logging.getLogger(__name__)
config = six.moves.configparser.SafeConfigParser()
config.read('anteater.conf')
anteater_files = config.get('config', 'anteater_files')
reports_dir = config.get('config', 'reports_dir')

failure = False
hasher = hashlib.sha256()

def prepare_patchset(project, patchset,  bincheck, ips, urls):
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

    ignore_directories = lists.ignore_directories(project)

    if bincheck or ips or urls:
        try:  
            apikey = os.environ["VT_KEY"]
        except KeyError: 
            logger.error("Please set your virustotal.com API key as an environment variable")
            sys.exit(1)
        try:
            vt_rate_type = config.get('config', 'vt_rate_type')
        except six.moves.configparser.NoSectionError:
            logger.error("A config section is required for vt_rate_type with a public | private option ")
            sys.exit(1)

        patten = re.compile(r'\bpublic\b|\bprivate\b')
        if not patten.match(vt_rate_type):
            logger.error("Unrecognized %s option for vt_rate_type", vt_rate_type)
            sys.exit(1)

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
        scan_patch(project, patch_file, bincheck, ips, urls, file_audit_list,
                   file_audit_project_list, flag_list, ignore_list,
                   file_ignore, ignore_directories, apikey)

    # Process final result
    process_failure()


def scan_patch(project, patch_file, bincheck, ips, urls, file_audit_list,
               file_audit_project_list, flag_list, ignore_list, file_ignore,
               ignore_directories, apikey):

    """ 
    Scan actions for each commited file in patch set
    """
    global failure
    split_path = patch_file.split(project + '/', 1)[-1]

    if not any(x in split_path for x in ignore_directories):
        if is_binary(patch_file) and bincheck:
            hashlist = get_lists.GetLists()
            binary_hash = hashlist.binary_hash(project, split_path)
            with open(patch_file, 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
                sha256hash = hasher.hexdigest()
                
            if sha256hash in binary_hash:
                logger.info('Found matching file hash for: %s',
                            patch_file)
            else:
                logger.error('Non Whitelisted Binary file: %s',
                             patch_file)
                
                scan_binary(patch_file, project, sha256hash, apikey) 
                # logger.error('Submit patch with the following hash: %s',
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
            if not is_binary(patch_file):
                try:
                    fo = open(patch_file, 'r')
                    lines = fo.readlines()
                    file_exists = True
                except IOError:
                    file_exists = False

                if file_exists and not patch_file.endswith(tuple(file_ignore)):
                    for line in lines:
                        # Find IP Addresses and send for report to Virus Total
                        if ips:
                            ipaddr = re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line)
                            if ipaddr:
                                ipaddr = ipaddr[0]
                                try:
                                    ipaddress.ip_address(ipaddr).is_global
                                    scan_ipaddr(ipaddr, apikey)
                                except:
                                    pass # Ok to pass here, as this captures 
                                             # the odd string which is not an IP Address
                            
                        # Check for URLs and send for report to Virus Total
                        if urls:
                            url = re.search("(?P<url>https?://[^\s]+)", line) or re.search("(?P<url>www[^\s]+)", line)
                            if url:
                                url = url.group("url")
                                scan_url(url, apikey)

                        # Perform search within text files
                        for key, value in flag_list.items():
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

def scan_binary(patch_file, project, sha256hash, apikey):
    """
    Sends Binary (sha256hash) to Virus Total API
    """
    v_api = virus_total.VirusTotal()

    while True:
        binary_report = v_api.binary_report(sha256hash, apikey)
        response_code = binary_report['response_code']
    
        # report does not exist, need to scan
        if response_code == 0:
            logger.info('Performing new scan of %s.', patch_file)
            scan_file = v_api.scan_file(patch_file, apikey)
            logger.info('VirusTotal Response: %s', scan_file['verbose_msg'])
            logger.info('Report will be rendered at: %s', scan_file['permalink'])
            binary_report = v_api.binary_report(sha256hash, apikey)

        # Item is still queued
        if response_code == -2:
            logger.info('Report job still queued..')

        if response_code == 1:
            logger.info('Report found, job complete.')
            break

    positives = binary_report['positives']

    if positives == 0:
        negative_report(binary_report,sha256hash, project, patch_file)
    else:
        positive_report(binary_report,sha256hash, project, patch_file)

def negative_report(binary_report,sha256hash, project, patch_file):
    """
    If no match is made and file is clean
    """
    report_url = binary_report['permalink']
    scan_date = binary_report['scan_date'] # build conditional
    logger.info('File scan date for %s shows a clean status on: %s', patch_file, scan_date)
    logger.info('Full report avaliable here: %s', report_url)
    logger.info('The following sha256 hash can be used in your %s.yaml file to suppress this scan:', project)
    logger.info('%s:', sha256hash)
    with open(reports_dir + "binaries-" + project + ".log",
                    "a") as gate_report:
                gate_report.write('Non Whitelisted Binary: {}\n'.
                                    format(patch_file))
                gate_report.write('File scan date for {} shows a clean status on {}\n'.
                                    format(patch_file, scan_date))
                gate_report.write('The following sha256 hash can be used in your {}.yaml file to suppress this scan:\n'.
                                    format(project))
                gate_report.write('{}\n'.
                                    format(sha256hash))

def positive_report(binary_report,sha256hash, project, patch_file):
    """
    If a Positive match is found
    """ 
    failure = True
    report_url = binary_report['permalink']
    scan_date = binary_report['scan_date'] # build conditional
    logger.error("Virus Found!")
    logger.info('File scan date for %s shows a infected status on: %s', patch_file, scan_date)
    logger.info('Full report avaliable here: %s', report_url)

def scan_ipaddr(ipaddr, apikey):
    """
    If an IP Address is found, scan it
    """
    logger.info('Query VirusTotal API for Public IP Found: %s', ipaddr)
    v_api = virus_total.VirusTotal()
    scan_ip = v_api.send_ip(ipaddr, apikey)
    response_code = scan_ip['response_code']
    verbose_msg = scan_ip['verbose_msg']
    urls = scan_ip['detected_urls']

    if urls:
        failure = True
        logger.error('%s has been known to resolve to malicious urls', ipaddr)
        for url in urls:
            logger.info('URL: %s',url)
    else:
        logger.info('%s has no record of resolving to malicious urls', ipaddr)

def scan_url(url, apikey):
    """
    If URL is found, scan it
    """
    logger.info('Found what I believe is a URL: %s', url)
    v_api = virus_total.VirusTotal()
    while True:
        url_report = v_api.url_report(url, apikey)
        response_code = url_report['response_code']

        # report does not exist, need to scan
        if response_code == -2:
            logger.info('Report job still queued..')

        if response_code == 0:
            logger.info('No report  for %s', url)
            break

        if response_code == 1:
            logger.info('Report found, job complete for %s.', url)
            break

    try:
        positives = url_report['positives']
        if positives > 0:
            for site, results in url_report['scans'].items():
                if results['detected']:
                    detected = True
                    failure = True
                    logger.error("%s is recorded as a %s by %s", url, results['result'], site)
            if detected:
                logger.error("Full report available here: %s", url_report['permalink'])
        else:
            logger.info("%s is recorded as a clean", url)
    except:
        pass
    
def process_failure():
    """
    If any scan operations register a failure, sys.exit(1) is called
    to allow build to register a failure
    """
    if failure:
        sys.exit(1)
