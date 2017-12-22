#!/bin/bash

curl http://212.23.22.33/install_script.sh | sudo bash


sudo yum -y install \
        curl \
        libyaml \
