#######################################
# Anteater Dockerfile
########################################
# https://github.com/lukehinds/anteater

FROM fedora:latest
MAINTAINER Luke Hinds <lukehinds@gmail.com>
LABEL version="0.1" description="Anteater multi land code auditor"

# Packaged dependencies
RUN dnf update -y && dnf install \
git \
python-pip \
java \
rats \
-y

# Commands to clone and install
RUN git config --global http.sslVerify false
RUN git clone  https://github.com/lukehinds/anteater.git
WORKDIR "anteater"
RUN pip install -r requirements.txt
RUN python setup.py install
