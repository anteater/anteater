#!/usr/bin/env python
#
# jose.lausuch@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Logging levels:
#  Level     Numeric value
#  CRITICAL  50
#  ERROR     40
#  WARNING   30
#  INFO      20
#  DEBUG     10
#  NOTSET    0
#
# Usage:
#  import functest_logger as fl
#  logger = fl.Logger("script_name").getLogger()
#  logger.info("message to be shown with - INFO - ")
#  logger.debug("message to be shown with - DEBUG -")

import logging


class Logger:
    def __init__(self, logger_name):

        # CI_DEBUG = os.getenv('CI_DEBUG')
        CI_DEBUG = 'true'
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = 0
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # use the below for args
        if CI_DEBUG is not None and CI_DEBUG.lower() == "true":
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        self.logger.addHandler(ch)

        hdlr = logging.FileHandler('/tmp/anteater.log')
        hdlr.setFormatter(formatter)
        hdlr.setLevel(logging.DEBUG)
        self.logger.addHandler(hdlr)

    def getLogger(self):
        return self.logger
