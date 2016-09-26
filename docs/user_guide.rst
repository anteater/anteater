==========
User Guide
==========

Anteater is a wrapper framework around the following security lint scanners:

* Bandit (Python) https://github.com/openstack/bandit
* PMD (Java) https://pmd.github.io/
* Rats (C / C++) https://code.google.com/archive/p/rough-auditing-tool-for-security/

Anteater allows a user to quickly git clone / pull projects and then scan those
projects. Anteater will analyse the project files, and select the more suited
scanner to run (for example python projects are scanned with Bandit, C/C++ with
Rats Scanner).

Configuration
-------------

Most of anteaters configuration exists witin ``anteater.conf``::

    reports_dir = /tmp/reports/
    repos_dir = /tmp/repos
    JAVA_HOME = /usr/bin/java

* ``reports_dir``: location for scanners to send HTML reports
* ``repos_dir``: location where git repositories are cloned to. 
* ``JAVA_HOME``: Standard Java Edition is fine

Methods of Operation
--------------------

There are two ways of working with repositories / scanning in aneater.

Project Wide Operations
~~~~~~~~~~~~~~~~~~~~~~~

If you wish to clone an entire github user account to scan, then you can pass
``--ghuser`` argument to the commmand ``anteater clone all``.  This will then
pull all repositories under that github user account into the anteater/repos
directory.

Once a clone has taken place, the user can then scan all repositories with the
command ``anteater scan all``.

Alternatively a single repository can be scanned, by passing the repository
name with ``anteater scan <project>``


Single Repo Operations
~~~~~~~~~~~~~~~~~~~~~~

A individual project can be cherry picked by passing the ``--url`` argument,
for example::

    anteater clone --url https://github.com/lukehinds/insecure-python

Scanning
--------

All scans will self determine the language and scanner to use, unless the flag
--scanner is passed as an argument.

Self select scan of a Project::

    anteater scan <project>

Scan project while nominating a scanner::

    anteater scan <project> --scanner <bandit | pmd | rats>

Scan all projects using self selecting scan type::

    anteater scan all
