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
import os
import yaml
import re


config = six.moves.configparser.RawConfigParser()
config.read('anteater.conf')
logger = logging.getLogger(__name__)
master_list = config.get('config', 'master_list')
ignore_list = config.get('config', 'ignore_list')

with open(master_list, 'r') as f:
    ml = yaml.safe_load(f)

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
                if key in ml:
                    ml[key][project] = _merge(ml[key][project], ex.get(key, None)) \
                            if project in ml[key] else ex.get(key, None)
            self.loaded = True

    def binary_list(self, project):
        try:
            default_list = (ml['binaries']['binary_ignore'])
        except KeyError:
            logger.error('Key Error processing binary list values')

        binary_re = re.compile("|".join(default_list),
                               flags=re.IGNORECASE)
        return binary_re

    def binary_hash(self, project, patch_file):
        self.load_project_exception_file(ml.get('project_exceptions'), project)
        file_name = os.path.basename(patch_file)
        try:
            binary_hash = (ml['binaries'][project][file_name])
            return binary_hash
        except KeyError:
            binary_hash = 'null'
            return binary_hash


    def file_audit_list(self, project):
        project_list = False
        self.load_project_exception_file(ml.get('project_exceptions'), project)
        try:
            default_list = set((ml['file_audits']['file_names']))
        except KeyError:
            logger.error('Key Error processing file_names list values')
        try:
            project_list = set((ml['file_audits'][project]['file_names']))
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
        self.load_project_exception_file(ml.get('project_exceptions'), project)
        try:
            master_list = (ml['file_audits']['file_contents'])

        except KeyError:
            logger.error('Key Error processing file_contents list values')

        try:
            ignore_list = il['file_audits']['file_contents']

        except KeyError:
            logger.error('Key Error processing file_contents list values')

        try:
            project_list = ml['file_audits'][project]['file_contents']

        except KeyError:
            logger.info('No file_contents waivers found  for %s', project)

        ignore_list_merge = project_list + ignore_list

        ignore_list_re = re.compile("|".join(ignore_list_merge), flags=re.IGNORECASE)

        return master_list, ignore_list_re

    def file_ignore(self):
        try:
            file_ignore = (ml['file_ignore'])
        except KeyError:
            logger.error('Key Error processing file_ignore list values')
        return file_ignore

    def licence_extensions(self):
        try:
            licence_extensions = (ml['licence']['licence_ext'])
        except KeyError:
            logger.error('Key Error processing licence_extensions list values')
        return licence_extensions

    def licence_ignore(self):
        try:
            licence_ignore = (ml['licence']['licence_ignore'])
        except KeyError:
            logger.error('Key Error processing licence_ignore list values')
        return licence_ignore
