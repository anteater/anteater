========
Anteater
========

![anteater](http://i.imgur.com/BPvV3Gz.png)

Mutlti Lang Code Auditing System
---------------------------

Note: Tool is still under active development.

Description
-----------

A multi language tool to perform secure code linting, insecure library check,
and provide assurity of meeting the Linux Foundation Core Infrastructure
Security Badge Programme.

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

    <snip>

Clone a single project

    $ anteater clone all

    Cloning <project A>

Pull (update all projects)

    $ anteater pull all

    Performing pull on: <project A>

    Performing pull on: <project B>

    <snip>

Pull a single project

    $ anteater pull <project A>

    Performing pull on: <project b>

Perform secure coding scan

    $ anteater audit <python project>

    Performing Bandit scan against <python project>

    $ anteater audit <java project>

    Performing PMD Scan on: <java project>

    $ anteater audit <C / C++ project>

    Performing Rats Scan on: <C / C++ project>
