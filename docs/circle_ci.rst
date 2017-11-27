=====================
CircleCI Integration
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

``flag_list.yaml`` is where regular expressions are set, that if matched will
fail the build, thereby marking a failure on the github pull request page.

More examples can be found `here <https://github.com/lukehinds/anteater/blob/master/examples/>`_.

For information on ``flag_list``, please consult the :doc:`user_guide`

CircleCI Integration
--------------------

All that is required now is to make the following entries to your CircleCI
configuration file ``.circleci/config.yml``::

    # Python CircleCI 2.0 configuration file
    #
    # Check https://circleci.com/docs/2.0/language-python/ for more details
    #
    version: 2
    jobs:
      build:
        docker:
          # specify the version you desire here
          # use `-browsers` prefix for selenium tests, e.g. `3.6.1-browsers`
          - image: circleci/python:2.7

          # Specify service dependencies here if necessary
          # CircleCI maintains a library of pre-built images
          # documented at https://circleci.com/docs/2.0/circleci-images/
          # - image: circleci/postgres:9.4

        working_directory: ~/repo

        steps:
          - checkout

          # Download and cache dependencies
          - restore_cache:
              keys:
              - v1-dependencies-{{ checksum "requirements.txt" }}
              # fallback to using the latest cache if no exact match is found
              - v1-dependencies-

          - run:
              name: install dependencies
              command: |
                virtualenv ~/venv
                . ~/venv/bin/activate
                pip install -r requirements.txt
                git diff --name-only HEAD^ > ~/repo/patchset

          - save_cache:
              paths:
                - ./venv
              key: v1-dependencies-{{ checksum "requirements.txt" }}

          # run tests!
          - run:
              name: run tests
              command: |
                . ~/venv/bin/activate
                anteater --project ci-circle --patchset ~/repo/patchset

          - store_artifacts:
              path: test-reports
              destination: test-reports

An example config.yml can be found `here <https://github.com/lukehinds/anteater/blob/master/examples/config.yml>`_.

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