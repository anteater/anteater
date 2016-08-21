========
Anteater
========

Security Audit System for OPNFV Projects.

![anteater](http://i.imgur.com/BPvV3Gz.png)

Description
-----------

Note: Tool is still under active development.

Security Code Audit system
---------------------------

A multi lanuague secure code linter, insecure library check, and assurity of
meeting Linux Foundation Core Infrastructure Security Badge Programme.

* Audits current libaries used, to allow an inventory check for known CVE's [WP]

* Performs code scanning with auto recgonition of lanuague used (scanners
    include Bandit (python), PMD (Java), Rats (C / C++))

* Allows easy git clone, pull operations from a single CLI.

* Peforms checks required to insure Linux Foundation Badge Requirements [WP]

[WP] Still pending work

Examples:

Clone all projects (listed within /configs/projects.yml)

    $ anteater clone all

    Cloning <project A>

    Cloning <project B>

    Cloning <project C>

    <snip>

Pull (update all projects)

    $ anteater pull all

    Performing pull on: <project A>

    Performing pull on: <project B>

    Performing pull on: <project C>

    <snip>

Pull just a single project

    $ anteater pull <project A>

    Performing pull on: <project b>

Perform secure coding scan

    $ anteater audit <python project>

    Performing Bandit scan against <python project>

    $ anteater audit <java project>

    Performing PMD Scan on: <java project>

    $ anteater audit <C / C++ project>

    Performing Rats Scan on: <C / C++ project>

Note
----

This project has been set up using PyScaffold 2.5.6. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
