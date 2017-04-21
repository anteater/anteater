#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import sys
import re
import sh
import yaml
import anteater.utils.anteater_logger as antlog
from binaryornot.check import is_binary

logger = antlog.Logger(__name__).getLogger()
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'
licence_templates = os.path.join(wk_dir + 'licence-templates.yaml')

def scan_all(reports_dir, repos_dir):
    """ As it says on the tin. Performs complete scan of allocated
    repos found under `repos_dir`"""
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
    rb = False
    php = False
    perl = False
    projdir = repos_dir + project
    # Perform rudimentary scans
    run_binfind(project, projdir)
    run_secretsearch(project, projdir)
    run_licence_check(project, projdir)

    if scanner:
        print ("IS SCANNER")
        if scanner == 'bandit':
            run_bandit(reports_dir, project, projdir)
        elif scanner == 'pmd':
            run_pmd(reports_dir, project, projdir)
            pass
        elif scanner == 'rats':
            run_rats(reports_dir, project, projdir)
        else:
            logger.error("%s is not a recognised scanner tool", scanner)
    else:
        print("NOT SCANNER")
        """Let's try to guess which scanner to use, by file extension"""
        for root, dirs, files in os.walk(projdir):
            for file in files:
                if file.endswith(".c"):
                    c = True
                elif file.endswith(".py"):
                    py = True
                elif file.endswith(".java"):
                    java = True
                elif file.endswith(".rb"):
                    rb = True
                elif file.endswith(".php"):
                    php = True
                elif file.endswith(".pl"):
                    perl = True
        # Project contains only python files
        if py and not (java or c):
            run_bandit(reports_dir, project, projdir)
        # Project contains c files
        if c and not java:
            run_rats(reports_dir, project, projdir)
        # Project contains only java files
        if java and not (py or c):
            run_pmd(reports_dir, project, projdir)
        # Project contains a mix of c and python
        if c and py and not java:
            run_rats(reports_dir, project, projdir)
        if rb or php or perl:
            run_rats(reports_dir, project, projdir)


def run_bandit(reports_dir, project, projdir):
    """Run's Bandit Python Scanner"""
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Bandit Scan on: {0}'.format(projdir))
    try:
        sh.bandit('-r', '-f', 'html', '-o', reports_dir + report, projdir)
    except sh.ErrorReturnCode, e:
        if e.exit_code != 4:
            logger.error(e.stderr)


def run_rats(reports_dir, project, projdir):
    """Run's RATS C / Python Scanner"""
    report = ('{0}_report.html'.format(project))
    logger.info('Performing Rats Scan on: {0}'.format(projdir))
    try:
        sh.rats('--html', projdir, '>', _out=(reports_dir + report))
    except sh.ErrorReturnCode, e:
        if e.exit_code != 4:
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
        if e.exit_code != 4:
            logger.error(e.stderr)


def run_binfind(project, projdir):
    """Find binaries within a repo, unless the binary
    is listed in the binaries"""
    logger.info('Checking for Binary files in project: {0}'.format(project))
    binaries = os.path.join(wk_dir + 'binaries.yaml')
    with open(binaries, 'r') as f:
        yl = yaml.safe_load(f)
        waiverlist = (yl['defaults']['files'])
        try:

            projlist = (yl[project]['files'])
            if projlist:
                waiverlist = waiverlist + projlist
                logger.info('Project waivers found for project: {0}'.format(project))
                logger.info('Applying for the following file waivers list: {0}'.format(projlist))
        except KeyError, e:
            logger.info('No project waivers for project: {0}'.format(project))

        for root, dirs, files in os.walk(projdir):
            for items in files:
                fullpath = os.path.join(root, items)
                bincheck = is_binary(fullpath)
                words_re = re.compile("|".join(waiverlist), flags=re.IGNORECASE)

                if not words_re.search(fullpath) and bincheck:
                    logger.error('Non white listed binary found: {0}'.format(fullpath))

                    with open("anteater-gate.log", "a") as gatereport:
                        gatereport.write('Non white listed binary found: {0}\n'.format(fullpath))


