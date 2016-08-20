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

import logging
# from anteater import __version__
from src.git_tasks import clone_all, clone_project
from src.git_tasks import pull_all, pull_project
from src.scan_tasks import scan_all, scan_project

__author__ = "Luke Hinds"
__copyright__ = "Luke Hinds"
__license__ = "none"

_logger = logging.getLogger(__name__)


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
            scan_all()
        elif arguments['<project>']:
            scan_project(arguments['<project>'])
    elif arguments['pull']:
        if arguments['all']:
            pull_all()
        elif arguments['<project>']:
            pull_project(arguments['<project>'])
    else:
        print "didnae find nothing pal"


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
