=====================
Travis CI Integration
=====================

Set up steps
------------

First create an ```anteater.conf`` in the root directory of your repository::

    [config]
    anteater_files = anteater_files/
    reports_dir = %(anteater_files)s.reports/
    anteater_log = %(anteater_files)s/.reports/anteater.log
    flag_list =  %(anteater_files)s/flag_list.yaml
    ignore_list = %(anteater_files)s/ignore_list.yaml

``anteater_files``
------------------

``anteater_files`` is a location which anteater **wil not** scan.

The rationale about hiding this folder from anteater, is for the simple fact
anteater will report on the strings it uses itself as a guide for what to
search for.

``reports_dir`` & ``anteater_log``
----------------------------------

You can leave these as is, its a logging location used for when running the tool
locally.

``flag_list`` & ``ignore_list``
-------------------------------

``flag_list.yaml`` is where all regular expressions are set, that if matched
will fail the build, thereby marking a failure on the pull request page.

Some examples can be found here_.

.. _here: https://github.com/lukehinds/anteater/tree/master/examples

For information on ``flag_list``, please consult the :doc:`user_guide`

Travis Integration
------------------

All that is required now is to make the following entries to your yaml file::

    language: python

    python:
      - "2.7"

    install:
      - pip install anteater

    before_script:
      - git diff --name-only HEAD^ > ./patch
    script:
      - anteater --project antest --patchset ./patch


.. Note::

    Should you be using another language other then python (for example ruby), you
    can use ``matrix:include``

::

    matrix:
      include:
        - language: python
          python:
            - "2.7"
            - "3.6"

          install:
            - pip install anteater

          before_script:
            - git diff --name-only HEAD^ > ./patch

          script:
            - anteater --project antest --patchset ./patch

        - language: ruby
        # your project travis elements go here.

An example .travis.yml can be found here_.

.. _here: https://github.com/lukehinds/anteater/blob/master/examples/.travis.yml

Developer Workflow
------------------

1. Contributor forks , creates a branch

``git checkout -b mypullrequest``

2. Contributor commits and makes pull request

``git commit -m "My Pull Request"``
``git push origin mypullrequest``

3. A pull request is then made on the Contributors github page.

4. Travis CI runs anteater checks, checks fail.

5. Contributor addresses the failure.

``git commit -va -m "Correcting for anteater failures"``

6. Travis CI runs anteater again, and marks build as Passed.

7. Main developer see's test has passed, and merges Contributors pull request.