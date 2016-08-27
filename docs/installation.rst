============
Installation
============

Operating System Requirements
-----------------------------

This tool is best run on a Linux distribution, it may work on Mac, but has not
been tested as yet.

The main OS package requirements are listed below

Fedora / Centos
---------------

Rats::

    sudo dnf install rats

VirtualEnv::

    sudo dnf install python-virtualenv

Git::

    sudo dnf install git

Ubuntu / Debian
---------------

<PENDING>

Install Anteater
----------------

Clone the repository:

    git clone https://github.com/lukehinds/anteater

Create a virtualenv::

    virtualenv env

Source (activate) the virtualenv::

    source env/bin/activate::

Install requirements::

    pip install -r requirements.txt

Install anteater::

    python setup.py install
