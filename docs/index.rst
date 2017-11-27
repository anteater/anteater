=====================================
Anteater - CI/CD Gate Check Framework
=====================================

This is the documentation of Anteater - CI/CD Gate Check Framework .

Anteater is an application that is run as a gate / build check within a
continous Integration / DevOps deployment scenario.

It's main function is to block content based on regular expressions.

You can use it to protect against security risks, or automate a way of letting
developers know that their pull request contains content that is depreciated or
in some way no longer accepted by your project.

The tool can be run locally, or as a part of DevOps CI flow with systems such
as :doc:`travis_ci` or :doc:`circle_ci`, Jenkins etc.

Contents
========

.. toctree::
   :maxdepth: 2

   installation
   user_guide
   travis_ci
   circle_ci

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
