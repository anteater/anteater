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
import ipaddress
import logging
import hashlib
import six.moves.configparser
import os
import re
import sys
from time import sleep
from binaryornot.check import is_binary
from . import get_lists
from . import virus_total

logger = logging.getLogger(__name__)
config = six.moves.configparser.ConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')


def prepare_project(project, project_dir, binaries, ips, urls):
    """
    Generates blacklists / whitelists
    """

    # Get Various Lists / Project Waivers
    lists = get_lists.GetLists()

    # Get file name black list and project waivers
    file_audit_list, file_audit_project_list = lists.file_audit_list(project)

    # Get file content black list and project waivers
    flag_list, ignore_list = lists.file_content_list(project)

    # Get File Ignore Lists
    file_ignore = lists.file_ignore()

    ignore_directories = lists.ignore_directories(project)

    # Get URL Ignore Lists
    url_ignore = lists.url_ignore(project)

    # Get IP Ignore Lists
    ip_ignore = lists.ip_ignore(project)

    # Get Binary Ignore Lists
    hashlist = get_lists.GetLists()

    apikey = ""
    if binaries or ips or urls:
        try:
            apikey = os.environ["VT_KEY"]
        except KeyError:
            logger.error("Please set your virustotal.com API key as an environment variable")
            sys.exit(1)
        try:
            vt_rate_type = config.get('config', 'vt_rate_type')
        except six.moves.configparser.NoSectionError:
            logger.error("A config section is required for vt_rate_type with a public | private option")
            sys.exit(1)

        patten = re.compile(r'\bpublic\b|\bprivate\b')
        if not patten.match(vt_rate_type):
            logger.error("Unrecognized %s option for vt_rate_type", vt_rate_type)
            sys.exit(1)

    # Perform rudimentary scans
    issues_found = scan_file(project, project_dir, binaries, ips, urls, file_audit_list,
                             file_audit_project_list, flag_list, ignore_list, hashlist,
                             file_ignore, ignore_directories, url_ignore, ip_ignore, apikey)
    if issues_found:
        sys.exit(1)


def scan_file(project, project_dir, binaries, ips, urls, file_audit_list,
              file_audit_project_list, flag_list, ignore_list, hashlist,
              file_ignore, ignore_directories, url_ignore, ip_ignore, apikey):
    """
    Main scan tasks begin
    """
    logger.info("Commencing scan tasks..")
    issues_found = False
    for root, dirs, files in os.walk(project_dir):
        # Filter out ignored directories from list.
        for items in files:
            full_path = os.path.join(root, items)
            split_path = full_path.split(project + '/', 1)[-1]
            # Check for Blacklisted file names
            if not any(x in split_path for x in ignore_directories):
                if file_audit_list.search(full_path) and not \
                        file_audit_project_list.search(full_path):
                    match = file_audit_list.search(full_path)
                    logger.error('Blacklisted filename: %s', full_path)
                    logger.error('Matched String: %s', match.group())
                    issues_found = True
                    with open(reports_dir + "file-names_" + project + ".log", "a") as gate_report:
                        gate_report.write('Blacklisted filename: {0}\n'.format(full_path))
                        gate_report.write('Matched String: {0}'.format(match.group()))

                # Check if Binary is whitelisted
                if is_binary(full_path) and binaries:

                    split_path = full_path.split(project + '/', 1)[-1]
                    binary_hash = hashlist.binary_hash(project, split_path)
                    with open(full_path, 'rb') as afile:
                        hasher = hashlib.sha256()
                        buf = afile.read()
                        hasher.update(buf)
                        sha256hash = hasher.hexdigest()
                    if sha256hash in binary_hash:
                        logger.info('Found matching file hash for: %s', full_path)
                        logger.info('No further action needed for: %s', full_path)
                    else:
                        logger.info('Non Whitelisted Binary file: %s', full_path)
                        binary_issues_found = scan_binary(full_path, split_path, project, sha256hash, apikey)
                        issues_found = issues_found or binary_issues_found

                else:
                    if not items.endswith(tuple(file_ignore)) and not is_binary(full_path):
                        try:
                            fo = open(full_path, 'r')
                            lines = fo.readlines()
                        except IOError:
                            logger.error('%s does not exist', full_path)
                            lines = []
                        except UnicodeDecodeError:
                            logger.error('%s is not valid utf-8', full_path)
                            lines = []

                        for line in lines:
                            # Find IP Addresses and send for report to Virus Total
                            if ips:
                                ipaddr = re.findall(r'(?:\d{1,3}\.)+(?:\d{1,3})', line)
                                if ipaddr:
                                    ipaddr = ipaddr[0]
                                    if re.search(ip_ignore, ipaddr):
                                        logger.info('%s is in IP ignore list.', ipaddr)
                                    else:
                                        try:
                                            ipaddress.ip_address(ipaddr).is_global
                                            ipaddr_issues_found = scan_ipaddr(ipaddr, line, project, split_path, apikey)
                                            issues_found = issues_found or ipaddr_issues_found
                                        except:
                                            pass  # Ok to pass here, as this captures the odd string which is nt an IP Address

                            # Check for URLs and send for report to Virus Total
                            if urls:
                                url = re.search(r"(?P<url>https?://\S+)", line) or re.search(r"(?P<url>www\S+)", line)
                                if url:
                                    url = url.group("url")
                                    if re.search(url_ignore, url):
                                        logger.info('%s is in URL ignore list.', url)
                                    else:
                                        url_issues_found = scan_url(url, line, project, split_path, apikey)
                                        issues_found = issues_found or url_issues_found

                            # Check flagged content in files
                            for key, value in flag_list.items():
                                regex = value['regex']
                                desc = value['desc']
                                if re.search(regex, line) and not re.search(ignore_list, line):
                                    logger.error('File contains violation: %s', full_path)
                                    logger.error('Flagged Content: %s', line.rstrip())
                                    logger.error('Matched Regular Exp: %s', regex)
                                    logger.error('Rationale: %s', desc.rstrip())
                                    issues_found = True
                                    with open(reports_dir + "contents-" + project + ".log", "a") as gate_report:
                                        gate_report.write('File contains violation: {0}\n'.format(full_path))
                                        gate_report.write('Flagged Content: {0}'.format(line))
                                        gate_report.write('Matched Regular Exp: {0}'.format(regex))
                                        gate_report.write('Rationale: {0}\n'.format(desc.rstrip()))

    return issues_found


