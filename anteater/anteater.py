#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017 Luke Hinds <lhinds@redhat.com>, Red Hat
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# from __future__ import division, print_function, absolute_import

"""Anteater - CI Gate Checks.

Usage:
  anteater (-p |--project) <project> [(-ps |--patchset) <patchset>]
  anteater (-p |--project) <project> [--path <project_path>]
  anteater (-h | --help)
  anteater --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import ConfigParser
from docopt import docopt
import os
from src.patch_scan import prepare_patchset
from src.project_scan import prepare_project
import utils.anteater_logger as antlog


config = ConfigParser.RawConfigParser()
config.read('anteater.conf')
reports_dir = config.get('config', 'reports_dir')
logger = antlog.Logger(__name__).getLogger()
__version__ = "0.1"


def check_dir():
    """ Creates a directory for scan reports """
    try:
        os.makedirs(reports_dir)
        logger.info('Creating reports directory: {0}'.format(reports_dir))
    except OSError as e:
        if not os.path.isdir(reports_dir):
            logger.error(e)


def main():
    """ Main function, mostly for passing arguments """
    check_dir()
    arguments = docopt(__doc__, version=__version__)

    if arguments['<patchset>']:
        prepare_patchset(arguments['<project>'], arguments['<patchset>'])
    elif arguments['<project_path>']:
        prepare_project(arguments['<project>'], arguments['<project_path>'])


if __name__ == "__main__":
    main()
