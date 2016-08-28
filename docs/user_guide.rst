==========
User Guide
==========

Configuration
-------------

Most of anteaters configuration exists witin ``anteater.conf``::

    reports_dir = /tmp/reports/
    JAVA_HOME = /usr/bin/java
    root_url = https://github.com/lukehinds

* ``reports_dir``: location for scanners to send HTML reports
* ``JAVA_HOME``: Standard Java Edition is fine
* ``root_url``: Used as base URL for each project in projects.yml (see 'Project
Wide Operations')

Methods of Operation
--------------------

There are two ways of working with repositories / scanning in aneater.

Project Wide Operations
~~~~~~~~~~~~~~~~~~~~~~~

If you wish to scan an entire organization / user, then you can set ``root_url``
in ``anteater.conf``.  This will then allow you to set a list projects in
``configs/projects.yml`` and perform 'all' operations, such as
``aneater clone all`` or ``anteater pull <project>``, ``anteater scan all``

Single Repo Operations
~~~~~~~~~~~~~~~~~~~~~~

A individual project can be cherry picked by passing the ``--url`` argument,
for example::

    anteater clone --url https://github.com/lukehinds/anteater

Git Operations
--------------

Clone an individual project::

    anteater clone <project>

Clone all project::

    anteater clone all

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
