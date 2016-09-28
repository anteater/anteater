============
Installation
============

Operating System Requirements
-----------------------------

This tool is best run on a Linux distribution, it may work on Mac, but has not been tested as yet. The recommended way is using docker, as that way it will
not interfere with your local systems package installations.

The main OS package requirements are listed below

Docker
------

Get the latest Dockerfile::

    wget https://raw.githubusercontent.com/lukehinds/anteater/master/docker/Dockerfile

Build the Image::

    docker build -t anteater .


Run an instance::

    docker run -t -i anteater /bin/bash

To retrieve the html reports, use docker cp::

    docker cp <containerId>:/file/path/reports /host/path/reports

Fedora / Centos
---------------

Rats::

    sudo dnf install rats

VirtualEnv::

    sudo dnf install python-virtualenv

Python Pip::

    sudo dnf install python-pip

Git::

    sudo dnf install git

Ubuntu / Debian
---------------

Work in progress:

    sudo apt-get install git, python-virtualenv, python-pip, rats

Install Anteater
----------------

Clone the repository:

    git clone https://github.com/lukehinds/anteater

Create a virtualenv::

    virtualenv env

Source (activate) the virtualenv::

    source env/bin/activate

Install requirements::

    pip install -r requirements.txt

Install anteater::

    python setup.py install
