#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import division, print_function, absolute_import
"""Anteater.

Usage:
  anteater pull all
  anteater pull <project>
  anteater scan all
  anteater scan all --scanner <scanner>
  anteater scan <project>
  anteater scan <project> --scanner <scanner>
  anteater clone all --ghuser <ghuser>
  anteater clone --ghuser <ghuser> --project <project>
  anteater clone --url <url>
  anteater(-h | --help)
  anteater --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import ConfigParser
from docopt import docopt
from src.git_tasks import clone_all, clone_project, clone_project_url
import os
from src.git_tasks import pull_all, pull_project
from src.scan_tasks import scan_all, scan_project
import utils.anteater_logger as antlog

config = ConfigParser.RawConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')
repos_dir = config.get('config', 'repos_dir')
wk_dir = os.path.dirname(os.path.realpath('__file__')) + '/'
logger = antlog.Logger(__name__).getLogger()
os.environ["JAVA_HOME"] = (config.get('config', 'JAVA_HOME'))
__version__ = "0.1.0"


def print_symbol():
    print("""\


     █████╗ ███╗   ██╗████████╗███████╗ █████╗ ████████╗███████╗██████╗
    ██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
    ███████║██╔██╗ ██║   ██║   █████╗  ███████║   ██║   █████╗  ██████╔╝
    ██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██║   ██║   ██╔══╝  ██╔══██╗
    ██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║   ██║   ███████╗██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    Multi Lang Code Auditing System https://github.com/lukehinds/anteater
    """)


def check_dir():
    '''
    Creates a directory for scan reports
    '''
    try:
        os.makedirs(reports_dir)
        logger.info('Creating reports directory: {0}'.format(reports_dir))
    except OSError:
        if not os.path.isdir(reports_dir):
            pass
    try:
        os.makedirs(repos_dir)
        logger.info('Creating repository directory: {0}'.format(repos_dir))
    except OSError:
            pass


def main():
    print_symbol()
    """ Main function, mostly for passing arguments """
    check_dir()
    arguments = docopt(__doc__, version='Anteater 0.1')
    if arguments['pull']:
        if arguments['all']:
            pull_all(repos_dir)
        elif arguments['<project>']:
            pull_project(arguments['<project>'], repos_dir)
    elif arguments['clone']:
        if arguments['all']:
            clone_all(arguments['<ghuser>'], repos_dir)
        elif arguments['<ghuser>']:
            clone_project(arguments['<ghuser>'], arguments['<project>'],
                          repos_dir)
        elif arguments['<url>']:
            clone_project_url(arguments['<url>'], repos_dir)
    elif arguments['scan']:
        if arguments['all']:
            scan_all(reports_dir, repos_dir)
        elif arguments['<project>']:
            if arguments['<scanner>'] == "":
                scan_project(reports_dir, arguments['<project>'])
            else:
                scan_project(reports_dir, arguments['<project>'],
                             arguments['<scanner>'], repos_dir)


if __name__ == "__main__":
    main()
