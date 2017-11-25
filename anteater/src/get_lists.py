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

import logging
import six.moves.configparser
import copy
import yaml
import re

config = six.moves.configparser.SafeConfigParser()
config.read('anteater.conf')
logger = logging.getLogger(__name__)
anteater_files = config.get('config', 'anteater_files')
flag_list = config.get('config', 'flag_list')
ignore_list = config.get('config', 'ignore_list')
ignore_dirs = ['.git', 'examples', anteater_files]

with open(flag_list, 'r') as f:
    fl = yaml.safe_load(f)

with open(ignore_list, 'r') as f:
    il = yaml.safe_load(f)


def _remove_nullvalue(contents):
    if contents and len(contents) > 2 and 'nullvalue' in contents:
        contents.remove('nullvalue')


def _merge(org, ded):
    ret = copy.deepcopy(org)
    for key in list(set([k for k in org] + [k for k in ded])):
        if key in org and key in ded:
            ret[key] = list(set(ret[key] + ded[key]))
            _remove_nullvalue(ret[key])
        elif key in ded:
            ret[key] = ded[key]
    return ret


class GetLists(object):
    def __init__(self, *args):
        # Placeholder for future args if more filters are needed
        self.args = args
        self.loaded = False

    def load_project_exception_file(self, project_exceptions, project):
        if self.loaded:
            return
        exception_file = None
        for item in project_exceptions:
            if project in item:
                exception_file = item.get(project)
        if exception_file is not None:
            with open(exception_file, 'r') as f:
                ex = yaml.safe_load(f)
            for key in ex:
                if key in fl:
                    fl[key][project] = _merge(fl[key][project], ex.get(key, None)) \
                            if project in fl[key] else ex.get(key, None)
            self.loaded = True

    def load_binary_exception_file(self, project_exceptions, project):
        if self.loaded:
            return
        exception_file = None
        for item in project_exceptions:
            if project in item:
                exception_file = item.get(project)
        if exception_file is not None:
            with open(exception_file, 'r') as f:
                ex = yaml.safe_load(f)
            for key in ex:
                if key in il:
                    il[key][project] = _merge(il[key][project], ex.get(key, None)) \
                            if project in il[key] else ex.get(key, None)
            self.loaded = True

    def binary_hash(self, project, patch_file):
        self.load_binary_exception_file(il.get('project_exceptions'), project)

        try:
            main_binary_hash = (il['binaries'][patch_file])
        except KeyError:
            main_binary_hash = []

        try:
            project_binary_hash = (il['binaries'][project][patch_file])
        except KeyError:
            project_binary_hash = []

        if main_binary_hash and project_binary_hash :
            logger.error('Warning: You have two hash entries for the %s file',
                         patch_file)
            logger.error('Check for duplicate entries in %s and %s.yaml for %s',
                         ignore_list, project, patch_file)

        new_list = main_binary_hash + project_binary_hash
        return new_list

    def file_audit_list(self, project):
        project_list = False
        self.load_project_exception_file(il.get('project_exceptions'), project)
        try:
            default_list = set((fl['file_audits']['file_names']))
        except KeyError:
            logger.error('Key Error processing file_names list values')
        try:
            project_list = set((fl['file_audits'][project]['file_names']))
            logger.info('file_names waivers found for %s', project)
        except KeyError:
            logger.info('No file_names waivers found for %s', project)

        file_names_re = re.compile("|".join(default_list),
                                   flags=re.IGNORECASE)

        if project_list:
            file_names_proj_re = re.compile("|".join(project_list),
                                            flags=re.IGNORECASE)
            return file_names_re, file_names_proj_re
        else:
            file_names_proj_re = re.compile("")
            return file_names_re, file_names_proj_re

    def file_content_list(self,  project):
        project_list = False
        self.load_project_exception_file(il.get('project_exceptions'), project)
        try:
            flag_list = (fl['file_audits']['file_contents'])

        except KeyError:
            logger.error('Key Error processing file_contents list values')

        try:
            ignore_list = il['file_audits']['file_contents']

        except KeyError:
            logger.error('Key Error processing file_contents list values')

        try:
            project_list = fl['file_audits'][project]['file_contents']

        except KeyError:
            logger.info('No file_contents waivers found  for %s', project)

        if project_list:
            ignore_list_merge = project_list + ignore_list

            ignore_list_re = re.compile("|".join(ignore_list_merge), flags=re.IGNORECASE)

            return flag_list, ignore_list_re
        else:
            ignore_list_re = re.compile("|".join(ignore_list),
                                        flags=re.IGNORECASE)
            return flag_list, ignore_list_re

    def file_ignore(self):
        try:
            file_ignore = (il['file_ignore'])
        except KeyError:
            logger.error('Key Error processing file_ignore list values')
        return file_ignore
