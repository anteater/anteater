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
    Gathers various values from the gate check yaml file and return them to the
    calling instance
"""

import anteater.utils.anteater_logger as antlog
import ConfigParser
import yaml
import re

config = ConfigParser.RawConfigParser()
config.read('anteater.conf')
logger = antlog.Logger(__name__).getLogger()
gate_checks = config.get('config', 'gate_checks')

with open(gate_checks, 'r') as f:
    yl = yaml.safe_load(f)


class GetLists(object):
    def __init__(self, *args):
        # Placeholder for future args if more filters are needed
        self.args = args

    def binary_list(self, project):
        project_list = False
        try:
            default_list = (yl['binaries']['binary_ignore'])
        except KeyError:
            logger.error('Key Error processing binary list values')
        try:
            project_list = (yl['binaries'][project]['binary_ignore'])
        except KeyError:
            logger.info('No binary waivers found for {0}'.
                        format(project))

        binary_re = re.compile("|".join(default_list),
                flags=re.IGNORECASE)

        if project_list:
            binary_project_re = re.compile("|".join(project_list),
                                           flags=re.IGNORECASE)
            return binary_re, binary_project_re
        else:
            binary_project_re = re.compile("")
            return binary_re, binary_project_re

    def file_audit_list(self, project):
        project_list = False
        try:
            default_list = set((yl['file_audits']['file_names']))
        except KeyError:
            logger.error('Key Error processing file_names list values')
        try:
            project_list = set((yl['file_audits'][project]['file_names']))
            logger.info('file_names waivers found for {0}'.
                        format(project))
        except KeyError:
            logger.info('No file_names waivers found for {0}'.
                        format(project))

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
        try:
            default_list = set((yl['file_audits']['file_contents']))
        except KeyError:
            logger.error('Key Error processing file_contents list values')
        try:
            project_list = set((yl['file_audits'][project]['file_contents']))
        except KeyError:
            logger.info('No file_contents waivers found  for {0}'.
                        format(project))

        file_contents_re = re.compile("|".join(default_list),
                                      flags=re.IGNORECASE)

        if project_list:
            file_contents_proj_re = re.compile("|".join(project_list),
                                               flags=re.IGNORECASE)
            return file_contents_re, file_contents_proj_re
        else:
            file_contents_proj_re = re.compile("")
            return file_contents_re, file_contents_proj_re

    def licence_extensions(self):
        try:
            licence_extensions = (yl['licence']['licence_ext'])
        except KeyError:
            logger.error('Key Error processing licence_extensions list values')
        return licence_extensions

    def licence_ignore(self):
        try:
            licence_ignore = (yl['licence']['licence_ignore'])
        except KeyError:
            logger.error('Key Error processing licence_ignore list values')
        return licence_ignore