def scan_binary(full_path, split_path, project, sha256hash, apikey):
    """
    Sends Binary (sha256hash) to Virus Total API
    """
    v_api = virus_total.VirusTotal()

    while True:
        binary_report = v_api.binary_report(sha256hash, apikey)
        response_code = binary_report['response_code']

        # report does not exist, need to scan
        if response_code == 0:
            logger.info('Performing new scan of %s.', split_path)
            scan_file = v_api.scan_file(full_path, apikey)
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
        negative_report(binary_report, sha256hash, split_path, project, full_path)
        return False
    else:
        positive_report(binary_report, sha256hash, split_path, project, full_path)
        return True


def negative_report(binary_report, sha256hash, split_path, project, full_path):
    """
    If no match is made and file is clean
    """
    report_url = binary_report['permalink']
    scan_date = binary_report['scan_date']
    logger.info('File scan date for %s shows a clean status on: %s', split_path, scan_date)
    logger.info('Full report available here: %s', report_url)
    logger.info('The following sha256 hash can be used in your %s.yaml file to suppress this scan:', project)
    logger.info('%s:', sha256hash)
    with open(reports_dir + "binaries-" + project + ".log", "a") as gate_report:
        gate_report.write('Non Whitelisted Binary: {}\n'.format(full_path))
        gate_report.write('File scan date for {} shows a clean status on {}\n'.format(split_path, scan_date))
        gate_report.write('The following sha256 hash can be used in your {}.yaml file to suppress this scan:\n'.format(project))
        gate_report.write('{}\n'.format(sha256hash))


def positive_report(binary_report, sha256hash, split_path, project, full_path):
    """
    If a Positive match is found
    """
    report_url = binary_report['permalink']
    scan_date = binary_report['scan_date']
    logger.error("Virus Found!")
    logger.info('File scan date for %s shows a infected status on: %s', split_path, scan_date)
    logger.info('Full report available here: %s', report_url)
    with open(reports_dir + "binaries-" + project + ".log", "a") as gate_report:
        gate_report.write('Virus Found!: {}\n'.format(full_path))
        gate_report.write('File scan date for {} shows a infected status on: {}\n'.format(split_path, scan_date))
        gate_report.write('Full report avaliable here: {}\n'.format(report_url))


def scan_ipaddr(ipaddr, line, project, split_path, apikey):
    """
    If an IP Address is found, scan it
    """
    logger.info('Found what I believe is an IP Address: %s', line.strip())
    logger.info('File %s. Parsed IP Address: %s', split_path, ipaddr)
    with open(reports_dir + "ips-" + project + ".log", "a") as gate_report:
        gate_report.write('File {} contains what I believe is an IP Address: {}\n'.format(split_path, ipaddr))
    v_api = virus_total.VirusTotal()
    scan_ip = v_api.send_ip(ipaddr, apikey)
    response_code = scan_ip['response_code']
    verbose_msg = scan_ip['verbose_msg']
    urls = scan_ip['detected_urls']
    with open(reports_dir + "ips-" + project + ".log", "a") as gate_report:
        if urls:
            logger.error('%s has been known to resolve to the following malicious urls:', ipaddr)
            gate_report.write('{} has been known to resolve to the following malicious urls:\n'.format(ipaddr))

            for url in urls:
                logger.info('%s on date: %s', url['url'], url['scan_date'])
                gate_report.write('{} on {}\n'.format(url['url'], url['scan_date']))
                sleep(0.2)
            return True
        else:
            logger.info('No malicious DNS history found for: %s', ipaddr)
            gate_report.write('No malicious DNS history found for: {}\n'.format(ipaddr))
            return False


def scan_url(url, line, project, split_path, apikey):
    """
    If URL is found, scan it
    """
    logger.info('File %s contains what I believe is a URL: %s', split_path, line.strip())
    logger.info('Scanning: %s', url)
    with open(reports_dir + "urls-" + project + ".log", "a") as gate_report:
        gate_report.write('File {} contains what I believe is a URL: {}\n'.format(split_path, url))

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
                printed = False
                if results['detected']:
                    with open(reports_dir + "urls-" + project + ".log", "a") as gate_report:
                        logger.error("%s is recorded as a %s by %s", url, results['result'], site)
                        gate_report.write('{} is recorded as a {} by {}\n'.format(url, results['result'], site))
            if not printed:
                printed = True
                with open(reports_dir + "urls-" + project + ".log", "a") as gate_report:
                    logger.error("Full report available here: %s", url_report['permalink'])
                    gate_report.write('Full report available here: {}\n'.format(url_report['permalink']))
            return True

        else:
            logger.info("%s is recorded as a clean", url)
            with open(reports_dir + "urls-" + project + ".log", "a") as gate_report:
                gate_report.write('{} is recorded as a clean\n'.format(url))
            return False

    except:
        # No positives so we can pass this
        return False
