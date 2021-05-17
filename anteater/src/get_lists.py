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
    Gathers various values from the gate check yaml file and return them to the
    calling instance
"""
from __future__ import absolute_import
import collections
import logging
import six.moves.configparser
import copy
import re
import yaml
import sys


config = six.moves.configparser.ConfigParser()
config.read('anteater.conf')
logger = logging.getLogger(__name__)
anteater_files = config.get('config', 'anteater_files')
flag_list = config.get('config', 'flag_list')
ignore_list = config.get('config', 'ignore_list')
ignore_dirs = ['.git', anteater_files]

try:
    with open(flag_list, 'r') as f:
        fl = yaml.safe_load(f)
except IOError:
    logger.error('File not found: %s', ignore_list)
    sys.exit(0)
try:
    with open(ignore_list, 'r') as f:
        il = yaml.safe_load(f)
except IOError:
    logger.error('File not found: %s', ignore_list)
    sys.exit(0)


def unique(sequence):
    return list(set(sequence))


def _remove_nullvalue(contents):
    """ Removes nullvalue placeholders required to prevent key errors"""
    if contents and len(contents) > 2 and 'nullvalue' in contents:
        contents.remove('nullvalue')


class GetLists(object):
    def __init__(self, *args):
        self.args = args
        self.loaded = False

    def load_project_flag_list_file(self, project_exceptions, project):
        """ Loads project specific lists """
        if self.loaded:
            return
        exception_file = None
        for item in project_exceptions:
            if project in item:
                exception_file = item.get(project)
        if exception_file is not None:
            try:
                with open(exception_file, 'r') as f:
                    ex = yaml.safe_load(f)
            except IOError:
                logger.error('File not found: %s', exception_file)
                sys.exit(0)
            for key in ex:
                if key in fl:
                    fl[key][project] = _merge(fl[key][project], ex.get(key, None)) \
                        if project in fl[key] else ex.get(key, None)
            self.loaded = True
        else:
            logger.info('%s not found in %s', project, ignore_list)
            logger.info('No project specific exceptions will be applied')

    def load_project_ignore_list_file(self, project_exceptions, project):
        """ Loads project specific ignore lists """
        if self.loaded:
            return
        exception_file = None
        for item in project_exceptions:
            if project in item:
                exception_file = item.get(project)
            else:
                logger.info('%s not found in %s', project, ignore_list)
                sys.exit(0)
        if exception_file is not None:
            try:
                with open(exception_file, 'r') as f:
                    ex = yaml.safe_load(f)
            except IOError:
                logger.error('File not found: %s', exception_file)
                sys.exit(0)

            ex.pop('ignore_directories', None)

            for key in ex:
                if key in il:
                    il[key][project] = _merge(il[key][project], ex.get(key, None)) \
                        if project in il[key] else ex.get(key, None)
            self.loaded = True
        else:
            logger.info('%s not found in %s', project, ignore_list)
            logger.info('No project specific exceptions will be applied')

    def binary_hash(self, project, patch_file):
        """ Gathers sha256 hashes from binary lists """
        global il
        try:
            project_exceptions = il.get('project_exceptions')
        except KeyError:
            logger.info('project_exceptions missing in %s for %s', ignore_list, project)
            project_exceptions = []

        for project_files in project_exceptions:
            if project in project_files:
                exception_file = project_files.get(project)
                with open(exception_file, 'r') as f:
                    bl = yaml.safe_load(f)

                for key, value in bl.items():
                    if key == 'binaries':
                        if patch_file in value:
                            hashvalue = value[patch_file]
                            return hashvalue
                        else:
                            for key, value in il.items():
                                if key == 'binaries':
                                    if patch_file in value:
                                        hashvalue = value[patch_file]
                                        return hashvalue
                                    else:
                                        hashvalue = ""
                                        return hashvalue
            else:
                logger.info('%s not found in %s', project, ignore_list)
                logger.info('No project specific exceptions will be applied')
                hashvalue = ""
                return hashvalue

    def file_audit_list(self, project):
        """ Gathers file name lists """
        self.load_project_flag_list_file(il.get('project_exceptions'), project)
        try:
            default_list = set((fl['file_audits']['file_names']))
        except KeyError:
            logger.warning('No file_names found')
            default_list = set()
        try:
            project_list = set((fl['file_audits'][project]['file_names']))
            logger.info('Loaded %s specific file_audits entries', project)
        except KeyError:
            logger.info('No project specific file_names section for project %s', project)
            project_list = set()

        file_names_re = re.compile("|".join(default_list),
                                   flags=re.IGNORECASE)

        if project_list:
            file_names_proj_re = re.compile("|".join(project_list),
                                            flags=re.IGNORECASE)
            return file_names_re, file_names_proj_re
        else:
            file_names_proj_re = re.compile("")
            return file_names_re, file_names_proj_re

    def file_content_list(self, project):
        """ gathers content strings """
        self.load_project_flag_list_file(il.get('project_exceptions'), project)
        try:
            flag_list = (fl['file_audits']['file_contents'])
        except KeyError:
            logger.warning('No file_contents found')
            flag_list = {}

        try:
            ignore_list = il['file_audits']['file_contents']
        except KeyError:
            logger.warning('No file_contents ignore list found')
            ignore_list = []

        try:
            project_list = fl['file_audits'][project]['file_contents']
            logger.info('Loaded %s specific file_contents entries', project)
        except KeyError:
            logger.info('No project specific file_contents section for project %s', project)
            project_list = []

        if project_list:
            ignore_list_merge = project_list + ignore_list

            ignore_list_re = re.compile("|".join(ignore_list_merge), flags=re.IGNORECASE)

            return flag_list, ignore_list_re
        else:
            ignore_list_re = re.compile("|".join(ignore_list),
                                        flags=re.IGNORECASE)
            return flag_list, ignore_list_re

    def ignore_directories(self, project):
        """ Gathers a list of directories to ignore """
        project_list = []
        try:
            ignore_directories = il['ignore_directories']
        except KeyError:
            logger.warning('No ignore_directories found')
            ignore_directories = []

        try:
            project_exceptions = il.get('project_exceptions')
            for item in project_exceptions:
                if project in item:
                    exception_file = item.get(project)
                    with open(exception_file, 'r') as f:
                        test_list = yaml.safe_load(f)
                        project_list = test_list['ignore_directories']
        except KeyError:
            logger.info('No ignore_directories for %s', project)

        if project_list:
            ignore_directories = ignore_directories + project_list
        return ignore_directories + ignore_dirs

    def url_ignore(self, project):
        """ Gathers a list of URLs to ignore """
        project_list = []
        try:
            url_ignore = il['url_ignore']
        except KeyError:
            logger.warning('No url_ignore found')
            url_ignore = []

        try:
            project_exceptions = il.get('project_exceptions')
            for item in project_exceptions:
                if project in item:
                    exception_file = item.get(project)
                    with open(exception_file, 'r') as f:
                        url_list = yaml.safe_load(f)
                        project_list = url_list['url_ignore']
        except KeyError:
            logger.info('No url_ignore for %s', project)

        if project_list:
            url_ignore = url_ignore + project_list
            url_ignore_re = re.compile("|".join(url_ignore), flags=re.IGNORECASE)
            return url_ignore_re
        else:
            url_ignore_re = re.compile("|".join(url_ignore), flags=re.IGNORECASE)
            return url_ignore_re

    def ip_ignore(self, project):
        """ Gathers a list of URLs to ignore """
        project_list = []
        try:
            ip_ignore = il['ip_ignore']
        except KeyError:
            logger.warning('No ip_ignore found')
            ip_ignore = []

        try:
            project_exceptions = il.get('project_exceptions')
            for item in project_exceptions:
                if project in item:
                    exception_file = item.get(project)
                    with open(exception_file, 'r') as f:
                        ip_list = yaml.safe_load(f)
                        project_list = ip_list['ip_ignore']
        except KeyError:
            logger.info('No ip_ignore for %s', project)

        if project_list:
            ip_ignore = ip_ignore + project_list
            ip_ignore_re = re.compile("|".join(ip_ignore), flags=re.IGNORECASE)
            return ip_ignore_re
        else:
            ip_ignore_re = re.compile("|".join(ip_ignore), flags=re.IGNORECASE)
            return ip_ignore_re

    def file_ignore(self):
        """ Gathers a list of files to ignore """
        try:
            file_ignore = (il['file_ignore'])
        except KeyError:
            logger.warning('No file_ignore found')
            return {}
        return file_ignore

    def report_url(self, project):
        project_report_url = False
        report_url = False
        try:
            project_exceptions = il.get('project_exceptions')
            for item in project_exceptions:
                if project in item:
                    exception_file = item.get(project)
                    with open(exception_file, 'r') as f:
                        report_list = yaml.safe_load(f)
                        project_report_url = report_list['report_url']
        except KeyError:
            logger.info('No report_url for %s', project)

        try:
            report_url = il['report_url']
        except KeyError:
            logger.warning('No report_url found')

        if project_report_url:
            return project_report_url
        elif report_url:
            return report_url
