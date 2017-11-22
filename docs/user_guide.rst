==========
User Guide
==========


Configuration
-------------

Most of anteaters configuration exists witin ``anteater.conf``::

    [config]
    reports_dir =  .reports/
    anteater_log = .reports/anteater.log
    flag_list =  ./flag_list.yaml
    ignore_list = ./ignore_list.yaml

* ``reports_dir``: location for anteater to send reports
* ``anteater_log``: location where anteater logging framework writes to.
* ``flag_list``: The main list of regexp's are listed. See RegExp Framework
  for more details.
* ``ignore_list``: The main list of regexp's which are ignored,
  thereby in effect overwriting ``flag_list`` and removing false postives.
  Note that ignore_list is only really useful when you're running multiple
  projects.

Methods of Operation
--------------------

Anteater has a simple argument system, using a standard POSIX format.

The main usage  parameters are ``--project`` and either ``---path``
--patchset``.

Anteater always requires a project name passwed with the ``--project`` argument.
The project argument is used for multiple reasons. Its allows a multiple project
scenario for a gerrit multi account deployment and also allows seperation for
repors.

Anteater can be run with by two methods, ``--patchset`` or ``--path``. When
``--patchset`` is passed as an argument, it is expected that a text file be
provided that consists of a list of files, using a relative or full POSIX path.
Anteater will then iterate scans over each file, with the files seperated by
a new line. For example::

    % cat /tmp/patchset
    /home/luke/repos/myrepo/fileone.sh
    /home/luke/repos/myrepo/filetwo.sh
    /home/luke/repos/myrepo/filethree.txt

This would then be called with::

    anteater --project myrepo --patchset /tmp/patchset

When ``--path`` is  provided, the argument should be a single relative or full POSIX
path to your repositories folder. Anteater will then perform a recursive walk through all files in the
projects folder. For example::

    anteater --project myproject --path /home/luke/repos/myrepo

RegExp Framework and the flag_list
==================================

The RegExp Framework is a YAML formatted file which is declared in
``anteater.conf`` under the directive ``flag_list``.

Examples of these files can be found under
https://github.com/lukehinds/anteater/examples.

binary_ignore
-------------

``binary_ignore`` is a list (using ``-`` seperators to each new line) of binary
files that can be ignored. Using the example above, we  ignore all of the git
artefacts present in all git repositories. You will also note that the string is
using standard regular expression formatting::

    binaries:
      binary_ignore:
      - \.git/(index|objects)

file_audits
-----------

``file_audits`` is a list of full filenames to flag by anteater. For example,
the following would flag someones shell history::

    file_audits:
        file_names:
          - (irb|plsq|mysql|bash|zsh)_history

If a user then accidently checks in a ``zsh_history`` then anteater will flag
this.

file_contents
-------------

``file_contents`` is a list of regular expression strings that will be searched
for within any file type that is not a binary / blob.

The structure of the file is as follows::

   file_contents:
      unique_name:
          regex: <Regular Expression to Match>
          desc: <Line of text to describe the rationale behind flagging the string>

The following would be examples for ensuring no insecure cryptos are used and
a depreciated function is also flagged::

  file_contents:
    md245:
      regex: md[245]
      desc: "Insecure hashing algorithm"

      depreciated_function:
        regex: depreciated_function\(.*\)
        desc: This function was depreciated in release X, use Y function.

So the above would match the following lines::

    depreciated_function(some_value):

    hashlib.md5(myhash)

Exceptions
==========

Exceptions are made using ``ignore_list`` and allow you to overule a string 
set within the ``flag_list`` file and address false postives. The format is
very similiar to the above cases to set strings that are flagged, but in
this case a specific regular expression can be used to stop a specific flag
from being raised.

file_name exceptions
--------------------

TD

file_contents exceptions
------------------------

``file_contents`` exceptions are used to cancel out a ``flag_list`` entry by
using a regular expression that matches a unique string that has been
incorrectly flagged and is a false positive.

Let's say we wish to have some control over git repositories that can be cloned.

First we make an entry in the ``flag_list`` around git clone::

    clone:
      regex: git.*clone
      desc: "Clone blocked as using an non approved external source"

The above would flag any instance of a clone, for example::

    git clone http://github.com/someuser/somerepo.git

Now let's assume we want to allow all clones from a specific github org called
'acme', but no other github repositories.

We could do this by using the following Exception::

   - git clone https:\/\/github\.com\\acme\\.+

This would then allow the following strings::

    git clone https://github.com/acme/repository
    git clone https://github.com/acme/another_repository

binary exceptions
-----------------

By default, anteater blocks all binary files unless a sha256 checksum of the
file is entered as an exeception. This is done using the relative path from the
root of the respository. For example::

  media/images/weather-storm.png:
    - 48f38bed00f002f22f1e61979ba258bf9006a2c4937dde152311b77fce6a3c1c
  media/images/stop_light.png:
    - 5a1101e8b1796f6b40641b90643d83516e72b5b54b1fd289cf233745ec534ec9
