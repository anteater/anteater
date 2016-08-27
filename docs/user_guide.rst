==========
User Guide
==========

Configuration
-------------

Most of anteaters configuration exists witin ``anteater.conf``::

    reports_dir = /tmp/reports/
    JAVA_HOME = /usr/bin/java
    repo_url = https://github.com/lukehinds

Projects are set within ``config/projects.yml``

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
