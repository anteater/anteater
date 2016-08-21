========
Anteater
========

Security Audit System for OPNFV Projects.

![anteater](http://i.imgur.com/BPvV3Gz.png)

Description
-----------

Security Code Audit system (used on the OPNFV project).

* [WP] Audits current libaries used, to allow an inventory check for known CVE's

* Performs code scanning with auto recgonition of lanuague used (scanners
    include Bandit (python), PMD (Java), Rats (C / C++))

* Allows easy git clone, pull operations from a single CLI.

* [WP]Peforms checks required to insure Linux Foundation Badge Requirements

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
