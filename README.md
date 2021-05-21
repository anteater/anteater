# Anteater - CI/CD Gate Check Framework

![anteater](http://i.imgur.com/BPvV3Gz.png)

[![Build Status](https://travis-ci.org/anteater/anteater.svg?branch=master)](https://travis-ci.org/anteater/anteater)
[![Documentation Status](https://readthedocs.org/projects/anteater/badge/?version=latest)](http://anteater.readthedocs.io/en/latest/?badge=latest)

Description
-----------

Anteater is an open framework to prevent the unwanted merging of nominated strings,
filenames, binaries, depreciated functions, staging enviroment code / credentials
etc. Anything that can be specified with regular expression syntax, can be
sniffed out by anteater.

You tell anteater exactly what you don't want to get merged, and anteater looks
after the rest.

If anteater finds something, it exits with a non-zero code which in turn fails
the build of your CI tool, with the idea that it would prevent a pull request
merging. Any false positives are easily negated by using the
same RegExp framework to cancel out the false match.

Entire projects may also be scanned also, using a recursive directory walk.

With a few simple steps it can be easily implemented into a CI / CD workflow
with tooling such as [Travis CI](https://travis-ci.org/), [CircleCI](https://circleci.com/), [Gitlab CI/CD](https://about.gitlab.com/features/gitlab-ci-cd/) and [Jenkins](https://jenkins.io/).

It is currently used in the Linux Foundations project ['OPNFV'](https://opnfv.org)
as means to provide automated security checks at gate, but as shown in the
examples below, it can be used for other scenarios.

Anteater also provides integrates with the Virus Total API, so any binaries,
public IP addresses or URL's found by anteater, will be sent to the Virus Total
API and a report will be returned. If any object is reported as malicous,
it will fail the CI build job.

Example content is provided for those unsure of what to start with and its
encouraged and welcomed to share any Anteater filter strings you find useful.

Why would I want to use this?
-----------------------------

Anteater has many uses, and can easily be bent to cover your own specific needs.

First, as mentioned, it can be set up to block strings and files with a
potential security impact or risk. This could include private keys, a shell
history, aws credentials etc.

It is especially useful at ensuring that elements used in a staging /
development enviroment don't find there way into a production enviroment.

Let's take a look at some examples:

```
apprun:
  regex: app\.run\s*\(.*debug.*=.*True.*\)
  desc: "Running flask in debug mode could potentially leak sensitive data"
```

The above will match code where a flask server is set to running in debug mode
`` app.run(host='0.0.0.0' port=80 debug=true)``, which can be typical to a
developers enviroment and mistakenly staged into production.

For a rails app, this could be:

``  regex: \<%=.*debug.*%>``

Even more simple, look for the following in most logging frameworks:

`` regex: log\.debug``

Need to stop developers mistakenly adding a private key?

```
  private_key:
    regex: -----BEGIN\sRSA\sPRIVATE\sKEY----
    desc: "This looks like it could be a private key"
```

How about credential files that would cause a job loss if ever leaked into
production? Anteater works with file names too.

For Example:

``jenkins\.plugins\.publish_over_ssh\.BapSshPublisherPlugin\.xml``

Or even..

```
- \.pypirc
- \.gem\/credentials
- aws_access_key_id
- aws_secret_access_key
- LocalSettings\.php
```

If your app has its own custom secrets / config file, then its very easy to
add your own regular expressions. Everything is set using YAML formatting,
so no need to change anteaters code.

Depreciated functions, classes etc
----------------------------------

Another use is for when a project depreciates an old function, yet developers
might still make pull requests using the old function naming:

```
depreciated_function:``
  regex: depreciated_function\(.*\)
  desc: This function was depreciated in release X, use Y function.
```

Or perhaps stopping people from using 1.x versions of a framework:

``<script.src.*="https:\/\/ajax\.googleapis\.com\/ajax\/libs\/angularjs\/1.*<\/script>``

What if I get false postives?
-----------------------------

Easy, you set a RegExp to stop the match , kind of like RegExp'ception.

Let's say we want to stop use of MD5:

```
md245:
  regex: md[245]
  desc: "Insecure hashing algorithm"
```

This then incorrectly gets matched to the following:

``mystring = int(amd500) * 4``

We set a specific ignore RegEx, so it matches and then is unmatched by the
ignore entry.

``mystring.=.int\(amd500\).*``

Yet other instance of ``MD5`` continue to get flagged.

Binaries
--------

With anteater, if you pass the argument ``--binaries``, any binary found
causes a build failure on the originating pull request. It is not until a
sha256 checksum is set within anteater's YAML ignore files, that the build is
allowed to pass.

This means you can block people from checking in compiled objects, images, PDFs
etc that may have an unknown origin or tampering with the existing binary files.

An example:

```
$ anteater --binaries --project myproj --patchset /tmp/patch
Non Whitelisted Binary file: /folder/to/repo/images/pal.png
Please submit patch with this hash: 3aeae9c71e82942e2f34341e9185b14b7cca9142d53f8724bb8e9531a73de8b2
```
Let's enter the hash::
```
binaries:
  images/pal.png:
    - 3aeae9c71e82942e2f34341e9185b14b7cca9142d53f8724bb8e9531a73de8b2
```
Run the job again::
```
$ anteater --binaries --project myproj --patchset /tmp/patch
Found matching file hash for: /folder/to/repo/images/pal.png
```

This way we can sure binaries are not tampered with by means of a failed
cryptographic signature / checksum.

Any binaries not having a sha256 checksum will also be sent to the Virus Total
API for scanning.

Virus Total API
---------------

If the following flags (combined or individually) ``--ips``, ``-urls``, ``--binaries``
are used, anteater will perform a lookup to the Virus Total API.

IP addresses, will be have their DNS history checked for any previous or present connection
with known black listed domains marked as malicious or containing malware.

URLs, will be checked for any previous or present connection with known black listed domains
marked as malicious or containing malware.

As mentioned, Binaries will be sent to Virus Total and verified as clean / infected.

For more details and indepth documentation, please visit [readthedocs](http://anteater.readthedocs.io/en/latest/)

Last of all, if you do use anteater, I would love to know (twitter: @decodebytes)
and pull requests / issues are welcome!

Contribute
----------

Contributions are welcome.

Please make a pull request in a new branch, and not master.

```
git checkout -b mypatch
```

```
git push origin mypatch
```

Unit tests and PEP8 checks are in tox, so simply run the `tox` command before
pushing your code.

If your patch fixes and issue, please paste the issue url into the commit
message.

