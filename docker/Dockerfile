##############################################################################
# Anteater Dockerfile
##############################################################################
# Copyright (c) 2017 Luke Hinds <lukehinds@gmail.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

FROM centos:latest
MAINTAINER Luke Hinds <lukehinds@gmail.com>
LABEL version="0.1" description="Anteater - CI Validation Framework"

# environment variables
ARG BRANCH=master
ARG ANTEATER_USER=antuser

# Anteater is run as user 'antuser'
RUN useradd -U -m -s /bin/bash ${ANTEATER_USER}

ENV HOME /home/${ANTEATER_USER}
ENV ANTEATER_HOME ${HOME}/anteater

# Packaged dependencies
RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install git python-devel python-pip python-virtualenv redis
RUN yum clean all

# Start Redis Server
RUN systemctl start redis

# Run all following commands and container as non-root user
USER ${ANTEATER_USER}

# Commands to clone and install
RUN mkdir -p ${ANTEATER_HOME}
RUN git clone https://github.com/anteater ${ANTEATER_HOME}
WORKDIR ${ANTEATER_HOME}
RUN virtualenv ~/venv
RUN . ~/venv/bin/activate
RUN ~/venv/bin/pip install -r ${ANTEATER_HOME}/requirements.txt
RUN ~/venv/bin/python ${ANTEATER_HOME}/setup.py install
