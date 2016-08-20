#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import sh
import yaml

__author__ = "Luke Hinds"
__copyright__ = "Luke Hinds"
__license__ = "none"

with open('configs/projects.yml', 'r') as ymlcfg:
    cfg = yaml.safe_load(ymlcfg)
    projects = (cfg['projects'])


def url_formatter(arg):
    pass


def clone_all():
    # Progrss bar
    for project in projects:
        print('Cloning {0}.'.format(project))
        # Lets move the below gerrit url to a variable
        url = 'https://gerrit.opnfv.org/gerrit/{0}'.format(project)
        projdir = 'repos/{0}'.format(project)
        try:
            sh.git.clone(url, projdir)
        except sh.ErrorReturnCode, e:
            print(e.stderr)


def clone_project(project):
    print('Cloning: {0}'.format(project))
    url = 'https://gerrit.opnfv.org/gerrit/{0}'.format(project)
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git.clone(url, projdir)
    except sh.ErrorReturnCode, e:
        print(e.stderr)


def pull_all():
    for project in projects:
        print('Performing pull on: {0}'.format(project))
        projdir = 'repos/{0}'.format(project)
        try:
            sh.git('-C', projdir, 'pull')
        except sh.ErrorReturnCode, e:
            print(e.stderr)


def pull_project(project):
    print('Performing pull on: {0}'.format(project))
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git('-C', projdir, 'pull')
    except sh.ErrorReturnCode, e:
        print(e.stderr)
