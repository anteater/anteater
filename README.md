========
Anteater
========

[![Documentation Status](https://readthedocs.org/projects/anteater/badge/?version=latest)](http://anteater.readthedocs.io/en/latest/?badge=latest)

![anteater](http://i.imgur.com/BPvV3Gz.png)

Multi Lang Code Auditing System
-------------------------------

Description
-----------

Performs vulnerability code scanning with auto recgonition of language:

* Bandit (Python) https://github.com/openstack/bandit
* PMD v 5.5.1 (Java) https://pmd.github.io/
* Rats (C / C++, Ruby, Perl, PHP) https://code.google.com/archive/p/rough-auditing-tool-for-security/

Searchs repositories for compiled binaries, private keys, passwords and senstive strings

Provides exeception / waiver lists to whitelist files, data.

Provides option to add own file types for white / blacklisting

Features:

* Easy git clone, pull operations to assist quick scanning of repositories.

* Finds low hanging fruit (dodgy shell executions, xss attacks etc)

* Each scan renders full html report.

Consult the [Documentation](http://anteater.readthedocs.io/en/latest/) on how to use
