#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import sh
import yaml
import time

__author__ = "Luke Hinds"
__copyright__ = "Luke Hinds"
__license__ = "none"

with open('configs/anteater.yml', 'r') as ymlcfg:
    cfg = yaml.safe_load(ymlcfg)
    projects = (cfg['projects'])


def clone_all():
    # Progrss bar
    for project in projects:
        print('Cloning {0}.'.format(project))
        sh.git.clone('https://gerrit.opnfv.org/gerrit/{0}'.format(project))


def clone_project(project):
    print('Cloning: {0}'.format(project))
    sh.git.clone('https://gerrit.opnfv.org/gerrit/{0}'.format(project))


def pull_all(project):
    print('Cloning: {0}'.format(project))
    sh.git.clone(project)


def pull_project(project):
    print('Cloning: {0}'.format(project))
    sh.git.clone(project)


def audit_all(project):
        print('Cloning: {0}'.format(project))
        sh.git.clone(project)


def audit_project(project):
        print('Cloning: {0}'.format(project))
        sh.git.clone(project)


if __name__ == "__main__":
    project = 'https://github.com/lukehinds/dotfiles'
    clone_project(project)
