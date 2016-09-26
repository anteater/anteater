#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import sh
import anteater.utils.anteater_logger as antlog

logger = antlog.Logger(__name__).getLogger()
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'


def scan_all(reports_dir, repos_dir):
    scanner = ''
    for project in os.listdir(repos_dir):
        scan_project(reports_dir, project, scanner, repos_dir)


def scan_project(reports_dir, project, scanner, repos_dir):
    """ Passed project name and declares repo directory 'projdir'.
    Performs recursive search to find file extensions.
    When extension matches, it breaks loop with True and runs related scanner
    """
    py = False
    java = False
    c = False
    projdir = repos_dir + project
    if scanner:
        if scanner == 'bandit':
            run_bandit(reports_dir, project, projdir)
        elif scanner == 'pmd':
            run_pmd(reports_dir, project, projdir)
        elif scanner == 'rats':
            run_rats(reports_dir, project, projdir)
        else:
            logger.error("%s is not a recognised scanner tool", scanner)
    else:
        """Let's try to guess which scanner to use, by file extension"""
        for root, dirs, files in os.walk(projdir):
            for file in files:
                if file.endswith(".c"):
                    c = True
                elif file.endswith(".py"):
                    py = True
                elif file.endswith(".java"):
                    java = True
        # Project contains only python files
        if py and not (java or c):
            run_bandit(reports_dir, project, projdir)
        # Project contains c files
        if c and not (java):
            run_rats(reports_dir, project, projdir)
        # Project contains only java files
        if java and not (py or c):
            run_pmd(reports_dir, project, projdir)
        # Project contains a mix of c and python
        if c and py and not (java):
            run_rats(reports_dir, project, projdir)


def run_bandit(reports_dir, project, projdir):
    """Run's Bandit Python Scanner"""
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Bandit Scan on: {0}'.format(projdir))
    try:
        sh.bandit('-r', '-f', 'html', '-o', reports_dir + report, projdir)
    except sh.ErrorReturnCode, e:
        # logger.error(e.stderr)
        pass


def run_rats(reports_dir, project, projdir):
    """Run's RATS C / Python Scanner"""
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Rats Scan on: {0}'.format(projdir))
    try:
        sh.rats('--html', projdir, '>', _out=(reports_dir + report))
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


# Change to direct java call
def run_pmd(reports_dir, project, projdir):
    """Run's PMD Java Scanner"""
    report = ('{0}_report.html'.format(project))
    logger.info('Performing PMD Scan on: {0}'.format(projdir))
    try:
        sh.command(wk_dir + 'anteater/utils/pmd/bin/run.sh', 'pmd', '-dir',
                   projdir, '-f', 'html', '-rulesets', 'java-basic',
                   '-reportfile', reports_dir + report)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
