#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import os
import requests
import sh
import anteater.utils.anteater_logger as antlog

logger = antlog.Logger(__name__).getLogger()
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'


def clone_all(ghuser, repos_dir):
    """ git clone all repositories listed in projects.yml """
    req = requests.get('https://api.github.com/users/' + ghuser + '/repos')
    repos = req.json()
    try:
        os.chdir(repos_dir)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
    for repo in repos:
        html_url = repo['html_url']
        repo = repo['name']
        logger.info('Cloning {0}.'.format(repo))
        try:
            sh.git.clone(html_url)
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def clone_project(ghuser, project, repos_dir):
    """ git clone repository given as arg """
    url = 'https://github.com/' + ghuser + '/' + project
    logger.info('Cloning: {0}'.format(project))
    try:
        os.chdir(repos_dir)
        sh.git.clone(url)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def clone_project_url(url, repos_dir):
    """ git clone full URL  """
    logger.info('Cloning: {0}'.format(url))
    try:
        os.chdir(repos_dir)
        sh.git.clone(url)
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)


def pull_all(repos_dir):
    """ need to change to work on project folders"""
    for project in os.listdir(repos_dir):
        logger.info('Performing pull on: {0}'.format(project))
        try:
            os.chdir(repos_dir)
            sh.git('-C', repos_dir, 'pull')
        except sh.ErrorReturnCode, e:
            logger.error(e.stderr)


def pull_project(repos_dir, project):
    """ git pull repository given as arg """
    logger.info('Performing pull on: {0}'.format(project))
    try:
        os.chdir(repos_dir)
        sh.git('-C', repos_dir, 'pull')
    except sh.ErrorReturnCode, e:
        logger.error(e.stderr)
