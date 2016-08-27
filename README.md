========
Anteater
========

[![Documentation Status](https://readthedocs.org/projects/anteater/badge/?version=latest)](http://anteater.readthedocs.io/en/latest/?badge=latest)

![anteater](http://i.imgur.com/BPvV3Gz.png)

Multi Lang Code Auditing System
---------------------------

Note: Tool is still under active development.

Description
-----------

A multi language tool to perform secure code linting, insecure library check,
and provide assurity of meeting the Linux Foundation Core Infrastructure
Security Badge Programme.

* Audits current libaries used, to allow an inventory check for known CVE's [WP]

* Performs vulnerability code scanning with auto recgonition of language:
    * Bandit (Python)
    * PMD (Java)
    * Rats (C / C++)


* Easy git clone, pull operations to assist quick scanning of repositories.

* Peforms checks required to insure Linux Foundation Badge Requirements [WP]

[WP] Still pending work

Examples:

Perform secure coding scan

    $ anteater audit <python project>

    Performing Bandit scan of: <python project>

    $ anteater audit <java project>

    Performing PMD Scan of: <java project>

    $ anteater audit <C / C++ project>

    Performing Rats Scan of: <C / C++ project>

Clone all projects (listed within /configs/projects.yml)

    $ anteater clone all

    Cloning <project A>

    Cloning <project B>

    <snip>

Clone a single project

    $ anteater clone <project A>

    Cloning <project A>

Pull (update all projects)

    $ anteater pull all

    Performing pull on: <project A>

    Performing pull on: <project B>

    <snip>

Pull a single project

    $ anteater pull <project A>

    Performing pull on: <project b>
