#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import division, print_function, absolute_import
"""Anteater.

Usage:
  anteater scan all
  anteater scan <project>
  anteater clone all
  anteater clone <project>
  anteater pull all
  anteater pull <project>
  anteater(-h | --help)
  anteater --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
import os
import ConfigParser
# from anteater import __version__
from src.git_tasks import clone_all, clone_project
from src.git_tasks import pull_all, pull_project
from src.scan_tasks import scan_all, scan_project

__author__ = "Luke Hinds"
__copyright__ = "Luke Hinds"
__license__ = "none"

wk_dir = os.path.dirname(os.path.realpath('__file__'))

config = ConfigParser.RawConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')


def main():
    arguments = docopt(__doc__, version='Anteater 0.1')
    # print('Args: {0}'.format(arguments))
    if arguments['clone']:
        if arguments['all']:
            clone_all()
        elif arguments['<project>']:
            clone_project(arguments['<project>'])
    elif arguments['scan']:
        if arguments['all']:
            scan_all(reports_dir)
        elif arguments['<project>']:
            scan_project(reports_dir, arguments['<project>'])
    elif arguments['pull']:
        if arguments['all']:
            pull_all()
        elif arguments['<project>']:
            pull_project(arguments['<project>'])


if __name__ == "__main__":
    main()


'''
docopts reference
{'--help': False,
 '--version': False,
 '<project>': 'inspector',
 'all': False,
 'anteater': False,
 'scan': False,
 'clone': True,
 'pull': False}
'''
