#!/usr/bin/env python
#
# jose.lausuch@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import logging


class Logger:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = 0
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

        hdlr = logging.FileHandler('/tmp/anteater.log')
        hdlr.setFormatter(formatter)
        hdlr.setLevel(logging.DEBUG)
        self.logger.addHandler(hdlr)

    def getLogger(self):
        return self.logger
