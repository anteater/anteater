#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import sh
import yaml
import anteater.utils.anteater_logger as antlog

logger = antlog.Logger(__name__).getLogger()

with open('configs/projects.yml', 'r') as ymlcfg:
    cfg = yaml.safe_load(ymlcfg)
    projects = (cfg['projects'])


def url_formatter(arg):
    pass


def clone_all(repo_url):
    """ git clone all repositories listed in projects.yml """
    for project in projects:
        logger.info('Cloning {0}.'.format(project))
        # Lets move the below gerrit url to a variable
        url = repo_url + '/{0}'.format(project)
        projdir = 'repos/{0}'.format(project)
        try:
            sh.git.clone(url, projdir)
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def clone_project(repo_url, project):
    """ git clone repository given as arg """
    url = repo_url + '/{0}'.format(project)
    logger.info('Cloning: {0}'.format(url))
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git.clone(url, projdir)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def clone_project_url(url):
    print(url)
    """ git clone full URL  """
    projdir = 'repos/'
    try:
        os.chdir(projdir)
        sh.git.clone(url)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def pull_all(repo_url):
    """ git pull all repositories listed in projects.yml """
    for project in projects:
        logger.info('Performing pull on: {0}'.format(project))
        projdir = 'repos/{0}'.format(project)
        try:
            sh.git('-C', projdir, 'pull')
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def pull_project(repo_url, project):
    """ git pull repository given as arg """
    logger.info('Performing pull on: {0}'.format(project))
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git('-C', projdir, 'pull')
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