def run_secretsearch(project, projdir):
    """Searchs for banned strings and files that are listed
    in secretlist.yaml """
    secretlist = os.path.join(wk_dir + 'secretlist.yaml')

    with open(secretlist, 'r') as f:
        yl = yaml.safe_load(f)
        file_names = (yl['secrets']['file_names'])
        file_contents = (yl['secrets']['file_contents'])
        file_names_re = re.compile("|".join(file_names), flags=re.IGNORECASE)
        file_contents_re = re.compile("|".join(file_contents), flags=re.IGNORECASE)

        try:
            waiver_files = (yl['waivers'][project]['file_names'])
            if waiver_files:
                waiver_files_re = re.compile("|".join(waiver_files), flags=re.IGNORECASE)
                waiver_files_set = True
        except:
            waiver_files_set = False

        try:
            waiver_contents = (yl['waivers'][project]['file_contents'])
            if waiver_contents:
                waiver_contents_re = re.compile("|".join(waiver_contents), flags=re.IGNORECASE)
                waiver_contents_set = True
        except:
            waiver_contents_set = False

        logger.info('Checking for blaclisted file types and senstive data in project: {0}'.format(project))

        for root, dirs, files in os.walk(projdir):
            for items in files:
                fullpath = os.path.join(root, items)
                if waiver_files_set:
                    if not waiver_files_re.search(fullpath) and file_names_re.search(fullpath):
                        logger.info('Found what looks like a blacklisted file: {0}'.format(fullpath))
                        with open("anteater-gate.log", "a") as gatereport:
                            gatereport.write('Found what looks like a blacklisted file: {0}\n'.format(fullpath))
                else:
                    if file_names_re.search(fullpath):
                        logger.info('Found what looks like a blacklisted file: {0}'.format(fullpath))
                        with open('anteater-gate.log', "a") as gatereport:
                           gatereport.write('Found what looks like a blacklisted file: {0}\n'.format(fullpath))

                if not is_binary(fullpath):
                    fo = open(fullpath, 'r')
                    lines = fo.readlines()
                    for line in lines:
                        if waiver_contents_set:
                            if not waiver_contents_re.search(line) and file_contents_re.search(line):
                                logger.info('Found what looks like a senstive content in: {0}'.format(fullpath))
                                with open("anteater-gate.log", "a") as gatereport:
                                    gatereport.write('Found what looks like senstive data: {0}:\n'.format(fullpath))
                                    gatereport.write('String: {0}'.format(line))
                        else:
                            if file_contents_re.search(line):
                                logger.info('Found what looks like senstive data: {0}'.format(fullpath))
                                with open("anteater-gate.log", "a") as gatereport:
                                    gatereport.write('Found what looks like senstive data in: {0}:\n'.format(fullpath))
                                    gatereport.write('String: {0}'.format(line))


def run_licence_check(project, projdir):
    logger.info('Running Licence Check on: {0}'.format(project))
    for root, dirs, files in os.walk(projdir):
        for item in files:
            fullpath = os.path.join(root, item)
            if item.endswith(('.py', '.sh')):
                file_type = 'pybash'
                license_regex(fullpath, item, file_type)
            elif item.endswith(('.c', '.cc', '.cpp', '.h', '.java')):
                file_type = 'cjava'
                license_regex(fullpath, item, file_type)
            elif item.endswith('xml'):
                file_type = 'xml'
                license_regex(fullpath, item, file_type)
            elif item.endswith('patch'):
                file_type = 'patch'
                license_regex(fullpath, item, file_type)
            elif item.endswith('rst'):
                file_type = 'rst'
                license_regex(fullpath, item, file_type)


def license_regex(fullpath, item, file_type):
    with open(licence_templates, 'r') as f:
        yl = yaml.safe_load(f)
    template = (yl[file_type])

    fo = open(fullpath, 'r')
    content = fo.read()
    processed = re.sub(r'(?<=2017 )(.*)(?=and others)', '', content) # use a re.compile here
    if template in processed:
        logger.info('Licence Check passed for: {0}'.format(fullpath))
    else:
        logger.error('No License file within: {0}'.format(fullpath))
        with open("anteater-gate.log", "a") as gatereport:
            gatereport.write('No License File found within: {0}\n'.format(fullpath))
