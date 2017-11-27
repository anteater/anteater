#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017 Luke Hinds <lukehinds@gmail.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# from __future__ import division, print_function, absolute_import

"""Anteater - CI Gate Checks.

Usage:
  anteater [--bincheck] (-p |--project) <project> [(-ps |--patchset) <patchset>]
  anteater [--bincheck] (-p |--project) <project> [--path <project_path>]
  anteater (-h | --help)
  anteater --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from __future__ import absolute_import

import errno
import logging

import os
import six.moves.configparser
from docopt import docopt

from anteater import LOG
from anteater.src.patch_scan import prepare_patchset
from anteater.src.project_scan import prepare_project

config = six.moves.configparser.SafeConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')
__version__ = "0.14"
logger = logging.getLogger(__name__)


def _init_logging(anteater_log):
    """ Setup root logger for package """

    LOG.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                  '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)

    # create the directory if it does not exist
    path = os.path.dirname(anteater_log)
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    handler = logging.FileHandler(anteater_log)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    del logging.root.handlers[:]
    logging.root.addHandler(ch)
    logging.root.addHandler(handler)


def check_dir():
    """ Creates a directory for scan reports """
    try:
        os.makedirs(reports_dir)
        logger.info('Creating reports directory: %s', reports_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def main():
    """ Main function, mostly for passing arguments """
    _init_logging(config.get('config', 'anteater_log'))
    check_dir()
    arguments = docopt(__doc__, version=__version__)

    if arguments['<patchset>']:
        prepare_patchset(arguments['<project>'], arguments['<patchset>'],
                         arguments['--bincheck'])
    elif arguments['<project_path>']:
        prepare_project(arguments['<project>'], arguments['<project_path>'],
                        arguments['--bincheck'])


if __name__ == "__main__":
    main()
