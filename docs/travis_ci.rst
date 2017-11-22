=====================
Travis CI Integration
=====================


Set up steps
------------

To use anteater as a build check for any github pull requests, first start by
creating a main list and ignore list in the repository that you wish to monitor.

First create an `anteater.conf` in the root directory of your repository::

    [config]
    reports_dir =  .reports/
    anteater_log = .reports/anteater.log
    master_list =  ./check_list.yaml
    ignore_list =  ./ignore_list.yaml

reports_dir & anteater_log
--------------------------

You can leave this as is, its a logging location used for when running the tool
locally.

master_list
-----------

Master list is the regular expressions that if matched will fail the build,
thereby marking a failure on the github pull request page.

Some examples can be found at:

https://github.com/lukehinds/anteater/tree/master/examples

For more in depth details of creating your own entries, please consult the user
guide.

ignore_list
-----------

Ignore list is the regular expressions that if matched within the master list
can be 'waived' in the ignore list, thereby marking a failure on the github
pull request page. This actual file is more useful when dealing with multiple
projects, and so may not be relevant to a single project.

Some examples can be found at:

https://github.com/lukehinds/anteater/tree/master/examples

For more in depth details of creating your own ignore entries, please consult
the user guide.

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

*Note:*

Should you be using another language other then python (for example ruby), you
can use `matrix:include`, for example::

    matrix:
      include:
        - language: python
          python:
            - "2.7"
            - "pypy"

          install:
            - pip install anteater

          before_script:
            - git diff --name-only HEAD^ > ./patch

          script:
            - anteater --project antest --patchset ./patch

        - language: ruby
        # your project travis elements go here.

TODO: Add example projects on github.com/lukehinds
