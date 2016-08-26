#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import sh
import yaml
import anteater.utils.anteater_logger as antlog

logger = antlog.Logger(__name__).getLogger()
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'

with open('configs/projects.yml', 'r') as ymlcfg:
    cfg = yaml.safe_load(ymlcfg)
    projects = (cfg['projects'])


def scan_all(reports_dir):
    for project in projects:
        scan_project(reports_dir, project)


def scan_project(reports_dir, project):
    '''
    Passed project name and declares repo directory 'projdir'.
    Performs recursive search to find file extensions.
    When extension matches, it breaks loop with True and runs related scanner
    '''
    py = False
    shell = False
    java = False
    c = False
    projdir = 'repos/{0}'.format(project)
    for dirname, dirnames, filenames in os.walk(projdir):
        for filename in filenames:
            if filename.endswith('.c'):
                c = True
                # break
            elif filename.endswith('.py'):
                py = True
                # break
            elif filename.endswith('.sh'):
                shell = True
                # break
            elif filename.endswith('.java'):
                java = True
                # break

    if c and py:
        run_rats(reports_dir, project, projdir)
    elif java and py:
            run_pmd(reports_dir, project, projdir)
    elif py:
        run_bandit(reports_dir, project, projdir)
    elif shell:
        pass


def run_bandit(reports_dir, project, projdir):
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Bandit Scan on: {0}'.format(projdir))
    try:
        sh.bandit('-r', '-f', 'html', '-o', reports_dir + report, projdir)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def run_rats(reports_dir, project, projdir):
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Rats Scan on: {0}'.format(projdir))
    try:
        sh.rats('--html', projdir, '>', _out=(reports_dir + report))
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


# Change to direct java call
def run_pmd(reports_dir, project, projdir):
    report = ('{0}_report.html'.format(project))
    logger.info('Performing PMD Scan on: {0}'.format(projdir))
    try:
        sh.command(wk_dir + 'anteater/utils/pmd/bin/run.sh', 'pmd', '-dir',
                   wk_dir + projdir, '-f', 'html', '-rulesets', 'java-basic',
                   '-reportfile', reports_dir + report)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
