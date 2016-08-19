========
Anteater
========

Security Audit System for OPNFV Projects.

Description
-----------

Security Code Audit system (used on the OPNFV project).

* Audits current libaries used, to allow an inventory check for known CVE's

* Performs code scanning (currently using Bandit and Rats).

* Allows easy clone, pull operations from a single CLI.

Examples:

    $ anteater clone all
    Cloning inspector.
    Cloning doctor.
    Cloning promise.

    $ anteater pull all
    Performing pull on: inspector
    Performing pull on: doctor
    Performing pull on: promise

    $ anteater pull inspector
    Performing pull on: inspector

    $ anteater audit inspector
    Performing Bandit scan against inspector

Note
----

This project has been set up using PyScaffold 2.5.6. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
