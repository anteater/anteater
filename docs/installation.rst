============
Installation
============

Operating System Requirements
-----------------------------

This tool is best run on a Linux distribution, it may work on Mac, but has not
been tested as yet. The recommended way is using docker, as that way it will
not interfere with your local systems package installations.

The main OS package requirements are listed below.

.. Note::
    If you only intend to use anteater as part of a Travis CI / CircleCI gate,
    then you can likely bypass this chapter which is more centered on
    installation for self hosted CI enviroments. See :doc:`travis_ci` or
    :doc:`circle_ci` for setup details.
    details.

Docker
------

Get the latest Dockerfile (read the Dockerfile first before running!)::

    wget https://raw.githubusercontent.com/lukehinds/anteater/master/docker/Dockerfile

Build the Image::

    docker build -t anteater .


Run an instance::

    docker run -t -i anteater /bin/bash

Or to run from a job::

    PROJECT="myrepo"
    git diff --name-only HEAD^ > /tmp/patch
    vols="-v /home/user/repos/$PROJECT"
    docker run -i $vols ~/venv/bin/anteater --project $PROJECT --patchset /tmp/patch"

Install Anteater
----------------

The best method to install anteater, is via pip::

    pip install anteater

Contribute
----------

All contributions must be made as pull requests from your forked repository of
anteater.

To install from source (recommend a virtualenv for isolation / non root use):

Install requirements::

    pip install -r requirements.txt

Install anteater::

    python setup.py install
