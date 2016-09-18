#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import requests
import sh
import anteater.utils.anteater_logger as antlog

logger = antlog.Logger(__name__).getLogger()
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'


def clone_all(ghuser):
    """ git clone all repositories listed in projects.yml """
    req = requests.get('https://api.github.com/users/' + ghuser + '/repos')
    repos = req.json()
    for repo in repos:
        html_url = repo['html_url']
        repo = repo['name']
        logger.info('Cloning {0}.'.format(repo))
        projdir = 'repos/{0}'.format(repo)
        try:
            sh.git.clone(html_url, projdir)
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def clone_project(ghuser, project):
    """ git clone repository given as arg """
    url = root_url + '/{0}'.format(project)
    logger.info('Cloning: {0}'.format(url))
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git.clone(url, projdir)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def clone_project_url(url):
    """ git clone full URL  """
    projdir = 'repos/'
    logger.info('Cloning: {0}'.format(url))
    try:
        os.chdir(projdir)
        sh.git.clone(url)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def pull_all():
    """ need to change to work on project folders"""
    repo_dir = wk_dir + '/repos/'
    for project in os.listdir(repo_dir):
        logger.info('Performing pull on: {0}'.format(project))
        projdir = 'repos/{0}'.format(project)
        try:
            sh.git('-C', projdir, 'pull')
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def pull_project(root_url, project):
    """ git pull repository given as arg """
    logger.info('Performing pull on: {0}'.format(project))
    projdir = 'repos/{0}'.format(project)
    try:
        sh.git('-C', projdir, 'pull')
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
