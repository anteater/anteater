#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import sh
import yaml

__author__ = "Luke Hinds"
__copyright__ = "Luke Hinds"
__license__ = "none"


with open('configs/anteater.yml', 'r') as ymlcfg:
    cfg = yaml.safe_load(ymlcfg)
    projects = (cfg['projects'])


def audit_all():
    for project in projects:
        print('Scanning {0}.'.format(project))


def audit_project(project):
    # Counter for the amount of Python Files
    py = 0
    # Counter for the amount of shell scripts
    shell = 0
    # Counter for the amount of Java files
    java = 0
    # Counter for the amount of C source files
    c = 0
    projdir = 'repos/{0}'.format(project)
    for dirname, dirnames, filenames in os.walk(projdir):
        for filename in filenames:
            # check if python file
            if filename.endswith('.py'):
                py = py + 1
                break
            elif filename.endswith('.sh'):
                shell = shell + 1
                break
            elif filename.endswith('.java'):
                java = java + 1
                break
            elif filename.endswith('.c'):
                c = c + 1
                break
    if py > 1:
        run_bandit(project, projdir)


def run_bandit(project, projdir):
    report = ('{0}_report.html'.format(project))
    print ('Performing Bandit Scan on: {0}'.format(projdir))
    try:
        sh.bandit('-r', '-f', 'html', '-o', report, projdir)
    except sh.ErrorReturnCode_1:
        pass
